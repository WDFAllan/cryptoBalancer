from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import pandas as pd

from app.main import app
from app.api.v1.controllers import backtestController

client = TestClient(app)


def test_run_any_strategy_returns_records():
    mock_service = MagicMock()
    # return a small DataFrame as the service would
    df = pd.DataFrame([{"a": 1}])
    mock_service.runStrategy.return_value = df

    app.dependency_overrides[backtestController.backtestService] = lambda db=None: mock_service
    try:
        resp = client.post("/api/v1/strategy/mystrategy?userId=1")
        assert resp.status_code == 200
        assert resp.json() == [{"a": 1}]
    finally:
        app.dependency_overrides.pop(backtestController.backtestService, None)
