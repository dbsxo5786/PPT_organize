import './css/result.css';
import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const Result = ({ selectedFile, level, analysisResult }) => {
    const navigate = useNavigate();
    const location = useLocation();

    const [isLoading, setIsLoading] = useState(true);
    const [htmlContent, setHtmlContent] = useState("");
    const [downloadData, setDownloadData] = useState(null); // 💡 다운로드용 전체 데이터 저장

    const finalEffectiveLevel = location.state?.finalLevel || level;

    useEffect(() => {
        if (!selectedFile || !analysisResult) {
            alert("요약할 파일 데이터가 없습니다. 메인 페이지로 돌아갑니다.");
            navigate('/');
            return;
        }

        const fetchAllData = async () => {
            try {
                // 1. 모든 키워드 목록을 중복 없이 준비
                const allKeywords = [...new Set(Object.values(analysisResult.keywords).flat())];

                // 2. 슬라이드 요약과 키워드 설명을 동시에 요청
                const [explainResponse, definitionsResponse] = await Promise.all([
                    fetch("http://127.0.0.1:5000/explain/slides", {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ ...analysisResult, level: finalEffectiveLevel })
                    }),
                    fetch("http://127.0.0.1:5000/explain/batch_keywords", {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ keywords: allKeywords, subject: analysisResult.subject, level: finalEffectiveLevel })
                    })
                ]);

                if (!explainResponse.ok || !definitionsResponse.ok) {
                    throw new Error("AI 데이터 생성에 실패했습니다.");
                }

                const { explanations } = await explainResponse.json();
                const { definitions } = await definitionsResponse.json();

                // 3. 다운로드와 미리보기에 사용할 전체 데이터 객체 생성
                const fullData = {
                    ...analysisResult,
                    level: finalEffectiveLevel,
                    explanations,
                    keyword_definitions: definitions // 💡 키워드 설명 데이터 추가
                };
                setDownloadData(fullData); // 💡 다운로드용으로 저장

                // 4. 미리보기용 HTML 요청
                const previewResponse = await fetch("http://127.0.0.1:5000/preview", {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(fullData)
                });
                if (!previewResponse.ok) throw new Error("미리보기 생성에 실패했습니다.");
                const { html_content } = await previewResponse.json();
                setHtmlContent(html_content);

            } catch (error) {
                console.error("결과 생성 중 오류:", error);
                alert(error.message);
            } finally {
                setIsLoading(false);
            }
        };

        fetchAllData();
    }, [selectedFile, analysisResult, finalEffectiveLevel, navigate]);

    // 다운로드 핸들러는 이제 저장된 데이터를 사용
    const handleDownload = async () => {
        if (!downloadData) {
            alert("다운로드할 데이터가 준비되지 않았습니다.");
            return;
        }
        try {
            const response = await fetch("http://127.0.0.1:5000/download", {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(downloadData) // 💡 저장된 전체 데이터 사용
            });

            if (!response.ok) throw new Error("파일 다운로드에 실패했습니다.");
            
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = "result.zip";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        } catch (error) {
            console.error("다운로드 중 오류 발생:", error);
            alert(error.message);
        }
    };

    const handleGoHome = () => navigate('/');
    
    // ... (로딩 및 JSX return 부분은 이전과 동일)
    if (isLoading) {
        return (
            <div className="result-container">
                <h2>AI가 요약 노트를 생성 중입니다...</h2>
                <p>잠시만 기다려주세요.</p>
            </div>
        );
    }

    return (
        <div className="result-container">
            <h1>생성된 노트 미리보기</h1>
            <div className="preview-box">
                <iframe
                    srcDoc={htmlContent}
                    title="결과 미리보기"
                    width="100%"
                    height="500px"
                    frameBorder="0"
                ></iframe>
            </div>
            <div className="button-group">
                <button onClick={handleDownload} className="btn-result download">ZIP 파일 다운로드</button>
                <button onClick={handleGoHome} className="btn-result go-home">처음으로</button>
            </div>
        </div>
    );
};

export default Result;