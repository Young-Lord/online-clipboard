import datetime
import functools
import json
from typing import Any, Optional

from flask import request
from flask_restx import Resource, fields

from app.models.datastore import (
    Note,
    RedeemCode,
    RedeemRecord,
    datastore,
    effective_limits,
    sanitize_benefits,
    verify_redeem_code,
)
from app.note_const import ADMIN_TOKEN, BENEFIT_KEYS
from app.utils import return_json

from .base import api_restx as api, api_bp, limiter
from .note import (
    BaseRest,
    base_decorators,
    note_limiter,
)
from flask import g


# ----------------- User-facing benefit / redeem endpoints -----------------


redeem_input_model = api.model(
    "RedeemInput",
    {
        "code": fields.String(required=True, description="Redeem code to apply"),
    },
)

benefit_model = api.model(
    "BenefitEntry",
    {
        "code": fields.String(required=True),
        "note": fields.String(required=True),
        "benefits": fields.Raw(required=True),
        "activated_at": fields.DateTime(required=True),
        "expires_at": fields.DateTime(required=False),
    },
)


def _record_to_dict(record: RedeemRecord) -> dict[str, Any]:
    return {
        "id": record.id,
        "code": record.redeem_code.code if record.redeem_code else "",
        "note": record.redeem_code.note if record.redeem_code else "",
        "benefits": record.benefits_dict,
        "activated_at": record.activated_at.isoformat() if record.activated_at else None,
        "expires_at": record.expires_at.isoformat() if record.expires_at else None,
    }


def _benefits_payload_for_note(note: Note) -> dict[str, Any]:
    records = datastore.get_records_for_note(note)
    active = [r for r in records if r.is_active]
    return {
        "effective_limits": effective_limits(active),
        "active_records": [_record_to_dict(r) for r in active],
        "history": [_record_to_dict(r) for r in records if not r.is_active],
    }


@api.doc(security="headers")
@api.route("/note/<string:name>/redeem")
class NoteRedeemRest(BaseRest):
    decorators = [note_limiter] + base_decorators

    @api.expect(redeem_input_model)
    def post(self, name: str):
        if g.note is None or g.is_readonly:
            return return_json(status_code=404, message="No note found")
        data = g.data
        code = (data.get("code") or "").strip().upper()
        if not code or not verify_redeem_code(code):
            return return_json(
                status_code=400,
                message="Invalid code format",
                error_id="INVALID_CODE_FORMAT",
            )
        try:
            record = datastore.redeem_code_for_note(g.note, code)
        except ValueError as e:
            err = str(e)
            mapping = {
                "CODE_NOT_FOUND": 404,
                "CODE_INACTIVE": 403,
                "CODE_EXPIRED": 410,
                "CODE_USED_UP": 410,
                "CODE_NO_BENEFITS": 400,
            }
            return return_json(
                status_code=mapping.get(err, 400),
                message=err,
                error_id=err,
            )
        payload = _benefits_payload_for_note(g.note)
        payload["just_redeemed"] = _record_to_dict(record)
        return return_json(status_code=200, message="OK", data=payload)

    def get(self, name: str):
        if g.note is None:
            return return_json(status_code=404, message="No note found")
        return return_json(
            status_code=200, message="OK", data=_benefits_payload_for_note(g.note)
        )


# ----------------- Admin endpoints -----------------


def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if not ADMIN_TOKEN:
            return return_json(
                status_code=403,
                message="Admin features are disabled (ADMIN_TOKEN not configured)",
                error_id="ADMIN_DISABLED",
            )
        provided = request.headers.get("X-Admin-Token", "")
        # constant-time compare
        import hmac

        if not hmac.compare_digest(provided, ADMIN_TOKEN):
            return return_json(
                status_code=403,
                message="Invalid admin token",
                error_id="ADMIN_TOKEN_INVALID",
            )
        return f(*args, **kwargs)

    return decorated_function


def _code_to_dict(rc: RedeemCode) -> dict[str, Any]:
    return {
        "id": rc.id,
        "code": rc.code,
        "note": rc.note,
        "benefits": rc.benefits_dict,
        "max_uses": rc.max_uses,
        "used_count": rc.used_count,
        "valid_until": rc.valid_until.isoformat() if rc.valid_until else None,
        "effect_duration_seconds": rc.effect_duration_seconds,
        "is_active": rc.is_active,
        "created_at": rc.created_at.isoformat() if rc.created_at else None,
        "updated_at": rc.updated_at.isoformat() if rc.updated_at else None,
    }


