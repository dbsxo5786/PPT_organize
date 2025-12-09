# backend/routes/analyze.py
import re
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
from ..services.ppt_parser import parse_ppt
from ..services.keywords import extract_keywords 
from ..services.gpt import call_chatgpt, first_text

analyze_bp = Blueprint("analyze", __name__)
UPLOAD_DIR = Path("uploads"); UPLOAD_DIR.mkdir(exist_ok=True)

@analyze_bp.route("/analyze", methods=["POST"])
def analyze():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    f = request.files["file"]
    fname = secure_filename(f.filename) or "upload.pptx"
    fpath = UPLOAD_DIR / fname
    f.save(fpath)

    slides = parse_ppt(str(fpath))
    keywords = {sid: extract_keywords(txt) for sid, txt in slides.items()}
    flat = list(dict.fromkeys([kw for kw_list in keywords.values() for kw in kw_list]))

    # 💡 프롬프트 수정: AI가 핵심 주제에 더 집중하도록 명령을 구체화
    prompt_subject = (
        f"다음 핵심 단어 목록을 보고 이 프레젠테이션의 가장 핵심적인 전공 과목명을 1개만 따옴표 안에 넣어 출력하세요. "
        f"목록의 마지막 부분에 나오는 '인공지능', '데이터 분석' 등은 미래 전망이나 응용 분야로 언급된 것일 수 있으니, "
        f"가장 지배적으로 나타나는 기본 주제에 집중해야 합니다.\n\n"
        f"핵심 단어: {', '.join(flat[:20])}"
    )
    subj_resp = call_chatgpt([{"role": "user", "content": prompt_subject}])
    raw_subject = first_text(subj_resp).strip()

    match = re.search(r'["\'](.*?)["\']', raw_subject)
    subject = match.group(1) if match else raw_subject

    all_text = "\n".join(slides.values())
    prompt_summary = (
        f"다음은 '{subject}' 과목에 대한 프레젠테이션의 전체 텍스트입니다. "
        "이 프레젠테이션의 핵심 내용을 2~3문장으로 요약해 주세요.\n\n"
        f"전체 텍스트:\n{all_text[:4000]}"
    )
    summary_resp = call_chatgpt([{"role": "user", "content": prompt_summary}])
    total_summary = first_text(summary_resp).strip()

    return jsonify({
        "slides": slides,
        "keywords": keywords,
        "subject": subject,
        "total_summary": total_summary
    })