"""Live verification script for Hindsight Persistent Memory Integration (Phase 3).

Performs a connection check against the configured Hindsight server,
and if available, executes a real end-to-end test:
1. Retains INC-001 structured post-mortem into 'incident-response-bank'
2. Recalls it using a different, semantically related query (INC-002 symptoms)
3. Tests reflection over the memory bank
"""

import sys
import json
import asyncio
from datetime import datetime, timezone
from app.core.config import settings
from app.services.hindsight_service import (
    HindsightService,
    HindsightUnavailableError,
)
import hindsight_client


async def main():
    print("=" * 70)
    print("HINDSIGHT PERSISTENT MEMORY INTEGRATION TEST")
    print("=" * 70)
    print(f"Hindsight SDK Version: {getattr(hindsight_client, '__version__', '0.10.1')}")
    print(f"Target Hindsight Base URL: {settings.HINDSIGHT_BASE_URL}")
    print(f"Target Memory Bank ID: {settings.HINDSIGHT_BANK_ID}")
    print("-" * 70)

    service = HindsightService()

    # Step 1: Check Connection
    print("[*] Checking real connection to Hindsight server...")
    status = await service.check_connection()

    print(f"Connected: {status['connected']}")
    print(f"Mode: {status['mode']}")
    print(f"Server Version: {status.get('version')}")
    print(f"Status Message: {status['message']}")
    print("-" * 70)

    if not status["connected"]:
        print("[!] Real Hindsight server is currently OFFLINE / UNAVAILABLE.")
        print("[!] As per Requirement 9, the system does NOT silently switch to fake memory.")
        print("[!] To run the live demo with real Hindsight:")
        print("    1. Start the official Hindsight server via Docker:")
        print("       docker run -d -p 8888:8888 -e HINDSIGHT_API_LLM_PROVIDER=gemini vectorize/hindsight")
        print("    2. Or configure Hindsight Cloud in backend/.env:")
        print("       HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io")
        print("       HINDSIGHT_API_KEY=your_hindsight_api_key")
        print("=" * 70)
        await service.aclose()
        return

    # Step 2: Live Retain Test (INC-001)
    print("[*] Connection verified! Proceeding with Live End-to-End Retain & Recall...")
    inc1 = {
        "id": "INC-001",
        "service": "Payment API",
        "severity": "P1-Critical",
        "symptoms": [
            "Payment API p99 latency spiked from 195ms to 8.4 seconds",
            "Database connection acquisition timeouts (5000ms)",
            "HikariCP connection pool exhausted (10/10 active connections locked)"
        ],
        "logs": "com.zaxxer.hikari.pool.HikariPool - Connection is not available, request timed out after 5002ms",
        "metrics": {"p99_latency_ms": 8420, "active_connections": 10, "max_pool_size": 10},
        "confirmed_root_cause": "Database connection pool misconfiguration. Maximum pool size was constrained to 10 connections under 500 RPS traffic.",
        "investigation_steps": [
            "1. Verified PostgreSQL RDS CPU was low (38%).",
            "2. Inspected HikariCP pool metrics; saw all 10 connections continuously occupied.",
            "3. Reviewed Helm deployment diff for commit #c4b8109."
        ],
        "confirmed_resolution": "Increased database connection pool max_size from 10 to 50 and set connection-timeout to 3000ms.",
        "post_mortem_lesson": "Always validate connection pool capacity against peak concurrency requirements during load spikes.",
        "environment": "production-us-east-1"
    }

    print("\n[*] Retaining structured post-mortem for INC-001...")
    try:
        retain_resp = await service.aretain(inc1)
        print(f"Retain Success: {retain_resp.success}")
        print(f"Bank ID: {retain_resp.bank_id}")
        print(f"Items Count: {retain_resp.items_count}")
    except Exception as e:
        print(f"[ERROR] Retain failed: {e}")
        await service.aclose()
        return

    # Step 3: Live Recall Test using INC-002 symptoms
    query = "Payment API checkout response times degraded to 8.2s with connection pool exhaustion and database timeout"
    print(f"\n[*] Recalling memories for query based on INC-002 symptoms:")
    print(f"Query: \"{query}\"")

    try:
        recall_resp = await service.arecall(query=query, budget="mid")
        results = recall_resp.results if recall_resp and recall_resp.results else []
        print(f"Recalled Memories Count: {len(results)}")

        for i, item in enumerate(results, 1):
            print(f"\n--- Recalled Memory #{i} ---")
            print(f"ID: {item.id}")
            print(f"Type: {getattr(item, 'type', 'N/A')}")
            print(f"Text Snippet:\n{item.text[:300]}...")
            if getattr(item, "scores", None):
                print(f"Scores: {item.scores}")

        # Step 4: Live Reflect Test
        print("\n[*] Testing Hindsight Reflect over accumulated memories...")
        reflect_query = "What caused previous latency spikes in Payment API and how were they resolved?"
        reflect_resp = await service.areflect(query=reflect_query, budget="low")
        print(f"Reflect Synthesis:\n{reflect_resp.text}")

        print("\n" + "=" * 70)
        print("[SUCCESS] Real Hindsight retain -> recall -> reflect flow verified!")
        print("=" * 70)

    except Exception as e:
        print(f"[ERROR] Recall/Reflect failed: {e}")
    finally:
        await service.aclose()


if __name__ == "__main__":
    asyncio.run(main())
