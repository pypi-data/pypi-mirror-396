# auth/exception_handler.py
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

def _flatten(detail, field=None):
    out = []

    if isinstance(detail, dict):
        for k, v in detail.items():
            nested_field = f"{field}.{k}" if field else k
            out.extend(_flatten(v, nested_field))
        return out

    if isinstance(detail, list):
        for item in detail:
            out.extend(_flatten(item, field))
        return out

    code = getattr(detail, "code", "error")
    out.append({"field": field, "code": str(code)})
    return out


def custom_exception_handler(exc, context):
    resp = drf_exception_handler(exc, context)
    if resp is None:
        return None

    if isinstance(exc, ValidationError):
        return Response({"errors": _flatten(resp.data)}, status=resp.status_code)

    return resp
