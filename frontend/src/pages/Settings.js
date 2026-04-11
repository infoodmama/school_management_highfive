import React, { useState, useEffect } from 'react';
import { Save, MessageSquare, Database, CheckCircle, XCircle } from 'lucide-react';
import { api } from '../lib/api';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';

const Settings = () => {
  const [loading, setLoading] = useState(true);
  const [savingWhatsApp, setSavingWhatsApp] = useState(false);
  const [savingDb, setSavingDb] = useState(false);
  const [dbStatus, setDbStatus] = useState(null); // null | 'success' | 'error'
  const [whatsAppSettings, setWhatsAppSettings] = useState({ phoneNumberId: '', accessToken: '' });
  const [dbSettings, setDbSettings] = useState({ mongoUrl: '', dbName: '' });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const [waResp, dbResp] = await Promise.all([
        api.getWhatsAppSettings(),
        api.getDatabaseSettings(),
      ]);
      setWhatsAppSettings(waResp.data);
      setDbSettings({ mongoUrl: dbResp.data.mongoUrl || '', dbName: dbResp.data.dbName || '' });
    } catch (error) {
      toast.error('Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveWhatsApp = async (e) => {
    e.preventDefault();
    try {
      setSavingWhatsApp(true);
      await api.updateWhatsAppSettings(whatsAppSettings);
      toast.success('WhatsApp settings saved');
    } catch (error) {
      toast.error('Failed to save WhatsApp settings');
    } finally {
      setSavingWhatsApp(false);
    }
  };

  const handleSaveDatabase = async (e) => {
    e.preventDefault();
    try {
      setSavingDb(true);
      setDbStatus(null);
      await api.updateDatabaseSettings(dbSettings);
      setDbStatus('success');
      toast.success('Database connected successfully!');
    } catch (error) {
      setDbStatus('error');
      toast.error(error.response?.data?.detail || 'Failed to connect to database');
    } finally {
      setSavingDb(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-500"></div>
      </div>
    );
  }

  return (
    <div className="max-w-[1600px] mx-auto space-y-6">
      <div>
        <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-900" style={{ fontFamily: 'Nunito' }}>Settings</h1>
        <p className="text-base font-medium text-slate-600 mt-1" style={{ fontFamily: 'Figtree' }}>Configure WhatsApp API and Database connection</p>
      </div>

      <Tabs defaultValue="whatsapp" className="space-y-6">
        <TabsList className="bg-slate-100 p-1 rounded-xl inline-flex">
          <TabsTrigger data-testid="whatsapp-settings-tab" value="whatsapp" className="data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-lg px-6 py-2 font-bold">
            <MessageSquare className="w-4 h-4 mr-2" />WhatsApp API
          </TabsTrigger>
          <TabsTrigger data-testid="database-settings-tab" value="database" className="data-[state=active]:bg-white data-[state=active]:shadow-sm rounded-lg px-6 py-2 font-bold">
            <Database className="w-4 h-4 mr-2" />Database
          </TabsTrigger>
        </TabsList>

        {/* WhatsApp Settings */}
        <TabsContent value="whatsapp">
          <div className="bg-white rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.04)] border border-slate-100 p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 bg-gradient-to-br from-emerald-400 to-emerald-600 rounded-xl flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-slate-900">WhatsApp API Configuration</h2>
                <p className="text-sm text-slate-600">Configure WhatsApp messaging for attendance alerts and fee receipts</p>
              </div>
            </div>

            <form onSubmit={handleSaveWhatsApp} className="space-y-6">
              <div>
                <Label className="text-base font-bold">Phone Number ID *</Label>
                <Input data-testid="whatsapp-phone-id-input" required value={whatsAppSettings.phoneNumberId} onChange={(e) => setWhatsAppSettings({ ...whatsAppSettings, phoneNumberId: e.target.value })} className="rounded-xl h-12 mt-2" placeholder="e.g., 488774804320252" />
                <p className="text-xs text-slate-500 mt-2">Your WhatsApp Business phone number ID</p>
              </div>
              <div>
                <Label className="text-base font-bold">Access Token *</Label>
                <Input data-testid="whatsapp-access-token-input" required type="password" value={whatsAppSettings.accessToken} onChange={(e) => setWhatsAppSettings({ ...whatsAppSettings, accessToken: e.target.value })} className="rounded-xl h-12 mt-2" placeholder="Enter your access token" />
              </div>
              <div className="bg-sky-50 border border-sky-200 rounded-xl p-4">
                <h3 className="font-bold text-sky-900 mb-2">Template Messages Configured:</h3>
                <ul className="text-sm text-sky-800 space-y-1 list-disc list-inside">
                  <li><b>fee_paid_bill</b> - Sends invoice PDF with amount, fee name, student name</li>
                  <li><b>absent_hifg</b> - Sends student name, class, date when marked absent</li>
                  <li><b>holi</b> - Sends event name & date (when notification enabled)</li>
                </ul>
              </div>
              <div className="flex justify-end pt-4">
                <Button data-testid="save-whatsapp-btn" type="submit" disabled={savingWhatsApp} className="bg-sky-500 hover:bg-sky-600 text-white font-bold rounded-xl px-8 active:scale-95 transition-transform">
                  <Save className="w-5 h-5 mr-2" />{savingWhatsApp ? 'Saving...' : 'Save Settings'}
                </Button>
              </div>
            </form>
          </div>
        </TabsContent>

        {/* Database Settings */}
        <TabsContent value="database">
          <div className="bg-white rounded-2xl shadow-[0_8px_30px_rgba(0,0,0,0.04)] border border-slate-100 p-6">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 bg-gradient-to-br from-indigo-400 to-indigo-600 rounded-xl flex items-center justify-center">
                <Database className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-slate-900">Database Connection</h2>
                <p className="text-sm text-slate-600">Connect to your own MongoDB database</p>
              </div>
            </div>

            <form onSubmit={handleSaveDatabase} className="space-y-6">
              <div>
                <Label className="text-base font-bold">MongoDB URL *</Label>
                <Input data-testid="db-mongo-url-input" required value={dbSettings.mongoUrl} onChange={(e) => setDbSettings({ ...dbSettings, mongoUrl: e.target.value })} className="rounded-xl h-12 mt-2" placeholder="mongodb+srv://user:pass@cluster.mongodb.net" />
                <p className="text-xs text-slate-500 mt-2">Enter your MongoDB connection string (local or cloud)</p>
              </div>
              <div>
                <Label className="text-base font-bold">Database Name *</Label>
                <Input data-testid="db-name-input" required value={dbSettings.dbName} onChange={(e) => setDbSettings({ ...dbSettings, dbName: e.target.value })} className="rounded-xl h-12 mt-2" placeholder="e.g., school_management" />
              </div>

              {dbStatus === 'success' && (
                <div className="flex items-center gap-3 p-4 bg-emerald-50 border border-emerald-200 rounded-xl">
                  <CheckCircle className="w-6 h-6 text-emerald-600" />
                  <p className="text-emerald-800 font-bold">Database connected successfully! All data will now be stored in your database.</p>
                </div>
              )}
              {dbStatus === 'error' && (
                <div className="flex items-center gap-3 p-4 bg-rose-50 border border-rose-200 rounded-xl">
                  <XCircle className="w-6 h-6 text-rose-600" />
                  <p className="text-rose-800 font-bold">Connection failed. Please check your credentials and try again.</p>
                </div>
              )}

              <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                <h3 className="font-bold text-amber-900 mb-2">Important:</h3>
                <ul className="text-sm text-amber-800 space-y-1 list-disc list-inside">
                  <li>The app will test the connection before switching</li>
                  <li>Data from the previous database will NOT be migrated automatically</li>
                  <li>Make sure your MongoDB instance is accessible from this server</li>
                  <li>For MongoDB Atlas, add 0.0.0.0/0 to IP whitelist for access</li>
                </ul>
              </div>

              <div className="flex justify-end pt-4">
                <Button data-testid="save-database-btn" type="submit" disabled={savingDb} className="bg-indigo-500 hover:bg-indigo-600 text-white font-bold rounded-xl px-8 active:scale-95 transition-transform">
                  <Database className="w-5 h-5 mr-2" />{savingDb ? 'Connecting...' : 'Connect Database'}
                </Button>
              </div>
            </form>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Settings;
