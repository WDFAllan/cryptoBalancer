from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.domain.models.user import User


client = TestClient(app)


def test_get_user_by_email_success():
    mock_user = User(id=1, email="allan@example.com", username="allan", createdAt=datetime.now())

    with patch("app.api.v1.controllers.userController.UserService") as MockService:
        mock_service = MagicMock()
        mock_service.getUserByEmail.return_value = mock_user
        MockService.return_value = mock_service

        response = client.get("/api/v1/user/getUserByEmail/allan@example.com")

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "allan@example.com"
        assert data["username"] == "allan"


def test_get_user_by_email_not_found():
    with patch("app.api.v1.controllers.userController.UserService") as MockService:
        mock_service = MagicMock()
        mock_service.getUserByEmail.side_effect = Exception("User not found")
        MockService.return_value = mock_service

        response = client.get("/api/v1/user/getUserByEmail/noone@example.com")

        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
