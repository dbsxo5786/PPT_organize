import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useState } from 'react';

// 컴포넌트 import
import Header from './component/header';
import Footer from './component/footer';
import Main from './pages/main';
import Result from './pages/result';
import Test from './pages/test';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [level, setLevel] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null); // API 분석 결과를 저장할 상태

  return (
    <BrowserRouter>
      <Header />
      <div className="content-wrap">
        <Routes>
          <Route 
            path="/" 
            element={<Main 
              selectedFile={selectedFile} 
              setSelectedFile={setSelectedFile}
              level={level}
              setLevel={setLevel}
              setAnalysisResult={setAnalysisResult}
            />} 
          />
          <Route 
            path="/test" 
            element={<Test 
              selectedFile={selectedFile} 
              analysisResult={analysisResult} 
            />} 
          />
          <Route 
            path="/result" 
            element={<Result 
              selectedFile={selectedFile} 
              level={level} 
              analysisResult={analysisResult} 
            />} 
          />
        </Routes>
      </div>
      <Footer />
    </BrowserRouter>
  );
}

export default App;