def _parse_optional_datetime(v: Any) -> Optional[datetime.datetime]:
    if v is None or v == "":
        return None
    if isinstance(v, str):
        try:
            return datetime.datetime.fromisoformat(v.replace("Z", "+00:00")).replace(
                tzinfo=None
            )
        except ValueError:
            raise ValueError("Invalid datetime format (expect ISO8601)")
    raise ValueError("Invalid datetime")


@api_bp.route("/admin/redeem_codes", methods=["GET", "POST"])
@limiter.limit("60/minute")
@admin_required
def admin_redeem_codes_collection():
    if request.method == "GET":
        try:
            limit = max(1, min(int(request.args.get("limit", 50)), 500))
            offset = max(0, int(request.args.get("offset", 0)))
        except (TypeError, ValueError):
            return return_json(status_code=400, message="Invalid pagination")
        query = request.args.get("q", "")
        rows, total = datastore.list_redeem_codes(query=query, limit=limit, offset=offset)
        return return_json(
            status_code=200,
            message="OK",
            data={"items": [_code_to_dict(r) for r in rows], "total": total},
        )

    # POST: create one or many codes
    body = request.get_json(silent=True) or {}
    count = int(body.get("count", 1))
    if count < 1 or count > 100:
        return return_json(status_code=400, message="count must be 1..100")
    code = (body.get("code") or "").strip().upper() or None
    note = (body.get("note") or "").strip()[:200]
    benefits = sanitize_benefits(body.get("benefits") or {})
    if not benefits:
        return return_json(
            status_code=400,
            message="Provide at least one benefit",
            error_id="EMPTY_BENEFITS",
        )
    try:
        max_uses = int(body.get("max_uses", -1))
    except (TypeError, ValueError):
        return return_json(status_code=400, message="Invalid max_uses")
    try:
        effect_duration_seconds = int(body.get("effect_duration_seconds", -1))
    except (TypeError, ValueError):
        return return_json(
            status_code=400, message="Invalid effect_duration_seconds"
        )
    try:
        valid_until = _parse_optional_datetime(body.get("valid_until"))
    except ValueError as e:
        return return_json(status_code=400, message=str(e))

    if count > 1 and code is not None:
        return return_json(
            status_code=400,
            message="Cannot specify a custom code when generating multiple",
        )

    created: list[RedeemCode] = []
    try:
        for _ in range(count):
            rc = datastore.create_redeem_code(
                code=code,
                note=note,
                benefits=benefits,
                max_uses=max_uses,
                valid_until=valid_until,
                effect_duration_seconds=effect_duration_seconds,
            )
            created.append(rc)
    except ValueError as e:
        return return_json(status_code=400, message=str(e))
    return return_json(
        status_code=200,
        message="OK",
        data={"items": [_code_to_dict(r) for r in created]},
    )


@api_bp.route("/admin/redeem_codes/<int:code_id>", methods=["GET", "PUT", "DELETE"])
@limiter.limit("60/minute")
@admin_required
def admin_redeem_code_item(code_id: int):
    rc = datastore.get_redeem_code(code_id)
    if rc is None:
        return return_json(status_code=404, message="Not found")
    if request.method == "GET":
        return return_json(status_code=200, message="OK", data=_code_to_dict(rc))
    if request.method == "DELETE":
        datastore.delete_redeem_code(rc)
        return return_json(status_code=200, message="Deleted")
    # PUT
    body = request.get_json(silent=True) or {}
    update_kwargs: dict[str, Any] = {}
    if "note" in body:
        update_kwargs["note"] = (body.get("note") or "")[:200]
    if "benefits" in body:
        update_kwargs["benefits"] = sanitize_benefits(body.get("benefits") or {})
    if "max_uses" in body:
        try:
            update_kwargs["max_uses"] = int(body["max_uses"])
        except (TypeError, ValueError):
            return return_json(status_code=400, message="Invalid max_uses")
    if "effect_duration_seconds" in body:
        try:
            update_kwargs["effect_duration_seconds"] = int(
                body["effect_duration_seconds"]
            )
        except (TypeError, ValueError):
            return return_json(
                status_code=400, message="Invalid effect_duration_seconds"
            )
    if "valid_until" in body:
        try:
            update_kwargs["valid_until"] = _parse_optional_datetime(
                body["valid_until"]
            )
            update_kwargs["_set_valid_until"] = True
        except ValueError as e:
            return return_json(status_code=400, message=str(e))
    if "is_active" in body:
        update_kwargs["is_active"] = bool(body["is_active"])
    rc = datastore.update_redeem_code(rc, **update_kwargs)
    return return_json(status_code=200, message="OK", data=_code_to_dict(rc))


@api_bp.route("/admin/ping")
@limiter.limit("30/minute")
@admin_required
def admin_ping():
    return return_json(status_code=200, message="OK", data={"ok": True})
