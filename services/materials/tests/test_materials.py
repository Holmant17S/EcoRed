from unittest.mock import MagicMock, patch

from bson import ObjectId
from django.test import SimpleTestCase
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIRequestFactory, force_authenticate

from firebase_auth import FirebaseUser
from firebase_auth.authentication import FirebaseAuthentication
from materials.views import MaterialListingViewSet, health


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


class MaterialsContractTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = FirebaseUser(uid="uid-test", email="test@ecored.com")
        self.company_id = str(ObjectId())

    def test_health_ok(self):
        request = self.factory.get("/api/v1/health/")
        response = health(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["service"], "materials-service")

    @patch("materials.views.material_listings_collection")
    def test_list_success(self, collection):
        mid = ObjectId()
        cid = ObjectId()
        collection.find.return_value = [
            {
                "_id": mid,
                "company_id": cid,
                "material_type": "PET",
                "quantity": 10,
                "unit": "kg",
                "location": "Bogotá",
                "descripcion": "Demo",
                "precio": 1000,
                "status": "available",
                "published_by": "uid-test",
                "created_at": "2026-03-10T00:00:00+00:00",
            }
        ]
        request = _auth_request(self.factory, self.user, "get", "/api/v1/materials/")
        response = MaterialListingViewSet.as_view({"get": "list"})(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["material_type"], "PET")
        self.assertEqual(response.data[0]["id"], str(mid))

    @patch("materials.views.material_listings_collection")
    def test_create_success(self, collection):
        mid = ObjectId()
        cid = ObjectId(self.company_id)
        created = {
            "_id": mid,
            "company_id": cid,
            "material_type": "PET",
            "quantity": 10,
            "unit": "kg",
            "location": "Bogotá",
            "descripcion": "Demo",
            "precio": 1000,
            "status": "available",
            "published_by": "uid-test",
            "created_at": "2026-03-10T00:00:00+00:00",
        }
        collection.insert_one.return_value = MagicMock(inserted_id=mid)
        collection.find_one.return_value = created
        request = _auth_request(
            self.factory,
            self.user,
            "post",
            "/api/v1/materials/",
            {
                "company_id": self.company_id,
                "material_type": "PET",
                "quantity": 10,
                "precio": 1000,
            },
        )
        response = MaterialListingViewSet.as_view({"post": "create"})(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["material_type"], "PET")

    @patch("materials.views.material_listings_collection")
    def test_create_invalid_data(self, collection):
        request = _auth_request(
            self.factory,
            self.user,
            "post",
            "/api/v1/materials/",
            {"company_id": "no-es-oid", "material_type": "", "quantity": -1, "precio": "x"},
        )
        response = MaterialListingViewSet.as_view({"post": "create"})(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["code"], "INVALID_DATA")

    def test_list_requires_auth(self):
        request = self.factory.get("/api/v1/materials/")
        response = MaterialListingViewSet.as_view({"get": "list"})(request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["code"], "UNAUTHENTICATED")

    def test_invalid_token_is_401(self):
        request = self.factory.get(
            "/api/v1/materials/",
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
            "/api/v1/materials/",
            HTTP_AUTHORIZATION="Bearer token-invalido-o-vencido",
        )
        response = MaterialListingViewSet.as_view({"get": "list"})(request)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["code"], "UNAUTHENTICATED")
        self.assertEqual(response.data["message"], "Token inválido o vencido")

    @patch("materials.views.material_listings_collection")
    def test_retrieve_not_found(self, collection):
        collection.find_one.return_value = None
        request = _auth_request(
            self.factory,
            self.user,
            "get",
            f"/api/v1/materials/{ObjectId()}/",
        )
        response = MaterialListingViewSet.as_view({"get": "retrieve"})(
            request, pk=str(ObjectId())
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["code"], "NOT_FOUND")
