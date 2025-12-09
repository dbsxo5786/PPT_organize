import './css/main.css';
import { useNavigate } from 'react-router-dom'; 

const LEVELS = ["하", "중", "상", "테스트"];

const Main = ({ selectedFile, setSelectedFile, level, setLevel, setAnalysisResult }) => {
    const navigate = useNavigate();

    const handleFileChange = (e) => {
        if (e.target.files.length > 0) {
            setSelectedFile(e.target.files[0]);
        }
    };

    const handleSubmit = async (e) => { // async 함수로 변경
        e.preventDefault();

        if (!selectedFile || !level) {
            alert("파일과 난이도를 모두 선택해주세요.");
            return;
        }

        // 로딩 UI 시작 (필요 시 추가)
        console.log("분석을 시작합니다...");

        const formData = new FormData();
        formData.append("file", selectedFile);

        try {
            const response = await fetch("http://127.0.0.1:5000/analyze", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                throw new Error("서버에서 파일 분석 중 오류가 발생했습니다.");
            }

            const data = await response.json();
            setAnalysisResult(data); // App.js의 상태 업데이트

            if (level === '테스트') {
                navigate('/test');
            } else {
                navigate('/result');
            }
        } catch (error) {
            console.error("API 호출 오류:", error);
            alert(error.message);
            // 로딩 UI 종료 (필요 시 추가)
        }
    };

    return (
        <div>
            <div className='upload'>
                <p className='intro'>
                    PPT 내용을 한 번에 정리하고 설명해드립니다.<br />
                    정리된 내용을 저장하고 활용해보세요!
                </p>
                <form onSubmit={handleSubmit}>
                    <div className='space-upload'>
                        <label className='btn-upload' htmlFor='input-file'>
                            {selectedFile ? selectedFile.name : "파일 업로드"}
                        </label>
                        <input
                            type='file'
                            id='input-file'
                            style={{ display: 'none' }}
                            onChange={handleFileChange}
                            accept=".ppt, .pptx"
                        />
                    </div>
                    <div className='level-select'>
                        <div className="level-buttons">
                            {LEVELS.map((lv) => (
                                <label
                                    key={lv}
                                    className={`level-btn ${level === lv ? "active" : ""}`}
                                >
                                    <input
                                        type="radio"
                                        name="level"
                                        value={lv}
                                        checked={level === lv}
                                        onChange={(e) => setLevel(e.target.value)}
                                    />
                                    {lv}
                                </label>
                            ))}
                        </div>
                    </div>
                    <button type='submit' className='btn-submit'>
                        정리 시작하기
                    </button>
                </form>
            </div>
            <div className='method'>
                <div className="method-content">
                    <h1>사용방법</h1>
                    <ol>
                        <li>원하는 PPT파일을 업로드하고 정리 시작하기 버튼을 누르세요.</li>
                        <li>AI가 파일을 읽고 전체적인 내용을 정리하는동안 기다리세요.</li>
                        <li>결과창으로 넘어가지면 다운로드 버튼을 눌러 저장하세요.</li>
                    </ol>
                </div>
                <div className="method-image"></div>
            </div>
        </div>
    );
};

export default Main;