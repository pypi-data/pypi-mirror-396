import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Dashboard from './components/Dashboard'
import Scenarios from './components/Scenarios'
import Runs from './components/Runs'
import Executors from './components/Executors'
import RunCreate from './components/RunCreate'
import ScenarioDetail from './components/ScenarioDetail'
import ResultDetail from './components/ResultDetail'
import CompareResults from './components/CompareResults'
import Datasets from './components/Datasets'
import DatasetDetail from './components/DatasetDetail'
import DatasetCreate from './components/DatasetCreate'
import DatasetAnalytics from './components/DatasetAnalytics'
import GlobalReport from './components/GlobalReport'
import Judgements from './components/Judgements'
import Navbar from './components/Navbar'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-canvas text-text-primary">
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 py-6 sm:px-6 lg:px-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/scenarios" element={<Scenarios />} />
            <Route path="/runs" element={<Runs />} />
            <Route path="/executors" element={<Executors />} />
            <Route path="/datasets" element={<Datasets />} />
            <Route path="/dataset/create" element={<DatasetCreate />} />
            <Route path="/dataset/:id" element={<DatasetDetail />} />
            <Route path="/dataset/:id/analytics" element={<DatasetAnalytics />} />
            <Route path="/run/create" element={<RunCreate />} />
            <Route path="/scenario/:id" element={<ScenarioDetail />} />
            <Route path="/result/:id" element={<ResultDetail />} />
            <Route path="/compare" element={<CompareResults />} />
            <Route path="/judgements" element={<Judgements />} />
            <Route path="/report" element={<GlobalReport />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App
