from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from companies.mongo import companies_collection
from firebase_auth import FirebaseIsAuthenticated


def _serialize_company(company: dict) -> dict:
    return {
        "id": str(company["_id"]),
        "owner_uid": company.get("owner_uid"),
        "name": company.get("name"),
        "nit": company.get("nit"),
        "city": company.get("city"),
        "sector": company.get("sector"),
        "descripcion": company.get("descripcion"),
        "comunidad": company.get("comunidad"),
        "created_at": company.get("created_at"),
    }


def _error(code, message, http_status, errors=None):
    payload = {"code": code, "message": message}
    if errors is not None:
        payload["errors"] = errors
    return Response(payload, status=http_status)


def _parse_object_id(pk):
    try:
        return ObjectId(pk)
    except (InvalidId, TypeError):
        return None


def _validate_company_payload(data, *, require_all=True):
    errors = {}
    name = (data.get("name") or "").strip()
    nit = (data.get("nit") or "").strip()

    if require_all or "name" in data:
        if not name or len(name) < 3 or len(name) > 100:
            errors["name"] = "El nombre es obligatorio (3 a 100 caracteres)"
    if require_all or "nit" in data:
        if not nit:
            errors["nit"] = "El NIT es obligatorio"

    return name, nit, errors


class CompanyViewSet(viewsets.ViewSet):
    permission_classes = [FirebaseIsAuthenticated]

    def list(self, request):
        uid = request.firebase_user.get("uid")
        companies = list(
            companies_collection.find(
                {"owner_uid": uid},
                {
                    "owner_uid": 1,
                    "name": 1,
                    "nit": 1,
                    "city": 1,
                    "sector": 1,
                    "descripcion": 1,
                    "comunidad": 1,
                    "created_at": 1,
                },
            )
        )
        return Response([_serialize_company(c) for c in companies])

    def create(self, request):
        uid = request.firebase_user.get("uid")
        data = request.data or {}
        name, nit, errors = _validate_company_payload(data)

        if errors:
            return _error(
                "INVALID_DATA",
                "Los datos enviados no son válidos",
                status.HTTP_400_BAD_REQUEST,
                errors,
            )

        if companies_collection.find_one({"nit": nit}):
            return _error(
                "INVALID_DATA",
                "Los datos enviados no son válidos",
                status.HTTP_400_BAD_REQUEST,
                {"nit": "El NIT debe ser único"},
            )

        document = {
            "owner_uid": uid,
            "name": name,
            "nit": nit,
            "city": data.get("city"),
            "sector": data.get("sector"),
            "descripcion": data.get("descripcion"),
            "comunidad": data.get("comunidad"),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        result = companies_collection.insert_one(document)
        created = companies_collection.find_one({"_id": result.inserted_id})
        return Response(_serialize_company(created), status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        uid = request.firebase_user.get("uid")
        oid = _parse_object_id(pk)
        if oid is None:
            return _error("NOT_FOUND", "Recurso no encontrado", status.HTTP_404_NOT_FOUND)

        company = companies_collection.find_one({"_id": oid, "owner_uid": uid})
        if not company:
            return _error("NOT_FOUND", "Recurso no encontrado", status.HTTP_404_NOT_FOUND)
        return Response(_serialize_company(company))

    def update(self, request, pk=None):
        uid = request.firebase_user.get("uid")
        oid = _parse_object_id(pk)
        if oid is None:
            return _error("NOT_FOUND", "Recurso no encontrado", status.HTTP_404_NOT_FOUND)

        existing = companies_collection.find_one({"_id": oid, "owner_uid": uid})
        if not existing:
            return _error("NOT_FOUND", "Recurso no encontrado", status.HTTP_404_NOT_FOUND)

        data = request.data or {}
        name, nit, errors = _validate_company_payload(data)
        if errors:
            return _error(
                "INVALID_DATA",
                "Los datos enviados no son válidos",
                status.HTTP_400_BAD_REQUEST,
                errors,
            )

        duplicate = companies_collection.find_one({"nit": nit, "_id": {"$ne": oid}})
        if duplicate:
            return _error(
                "INVALID_DATA",
                "Los datos enviados no son válidos",
                status.HTTP_400_BAD_REQUEST,
                {"nit": "El NIT debe ser único"},
            )

        companies_collection.update_one(
            {"_id": oid, "owner_uid": uid},
            {
                "$set": {
                    "name": name,
                    "nit": nit,
                    "city": data.get("city"),
                    "sector": data.get("sector"),
                    "descripcion": data.get("descripcion"),
                    "comunidad": data.get("comunidad"),
                }
            },
        )
        updated = companies_collection.find_one({"_id": oid})
        return Response(_serialize_company(updated))

    def destroy(self, request, pk=None):
        uid = request.firebase_user.get("uid")
        oid = _parse_object_id(pk)
        if oid is None:
            return _error("NOT_FOUND", "Recurso no encontrado", status.HTTP_404_NOT_FOUND)

        result = companies_collection.delete_one({"_id": oid, "owner_uid": uid})
        if result.deleted_count == 0:
            return _error("NOT_FOUND", "Recurso no encontrado", status.HTTP_404_NOT_FOUND)
        return Response({"status": "deleted", "id": str(oid)})


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok", "service": "companies-service"})
