from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from firebase_auth import FirebaseIsAuthenticated
from materials.mongo import material_listings_collection


def _serialize_material(item: dict) -> dict:
    company_id = item.get("company_id")
    return {
        "id": str(item["_id"]),
        "company_id": str(company_id) if company_id is not None else None,
        "material_type": item.get("material_type"),
        "quantity": item.get("quantity"),
        "unit": item.get("unit"),
        "location": item.get("location"),
        "descripcion": item.get("descripcion"),
        "precio": item.get("precio"),
        "status": item.get("status"),
        "published_by": item.get("published_by"),
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


def _validate_material_payload(data):
    errors = {}
    company_id_raw = (data.get("company_id") or "").strip()
    material_type = (data.get("material_type") or "").strip()
    company_oid = None

    try:
        company_oid = ObjectId(company_id_raw)
    except (InvalidId, TypeError):
        errors["company_id"] = "company_id debe ser un ObjectId válido"

    if not material_type:
        errors["material_type"] = "material_type es obligatorio"

    try:
        quantity = float(data.get("quantity"))
        if quantity <= 0:
            errors["quantity"] = "quantity debe ser mayor que 0"
    except (TypeError, ValueError):
        errors["quantity"] = "quantity debe ser numérico"
        quantity = None

    try:
        precio = float(data.get("precio"))
        if precio < 0:
            errors["precio"] = "precio no puede ser negativo"
    except (TypeError, ValueError):
        errors["precio"] = "precio debe ser numérico"
        precio = None

    return company_oid, material_type, quantity, precio, errors


class MaterialListingViewSet(viewsets.ViewSet):
    """
    Microservicio desacoplado: no consulta la colección companies.
    Filtra por published_by (uid Firebase) y guarda company_id como referencia.
    """

    permission_classes = [FirebaseIsAuthenticated]

    def list(self, request):
        uid = request.firebase_user.get("uid")
        items = list(material_listings_collection.find({"published_by": uid}))
        return Response([_serialize_material(item) for item in items])

    def create(self, request):
        uid = request.firebase_user.get("uid")
        data = request.data or {}
        company_oid, material_type, quantity, precio, errors = _validate_material_payload(data)

        if errors:
            return _error(
                "INVALID_DATA",
                "Los datos enviados no son válidos",
                status.HTTP_400_BAD_REQUEST,
                errors,
            )

        document = {
            "company_id": company_oid,
            "material_type": material_type,
            "quantity": quantity,
            "unit": data.get("unit") or "kg",
            "location": data.get("location"),
            "descripcion": data.get("descripcion"),
            "precio": precio,
            "status": data.get("status") or "available",
            "published_by": uid,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        result = material_listings_collection.insert_one(document)
        created = material_listings_collection.find_one({"_id": result.inserted_id})
        return Response(_serialize_material(created), status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        uid = request.firebase_user.get("uid")
        oid = _parse_object_id(pk)
        if oid is None:
            return _error("NOT_FOUND", "Recurso no encontrado", status.HTTP_404_NOT_FOUND)

        item = material_listings_collection.find_one({"_id": oid, "published_by": uid})
        if not item:
            return _error("NOT_FOUND", "Recurso no encontrado", status.HTTP_404_NOT_FOUND)
        return Response(_serialize_material(item))

    def update(self, request, pk=None):
        uid = request.firebase_user.get("uid")
        oid = _parse_object_id(pk)
        if oid is None:
            return _error("NOT_FOUND", "Recurso no encontrado", status.HTTP_404_NOT_FOUND)

        existing = material_listings_collection.find_one({"_id": oid, "published_by": uid})
        if not existing:
            return _error("NOT_FOUND", "Recurso no encontrado", status.HTTP_404_NOT_FOUND)

        data = request.data or {}
        company_oid, material_type, quantity, precio, errors = _validate_material_payload(data)
        if errors:
            return _error(
                "INVALID_DATA",
                "Los datos enviados no son válidos",
                status.HTTP_400_BAD_REQUEST,
                errors,
            )

        material_listings_collection.update_one(
            {"_id": oid, "published_by": uid},
            {
                "$set": {
                    "company_id": company_oid,
                    "material_type": material_type,
                    "quantity": quantity,
                    "unit": data.get("unit") or existing.get("unit") or "kg",
                    "location": data.get("location"),
                    "descripcion": data.get("descripcion"),
                    "precio": precio,
                    "status": data.get("status") or existing.get("status") or "available",
                }
            },
        )
        updated = material_listings_collection.find_one({"_id": oid})
        return Response(_serialize_material(updated))

    def destroy(self, request, pk=None):
        uid = request.firebase_user.get("uid")
        oid = _parse_object_id(pk)
        if oid is None:
            return _error("NOT_FOUND", "Recurso no encontrado", status.HTTP_404_NOT_FOUND)

        result = material_listings_collection.delete_one({"_id": oid, "published_by": uid})
        if result.deleted_count == 0:
            return _error("NOT_FOUND", "Recurso no encontrado", status.HTTP_404_NOT_FOUND)
        return Response({"status": "deleted", "id": str(oid)})


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"status": "ok", "service": "materials-service"})
