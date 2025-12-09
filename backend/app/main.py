from flask import Flask
from flask_cors import CORS

# 블루프린트 import
from .routes.analyze import analyze_bp
from .routes.subject import subject_bp
from .routes.explain import explain_bp
from .routes.mode import mode_bp
from .routes.download import download_bp
# from routes.level import level_bp # level.py 파일이 없으므로 주석 처리

# 1. Flask 앱을 한 번만 생성합니다.
app = Flask(__name__, static_folder="static")

# 2. 모든 설정을 여기에 순서대로 적용합니다.
app.config['JSON_AS_ASCII'] = False
CORS(app)  # CORS 설정을 가장 마지막에 적용하는 것이 안정적일 수 있습니다.


# 3. 블루프린트를 등록합니다.
app.register_blueprint(analyze_bp)
app.register_blueprint(subject_bp)
app.register_blueprint(explain_bp)
app.register_blueprint(mode_bp)
app.register_blueprint(download_bp)
# app.register_blueprint(level_bp)

@app.route("/")
def index():
    return app.send_static_file("index.html")

if __name__ == "__main__":
    app.run(debug=True)