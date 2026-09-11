from unittest.mock import MagicMock, patch

from bson import ObjectId
from django.test import SimpleTestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from firebase_auth import FirebaseUser
from solicitudes.views import MaterialRequestViewSet, health


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


class RequestsContractTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = FirebaseUser(uid="uid-test", email="test@ecored.com")
        self.material_id = str(ObjectId())
        self.company_id = str(ObjectId())

    def test_health_ok(self):
        request = self.factory.get("/api/v1/health/")
        response = health(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["service"], "requests-service")

    @patch("solicitudes.views.material_requests_collection")
    def test_list_success(self, collection):
        rid = ObjectId()
        collection.find.return_value = [
            {
                "_id": rid,
                "material_id": ObjectId(self.material_id),
                "company_id": ObjectId(self.company_id),
                "quantity": 10,
                "message": "Necesito PET",
                "status": "pending",
                "requested_by": "uid-test",
                "created_at": "2026-03-11T00:00:00+00:00",
            }
        ]
        request = _auth_request(self.factory, self.user, "get", "/api/v1/requests/")
        response = MaterialRequestViewSet.as_view({"get": "list"})(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["status"], "pending")
        self.assertEqual(response.data[0]["id"], str(rid))

    @patch("solicitudes.views.material_requests_collection")
    def test_create_success(self, collection):
        rid = ObjectId()
        created = {
            "_id": rid,
            "material_id": ObjectId(self.material_id),
            "company_id": ObjectId(self.company_id),
            "quantity": 10,
            "message": "Necesito PET",
            "status": "pending",
            "requested_by": "uid-test",
            "created_at": "2026-03-11T00:00:00+00:00",
        }
        collection.insert_one.return_value = MagicMock(inserted_id=rid)
        collection.find_one.return_value = created
        request = _auth_request(
            self.factory,
            self.user,
            "post",
            "/api/v1/requests/",
            {
                "material_id": self.material_id,
                "company_id": self.company_id,
                "quantity": 10,
                "message": "Necesito PET",
            },
        )
        response = MaterialRequestViewSet.as_view({"post": "create"})(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["status"], "pending")

    @patch("solicitudes.views.material_requests_collection")
    def test_create_invalid_data(self, collection):
        request = _auth_request(
            self.factory,
            self.user,
            "post",
            "/api/v1/requests/",
            {"material_id": "x", "company_id": "y", "quantity": -1},
        )
        response = MaterialRequestViewSet.as_view({"post": "create"})(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "INVALID_DATA")

    def test_list_requires_auth(self):
        request = self.factory.get("/api/v1/requests/")
        response = MaterialRequestViewSet.as_view({"get": "list"})(request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["code"], "UNAUTHENTICATED")

    @patch("solicitudes.views.material_requests_collection")
    def test_retrieve_not_found(self, collection):
        collection.find_one.return_value = None
        request = _auth_request(
            self.factory,
            self.user,
            "get",
            f"/api/v1/requests/{ObjectId()}/",
        )
        response = MaterialRequestViewSet.as_view({"get": "retrieve"})(
            request, pk=str(ObjectId())
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["code"], "NOT_FOUND")
