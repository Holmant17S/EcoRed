from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from firebase_auth import FirebaseIsAuthenticated
from solicitudes.mongo import material_requests_collection

ALLOWED_STATUSES = ("pending", "accepted", "rejected")


def _serialize_request(item: dict) -> dict:
    material_id = item.get("material_id")
    company_id = item.get("company_id")
    return {
        "id": str(item["_id"]),
        "material_id": str(material_id) if material_id is not None else None,
        "company_id": str(company_id) if company_id is not None else None,
        "quantity": item.get("quantity"),
        "message": item.get("message"),
        "status": item.get("status"),
        "requested_by": item.get("requested_by"),
        "created_at": item.get("created_at"),
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


def _validate_payload(data, *, partial=False):
    errors = {}
    material_oid = None
    company_oid = None

    if not partial or "material_id" in data:
        raw = str(data.get("material_id") or "").strip()
        try:
            material_oid = ObjectId(raw)
        except (InvalidId, TypeError):
            errors["material_id"] = "material_id debe ser un ObjectId válido"

    if not partial or "company_id" in data:
        raw = str(data.get("company_id") or "").strip()
        try:
            company_oid = ObjectId(raw)
        except (InvalidId, TypeError):
            errors["company_id"] = "company_id debe ser un ObjectId válido"

    quantity = None
    if not partial or "quantity" in data:
        try:
            quantity = float(data.get("quantity"))
            if quantity <= 0:
                errors["quantity"] = "quantity debe ser mayor que 0"
        except (TypeError, ValueError):
            errors["quantity"] = "quantity debe ser numérico"
            quantity = None

    status_value = (data.get("status") or "pending").strip()
    if status_value not in ALLOWED_STATUSES:
        errors["status"] = "status debe ser pending, accepted o rejected"

    message = (data.get("message") or "").strip()
    return material_oid, company_oid, quantity, status_value, message, errors


class MaterialRequestViewSet(viewsets.ViewSet):
    """
    Microservicio desacoplado: no consulta companies ni materials.
    Guarda material_id y company_id como referencias y filtra por requested_by.
    """

    permission_classes = [FirebaseIsAuthenticated]

    def list(self, request):
        uid = request.firebase_user.get("uid")
        items = list(material_requests_collection.find({"requested_by": uid}))
        return Response([_serialize_request(item) for item in items])

    def create(self, request):
        uid = request.firebase_user.get("uid")
        data = request.data or {}
        material_oid, company_oid, quantity, status_value, message, errors = (
            _validate_payload(data)
        )
        if errors:
            return _error(
                "INVALID_DATA",
                "Los datos enviados no son válidos",
                status.HTTP_400_BAD_REQUEST,
                errors,
            )

        document = {
            "material_id": material_oid,
            "company_id": company_oid,
            "quantity": quantity,
            "message": message,
            "status": "pending",
            "requested_by": uid,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        result = material_requests_collection.insert_one(document)
        created = material_requests_collection.find_one({"_id": result.inserted_id})
        return Response(_serialize_request(created), status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        uid = request.firebase_user.get("uid")
        oid = _parse_object_id(pk)
        if oid is None:
            return _error("NOT_FOUND", "Recurso no encontrado", status.HTTP_404_NOT_FOUND)

        item = material_requests_collection.find_one({"_id": oid, "requested_by": uid})
        if not item:
            return _error("NOT_FOUND", "Recurso no encontrado", status.HTTP_404_NOT_FOUND)
        return Response(_serialize_request(item))

    def update(self, request, pk=None):
        uid = request.firebase_user.get("uid")
        oid = _parse_object_id(pk)
        if oid is None:
            return _error("NOT_FOUND", "Recurso no encontrado", status.HTTP_404_NOT_FOUND)

        existing = material_requests_collection.find_one({"_id": oid, "requested_by": uid})
        if not existing:
            return _error("NOT_FOUND", "Recurso no encontrado", status.HTTP_404_NOT_FOUND)

        data = request.data or {}
        material_oid, company_oid, quantity, status_value, message, errors = (
            _validate_payload(data)
        )
        if errors:
            return _error(
                "INVALID_DATA",
                "Los datos enviados no son válidos",
                status.HTTP_400_BAD_REQUEST,
                errors,
            )

        material_requests_collection.update_one(
            {"_id": oid, "requested_by": uid},
            {
                "$set": {
                    "material_id": material_oid,
                    "company_id": company_oid,
                    "quantity": quantity,
                    "message": message,
                    "status": status_value,
                }
            },
        )
        updated = material_requests_collection.find_one({"_id": oid})
        return Response(_serialize_request(updated))

    def destroy(self, request, pk=None):
        uid = request.firebase_user.get("uid")
        oid = _parse_object_id(pk)
        if oid is None:
            return _error("NOT_FOUND", "Recurso no encontrado", status.HTTP_404_NOT_FOUND)

        result = material_requests_collection.delete_one({"_id": oid, "requested_by": uid})
        if result.deleted_count == 0:
            return _error("NOT_FOUND", "Recurso no encontrado", status.HTTP_404_NOT_FOUND)
        return Response({"status": "deleted", "id": str(oid)})


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok", "service": "requests-service"})
