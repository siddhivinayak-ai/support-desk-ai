from flask import Blueprint, jsonify, request

from desk import search, summarize, triage

bp = Blueprint("api", __name__)


@bp.post("/tickets/analyze")
def analyze_ticket():
    body = request.get_json()
    subject, text = body["subject"], body["body"]
    return jsonify(
        summary=summarize.summarize_ticket(subject, text),
        urgency=triage.classify_urgency(subject, text),
        auto_reply_ok=search.is_safe_to_auto_reply(text),
    )
