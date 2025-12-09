from flask import Blueprint, request, jsonify
from ..services.gpt import call_chatgpt, first_text

subject_bp = Blueprint("subject", __name__)

@subject_bp.route("/subject", methods=["POST"])
def subject():
    keywords = request.json.get("keywords", [])
    if not keywords:
        return jsonify({"error": "no keywords"}), 400

    prompt = (
        f"다음 핵심 단어들이 포함된 PPT는 어떤 전공 과목에 해당할 가능성이 높습니까? "
        f"가능한 한 구체적인 과목명을 알려주세요.\n\n"
        f"단어 목록: {', '.join(keywords)}"
    )
    resp = call_chatgpt([{"role": "user", "content": prompt}])
    return jsonify({"subject": first_text(resp)})
