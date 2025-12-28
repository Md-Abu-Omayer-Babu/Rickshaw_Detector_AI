import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import Dashboard from './pages/Dashboard';
import ImageDetection from './pages/ImageDetection';
import VideoDetection from './pages/VideoDetection';
import CCTV from './pages/CCTV';
import Analytics from './pages/Analytics';
import History from './pages/History';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="image" element={<ImageDetection />} />
          <Route path="video" element={<VideoDetection />} />
          <Route path="cctv" element={<CCTV />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="history" element={<History />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
