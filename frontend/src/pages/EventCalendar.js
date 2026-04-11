import React, { useState, useEffect, useCallback } from 'react';
import { Plus, Trash2, CalendarDays } from 'lucide-react';
import { api } from '../lib/api';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';

const EventCalendar = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showDialog, setShowDialog] = useState(false);
  const [form, setForm] = useState({ title: '', description: '', date: new Date().toISOString().split('T')[0] });
  const [selectedMonth, setSelectedMonth] = useState(new Date().toISOString().slice(0, 7));

  const loadEvents = useCallback(async () => {
    try { const r = await api.getEvents({ month: selectedMonth }); setEvents(r.data); }
    catch (e) { toast.error('Failed to load events'); }
    finally { setLoading(false); }
  }, [selectedMonth]);

  useEffect(() => { loadEvents(); }, [loadEvents]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.createEvent(form);
      toast.success('Event added');
      setShowDialog(false);
      setForm({ title: '', description: '', date: new Date().toISOString().split('T')[0] });
      loadEvents();
    } catch (error) { toast.error('Failed to add event'); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this event?')) return;
    try { await api.deleteEvent(id); toast.success('Event deleted'); loadEvents(); }
    catch (error) { toast.error('Failed to delete'); }
  };

  // Generate calendar days for the selected month
  const getDaysInMonth = () => {
    const [year, month] = selectedMonth.split('-').map(Number);
    const firstDay = new Date(year, month - 1, 1).getDay();
    const daysInMonth = new Date(year, month, 0).getDate();
    const days = [];
    for (let i = 0; i < firstDay; i++) days.push(null);
    for (let i = 1; i <= daysInMonth; i++) days.push(i);
    return days;
  };

  const getEventsForDay = (day) => {
    if (!day) return [];
    const dateStr = `${selectedMonth}-${String(day).padStart(2, '0')}`;
    return events.filter((e) => e.date === dateStr);
  };

  const monthName = new Date(selectedMonth + '-01').toLocaleDateString('en-IN', { month: 'long', year: 'numeric' });

  return (
    <div className="max-w-[1600px] mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900" style={{ fontFamily: 'Nunito' }}>Event Calendar</h1>
          <p className="text-base font-medium text-slate-600 mt-1" style={{ fontFamily: 'Figtree' }}>Manage school events and activities</p>
        </div>
        <div className="flex gap-3">
          <Input type="month" value={selectedMonth} onChange={(e) => setSelectedMonth(e.target.value)} className="rounded-xl h-12 w-48" />
          <Dialog open={showDialog} onOpenChange={setShowDialog}>
            <DialogTrigger asChild>
              <Button data-testid="add-event-btn" className="bg-sky-500 hover:bg-sky-600 text-white font-bold rounded-xl active:scale-95 transition-transform"><Plus className="w-5 h-5 mr-2" />Add Event</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader><DialogTitle className="text-2xl font-bold">Add Event</DialogTitle></DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div><Label>Title *</Label><Input data-testid="event-title" required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="rounded-xl h-12" placeholder="Event title" /></div>
                <div><Label>Date *</Label><Input type="date" required value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} className="rounded-xl h-12" /></div>
                <div><Label>Description *</Label><textarea required value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="w-full border border-slate-200 rounded-xl p-3 min-h-[100px] focus:ring-2 focus:ring-sky-500 focus:border-sky-500" placeholder="Event details..." /></div>
                <div className="flex justify-end gap-3 pt-4">
                  <Button type="button" variant="outline" onClick={() => setShowDialog(false)} className="rounded-xl">Cancel</Button>
                  <Button data-testid="submit-event-btn" type="submit" className="bg-sky-500 hover:bg-sky-600 text-white font-bold rounded-xl">Add Event</Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="bg-white rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.04)] border border-slate-100 p-6">
        <h2 className="text-2xl font-bold text-slate-800 mb-6 text-center">{monthName}</h2>
        <div className="grid grid-cols-7 gap-2 mb-2">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((d) => (
            <div key={d} className="text-center text-xs font-bold uppercase tracking-widest text-slate-400 py-2">{d}</div>
          ))}
        </div>
        <div className="grid grid-cols-7 gap-2">
          {getDaysInMonth().map((day, idx) => {
            const dayEvents = getEventsForDay(day);
            const today = new Date().toISOString().split('T')[0];
            const dateStr = day ? `${selectedMonth}-${String(day).padStart(2, '0')}` : '';
            const isToday = dateStr === today;
            return (
              <div key={idx} className={`min-h-[80px] rounded-xl p-2 border transition-all ${
                !day ? 'bg-transparent border-transparent' :
                isToday ? 'bg-sky-50 border-sky-300' : 'bg-slate-50 border-slate-100 hover:border-sky-200'
              }`}>
                {day && (
                  <>
                    <p className={`text-sm font-bold ${isToday ? 'text-sky-600' : 'text-slate-700'}`}>{day}</p>
                    {dayEvents.map((ev) => (
                      <div key={ev.id} className="mt-1 px-2 py-1 bg-amber-100 text-amber-800 rounded-lg text-xs font-bold truncate" title={ev.title}>
                        {ev.title}
                      </div>
                    ))}
                  </>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Event List */}
      <div className="bg-white rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.04)] border border-slate-100 p-6">
        <h2 className="text-xl font-bold text-slate-800 mb-4">Events This Month</h2>
        {events.length === 0 ? (
          <p className="text-slate-400 font-medium text-center py-8">No events this month</p>
        ) : (
          <div className="space-y-3">
            {events.sort((a, b) => a.date.localeCompare(b.date)).map((event) => (
              <div key={event.id} data-testid={`event-${event.id}`} className="flex items-start justify-between p-4 bg-slate-50 rounded-xl hover:bg-slate-100 transition-colors">
                <div className="flex items-start gap-4">
                  <div className="w-14 h-14 bg-gradient-to-br from-amber-400 to-amber-600 rounded-xl flex flex-col items-center justify-center text-white shadow">
                    <p className="text-xs font-bold">{new Date(event.date + 'T00:00:00').toLocaleDateString('en-IN', { month: 'short' })}</p>
                    <p className="text-xl font-extrabold leading-none">{new Date(event.date + 'T00:00:00').getDate()}</p>
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-900 text-lg">{event.title}</h3>
                    <p className="text-sm text-slate-600 mt-1">{event.description}</p>
                  </div>
                </div>
                <button onClick={() => handleDelete(event.id)} className="p-2 hover:bg-rose-100 rounded-lg transition-colors"><Trash2 className="w-4 h-4 text-rose-600" /></button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default EventCalendar;
