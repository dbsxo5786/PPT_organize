from flask import Blueprint, request, jsonify
from ..services.gpt import call_chatgpt, first_text

explain_bp = Blueprint("explain", __name__)

# 슬라이드 요약 API (변경 없음)
@explain_bp.route("/explain/slides", methods=["POST"])
def explain_slides():
    data = request.json or {}
    subject = data.get("subject","")
    level = data.get("level","")
    slides = data.get("slides",{})
    keywords = data.get("keywords",{})
    if not subject or not level or not slides or not keywords:
        return jsonify({"error":"missing fields"}), 400

    per_slide = {}
    for sid, text in slides.items():
        kw = keywords.get(sid, [])[:10]
        prompt = (
            f"과목: {subject}\n학습 수준: {level}\n슬라이드 원문: \"{text}\"\n"
            f"슬라이드 핵심 단어: {', '.join(kw)}\n\n"
            "위 슬라이드 원문 내용을 핵심 단어를 활용하여 해당 수준의 학습자가 이해하기 쉽게 3~5줄로 요약해 주세요."
        )
        resp = call_chatgpt([{"role":"user","content":prompt}])
        per_slide[sid] = first_text(resp).strip()

    return jsonify({"explanations": per_slide})

# 💡 신규 API: 모든 핵심 단어 설명을 한번에 생성
@explain_bp.route("/explain/batch_keywords", methods=["POST"])
def explain_batch_keywords():
    data = request.json or {}
    keywords = data.get("keywords", [])
    subject = data.get("subject", "일반")
    level = data.get("level", "중")

    if not keywords:
        return jsonify({"error": "keywords are required"}), 400

    definitions = {}
    for keyword in keywords:
        prompt = (
            f"'{subject}' 과목을 공부하는 '{level}' 수준의 학생에게 '{keyword}'라는 단어의 개념을 "
            f"1~2줄로 간결하고 명확하게 설명해 주세요."
        )
        resp = call_chatgpt([{"role": "user", "content": prompt}])
        definitions[keyword] = first_text(resp).strip()

    return jsonify({"definitions": definitions})