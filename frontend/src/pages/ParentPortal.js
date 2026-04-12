import React, { useState } from 'react';
import { GraduationCap, ClipboardCheck, DollarSign, CalendarDays, BookOpenCheck, LogOut, Download, User, Phone, MapPin, Menu, X } from 'lucide-react';
import { api } from '../lib/api';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Toaster } from '../components/ui/sonner';

const ParentPortal = () => {
  const [loggedIn, setLoggedIn] = useState(false);
  const [dashData, setDashData] = useState(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [mobileNav, setMobileNav] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const response = await api.parentLogin({ username, password });
      setLoggedIn(true);
      const dash = await api.getParentDashboard(response.data.student.id);
      setDashData(dash.data);
    } catch (error) { toast.error('Invalid credentials'); }
    finally { setLoading(false); }
  };

  const handleLogout = () => { setLoggedIn(false); setDashData(null); setUsername(''); setPassword(''); setActiveTab('overview'); };
  const getStatusColor = (s) => s === 'present' ? 'bg-emerald-100 text-emerald-700' : s === 'absent' ? 'bg-rose-100 text-rose-700' : s === 'holiday' ? 'bg-orange-100 text-orange-800' : 'bg-slate-100 text-slate-600';

  if (!loggedIn) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-sky-50 to-slate-100 flex items-center justify-center p-4">
        <Toaster position="top-right" richColors />
        <div className="bg-white rounded-3xl shadow-2xl border border-slate-100 p-6 sm:p-10 w-full max-w-md">
          <div className="flex flex-col items-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-br from-sky-400 to-sky-600 rounded-2xl flex items-center justify-center mb-4 shadow-lg">
              <GraduationCap className="w-9 h-9 text-white" />
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900" style={{ fontFamily: 'Nunito' }}>Parent Portal</h1>
            <p className="text-sm text-slate-500 mt-1">SchoolPro Management System</p>
          </div>
          <form onSubmit={handleLogin} className="space-y-4">
            <div><Label>Username</Label><Input data-testid="parent-username" required value={username} onChange={(e) => setUsername(e.target.value)} className="rounded-xl h-12" placeholder="Enter parent username" /></div>
            <div><Label>Password</Label><Input data-testid="parent-password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} className="rounded-xl h-12" placeholder="Enter password" /></div>
            <Button data-testid="parent-login-btn" type="submit" disabled={loading} className="w-full bg-sky-500 hover:bg-sky-600 text-white font-bold rounded-xl h-12 active:scale-95 transition-transform">
              {loading ? 'Logging in...' : 'Login'}
            </Button>
          </form>
        </div>
      </div>
    );
  }

  if (!dashData) return <div className="flex items-center justify-center h-screen"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-500"></div></div>;

  const { student, attendanceStats, feeStructure } = dashData;
  const totalFee = (feeStructure?.term1?.total || 0) + (feeStructure?.term2?.total || 0) + (feeStructure?.term3?.total || 0) + (feeStructure?.customFees || []).reduce((s, c) => s + c.total, 0);
  const totalPaid = (feeStructure?.term1?.paid || 0) + (feeStructure?.term2?.paid || 0) + (feeStructure?.term3?.paid || 0) + (feeStructure?.customFees || []).reduce((s, c) => s + c.paid, 0);
  const totalPending = totalFee - totalPaid;

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
      {/* Header */}
      <div className="bg-white border-b border-slate-200 px-4 py-3 sticky top-0 z-30">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button className="lg:hidden p-2 hover:bg-slate-100 rounded-xl" onClick={() => setMobileNav(!mobileNav)}>{mobileNav ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}</button>
            <div className="w-10 h-10 bg-gradient-to-br from-sky-400 to-sky-600 rounded-xl flex items-center justify-center"><GraduationCap className="w-5 h-5 text-white" /></div>
            <div className="hidden sm:block"><h1 className="text-base font-extrabold text-slate-900" style={{ fontFamily: 'Nunito' }}>Parent Portal</h1><p className="text-xs text-slate-500">{student.studentName} - Class {student.studentClass}-{student.section}</p></div>
          </div>
          <Button variant="outline" onClick={handleLogout} className="rounded-xl font-bold text-sm"><LogOut className="w-4 h-4 mr-1 sm:mr-2" /><span className="hidden sm:inline">Logout</span></Button>
        </div>
      </div>

      <div className="max-w-6xl mx-auto p-4 sm:p-6 space-y-6">
        {/* Tabs - scrollable on mobile */}
        <div className={`${mobileNav ? 'flex' : 'hidden lg:flex'} flex-wrap gap-2 pb-2`}>
          {tabs.map((t) => {
            const Icon = t.icon;
            return <button key={t.key} onClick={() => { setActiveTab(t.key); setMobileNav(false); }} className={`flex items-center gap-2 px-4 sm:px-5 py-2.5 rounded-xl font-bold text-xs sm:text-sm transition-all whitespace-nowrap ${activeTab === t.key ? 'bg-sky-500 text-white shadow-lg' : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'}`}><Icon className="w-4 h-4" />{t.label}</button>;
          })}
        </div>
        {/* Mobile: show active tab label */}
        <div className="lg:hidden flex items-center justify-between">
          <button onClick={() => setMobileNav(!mobileNav)} className="text-sm font-bold text-sky-600 underline">{tabs.find(t => t.key === activeTab)?.label} (tap to switch)</button>
        </div>

        {/* ========= OVERVIEW ========= */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Student Card */}
            <div className="bg-white rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.04)] border border-slate-100 p-5 sm:p-6">
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
                <div className="w-16 h-16 bg-gradient-to-br from-sky-400 to-sky-600 rounded-2xl flex items-center justify-center flex-shrink-0">
                  <User className="w-8 h-8 text-white" />
                </div>
                <div className="flex-1">
                  <h2 className="text-xl sm:text-2xl font-extrabold text-slate-900" style={{ fontFamily: 'Nunito' }}>{student.studentName}</h2>
                  <p className="text-sm text-slate-500 mt-1">Roll No: {student.rollNo} | Class {student.studentClass}-{student.section}</p>
                  <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2 text-xs text-slate-600">
                    <span className="flex items-center gap-1"><User className="w-3 h-3" />{student.fatherName}</span>
                    <span className="flex items-center gap-1"><Phone className="w-3 h-3" />{student.mobile}</span>
                    <span className="flex items-center gap-1"><MapPin className="w-3 h-3" />{student.address}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white rounded-2xl shadow p-4 sm:p-5 border border-slate-100">
                <p className="text-[10px] sm:text-xs font-bold uppercase tracking-widest text-slate-400">Attendance</p>
                <p className={`text-2xl sm:text-3xl font-extrabold mt-1 ${attendanceStats.percentage >= 75 ? 'text-emerald-600' : 'text-rose-600'}`}>{attendanceStats.percentage}%</p>
                <p className="text-xs text-slate-500 mt-1">{attendanceStats.presentDays}/{attendanceStats.totalDays} days</p>
              </div>
              <div className="bg-white rounded-2xl shadow p-4 sm:p-5 border border-slate-100">
                <p className="text-[10px] sm:text-xs font-bold uppercase tracking-widest text-slate-400">Total Fee</p>
                <p className="text-2xl sm:text-3xl font-extrabold mt-1 text-slate-900">{'\u20B9'}{totalFee.toLocaleString()}</p>
              </div>
              <div className="bg-white rounded-2xl shadow p-4 sm:p-5 border border-slate-100">
                <p className="text-[10px] sm:text-xs font-bold uppercase tracking-widest text-slate-400">Paid</p>
                <p className="text-2xl sm:text-3xl font-extrabold mt-1 text-emerald-600">{'\u20B9'}{totalPaid.toLocaleString()}</p>
              </div>
              <div className="bg-white rounded-2xl shadow p-4 sm:p-5 border border-slate-100">
                <p className="text-[10px] sm:text-xs font-bold uppercase tracking-widest text-slate-400">Pending</p>
                <p className="text-2xl sm:text-3xl font-extrabold mt-1 text-rose-600">{'\u20B9'}{totalPending.toLocaleString()}</p>
              </div>
            </div>

            {/* Quick upcoming */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-white rounded-2xl shadow p-5 border border-slate-100">
                <h3 className="text-base font-bold text-slate-800 mb-3">Upcoming Events</h3>
                {dashData.events.filter(e => e.date >= new Date().toISOString().split('T')[0]).slice(0, 3).map((ev) => (
                  <div key={ev.id} className="flex items-center gap-3 p-2 rounded-lg hover:bg-slate-50">
                    <div className="w-10 h-10 bg-amber-100 rounded-lg flex flex-col items-center justify-center flex-shrink-0">
                      <span className="text-[10px] font-bold text-amber-700">{new Date(ev.date+'T00:00:00').toLocaleDateString('en-IN',{month:'short'})}</span>
                      <span className="text-sm font-extrabold text-amber-800 leading-none">{new Date(ev.date+'T00:00:00').getDate()}</span>
                    </div>
                    <p className="text-sm font-bold text-slate-800 truncate">{ev.title}</p>
                  </div>
                ))}
                {dashData.events.filter(e => e.date >= new Date().toISOString().split('T')[0]).length === 0 && <p className="text-sm text-slate-400">No upcoming events</p>}
              </div>
              <div className="bg-white rounded-2xl shadow p-5 border border-slate-100">
                <h3 className="text-base font-bold text-slate-800 mb-3">Recent Homework</h3>
                {dashData.homework.slice(-3).reverse().map((hw) => (
                  <div key={hw.id} className="p-2 rounded-lg hover:bg-slate-50">
                    <div className="flex items-center gap-2">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-sky-100 text-sky-700">{hw.subject}</span>
                      {hw.dueDate < new Date().toISOString().split('T')[0] && <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-700">OVERDUE</span>}
                    </div>
                    <p className="text-sm font-bold text-slate-800 mt-1">{hw.title}</p>
                    <p className="text-xs text-slate-500">Due: {hw.dueDate}</p>
                  </div>
                ))}
                {dashData.homework.length === 0 && <p className="text-sm text-slate-400">No homework</p>}
              </div>
            </div>
          </div>
        )}

        {/* ========= ATTENDANCE ========= */}
        {activeTab === 'attendance' && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="bg-white rounded-xl shadow p-4 border text-center"><p className="text-xs font-bold text-slate-400 uppercase">Total</p><p className="text-2xl font-extrabold text-slate-900">{attendanceStats.totalDays}</p></div>
              <div className="bg-emerald-50 rounded-xl shadow p-4 border border-emerald-200 text-center"><p className="text-xs font-bold text-emerald-500 uppercase">Present</p><p className="text-2xl font-extrabold text-emerald-600">{attendanceStats.presentDays}</p></div>
              <div className="bg-rose-50 rounded-xl shadow p-4 border border-rose-200 text-center"><p className="text-xs font-bold text-rose-500 uppercase">Absent</p><p className="text-2xl font-extrabold text-rose-600">{attendanceStats.absentDays}</p></div>
              <div className={`rounded-xl shadow p-4 border text-center ${attendanceStats.percentage >= 75 ? 'bg-emerald-50 border-emerald-200' : 'bg-rose-50 border-rose-200'}`}><p className="text-xs font-bold text-slate-400 uppercase">Percentage</p><p className={`text-2xl font-extrabold ${attendanceStats.percentage >= 75 ? 'text-emerald-600' : 'text-rose-600'}`}>{attendanceStats.percentage}%</p></div>
            </div>
            <div className="bg-white rounded-2xl shadow p-4 sm:p-6 border border-slate-100">
              <h2 className="text-lg font-bold text-slate-800 mb-4">Last 30 Days</h2>
              <div className="space-y-2">
                {dashData.recentAttendance.slice().reverse().map((a, i) => (
                  <div key={i} className="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                    <p className="font-medium text-slate-700 text-sm">{a.date}</p>
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold ${getStatusColor(a.status)}`}>{a.status.toUpperCase()}</span>
                  </div>
                ))}
                {dashData.recentAttendance.length === 0 && <p className="text-slate-400 text-center py-8">No records yet</p>}
              </div>
            </div>
          </div>
        )}

        {/* ========= FEES ========= */}
        {activeTab === 'fees' && (
          <div className="space-y-6">
            {/* Fee Structure */}
            <div className="bg-white rounded-2xl shadow p-4 sm:p-6 border border-slate-100">
              <h2 className="text-lg font-bold text-slate-800 mb-4">Fee Structure</h2>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
                {['term1', 'term2', 'term3'].map((t, i) => {
                  const term = feeStructure?.[t] || { total: 0, paid: 0 };
                  const pending = term.total - term.paid;
                  const paid = term.paid >= term.total;
                  return (
                    <div key={t} className={`rounded-xl border p-4 ${paid ? 'border-emerald-300 bg-emerald-50/40' : term.paid > 0 ? 'border-amber-300 bg-amber-50/40' : 'border-slate-200'}`}>
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-bold text-slate-900">Term {i + 1}</h4>
                        {paid ? <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500 text-white">PAID</span>
                          : term.paid > 0 ? <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-500 text-white">PARTIAL</span>
                          : <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-700">UNPAID</span>}
                      </div>
                      <p className="text-xl font-extrabold text-slate-900">{'\u20B9'}{term.total.toLocaleString()}</p>
                      <div className="flex justify-between mt-2 text-xs">
                        <span className="text-emerald-600 font-bold">Paid: {'\u20B9'}{term.paid.toLocaleString()}</span>
                        {!paid && <span className="text-rose-600 font-bold">Due: {'\u20B9'}{pending.toLocaleString()}</span>}
                      </div>
                    </div>
                  );
                })}
              </div>
              {/* Custom Fees */}
              {(feeStructure?.customFees || []).length > 0 && (
                <>
                  <h3 className="text-base font-bold text-slate-700 mb-3 mt-4">Additional Fees</h3>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {feeStructure.customFees.map((cf) => {
                      const pending = cf.total - cf.paid;
                      const paid = cf.paid >= cf.total;
                      return (
                        <div key={cf.id} className={`rounded-xl border p-4 ${paid ? 'border-emerald-300 bg-emerald-50/40' : cf.paid > 0 ? 'border-amber-300 bg-amber-50/40' : 'border-slate-200'}`}>
                          <div className="flex items-center justify-between mb-1">
                            <h4 className="font-bold text-slate-900 text-sm">{cf.feeName}</h4>
                            {paid ? <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500 text-white">PAID</span>
                              : <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-rose-100 text-rose-700">DUE</span>}
                          </div>
                          {cf.dueDate && <p className="text-xs text-rose-500 font-medium">Due: {cf.dueDate}</p>}
                          <p className="text-lg font-extrabold text-slate-900 mt-1">{'\u20B9'}{cf.total.toLocaleString()}</p>
                          <div className="flex justify-between mt-1 text-xs">
                            <span className="text-emerald-600 font-bold">Paid: {'\u20B9'}{cf.paid.toLocaleString()}</span>
                            {!paid && <span className="text-rose-600 font-bold">Due: {'\u20B9'}{pending.toLocaleString()}</span>}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </>
              )}
              {/* Total Summary */}
              <div className="mt-4 p-4 bg-slate-50 rounded-xl grid grid-cols-3 gap-4 text-center">
                <div><p className="text-xs font-bold text-slate-400 uppercase">Total Fee</p><p className="text-lg font-extrabold text-slate-900">{'\u20B9'}{totalFee.toLocaleString()}</p></div>
                <div><p className="text-xs font-bold text-slate-400 uppercase">Total Paid</p><p className="text-lg font-extrabold text-emerald-600">{'\u20B9'}{totalPaid.toLocaleString()}</p></div>
                <div><p className="text-xs font-bold text-slate-400 uppercase">Balance</p><p className="text-lg font-extrabold text-rose-600">{'\u20B9'}{totalPending.toLocaleString()}</p></div>
              </div>
            </div>

            {/* Payment History */}
            <div className="bg-white rounded-2xl shadow p-4 sm:p-6 border border-slate-100">
              <h2 className="text-lg font-bold text-slate-800 mb-4">Payment History</h2>
              <div className="space-y-2">
                {dashData.payments.slice().reverse().map((p) => (
                  <div key={p.id} className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-3 bg-slate-50 rounded-xl gap-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="font-bold text-slate-900 text-sm">{p.receiptNumber}</span>
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold ${p.paymentMode === 'upi' ? 'bg-sky-100 text-sky-700' : 'bg-emerald-100 text-emerald-700'}`}>{p.paymentMode.toUpperCase()}</span>
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5">{p.termNumber ? `Term ${p.termNumber}` : (p.feeName || 'Custom')} | {typeof p.paymentDate === 'string' ? p.paymentDate.slice(0, 10) : ''}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="font-bold text-emerald-600">{'\u20B9'}{p.amount.toLocaleString()}</span>
                      <a href={api.getInvoiceUrl(p.id)} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 px-3 py-1.5 bg-sky-100 text-sky-700 hover:bg-sky-200 rounded-lg font-bold text-xs"><Download className="w-3 h-3" />Invoice</a>
                    </div>
                  </div>
                ))}
                {dashData.payments.length === 0 && <p className="text-slate-400 text-center py-8 text-sm">No payments yet</p>}
              </div>
            </div>
          </div>
        )}

        {/* ========= EVENTS ========= */}
        {activeTab === 'events' && (
          <div className="bg-white rounded-2xl shadow p-4 sm:p-6 border border-slate-100">
            <h2 className="text-lg font-bold text-slate-800 mb-4">School Events</h2>
            <div className="space-y-3">
              {dashData.events.sort((a, b) => b.date.localeCompare(a.date)).map((ev) => (
                <div key={ev.id} className="flex items-start gap-3 sm:gap-4 p-3 sm:p-4 bg-slate-50 rounded-xl">
                  <div className="w-12 h-12 sm:w-14 sm:h-14 bg-gradient-to-br from-amber-400 to-amber-600 rounded-xl flex flex-col items-center justify-center text-white shadow flex-shrink-0">
                    <p className="text-[10px] font-bold">{new Date(ev.date+'T00:00:00').toLocaleDateString('en-IN',{month:'short'})}</p>
                    <p className="text-lg sm:text-xl font-extrabold leading-none">{new Date(ev.date+'T00:00:00').getDate()}</p>
                  </div>
                  <div><h3 className="font-bold text-slate-900">{ev.title}</h3><p className="text-sm text-slate-600 mt-1">{ev.description}</p></div>
                </div>
              ))}
              {dashData.events.length === 0 && <p className="text-slate-400 text-center py-8 text-sm">No events</p>}
            </div>
          </div>
        )}

        {/* ========= HOMEWORK ========= */}
        {activeTab === 'homework' && (
          <div className="space-y-3">
            {dashData.homework.length === 0 && <div className="bg-white rounded-2xl shadow p-8 border text-center"><p className="text-slate-400">No homework assigned</p></div>}
            {dashData.homework.map((hw) => (
              <div key={hw.id} className={`bg-white rounded-2xl shadow p-4 sm:p-5 border transition-all ${hw.dueDate < new Date().toISOString().split('T')[0] ? 'border-rose-200' : 'border-slate-100'}`}>
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-sky-100 text-sky-700">{hw.subject}</span>
                  {hw.dueDate < new Date().toISOString().split('T')[0] && <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-rose-100 text-rose-700">OVERDUE</span>}
                </div>
                <h3 className="text-base font-bold text-slate-900">{hw.title}</h3>
                <p className="text-sm text-slate-600 mt-1">{hw.description}</p>
                <div className="flex items-center gap-4 mt-3 text-xs text-slate-500">
                  <span className={`font-bold ${hw.dueDate < new Date().toISOString().split('T')[0] ? 'text-rose-600' : 'text-slate-600'}`}>Due: {hw.dueDate}</span>
                  <span>By: {hw.assignedBy}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ParentPortal;
