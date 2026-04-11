import React, { useState, useEffect, useCallback } from 'react';
import { Plus, Edit, Trash2, Package } from 'lucide-react';
import { api } from '../lib/api';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../components/ui/table';

const Inventory = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showDialog, setShowDialog] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [form, setForm] = useState({ itemName: '', quantity: '', category: '', purchaseDate: new Date().toISOString().split('T')[0], amount: '' });

  const loadItems = useCallback(async () => {
    try { const r = await api.getInventory(); setItems(r.data); } catch (e) { toast.error('Failed to load inventory'); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { loadItems(); }, [loadItems]);

  const resetForm = () => { setForm({ itemName: '', quantity: '', category: '', purchaseDate: new Date().toISOString().split('T')[0], amount: '' }); setEditingItem(null); };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const data = { ...form, quantity: parseInt(form.quantity), amount: parseFloat(form.amount) };
    try {
      if (editingItem) { await api.updateInventory(editingItem.id, data); toast.success('Item updated'); }
      else { await api.createInventory(data); toast.success('Item added'); }
      setShowDialog(false); resetForm(); loadItems();
    } catch (error) { toast.error('Failed to save item'); }
  };

  const openEdit = (item) => {
    setEditingItem(item);
    setForm({ itemName: item.itemName, quantity: item.quantity, category: item.category, purchaseDate: item.purchaseDate, amount: item.amount });
    setShowDialog(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this item?')) return;
    try { await api.deleteInventory(id); toast.success('Item deleted'); loadItems(); }
    catch (error) { toast.error('Failed to delete'); }
  };

  const totalValue = items.reduce((sum, i) => sum + (i.amount * i.quantity), 0);

  return (
    <div className="max-w-[1600px] mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900" style={{ fontFamily: 'Nunito' }}>Inventory Management</h1>
          <p className="text-base font-medium text-slate-600 mt-1" style={{ fontFamily: 'Figtree' }}>Track school inventory and supplies</p>
        </div>
        <Dialog open={showDialog} onOpenChange={(open) => { setShowDialog(open); if (!open) resetForm(); }}>
          <DialogTrigger asChild>
            <Button data-testid="add-inventory-btn" className="bg-sky-500 hover:bg-sky-600 text-white font-bold rounded-xl active:scale-95 transition-transform"><Plus className="w-5 h-5 mr-2" />Add Item</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle className="text-2xl font-bold">{editingItem ? 'Edit Item' : 'Add Inventory Item'}</DialogTitle></DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div><Label>Item Name *</Label><Input data-testid="inventory-name" required value={form.itemName} onChange={(e) => setForm({ ...form, itemName: e.target.value })} className="rounded-xl h-12" placeholder="e.g., Whiteboard Markers" /></div>
              <div className="grid grid-cols-2 gap-4">
                <div><Label>Quantity *</Label><Input type="number" required value={form.quantity} onChange={(e) => setForm({ ...form, quantity: e.target.value })} className="rounded-xl h-12" /></div>
                <div><Label>Amount (per unit) *</Label><Input type="number" required value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} className="rounded-xl h-12" /></div>
              </div>
              <div><Label>Category *</Label><Input required value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} className="rounded-xl h-12" placeholder="e.g., Stationery, Furniture" /></div>
              <div><Label>Purchase Date *</Label><Input type="date" required value={form.purchaseDate} onChange={(e) => setForm({ ...form, purchaseDate: e.target.value })} className="rounded-xl h-12" /></div>
              <div className="flex justify-end gap-3 pt-4">
                <Button type="button" variant="outline" onClick={() => { setShowDialog(false); resetForm(); }} className="rounded-xl">Cancel</Button>
                <Button data-testid="submit-inventory-btn" type="submit" className="bg-sky-500 hover:bg-sky-600 text-white font-bold rounded-xl">{editingItem ? 'Update' : 'Add Item'}</Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="bg-gradient-to-br from-indigo-400 to-indigo-600 rounded-2xl shadow-lg p-8 text-white">
        <div className="flex items-center gap-3 mb-2"><Package className="w-6 h-6" /><p className="text-sm font-bold uppercase tracking-widest opacity-90">Total Inventory Value</p></div>
        <p className="text-4xl font-extrabold">{'\u20B9'}{totalValue.toLocaleString()}</p>
        <p className="text-sm opacity-80 mt-1">{items.length} items tracked</p>
      </div>

      <div className="bg-white rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.04)] border border-slate-100 overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-64"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-500"></div></div>
        ) : items.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64"><p className="text-slate-400 font-medium">No inventory items yet</p></div>
        ) : (
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="bg-slate-50">
                  <TableHead className="font-bold uppercase text-xs text-slate-600">Item Name</TableHead>
                  <TableHead className="font-bold uppercase text-xs text-slate-600">Category</TableHead>
                  <TableHead className="font-bold uppercase text-xs text-slate-600">Qty</TableHead>
                  <TableHead className="font-bold uppercase text-xs text-slate-600">Amount/Unit</TableHead>
                  <TableHead className="font-bold uppercase text-xs text-slate-600">Total</TableHead>
                  <TableHead className="font-bold uppercase text-xs text-slate-600">Purchase Date</TableHead>
                  <TableHead className="font-bold uppercase text-xs text-slate-600">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((item) => (
                  <TableRow key={item.id} className="hover:bg-slate-50/80">
                    <TableCell className="font-semibold text-slate-900">{item.itemName}</TableCell>
                    <TableCell><span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-indigo-100 text-indigo-700">{item.category}</span></TableCell>
                    <TableCell className="font-bold">{item.quantity}</TableCell>
                    <TableCell className="text-slate-600">{'\u20B9'}{item.amount.toLocaleString()}</TableCell>
                    <TableCell className="font-bold text-emerald-600">{'\u20B9'}{(item.amount * item.quantity).toLocaleString()}</TableCell>
                    <TableCell className="text-slate-600">{item.purchaseDate}</TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <button onClick={() => openEdit(item)} className="p-2 hover:bg-sky-100 rounded-lg transition-colors"><Edit className="w-4 h-4 text-sky-600" /></button>
                        <button onClick={() => handleDelete(item.id)} className="p-2 hover:bg-rose-100 rounded-lg transition-colors"><Trash2 className="w-4 h-4 text-rose-600" /></button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Inventory;
