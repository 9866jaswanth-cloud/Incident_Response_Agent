"""Foundation test verifying Phase 1 backend setup and imports."""

import pytest
from app.core.config import settings
from app.main import app
from hindsight_client import Hindsight, RecallResponse, RetainResponse


def test_settings_loaded():
    assert settings.PROJECT_NAME == "Incident Response Agent"
    assert settings.HINDSIGHT_BANK_ID == "incident-response-bank"
    assert settings.HINDSIGHT_BASE_URL == "http://localhost:8888"


def test_fastapi_app_created():
    assert app.title == "Incident Response Agent"


def test_hindsight_sdk_methods_available():
    # Verify official async methods exist on Hindsight client class
    assert hasattr(Hindsight, "aretain")
    assert hasattr(Hindsight, "arecall")
    assert hasattr(Hindsight, "areflect")
    assert hasattr(Hindsight, "aclose")
