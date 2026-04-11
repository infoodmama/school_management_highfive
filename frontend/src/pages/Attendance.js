import React, { useState, useEffect, useCallback } from 'react';
import { UserCheck, Calendar, Download, Send } from 'lucide-react';
import { api } from '../lib/api';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';

const Attendance = () => {
  const [activeTab, setActiveTab] = useState('take');
  const [classes, setClasses] = useState([]);
  const [students, setStudents] = useState([]);
  const [attendanceRecords, setAttendanceRecords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [takeAttendance, setTakeAttendance] = useState({ studentClass: '', section: '', date: new Date().toISOString().split('T')[0] });
  const [attendanceData, setAttendanceData] = useState([]);
  const [viewFilters, setViewFilters] = useState({ studentClass: '', section: '', startDate: '', endDate: '' });

  const loadClasses = useCallback(async () => {
    try { const r = await api.getClasses(); setClasses(r.data); } catch (e) { /* ignore */ }
  }, []);
  useEffect(() => { loadClasses(); }, [loadClasses]);

  const getSections = (cls) => { const f = classes.find((c) => c.className === cls); return f ? f.sections : []; };

  const handleLoadStudents = async () => {
    if (!takeAttendance.studentClass || !takeAttendance.section) { toast.error('Please select class and section'); return; }
    try {
      setLoading(true);
      const response = await api.getStudents({ studentClass: takeAttendance.studentClass, section: takeAttendance.section });
      setStudents(response.data);
      setAttendanceData(response.data.map((s) => ({ studentId: s.id, rollNo: s.rollNo, studentName: s.studentName, mobile: s.mobile, status: 'undefined' })));
    } catch (error) { toast.error('Failed to load students'); }
    finally { setLoading(false); }
  };

  const handleMarkAttendance = (index, status) => { const d = [...attendanceData]; d[index].status = status; setAttendanceData(d); };
  const handleBulkMark = (status) => { setAttendanceData(attendanceData.map((r) => ({ ...r, status }))); };

  const handleSubmitAttendance = async () => {
    try {
      await api.markAttendance({ studentClass: takeAttendance.studentClass, section: takeAttendance.section, date: takeAttendance.date, records: attendanceData });
      const absentRecords = attendanceData.filter((r) => r.status === 'absent');
      if (absentRecords.length > 0) {
        await api.sendAttendanceAlerts({ absentRecords: absentRecords.map((r) => ({ ...r, studentClass: takeAttendance.studentClass, section: takeAttendance.section, date: takeAttendance.date })) });
      }
      toast.success('Attendance marked successfully');
      setStudents([]); setAttendanceData([]);
    } catch (error) { toast.error('Failed to mark attendance'); }
  };

  const handleViewAttendance = async () => {
    if (!viewFilters.studentClass || !viewFilters.section) { toast.error('Please select class and section'); return; }
    try {
      setLoading(true);
      const response = await api.getAttendance(viewFilters);
      setAttendanceRecords(response.data);
    } catch (error) { toast.error('Failed to load attendance'); }
    finally { setLoading(false); }
  };

  const handleExport = async (format) => {
    if (!viewFilters.studentClass || !viewFilters.section || !viewFilters.startDate || !viewFilters.endDate) { toast.error('Please fill all filters'); return; }
    try {
      const response = await api.exportAttendance({ ...viewFilters, format });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url; link.setAttribute('download', `attendance.${format}`); document.body.appendChild(link); link.click(); link.remove();
      toast.success('Attendance exported');
    } catch (error) { toast.error('Failed to export'); }
  };

  const getStatusBadgeColor = (status) => {
    switch (status) {
      case 'present': return 'bg-emerald-100 text-emerald-700';
      case 'absent': return 'bg-rose-100 text-rose-700';
      case 'holiday': return 'bg-orange-100 text-orange-800';
      default: return 'bg-slate-100 text-slate-600';
    }
  };

  // Calculate attendance percentage per student
  const getStudentStats = () => {
    const stats = {};
    attendanceRecords.forEach((r) => {
      if (!stats[r.rollNo]) stats[r.rollNo] = { name: r.studentName, rollNo: r.rollNo, total: 0, present: 0 };
      stats[r.rollNo].total++;
      if (r.status === 'present') stats[r.rollNo].present++;
    });
    return Object.values(stats);
  };

  return (
    <div className="max-w-[1600px] mx-auto space-y-6">
      <div>
        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900" style={{ fontFamily: 'Nunito' }}>Attendance Management</h1>
        <p className="text-base font-medium text-slate-600 mt-1" style={{ fontFamily: 'Figtree' }}>Mark and view student attendance</p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="bg-slate-100 p-1 rounded-xl inline-flex">
          <TabsTrigger data-testid="take-attendance-tab" value="take" className="data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-lg px-6 py-2 font-bold">
            <UserCheck className="w-4 h-4 mr-2" />Take Attendance
          </TabsTrigger>
          <TabsTrigger data-testid="view-attendance-tab" value="view" className="data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-lg px-6 py-2 font-bold">
            <Calendar className="w-4 h-4 mr-2" />View Attendance
          </TabsTrigger>
        </TabsList>

        <TabsContent value="take" className="space-y-6">
          <div className="bg-white rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.04)] border border-slate-100 p-6">
            <h2 className="text-xl font-bold text-slate-800 mb-4">Select Class & Date</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <Label>Class *</Label>
                <Select value={takeAttendance.studentClass} onValueChange={(v) => setTakeAttendance({ ...takeAttendance, studentClass: v, section: '' })}>
                  <SelectTrigger data-testid="attendance-class-select" className="rounded-xl h-12"><SelectValue placeholder="Select Class" /></SelectTrigger>
                  <SelectContent>{classes.map((c) => <SelectItem key={c.className} value={c.className}>Class {c.className}</SelectItem>)}</SelectContent>
                </Select>
              </div>
              <div>
                <Label>Section *</Label>
                <Select value={takeAttendance.section} onValueChange={(v) => setTakeAttendance({ ...takeAttendance, section: v })}>
                  <SelectTrigger data-testid="attendance-section-select" className="rounded-xl h-12"><SelectValue placeholder="Select Section" /></SelectTrigger>
                  <SelectContent>{getSections(takeAttendance.studentClass).map((s) => <SelectItem key={s} value={s}>Section {s}</SelectItem>)}</SelectContent>
                </Select>
              </div>
              <div>
                <Label>Date *</Label>
                <Input type="date" data-testid="attendance-date-input" value={takeAttendance.date} onChange={(e) => setTakeAttendance({ ...takeAttendance, date: e.target.value })} className="rounded-xl h-12" />
              </div>
              <div className="flex items-end">
                <Button data-testid="load-students-btn" onClick={handleLoadStudents} className="bg-sky-500 hover:bg-sky-600 text-white font-bold rounded-xl h-12 w-full active:scale-95 transition-transform">Load Students</Button>
              </div>
            </div>
          </div>

          {students.length > 0 && (
            <>
              <div className="bg-white rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.04)] border border-slate-100 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-bold text-slate-800">Mark Attendance ({attendanceData.length} students)</h2>
                  <div className="flex gap-2">
                    <Button data-testid="bulk-mark-present" onClick={() => handleBulkMark('present')} className="bg-emerald-500 hover:bg-emerald-600 text-white font-bold rounded-xl active:scale-95 transition-transform">All Present</Button>
                    <Button data-testid="bulk-mark-absent" onClick={() => handleBulkMark('absent')} className="bg-rose-500 hover:bg-rose-600 text-white font-bold rounded-xl active:scale-95 transition-transform">All Absent</Button>
                  </div>
                </div>
                <div className="space-y-3">
                  {attendanceData.map((record, index) => (
                    <div key={record.studentId} data-testid={`attendance-row-${record.rollNo}`} className="flex items-center justify-between p-4 bg-slate-50 rounded-xl hover:bg-slate-100 transition-colors">
                      <div className="flex-1"><p className="font-bold text-slate-900">{record.rollNo} - {record.studentName}</p></div>
                      <div className="flex gap-2">
                        {['present', 'absent', 'holiday', 'undefined'].map((status) => (
                          <button key={status} data-testid={`mark-${status}-${record.rollNo}`} onClick={() => handleMarkAttendance(index, status)}
                            className={`px-4 py-2 rounded-full text-xs font-bold text-white transition-all active:scale-95 ${
                              record.status === status ? `ring-2 ring-offset-1 ${status === 'present' ? 'bg-emerald-600 ring-emerald-300' : status === 'absent' ? 'bg-rose-600 ring-rose-300' : status === 'holiday' ? 'bg-orange-500 ring-orange-300' : 'bg-slate-500 ring-slate-300'}`
                              : `${status === 'present' ? 'bg-emerald-500 hover:bg-emerald-600' : status === 'absent' ? 'bg-rose-500 hover:bg-rose-600' : status === 'holiday' ? 'bg-orange-400 hover:bg-orange-500' : 'bg-slate-300 hover:bg-slate-400'}`
                            }`}
                          >{status.charAt(0).toUpperCase() + status.slice(1)}</button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex justify-end">
                <Button data-testid="submit-attendance-btn" onClick={handleSubmitAttendance} className="bg-sky-500 hover:bg-sky-600 text-white font-bold rounded-xl px-8 active:scale-95 transition-transform">
                  <Send className="w-5 h-5 mr-2" />Submit Attendance
                </Button>
              </div>
            </>
          )}
        </TabsContent>

        <TabsContent value="view" className="space-y-6">
          <div className="bg-white rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.04)] border border-slate-100 p-6">
            <h2 className="text-xl font-bold text-slate-800 mb-4">Filters</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <Label>Class *</Label>
                <Select value={viewFilters.studentClass} onValueChange={(v) => setViewFilters({ ...viewFilters, studentClass: v, section: '' })}>
                  <SelectTrigger className="rounded-xl h-12"><SelectValue placeholder="Select Class" /></SelectTrigger>
                  <SelectContent>{classes.map((c) => <SelectItem key={c.className} value={c.className}>Class {c.className}</SelectItem>)}</SelectContent>
                </Select>
              </div>
              <div>
                <Label>Section *</Label>
                <Select value={viewFilters.section} onValueChange={(v) => setViewFilters({ ...viewFilters, section: v })}>
                  <SelectTrigger className="rounded-xl h-12"><SelectValue placeholder="Select Section" /></SelectTrigger>
                  <SelectContent>{getSections(viewFilters.studentClass).map((s) => <SelectItem key={s} value={s}>Section {s}</SelectItem>)}</SelectContent>
                </Select>
              </div>
              <div><Label>Start Date</Label><Input type="date" value={viewFilters.startDate} onChange={(e) => setViewFilters({ ...viewFilters, startDate: e.target.value })} className="rounded-xl h-12" /></div>
              <div><Label>End Date</Label><Input type="date" value={viewFilters.endDate} onChange={(e) => setViewFilters({ ...viewFilters, endDate: e.target.value })} className="rounded-xl h-12" /></div>
            </div>
            <div className="flex justify-between mt-4">
              <Button data-testid="view-attendance-btn" onClick={handleViewAttendance} className="bg-sky-500 hover:bg-sky-600 text-white font-bold rounded-xl active:scale-95 transition-transform">View Attendance</Button>
              <div className="flex gap-2">
                <Button data-testid="export-csv-btn" onClick={() => handleExport('csv')} variant="outline" className="font-bold rounded-xl"><Download className="w-4 h-4 mr-2" />Export CSV</Button>
                <Button data-testid="export-excel-btn" onClick={() => handleExport('xlsx')} variant="outline" className="font-bold rounded-xl"><Download className="w-4 h-4 mr-2" />Export Excel</Button>
              </div>
            </div>
          </div>

          {attendanceRecords.length > 0 && (
            <>
              {/* Percentage summary */}
              <div className="bg-white rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.04)] border border-slate-100 p-6">
                <h2 className="text-xl font-bold text-slate-800 mb-4">Attendance Summary</h2>
                <div className="space-y-2">
                  {getStudentStats().map((s) => (
                    <div key={s.rollNo} className="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                      <div className="flex-1 grid grid-cols-4 gap-4">
                        <p className="font-bold text-slate-900">{s.rollNo}</p>
                        <p className="font-medium text-slate-700">{s.name}</p>
                        <p className="text-slate-600">{s.present}/{s.total} days</p>
                        <span className={`inline-flex items-center justify-center px-3 py-1 rounded-full text-xs font-bold ${
                          (s.present / s.total * 100) >= 75 ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'
                        }`}>{s.total > 0 ? Math.round(s.present / s.total * 100) : 0}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Raw records */}
              <div className="bg-white rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.04)] border border-slate-100 p-6">
                <h2 className="text-xl font-bold text-slate-800 mb-4">Detailed Records</h2>
                <div className="space-y-2">
                  {attendanceRecords.map((record) => (
                    <div key={record.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-xl">
                      <div className="flex-1 grid grid-cols-4 gap-4">
                        <p className="font-bold text-slate-900">{record.rollNo}</p>
                        <p className="font-medium text-slate-700">{record.studentName}</p>
                        <p className="text-slate-600">{record.date}</p>
                        <span className={`inline-flex items-center justify-center px-3 py-1 rounded-full text-xs font-bold ${getStatusBadgeColor(record.status)}`}>{record.status.toUpperCase()}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Attendance;
