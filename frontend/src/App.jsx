import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import UploadPage from './pages/UploadPage';
import PatientsPage from './pages/PatientsPage';
import PatientReviewPage from './pages/PatientReviewPage';
import Navbar from './components/Navbar';

function App() {
  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<UploadPage />} />
        <Route path="/patients" element={<PatientsPage />} />
        <Route path="/patients/:patientId" element={<PatientReviewPage />} />
      </Routes>
    </Router>
  );
}

export default App;
