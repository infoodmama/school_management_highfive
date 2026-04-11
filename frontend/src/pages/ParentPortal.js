import React, { useState, useEffect } from 'react';
import { GraduationCap, ClipboardCheck, DollarSign, CalendarDays, BookOpenCheck, LogOut, Download } from 'lucide-react';
import { api } from '../lib/api';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Toaster } from '../components/ui/sonner';

const ParentPortal = () => {
  const [loggedIn, setLoggedIn] = useState(false);
  const [studentData, setStudentData] = useState(null);
  const [dashData, setDashData] = useState(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const response = await api.parentLogin({ username, password });
      setStudentData(response.data.student);
      setLoggedIn(true);
      const dash = await api.getParentDashboard(response.data.student.id);
      setDashData(dash.data);
    } catch (error) {
      toast.error('Invalid credentials');
    } finally { setLoading(false); }
  };

  const handleLogout = () => { setLoggedIn(false); setStudentData(null); setDashData(null); setUsername(''); setPassword(''); };

  const getStatusColor = (s) => s === 'present' ? 'bg-emerald-100 text-emerald-700' : s === 'absent' ? 'bg-rose-100 text-rose-700' : s === 'holiday' ? 'bg-orange-100 text-orange-800' : 'bg-slate-100 text-slate-600';

  if (!loggedIn) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
        <Toaster position="top-right" richColors />
        <div className="bg-white rounded-2xl shadow-xl border border-slate-100 p-8 w-full max-w-md">
          <div className="flex items-center gap-3 mb-8 justify-center">
            <div className="w-14 h-14 bg-gradient-to-br from-sky-400 to-sky-600 rounded-2xl flex items-center justify-center">
              <GraduationCap className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-extrabold text-slate-900" style={{ fontFamily: 'Nunito' }}>Parent Portal</h1>
              <p className="text-sm text-slate-500">SchoolPro Management</p>
            </div>
          </div>
          <form onSubmit={handleLogin} className="space-y-4">
            <div><Label>Username *</Label><Input data-testid="parent-username" required value={username} onChange={(e) => setUsername(e.target.value)} className="rounded-xl h-12" placeholder="Enter parent username" /></div>
            <div><Label>Password *</Label><Input data-testid="parent-password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} className="rounded-xl h-12" placeholder="Enter password" /></div>
            <Button data-testid="parent-login-btn" type="submit" disabled={loading} className="w-full bg-sky-500 hover:bg-sky-600 text-white font-bold rounded-xl h-12 active:scale-95 transition-transform">
              {loading ? 'Logging in...' : 'Login'}
            </Button>
          </form>
        </div>
      </div>
    );
  }

  if (!dashData) return <div className="flex items-center justify-center h-screen"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-500"></div></div>;

  const tabs = [
    { key: 'overview', label: 'Overview', icon: GraduationCap },
    { key: 'attendance', label: 'Attendance', icon: ClipboardCheck },
    { key: 'fees', label: 'Fees', icon: DollarSign },
    { key: 'events', label: 'Events', icon: CalendarDays },
    { key: 'homework', label: 'Homework', icon: BookOpenCheck },
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      <Toaster position="top-right" richColors />
      <div className="bg-white border-b border-slate-200 p-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-sky-400 to-sky-600 rounded-xl flex items-center justify-center"><GraduationCap className="w-5 h-5 text-white" /></div>
            <div>
              <h1 className="text-lg font-extrabold text-slate-900" style={{ fontFamily: 'Nunito' }}>Parent Portal</h1>
              <p className="text-xs text-slate-500">{dashData.student.studentName} - Class {dashData.student.studentClass}-{dashData.student.section}</p>
            </div>
          </div>
          <Button variant="outline" onClick={handleLogout} className="rounded-xl font-bold"><LogOut className="w-4 h-4 mr-2" />Logout</Button>
        </div>
      </div>

      <div className="max-w-6xl mx-auto p-6 space-y-6">
        <div className="flex gap-2 overflow-x-auto pb-2">
          {tabs.map((t) => {
            const Icon = t.icon;
            return <button key={t.key} onClick={() => setActiveTab(t.key)} className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm transition-all whitespace-nowrap ${activeTab === t.key ? 'bg-sky-500 text-white shadow-lg' : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'}`}><Icon className="w-4 h-4" />{t.label}</button>;
          })}
        </div>

        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white rounded-2xl shadow p-6 border border-slate-100">
              <p className="text-xs font-bold uppercase tracking-widest text-slate-400">Attendance</p>
              <p className={`text-4xl font-extrabold mt-2 ${dashData.attendanceStats.percentage >= 75 ? 'text-emerald-600' : 'text-rose-600'}`}>{dashData.attendanceStats.percentage}%</p>
              <p className="text-sm text-slate-600 mt-1">{dashData.attendanceStats.presentDays}/{dashData.attendanceStats.totalDays} days present</p>
            </div>
            <div className="bg-white rounded-2xl shadow p-6 border border-slate-100">
              <p className="text-xs font-bold uppercase tracking-widest text-slate-400">Total Payments</p>
              <p className="text-4xl font-extrabold mt-2 text-sky-600">{'\u20B9'}{dashData.payments.reduce((s, p) => s + p.amount, 0).toLocaleString()}</p>
              <p className="text-sm text-slate-600 mt-1">{dashData.payments.length} transactions</p>
            </div>
            <div className="bg-white rounded-2xl shadow p-6 border border-slate-100">
              <p className="text-xs font-bold uppercase tracking-widest text-slate-400">Upcoming Events</p>
              <p className="text-4xl font-extrabold mt-2 text-amber-600">{dashData.events.filter(e => e.date >= new Date().toISOString().split('T')[0]).length}</p>
            </div>
          </div>
        )}

        {activeTab === 'attendance' && (
          <div className="bg-white rounded-2xl shadow p-6 border border-slate-100">
            <h2 className="text-xl font-bold text-slate-800 mb-4">Recent Attendance</h2>
            <div className="space-y-2">
              {dashData.recentAttendance.slice().reverse().map((a, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                  <p className="font-medium text-slate-700">{a.date}</p>
                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold ${getStatusColor(a.status)}`}>{a.status.toUpperCase()}</span>
                </div>
              ))}
              {dashData.recentAttendance.length === 0 && <p className="text-slate-400 text-center py-8">No attendance records yet</p>}
            </div>
          </div>
        )}

        {activeTab === 'fees' && (
          <div className="bg-white rounded-2xl shadow p-6 border border-slate-100">
            <h2 className="text-xl font-bold text-slate-800 mb-4">Payment History</h2>
            <div className="space-y-2">
              {dashData.payments.slice().reverse().map((p) => (
                <div key={p.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                  <div className="flex-1 grid grid-cols-4 gap-4">
                    <p className="font-medium text-slate-700">{p.receiptNumber}</p>
                    <p className="text-slate-600">{p.termNumber ? `Term ${p.termNumber}` : (p.feeName || 'Custom')}</p>
                    <p className="font-bold text-emerald-600">{'\u20B9'}{p.amount.toLocaleString()}</p>
                    <a href={api.getInvoiceUrl(p.id)} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-sky-600 font-bold text-sm hover:underline"><Download className="w-3 h-3" />Invoice</a>
                  </div>
                </div>
              ))}
              {dashData.payments.length === 0 && <p className="text-slate-400 text-center py-8">No payments yet</p>}
            </div>
          </div>
        )}

        {activeTab === 'events' && (
          <div className="bg-white rounded-2xl shadow p-6 border border-slate-100">
            <h2 className="text-xl font-bold text-slate-800 mb-4">School Events</h2>
            <div className="space-y-3">
              {dashData.events.sort((a, b) => b.date.localeCompare(a.date)).map((ev) => (
                <div key={ev.id} className="flex items-start gap-4 p-4 bg-slate-50 rounded-xl">
                  <div className="w-14 h-14 bg-gradient-to-br from-amber-400 to-amber-600 rounded-xl flex flex-col items-center justify-center text-white shadow">
                    <p className="text-xs font-bold">{new Date(ev.date + 'T00:00:00').toLocaleDateString('en-IN', { month: 'short' })}</p>
                    <p className="text-xl font-extrabold leading-none">{new Date(ev.date + 'T00:00:00').getDate()}</p>
                  </div>
                  <div><h3 className="font-bold text-slate-900">{ev.title}</h3><p className="text-sm text-slate-600 mt-1">{ev.description}</p></div>
                </div>
              ))}
              {dashData.events.length === 0 && <p className="text-slate-400 text-center py-8">No events</p>}
            </div>
          </div>
        )}

        {activeTab === 'homework' && (
          <div className="bg-white rounded-2xl shadow p-6 border border-slate-100">
            <h2 className="text-xl font-bold text-slate-800 mb-4">Homework</h2>
            <div className="space-y-3">
              {dashData.homework.map((hw) => (
                <div key={hw.id} className={`p-4 rounded-xl border ${hw.dueDate < new Date().toISOString().split('T')[0] ? 'border-rose-200 bg-rose-50/30' : 'bg-slate-50 border-slate-100'}`}>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-sky-100 text-sky-700">{hw.subject}</span>
                    {hw.dueDate < new Date().toISOString().split('T')[0] && <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-700">OVERDUE</span>}
                  </div>
                  <h3 className="font-bold text-slate-900">{hw.title}</h3>
                  <p className="text-sm text-slate-600 mt-1">{hw.description}</p>
                  <p className="text-xs text-slate-500 mt-2">Due: {hw.dueDate} | By: {hw.assignedBy}</p>
                </div>
              ))}
              {dashData.homework.length === 0 && <p className="text-slate-400 text-center py-8">No homework assigned</p>}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ParentPortal;
