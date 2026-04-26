import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Plus, Upload, Download, Search, Edit, Trash2, TrendingUp, Filter, Eye } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';

const Students = () => {
  const navigate = useNavigate();
  const [students, setStudents] = useState([]);
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showPromoteDialog, setShowPromoteDialog] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [selectedIds, setSelectedIds] = useState([]);
  const [filters, setFilters] = useState({ studentClass: '', section: '', search: '' });
  const [formData, setFormData] = useState({
    studentCode: '', studentName: '', rollNo: '', studentClass: '', section: '',
    fatherName: '', motherName: '', mobile: '', address: '',
    feeTerm1: '', feeTerm2: '', feeTerm3: '', parentUsername: '', parentPassword: '',
  });
  const [promoteData, setPromoteData] = useState({ fromClass: '', toClass: '' });

  const loadClasses = useCallback(async () => {
    try { const r = await api.getClasses(); setClasses(r.data); } catch (e) { /* ignore */ }
  }, []);

  const loadStudents = useCallback(async () => {
    try {
      setLoading(true);
      const params = {};
      if (filters.studentClass) params.studentClass = filters.studentClass;
      if (filters.section) params.section = filters.section;
      if (filters.search) params.search = filters.search;
      const response = await api.getStudents(params);
      setStudents(response.data);
    } catch (error) { toast.error('Failed to load students'); }
    finally { setLoading(false); }
  }, [filters]);

  useEffect(() => { loadClasses(); }, [loadClasses]);
  useEffect(() => { loadStudents(); }, [loadStudents]);

  const getSections = (cls) => {
    const found = classes.find((c) => c.className === cls);
    return found ? found.sections : [];
  };

  // Use a ref-based updater to avoid re-rendering the whole form on each keystroke
  const updateField = useCallback((field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  }, []);

  const handleAddStudent = async (e) => {
    e.preventDefault();
    try {
      await api.createStudent({
        ...formData, feeTerm1: parseFloat(formData.feeTerm1),
        feeTerm2: parseFloat(formData.feeTerm2), feeTerm3: parseFloat(formData.feeTerm3),
      });
      toast.success('Student added successfully');
      setShowAddDialog(false); resetForm(); loadStudents();
    } catch (error) { toast.error(error.response?.data?.detail || 'Failed to add student'); }
  };

  const handleBulkUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    try {
      const response = await api.bulkUploadStudents(file);
      toast.success(`Added ${response.data.added} students`);
      if (response.data.errors.length > 0) toast.error(`Errors: ${response.data.errors.slice(0, 3).join(', ')}`);
      loadStudents();
    } catch (error) { toast.error('Failed to upload CSV'); }
  };

  const handleDownloadSample = async () => {
    try {
      const response = await api.getSampleCSV();
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url; link.setAttribute('download', 'sample_students.csv');
      document.body.appendChild(link); link.click(); link.remove();
    } catch (error) { toast.error('Failed to download sample CSV'); }
  };

  const handleEditStudent = async (e) => {
    e.preventDefault();
    try {
      await api.updateStudent(selectedStudent.id, {
        ...formData, feeTerm1: parseFloat(formData.feeTerm1),
        feeTerm2: parseFloat(formData.feeTerm2), feeTerm3: parseFloat(formData.feeTerm3),
      });
      toast.success('Student updated successfully');
      setShowEditDialog(false); resetForm(); loadStudents();
    } catch (error) { toast.error('Failed to update student'); }
  };

  const handleDeleteStudent = async (id) => {
    if (!window.confirm('Are you sure?')) return;
    try { await api.deleteStudent(id); toast.success('Student deleted'); loadStudents(); }
    catch (error) { toast.error('Failed to delete student'); }
  };

  const handleBulkDelete = async () => {
    if (selectedIds.length === 0) { toast.error('No students selected'); return; }
    if (!window.confirm(`Are you sure you want to delete ${selectedIds.length} students?`)) return;
    try {
      const response = await api.bulkDeleteStudents(selectedIds);
      toast.success(response.data.message);
      setSelectedIds([]);
      loadStudents();
    } catch (error) { toast.error('Failed to delete students'); }
  };

  const toggleSelectAll = () => {
    if (selectedIds.length === students.length) { setSelectedIds([]); }
    else { setSelectedIds(students.map((s) => s.id)); }
  };

  const toggleSelect = (id) => {
    setSelectedIds((prev) => prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]);
  };

  const handlePromote = async (e) => {
    e.preventDefault();
    try {
      const response = await api.promoteStudents(promoteData);
      toast.success(response.data.message);
      setShowPromoteDialog(false); setPromoteData({ fromClass: '', toClass: '' }); loadStudents();
    } catch (error) { toast.error('Failed to promote students'); }
  };

  const resetForm = () => {
    setFormData({ studentCode: '', studentName: '', rollNo: '', studentClass: '', section: '', fatherName: '', motherName: '', mobile: '', address: '', feeTerm1: '', feeTerm2: '', feeTerm3: '', parentUsername: '', parentPassword: '' });
  };

  const openEditDialog = (student) => {
    setSelectedStudent(student);
    setFormData({
      studentCode: student.studentCode || '', studentName: student.studentName, rollNo: student.rollNo,
      studentClass: student.studentClass, section: student.section,
      fatherName: student.fatherName, motherName: student.motherName,
      mobile: student.mobile, address: student.address,
      feeTerm1: student.feeTerm1, feeTerm2: student.feeTerm2, feeTerm3: student.feeTerm3,
      parentUsername: student.parentUsername || '', parentPassword: student.parentPassword || '',
    });
    setShowEditDialog(true);
  };

  // Inline form fields rendered directly (NOT as a sub-component to avoid focus loss)
  const renderFormFields = () => (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div><Label>Student ID * (Unique)</Label><Input data-testid="student-code-input" required value={formData.studentCode} onChange={(e) => updateField('studentCode', e.target.value)} className="rounded-xl h-12" placeholder="e.g., ADM001" /></div>
      <div><Label>Student Name *</Label><Input data-testid="student-name-input" required value={formData.studentName} onChange={(e) => updateField('studentName', e.target.value)} className="rounded-xl h-12" /></div>
      <div><Label>Roll No *</Label><Input data-testid="student-rollno-input" required value={formData.rollNo} onChange={(e) => updateField('rollNo', e.target.value)} className="rounded-xl h-12" placeholder="Class roll number" /></div>
      <div>
        <Label>Class *</Label>
        <Select value={formData.studentClass} onValueChange={(v) => setFormData(prev => ({ ...prev, studentClass: v, section: '' }))}>
          <SelectTrigger data-testid="student-class-select" className="rounded-xl h-12"><SelectValue placeholder="Select Class" /></SelectTrigger>
          <SelectContent>{classes.map((c) => <SelectItem key={c.className} value={c.className}>Class {c.className}</SelectItem>)}</SelectContent>
        </Select>
      </div>
      <div>
        <Label>Section *</Label>
        <Select value={formData.section} onValueChange={(v) => updateField('section', v)}>
          <SelectTrigger data-testid="student-section-select" className="rounded-xl h-12"><SelectValue placeholder="Select Section" /></SelectTrigger>
          <SelectContent>{getSections(formData.studentClass).map((s) => <SelectItem key={s} value={s}>Section {s}</SelectItem>)}</SelectContent>
        </Select>
      </div>
      <div><Label>Father Name *</Label><Input required value={formData.fatherName} onChange={(e) => updateField('fatherName', e.target.value)} className="rounded-xl h-12" /></div>
      <div><Label>Mother Name *</Label><Input required value={formData.motherName} onChange={(e) => updateField('motherName', e.target.value)} className="rounded-xl h-12" /></div>
      <div><Label>Mobile Number *</Label><Input required value={formData.mobile} onChange={(e) => updateField('mobile', e.target.value)} className="rounded-xl h-12" /></div>
      <div><Label>Address *</Label><Input required value={formData.address} onChange={(e) => updateField('address', e.target.value)} className="rounded-xl h-12" /></div>
      <div><Label>Fee Term 1 *</Label><Input type="number" required value={formData.feeTerm1} onChange={(e) => updateField('feeTerm1', e.target.value)} className="rounded-xl h-12" /></div>
      <div><Label>Fee Term 2 *</Label><Input type="number" required value={formData.feeTerm2} onChange={(e) => updateField('feeTerm2', e.target.value)} className="rounded-xl h-12" /></div>
      <div><Label>Fee Term 3 *</Label><Input type="number" required value={formData.feeTerm3} onChange={(e) => updateField('feeTerm3', e.target.value)} className="rounded-xl h-12" /></div>
      <div><Label>Parent Username</Label><Input value={formData.parentUsername} onChange={(e) => updateField('parentUsername', e.target.value)} className="rounded-xl h-12" placeholder="For parent portal login" /></div>
      <div><Label>Parent Password</Label><Input value={formData.parentPassword} onChange={(e) => updateField('parentPassword', e.target.value)} className="rounded-xl h-12" placeholder="Parent portal password" /></div>
    </div>
  );

  return (
    <div className="max-w-[1600px] mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900" style={{ fontFamily: 'Nunito' }}>Student Management</h1>
          <p className="text-base font-medium text-slate-600 mt-1" style={{ fontFamily: 'Figtree' }}>Manage student records and information</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <Dialog open={showAddDialog} onOpenChange={(open) => { setShowAddDialog(open); if (!open) resetForm(); }}>
            <DialogTrigger asChild>
              <Button data-testid="add-student-btn" className="bg-sky-500 hover:bg-sky-600 text-white font-bold rounded-xl active:scale-95 transition-transform"><Plus className="w-5 h-5 mr-2" />Add Student</Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
              <DialogHeader><DialogTitle className="text-2xl font-bold">Add New Student</DialogTitle></DialogHeader>
              <form onSubmit={handleAddStudent} className="space-y-4">
                {renderFormFields()}
                <div className="flex justify-end gap-3 pt-4">
                  <Button type="button" variant="outline" onClick={() => setShowAddDialog(false)} className="rounded-xl">Cancel</Button>
                  <Button data-testid="submit-student-btn" type="submit" className="bg-sky-500 hover:bg-sky-600 text-white font-bold rounded-xl">Add Student</Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>

          <label htmlFor="bulk-upload" className="cursor-pointer">
            <input id="bulk-upload" type="file" accept=".csv" onChange={handleBulkUpload} className="hidden" data-testid="bulk-upload-input" />
            <div className="inline-flex items-center px-4 py-2 bg-amber-400 hover:bg-amber-500 text-slate-900 font-bold rounded-xl active:scale-95 transition-transform"><Upload className="w-5 h-5 mr-2" />Bulk Upload</div>
          </label>

          <Button data-testid="download-sample-csv" onClick={handleDownloadSample} variant="outline" className="font-bold rounded-xl"><Download className="w-5 h-5 mr-2" />Sample CSV</Button>

          {selectedIds.length > 0 && (
            <Button data-testid="bulk-delete-btn" onClick={handleBulkDelete} className="bg-rose-500 hover:bg-rose-600 text-white font-bold rounded-xl active:scale-95 transition-transform">
              <Trash2 className="w-5 h-5 mr-2" />Delete ({selectedIds.length})
            </Button>
          )}

          <Dialog open={showPromoteDialog} onOpenChange={setShowPromoteDialog}>
            <DialogTrigger asChild>
              <Button data-testid="promote-students-btn" variant="outline" className="font-bold rounded-xl bg-amber-100 text-amber-800 hover:bg-amber-200 border-amber-200"><TrendingUp className="w-5 h-5 mr-2" />Promote</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader><DialogTitle className="text-2xl font-bold">Promote Students</DialogTitle></DialogHeader>
              <form onSubmit={handlePromote} className="space-y-4">
                <div><Label>From Class *</Label>
                  <Select value={promoteData.fromClass} onValueChange={(v) => setPromoteData({ ...promoteData, fromClass: v })}>
                    <SelectTrigger className="rounded-xl h-12"><SelectValue placeholder="From" /></SelectTrigger>
                    <SelectContent>{classes.map((c) => <SelectItem key={c.className} value={c.className}>Class {c.className}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
                <div><Label>To Class *</Label>
                  <Select value={promoteData.toClass} onValueChange={(v) => setPromoteData({ ...promoteData, toClass: v })}>
                    <SelectTrigger className="rounded-xl h-12"><SelectValue placeholder="To" /></SelectTrigger>
                    <SelectContent>{classes.map((c) => <SelectItem key={c.className} value={c.className}>Class {c.className}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
                <div className="flex justify-end gap-3 pt-4">
                  <Button type="button" variant="outline" onClick={() => setShowPromoteDialog(false)} className="rounded-xl">Cancel</Button>
                  <Button type="submit" className="bg-amber-500 hover:bg-amber-600 text-white font-bold rounded-xl">Promote</Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.04)] border border-slate-100 p-6">
        <div className="flex items-center gap-2 mb-4"><Filter className="w-5 h-5 text-slate-600" /><h2 className="text-lg font-bold text-slate-800">Filters</h2></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div><Label>Class</Label>
            <Select value={filters.studentClass || '_all'} onValueChange={(v) => setFilters({ ...filters, studentClass: v === '_all' ? '' : v, section: '' })}>
              <SelectTrigger className="rounded-xl h-12"><SelectValue placeholder="All" /></SelectTrigger>
              <SelectContent><SelectItem value="_all">All Classes</SelectItem>{classes.map((c) => <SelectItem key={c.className} value={c.className}>Class {c.className}</SelectItem>)}</SelectContent>
            </Select>
          </div>
          <div><Label>Section</Label>
            <Select value={filters.section || '_all'} onValueChange={(v) => setFilters({ ...filters, section: v === '_all' ? '' : v })}>
              <SelectTrigger className="rounded-xl h-12"><SelectValue placeholder="All" /></SelectTrigger>
              <SelectContent><SelectItem value="_all">All Sections</SelectItem>{getSections(filters.studentClass).map((s) => <SelectItem key={s} value={s}>Section {s}</SelectItem>)}</SelectContent>
            </Select>
          </div>
          <div><Label>Search</Label>
            <div className="relative">
              <Search className="absolute left-3 top-3.5 w-5 h-5 text-slate-400" />
              <Input data-testid="student-search-input" placeholder="Search name or roll no" value={filters.search} onChange={(e) => setFilters({ ...filters, search: e.target.value })} className="rounded-xl h-12 pl-10" />
            </div>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.04)] border border-slate-100 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-500"></div></div>
        ) : students.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64"><p className="text-slate-400 font-medium">No students found</p></div>
        ) : (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="bg-slate-50">
                  <TableHead className="w-10"><input type="checkbox" checked={selectedIds.length === students.length && students.length > 0} onChange={toggleSelectAll} className="w-4 h-4 rounded accent-sky-500" data-testid="select-all-checkbox" /></TableHead>
                  <TableHead className="font-bold uppercase text-xs text-slate-600">Student ID</TableHead>
                  <TableHead className="font-bold uppercase text-xs text-slate-600">Roll No</TableHead>
                  <TableHead className="font-bold uppercase text-xs text-slate-600">Name</TableHead>
                  <TableHead className="font-bold uppercase text-xs text-slate-600">Class</TableHead>
                  <TableHead className="font-bold uppercase text-xs text-slate-600">Section</TableHead>
                  <TableHead className="font-bold uppercase text-xs text-slate-600">Mobile</TableHead>
                  <TableHead className="font-bold uppercase text-xs text-slate-600">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {students.map((student) => (
                  <TableRow key={student.id} className="hover:bg-slate-50/80" data-testid={`student-row-${student.rollNo}`}>
                    <TableCell><input type="checkbox" checked={selectedIds.includes(student.id)} onChange={() => toggleSelect(student.id)} className="w-4 h-4 rounded accent-sky-500" /></TableCell>
                    <TableCell className="font-semibold text-slate-900">{student.studentCode}</TableCell>
                    <TableCell className="text-slate-700">{student.rollNo}</TableCell>
                    <TableCell className="font-medium text-slate-700">{student.studentName}</TableCell>
                    <TableCell><span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-sky-100 text-sky-700">{student.studentClass}</span></TableCell>
                    <TableCell><span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-700">{student.section}</span></TableCell>
                    <TableCell className="text-slate-600">{student.mobile}</TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <button onClick={() => navigate(`/students/${student.id}`)} data-testid={`view-student-${student.rollNo}`} className="p-2 hover:bg-indigo-100 rounded-lg transition-colors"><Eye className="w-4 h-4 text-indigo-600" /></button>
                        <button onClick={() => openEditDialog(student)} data-testid={`edit-student-${student.rollNo}`} className="p-2 hover:bg-sky-100 rounded-lg transition-colors"><Edit className="w-4 h-4 text-sky-600" /></button>
                        <button onClick={() => handleDeleteStudent(student.id)} data-testid={`delete-student-${student.rollNo}`} className="p-2 hover:bg-rose-100 rounded-lg transition-colors"><Trash2 className="w-4 h-4 text-rose-600" /></button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </div>

      {/* Edit Dialog */}
      <Dialog open={showEditDialog} onOpenChange={(open) => { setShowEditDialog(open); if (!open) resetForm(); }}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader><DialogTitle className="text-2xl font-bold">Edit Student</DialogTitle></DialogHeader>
          <form onSubmit={handleEditStudent} className="space-y-4">
            {renderFormFields()}
            <div className="flex justify-end gap-3 pt-4">
              <Button type="button" variant="outline" onClick={() => setShowEditDialog(false)} className="rounded-xl">Cancel</Button>
              <Button data-testid="submit-student-btn" type="submit" className="bg-sky-500 hover:bg-sky-600 text-white font-bold rounded-xl">Update Student</Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Students;
