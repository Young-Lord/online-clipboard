from app.note_const import Metadata
from app.utils import cors_decorator, return_json
from app.resources.note import api_restx as api_restx
from app.resources.base import api_bp as api


@api.route("/metadata")
@cors_decorator
def api_metadata():
    return return_json(data=Metadata.to_dict())
