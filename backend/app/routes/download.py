from flask import Blueprint, request, send_file, jsonify, render_template_string
from zipfile import ZipFile
from io import BytesIO
import re

download_bp = Blueprint("download", __name__)

# 💡 최종 디자인 개선: 최대 너비, 아이콘, 디테일 추가
TEMPLATE = """<!doctype html><html lang="ko"><meta charset="utf-8">
<head>
<title>{{subject}} 요약 노트</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
<script src="https://unpkg.com/feather-icons"></script>
<style>
:root {
    --bg-color: #f8f9fa; --main-bg: #ffffff; --primary-color: #4C6EF5; --text-color: #343a40;
    --border-color: #e9ecef; --shadow-color: rgba(0, 0, 0, 0.04); --keyword-bg: #e7f5ff;
    --keyword-hover-bg: #d0ebff; --summary-bg: #f1f3f5; --summary-border: #adb5bd;
}
html { scroll-behavior: smooth; }
body {
    font-family: 'Noto Sans KR', sans-serif; background-color: var(--bg-color);
    margin: 0; padding: 40px 20px; line-height: 1.7; color: var(--text-color);
    -webkit-font-smoothing: antialiased;
}
.container { max-width: 900px; margin: 0 auto; }
h1, h2, h3 { font-weight: 700; display: flex; align-items: center; gap: 8px;}
h1 {
    font-size: 2em; justify-content: center; margin-bottom: 40px;
    color: var(--primary-color);
}
.note {
    background: var(--main-bg); border: 1px solid var(--border-color);
    border-left: 5px solid var(--primary-color); padding: 30px;
    margin-bottom: 30px; box-shadow: 0 5px 20px var(--shadow-color);
    border-radius: 12px;
}
.slide-title { font-size: 1.6em; margin-bottom: 25px; }
.section { margin-top: 25px; padding-top: 25px; border-top: 1px solid var(--border-color); }
.note .section:first-of-type { margin-top: 0; padding-top: 0; border-top: none; }
.summary { background: var(--summary-bg); border-left-color: var(--summary-border); }
.summary h2 { color: #495057; font-size: 1.2em; }
.keyword-list { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 15px; }
.keyword {
    background: var(--keyword-bg); color: var(--primary-color); padding: 5px 12px;
    border-radius: 15px; font-size: 0.9em; font-weight: 700; cursor: pointer;
    position: relative; transition: all 0.2s ease; border: 1px solid #cde5f7;
}
.keyword:hover { background: var(--keyword-hover-bg); transform: translateY(-2px); }
.tooltip {
    visibility: hidden; opacity: 0; position: absolute; bottom: 130%; left: 50%;
    transform: translateX(-50%); background-color: #343a40; color: #fff; text-align: center;
    border-radius: 8px; padding: 10px 14px; z-index: 10; width: 240px; font-size: 0.9em;
    box-shadow: 0 5px 15px rgba(0,0,0,0.15); transition: opacity 0.3s, transform 0.3s;
    white-space: normal;
}
.tooltip.visible { visibility: visible; opacity: 1; transform: translateX(-50%) translateY(-5px); }
.tooltip::after {
    content: ""; position: absolute; top: 100%; left: 50%; margin-left: -6px;
    border-width: 6px; border-style: solid; border-color: #343a40 transparent transparent transparent;
}
</style>
</head>
<body>
<div class="container">
    <h1><i data-feather="book-open"></i>{{subject}} 요약 노트</h1>
    <div class="note summary">
        <h2><i data-feather="align-left"></i>총괄 요약</h2>
        <p>{{ total_summary | default('요약 정보가 없습니다.') }}</p>
    </div>
    {% for sid in order %}
    <div class="note">
        <div class="slide-title">Slide {{sid}}</div>
        <div class="section">
            <h3><i data-feather="file-text"></i>슬라이드 원문</h3>
            <p>{{slides.get(sid, "")}}</p>
        </div>
        <div class="section">
            <h3><i data-feather="key"></i>핵심 단어 (클릭)</h3>
            <div class="keyword-list">
                {% for kw in (keywords.get(sid) or []) %}
                <span class="keyword" onclick="showExplanation(this)">{{kw}}</span>
                {% endfor %}
            </div>
        </div>
        <div class="section">
            <h3><i data-feather="star"></i>슬라이드 요약</h3>
            <div>{{explanations.get(sid, "요약 없음")}}</div>
        </div>
    </div>
    {% endfor %}
</div>
<script>
    feather.replace(); // 아이콘 렌더링
    const definitions = {{ keyword_definitions | tojson }};
    function closeAllTooltips(exceptThisOne = null) {
        document.querySelectorAll('.tooltip').forEach(tooltip => {
            if (tooltip !== exceptThisOne) tooltip.remove();
        });
    }
    function showExplanation(element) {
        const existingTooltip = element.querySelector('.tooltip');
        if (existingTooltip) { existingTooltip.remove(); return; }
        closeAllTooltips();
        const keyword = element.textContent;
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = definitions[keyword] || '설명을 찾을 수 없습니다.';
        element.appendChild(tooltip);
        setTimeout(() => tooltip.classList.add('visible'), 10);
    }
    document.addEventListener('click', (event) => {
        if (!event.target.closest('.keyword')) closeAllTooltips();
    }, true);
</script>
</body>
</html>"""

def get_rendered_html(data):
    slides = data.get("slides", {})
    def extract_num(sid: str) -> int:
        m = re.search(r'\d+', sid)
        return int(m.group()) if m else 0
    order = sorted(slides.keys(), key=extract_num)
    return render_template_string(TEMPLATE, **data, order=order)

@download_bp.route("/preview", methods=["POST"])
def preview():
    try:
        data = request.json or {}
        required = ["subject", "level", "slides", "keywords", "explanations", "total_summary", "keyword_definitions"]
        for k in required:
            if k not in data: return jsonify({"error": f"missing field {k}"}), 400
        html_content = get_rendered_html(data)
        return jsonify({"html_content": html_content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@download_bp.route("/download", methods=["POST"])
def download():
    try:
        data = request.json or {}
        required = ["subject", "level", "slides", "keywords", "explanations", "total_summary", "keyword_definitions"]
        for k in required:
            if k not in data: return jsonify({"error": f"missing field {k}"}), 400
        html = get_rendered_html(data)
        mem = BytesIO()
        with ZipFile(mem, "w") as zf: zf.writestr("result.html", html)
        mem.seek(0)
        return send_file(mem, as_attachment=True, download_name="result.zip", mimetype="application/zip")
    except Exception as e:
        return jsonify({"error": str(e)}), 500