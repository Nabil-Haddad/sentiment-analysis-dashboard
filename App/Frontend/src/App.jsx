import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import NewAnalysis from './pages/NewAnalysis';
import History from './pages/History';
import AnalysisDetail from './pages/AnalysisDetail';
import Aspects from './pages/Aspects';

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/new" element={<NewAnalysis />} />
        <Route path="/history" element={<History />} />
        <Route path="/analysis/:id" element={<AnalysisDetail />} />
        <Route path="/aspects" element={<Aspects />} />
      </Routes>
    </Layout>
  );
}
