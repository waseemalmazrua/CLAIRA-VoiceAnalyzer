import { Route, Routes } from "react-router";

import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import VoiceAnalyzerPage from "./pages/VoiceAnalyzerPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/voice" element={<VoiceAnalyzerPage />} />
    </Routes>
  );
}

export default App;
