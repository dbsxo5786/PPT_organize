from flask import Blueprint, request, jsonify
import json
from ..services.gpt import call_chatgpt, first_text
import re # re 모듈 import

mode_bp = Blueprint("mode", __name__)

# A모드: 레벨 직접 선택 (변경 없음)
@mode_bp.route("/mode/select", methods=["POST"])
def mode_select():
    data = request.json or {}
    level = data.get("level")
    subject = data.get("subject","")
    keywords = data.get("keywords",{})
    if not level or not subject or not keywords:
        return jsonify({"error":"missing level/subject/keywords"}), 400
    return jsonify({"level": level, "subject": subject, "keywords": keywords})

# B모드 시작: 문제 생성 (변경 없음)
@mode_bp.route("/mode/test/start", methods=["POST"])
def test_start():
    subject = (request.json or {}).get("subject", "")
    if not subject:
        return jsonify({"error":"missing subject"}), 400

    prompt = (
        f"당신은 {subject} 과목 교수입니다. 객관식 5문제를 JSON 배열로 만드세요. "
        "각 문제는 {'question': '...', 'options': ['A','B','C'], 'answer': '정답'} 형태. "
        "오직 JSON만 출력."
    )
    resp = call_chatgpt([{"role":"user","content":prompt}])
    text = first_text(resp)

    match = re.search(r"\[.*\]", text, re.S)
    questions = []
    if match:
        try:
            questions = json.loads(match.group())
        except:
            questions = []
    return jsonify({"questions": questions})


# 💡 B모드 제출: 채점 로직 전체 수정
@mode_bp.route("/mode/test/submit", methods=["POST"])
def test_submit():
    data = request.json or {}
    questions = data.get("questions",[])  # [{question, options, answer}, ...]
    user_answers = data.get("answers",[])   # ["user_ans_1", "user_ans_2", ...]

    if not questions or not user_answers or len(questions) != len(user_answers):
        return jsonify({"error": "Invalid questions or answers data"}), 400

    correct_count = 0
    total_questions = len(questions)

    # 1. 서버가 직접 정답을 비교하여 채점
    for i in range(total_questions):
        correct_answer = questions[i].get("answer")
        user_answer = user_answers[i]
        
        # 정답과 사용자 답이 일치하는지 확인
        if correct_answer and user_answer and correct_answer.strip() == user_answer.strip():
            correct_count += 1
            
    # 2. 점수 계산
    score = 0
    if total_questions > 0:
        score = round((correct_count / total_questions) * 100)

    # 3. 점수에 따른 등급 부여
    level = ""
    if score >= 85:
        level = "상"
    elif score >= 60:
        level = "중"
    else:
        level = "하"

    # 4. 결과 반환
    result = {"score": score, "level": level}
    return jsonify(result)