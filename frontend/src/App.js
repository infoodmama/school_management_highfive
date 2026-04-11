import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Classes from './pages/Classes';
import Students from './pages/Students';
import StudentDetail from './pages/StudentDetail';
import Attendance from './pages/Attendance';
import Fees from './pages/Fees';
import Expenses from './pages/Expenses';
import Inventory from './pages/Inventory';
import EventCalendar from './pages/EventCalendar';
import HomeworkPage from './pages/HomeworkPage';
import Settings from './pages/Settings';
import Layout from './components/Layout';
import { Toaster } from './components/ui/sonner';
import './App.css';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="classes" element={<Classes />} />
            <Route path="students" element={<Students />} />
            <Route path="students/:id" element={<StudentDetail />} />
            <Route path="attendance" element={<Attendance />} />
            <Route path="fees" element={<Fees />} />
            <Route path="expenses" element={<Expenses />} />
            <Route path="inventory" element={<Inventory />} />
            <Route path="calendar" element={<EventCalendar />} />
            <Route path="homework" element={<HomeworkPage />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" richColors />
    </div>
  );
}

export default App;
