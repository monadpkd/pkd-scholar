import { HashRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import WorkDetail from './pages/WorkDetail';
import SegmentDetail from './pages/SegmentDetail';
import Search from './pages/Search';
import Topics from './pages/Topics';
import TopicDetail from './pages/TopicDetail';
import Studies from './pages/Studies';
import StudyDetail from './pages/StudyDetail';

export default function App() {
  return (
    <HashRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/studies" element={<Studies />} />
          <Route path="/studies/:slug" element={<StudyDetail />} />
          <Route path="/works/:slug" element={<WorkDetail />} />
          <Route path="/segments/:segId" element={<SegmentDetail />} />
          <Route path="/search" element={<Search />} />
          <Route path="/topics" element={<Topics />} />
          <Route path="/topics/:slug" element={<TopicDetail />} />
        </Route>
      </Routes>
    </HashRouter>
  );
}
