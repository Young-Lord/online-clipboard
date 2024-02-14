from app.note_const import Metadata
from app.utils import return_json
from app.resources.base import api_bp, api_bp_at_root


@api_bp.route("/metadata")
def api_metadata():
    return return_json(data=Metadata.to_dict())
