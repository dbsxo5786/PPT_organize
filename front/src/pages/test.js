import './css/test.css';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Test = ({ selectedFile, analysisResult }) => {
    const navigate = useNavigate();

    const [isLoading, setIsLoading] = useState(true);
    const [questions, setQuestions] = useState([]);
    const [userAnswers, setUserAnswers] = useState({});
    const [score, setScore] = useState(null);
    const [finalLevel, setFinalLevel] = useState('');

    useEffect(() => {
        if (!selectedFile || !analysisResult) {
            alert("분석된 파일 정보가 없습니다. 메인 페이지로 돌아갑니다.");
            navigate('/');
            return;
        }

        const fetchQuestions = async () => {
            setIsLoading(true); // 로딩 시작
            try {
                const response = await fetch("http://127.0.0.1:5000/mode/test/start", {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ subject: analysisResult.subject })
                });
                if (!response.ok) throw new Error("문제 로딩 실패");
                const data = await response.json();
                setQuestions(data.questions);
            } catch (error) {
                console.error("문제 생성 오류:", error);
                alert("문제를 불러오는 데 실패했습니다.");
            } finally {
                setIsLoading(false); // 로딩 종료
            }
        };

        fetchQuestions();
    }, [selectedFile, analysisResult, navigate]);

    const handleAnswerChange = (questionId, answer) => {
        setUserAnswers(prevAnswers => ({
            ...prevAnswers,
            [questionId]: answer,
        }));
    };

    const handleSubmitQuiz = async () => {
        if (Object.keys(userAnswers).length !== questions.length) {
            alert("모든 문제에 답해주세요.");
            return;
        }
        
        try {
            const response = await fetch("http://127.0.0.1:5000/mode/test/submit", {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    subject: analysisResult.subject,
                    questions: questions,
                    answers: questions.map(q => userAnswers[q.question] || "")
                })
            });
            if (!response.ok) throw new Error("채점 실패");
            const result = await response.json();
            setScore(result.score);
            setFinalLevel(result.level);
        } catch (error) {
            console.error("채점 오류:", error);
            alert("채점에 실패했습니다.");
        }
    };
    
    const goToResultPage = () => {
        // finalLevel과 함께 /result 페이지로 이동
        navigate('/result', { state: { finalLevel: finalLevel } });
    };

    // 로딩 중일 때 표시할 UI
    if (isLoading) {
        return <div className="test-container"><h2>문제를 불러오는 중입니다...</h2></div>;
    }

    // 채점이 완료되었을 때 표시할 UI
    if (score !== null) {
        return (
            <div className="test-container">
                <div className="result-summary">
                    <h1>퀴즈 결과</h1>
                    <p className="score">점수: <strong>{score}점</strong></p>
                    <p className="recommendation">
                        AI가 판단한 최적의 정리 수준은 <strong>'{finalLevel}'</strong> 입니다.
                    </p>
                    <button onClick={goToResultPage} className="btn-submit">
                        '{finalLevel}' 수준으로 결과 보기
                    </button>
                </div>
            </div>
        );
    }

    // 퀴즈를 푸는 UI
    return (
        <div className="test-container">
            <h1>{selectedFile.name} 내용 확인 퀴즈</h1>
            <p>문제를 풀고 자신에게 맞는 요약 수준을 추천받으세요.</p>
            <div className="quiz-form">
                {questions.map((q, index) => (
                    <div key={index} className="question-block">
                        <h3>{index + 1}. {q.question}</h3>
                        <div className="options">
                            {q.options.map(option => (
                                <label key={option} className="option-label">
                                    <input
                                        type="radio"
                                        name={`question-${index}`}
                                        value={option}
                                        onChange={() => handleAnswerChange(q.question, option)}
                                        checked={userAnswers[q.question] === option}
                                    />
                                    {option}
                                </label>
                            ))}
                        </div>
                    </div>
                ))}
                <button onClick={handleSubmitQuiz} className="btn-submit">채점하기</button>
            </div>
        </div>
    );
};

export default Test;