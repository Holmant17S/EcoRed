from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from bson import ObjectId
from django.test import SimpleTestCase
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIRequestFactory, force_authenticate

from companies.views import CompanyViewSet, health
from firebase_auth import FirebaseUser
from firebase_auth.authentication import FirebaseAuthentication


def _auth_request(factory, user, method, path, data=None):
    if method == "post":
        request = factory.post(path, data or {}, format="json")
    elif method == "put":
        request = factory.put(path, data or {}, format="json")
    elif method == "delete":
        request = factory.delete(path)
    else:
        request = factory.get(path)
    request.firebase_user = {"uid": user.uid}
    force_authenticate(request, user=user)
    return request


class CompaniesContractTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = FirebaseUser(uid="uid-test", email="test@ecored.com")

    def test_health_ok(self):
        request = self.factory.get("/api/v1/health/")
        response = health(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "ok")
        self.assertEqual(response.data["service"], "companies-service")

    @patch("companies.views.companies_collection")
    def test_list_success(self, collection):
        oid = ObjectId()
        collection.find.return_value = [
            {
                "_id": oid,
                "owner_uid": "uid-test",
                "name": "EcoRed SAS",
                "nit": "900123456",
                "city": "Bogotá",
                "sector": "Reciclaje",
                "descripcion": "Demo",
                "comunidad": "Norte",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
        ]
        request = _auth_request(self.factory, self.user, "get", "/api/v1/companies/")
        response = CompanyViewSet.as_view({"get": "list"})(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "EcoRed SAS")
        self.assertEqual(response.data[0]["id"], str(oid))

    @patch("companies.views.companies_collection")
    def test_create_success(self, collection):
        oid = ObjectId()
        created = {
            "_id": oid,
            "owner_uid": "uid-test",
            "name": "EcoRed SAS",
            "nit": "900123456",
            "city": "Bogotá",
            "sector": "Reciclaje",
            "descripcion": "Demo",
            "comunidad": "Norte",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        collection.find_one.side_effect = [None, created]
        collection.insert_one.return_value = MagicMock(inserted_id=oid)
        request = _auth_request(
            self.factory,
            self.user,
            "post",
            "/api/v1/companies/",
            {"name": "EcoRed SAS", "nit": "900123456", "city": "Bogotá"},
        )
        response = CompanyViewSet.as_view({"post": "create"})(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["name"], "EcoRed SAS")

    @patch("companies.views.companies_collection")
    def test_create_invalid_data(self, collection):
        request = _auth_request(self.factory, self.user, "post", "/api/v1/companies/", {})
        response = CompanyViewSet.as_view({"post": "create"})(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "INVALID_DATA")

    def test_list_requires_auth(self):
        request = self.factory.get("/api/v1/companies/")
        response = CompanyViewSet.as_view({"get": "list"})(request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["code"], "UNAUTHENTICATED")

    def test_invalid_token_is_401(self):
        request = self.factory.get(
            "/api/v1/companies/",
            HTTP_AUTHORIZATION="Bearer ",
        )
        with self.assertRaises(AuthenticationFailed):
            FirebaseAuthentication().authenticate(request)

    @patch("firebase_auth.authentication.ensure_firebase_initialized")
    @patch(
        "firebase_auth.authentication.auth.verify_id_token",
        side_effect=Exception("expired"),
    )
    def test_expired_token_view_returns_401(self, _verify, _init):
        request = self.factory.get(
            "/api/v1/companies/",
            HTTP_AUTHORIZATION="Bearer token-invalido-o-vencido",
        )
        response = CompanyViewSet.as_view({"get": "list"})(request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["code"], "UNAUTHENTICATED")
        self.assertEqual(response.data["message"], "Token inválido o vencido")

    @patch("companies.views.companies_collection")
    def test_retrieve_not_found(self, collection):
        collection.find_one.return_value = None
        request = _auth_request(
            self.factory,
            self.user,
            "get",
            f"/api/v1/companies/{ObjectId()}/",
        )
        response = CompanyViewSet.as_view({"get": "retrieve"})(
            request, pk=str(ObjectId())
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["code"], "NOT_FOUND")
