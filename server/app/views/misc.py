import sys
from flask import Blueprint, make_response, request

csp_report = Blueprint(
    "csp_report",
    "csp_report",
)


@csp_report.route("/csp-report", methods=["POST"])
def csp_report_handler():
    print(request.get_json(force=True), file=sys.stderr)
    return make_response()
