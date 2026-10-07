"""Dedicated Hindsight Persistent Memory Integration Service.

Interacts with the official Hindsight SDK (hindsight_client.Hindsight) by Vectorize.io.
Provides asynchronous methods (aretain, arecall, areflect) for FastAPI endpoints.
Strictly reports server status and NEVER silently substitutes fake memory systems.
"""

import logging
import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union
from hindsight_client import (
    Hindsight,
    RecallResponse,
    RecallResult,
    RetainResponse,
    ReflectResponse,
)
from app.core.config import settings

logger = logging.getLogger("hindsight_service")


class HindsightUnavailableError(Exception):
    """Raised when an operation is attempted while the Hindsight server is unreachable."""
    pass


class HindsightService:
    """Service wrapping the official Hindsight client with connection resilience and structured incident schemas."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        bank_id: Optional[str] = None,
    ):
        self.base_url = (base_url or settings.HINDSIGHT_BASE_URL).rstrip("/")
        self.api_key = api_key or settings.HINDSIGHT_API_KEY or None
        self.bank_id = bank_id or settings.HINDSIGHT_BANK_ID or "incident-response-bank"
        self._client: Optional[Hindsight] = None
        self._loop = None

    async def get_client(self) -> Hindsight:
        """Lazily initialize and return the official Hindsight client."""
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        if self._client is None or getattr(self, "_loop", None) != current_loop:
            logger.info(
                f"Initializing official Hindsight client (bank: {self.bank_id}) pointing to {self.base_url}"
            )
            self._client = Hindsight(
                base_url=self.base_url,
                api_key=self.api_key,
                timeout=30.0,
            )
            self._loop = current_loop
        return self._client

    async def aclose(self) -> None:
        """Gracefully close the underlying Hindsight HTTP client session."""
        if self._client is not None:
            try:
                await self._client.aclose()
            except Exception as e:
                logger.warning(f"Error closing Hindsight client: {e}")
            finally:
                self._client = None
                self._loop = None


    async def check_connection(self) -> Dict[str, Any]:
        """
        Check if the REAL Hindsight server is reachable.
        Calls aget_version() on the server to verify API responsiveness.
        NEVER reports connected if the server is offline.
        """
        client = await self.get_client()
        try:
            # Check version with a short timeout to prevent blocking during health checks
            version_response = await asyncio.wait_for(client.aget_version(), timeout=3.5)
            version_str = getattr(version_response, "version", "available")
            return {
                "connected": True,
                "base_url": self.base_url,
                "bank_id": self.bank_id,
                "version": str(version_str),
                "mode": "REAL_HINDSIGHT",
                "message": f"Real Hindsight server connected successfully at {self.base_url} (Version: {version_str}).",
            }
        except Exception as e:
            logger.debug(f"Hindsight server connection failed at {self.base_url}: {e}")
            return {
                "connected": False,
                "base_url": self.base_url,
                "bank_id": self.bank_id,
                "version": None,
                "mode": "UNAVAILABLE",
                "message": (
                    f"Real Hindsight server is NOT reachable at {self.base_url}. "
                    "Start a Hindsight instance (e.g. docker run -p 8888:8888 vectorize/hindsight) "
                    "or set HINDSIGHT_BASE_URL to your Hindsight Cloud endpoint."
                ),
                "error_details": str(e),
            }

    @staticmethod
    def format_incident_post_mortem(incident: Union[Dict[str, Any], Any]) -> str:
        """
        Format a confirmed incident into a structured post-mortem document.
        Structures key facts, entities, symptoms, root cause, and lessons
        for Hindsight entity-graph and causal extraction.
        """
        if hasattr(incident, "__dict__"):
            inc_id = getattr(incident, "id", "UNKNOWN")
            service = getattr(incident, "service", "UNKNOWN")
            severity = getattr(incident, "severity", "UNKNOWN")
            symptoms = getattr(incident, "symptoms", [])
            root_cause = getattr(incident, "confirmed_root_cause", None) or "Unconfirmed"
            resolution = getattr(incident, "confirmed_resolution", None) or "Unconfirmed"
            investigation_steps = getattr(incident, "investigation_steps", []) or []
            lesson = getattr(incident, "post_mortem_lesson", None) or "None recorded"
            logs = getattr(incident, "logs", "")
            metrics = getattr(incident, "metrics", {})
            env = getattr(incident, "environment", "production")
        else:
            inc_id = incident.get("id", "UNKNOWN")
            service = incident.get("service", "UNKNOWN")
            severity = incident.get("severity", "UNKNOWN")
            symptoms = incident.get("symptoms", [])
            root_cause = incident.get("confirmed_root_cause") or "Unconfirmed"
            resolution = incident.get("confirmed_resolution") or "Unconfirmed"
            investigation_steps = incident.get("investigation_steps", [])
            lesson = incident.get("post_mortem_lesson") or "None recorded"
            logs = incident.get("logs", "")
            metrics = incident.get("metrics", {})
            env = incident.get("environment", "production")

        symptoms_str = "\n".join([f"- {s}" for s in symptoms]) if isinstance(symptoms, list) else str(symptoms)
        steps_str = "\n".join([f"- {step}" for step in investigation_steps]) if investigation_steps else "- SRE verified telemetry and applied resolution."

        # Keep a concise summary of metrics
        metrics_summary = ", ".join([f"{k}={v}" for k, v in list(metrics.items())[:6]]) if metrics else "No metrics recorded"

        # Extract top 3 lines of logs for context
        log_sample = "\n".join(logs.strip().splitlines()[:3]) if logs else "No logs"

        return (
            f"=== INCIDENT POST-MORTEM EXPERIENCE: {inc_id} ===\n"
            f"Incident ID: {inc_id}\n"
            f"Target Service: {service}\n"
            f"Severity Level: {severity}\n"
            f"Environment: {env}\n"
            f"Observed Symptoms:\n{symptoms_str}\n\n"
            f"Key Telemetry & Logs:\n{log_sample}\nMetrics: {metrics_summary}\n\n"
            f"Confirmed Root Cause:\n{root_cause}\n\n"
            f"Investigation Steps Executed by SRE:\n{steps_str}\n\n"
            f"Confirmed Successful Resolution:\n{resolution}\n\n"
            f"Operational Outcome:\nIncident successfully resolved. System returned to healthy operating baseline.\n\n"
            f"Post-Mortem Lessons Learned:\n{lesson}\n"
            f"=== END OF POST-MORTEM: {inc_id} ==="
        )

    async def aretain(
        self,
        incident: Union[Dict[str, Any], Any],
        custom_content: Optional[str] = None,
        context: Optional[str] = None,
    ) -> RetainResponse:
        """
        Retain an incident experience into the Hindsight memory bank.
        Uses the official asynchronous aretain method.
        """
        client = await self.get_client()
        content = custom_content or self.format_incident_post_mortem(incident)

        inc_id = getattr(incident, "id", None) if hasattr(incident, "__dict__") else incident.get("id")
        service = getattr(incident, "service", None) if hasattr(incident, "__dict__") else incident.get("service")

        tags = ["incident-experience"]
        if service:
            tags.append(service.lower().replace(" ", "-"))

        try:
            response = await client.aretain(
                bank_id=self.bank_id,
                content=content,
                document_id=inc_id,
                context=context or f"Post-mortem experience for incident {inc_id} in {service}",
                tags=tags,
                retain_async=False,
            )
            logger.info(f"Retained incident {inc_id} into Hindsight bank '{self.bank_id}'. Success: {response.success}")
            return response
        except Exception as e:
            logger.error(f"Hindsight aretain failed for {inc_id} at {self.base_url}: {e}")
            raise HindsightUnavailableError(f"Hindsight aretain failed: {e}") from e

    async def arecall(
        self,
        query: str,
        budget: str = "mid",
        max_tokens: int = 4096,
        types: Optional[List[str]] = None,
    ) -> RecallResponse:
        """
        Recall relevant historical incident memories from Hindsight based on a query.
        Uses the official asynchronous arecall method.
        """
        client = await self.get_client()
        try:
            response = await client.arecall(
                bank_id=self.bank_id,
                query=query,
                budget=budget,
                max_tokens=max_tokens,
                types=types,
            )
            count = len(response.results) if response and response.results else 0
            logger.info(f"Recalled {count} memories from Hindsight bank '{self.bank_id}' for query: '{query[:60]}...'")
            return response
        except Exception as e:
            logger.error(f"Hindsight arecall failed at {self.base_url}: {e}")
            raise HindsightUnavailableError(f"Hindsight arecall failed: {e}") from e

    async def areflect(
        self,
        query: str,
        budget: str = "low",
    ) -> ReflectResponse:
        """
        Perform reflective reasoning over memories in the Hindsight bank.
        Uses the official asynchronous areflect method.
        """
        client = await self.get_client()
        try:
            response = await client.areflect(
                bank_id=self.bank_id,
                query=query,
                budget=budget,
            )
            return response
        except Exception as e:
            logger.error(f"Hindsight areflect failed at {self.base_url}: {e}")
            raise HindsightUnavailableError(f"Hindsight areflect failed: {e}") from e


# Singleton service instance configured from environment
hindsight_service = HindsightService()
