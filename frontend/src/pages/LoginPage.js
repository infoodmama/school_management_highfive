import React, { useState } from 'react';
import { GraduationCap } from 'lucide-react';
import { api } from '../lib/api';
import { useAuth } from '../lib/AuthContext';
import { toast } from 'sonner';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';

const LoginPage = () => {
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const response = await api.login({ username, password });
      login(response.data.user, response.data.role);
      toast.success(`Welcome, ${response.data.user.name || response.data.user.username}!`);
    } catch (error) {
      toast.error('Invalid username or password');
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl border border-slate-100 p-8 w-full max-w-md">
        <div className="flex items-center gap-3 mb-8 justify-center">
          <div className="w-14 h-14 bg-gradient-to-br from-sky-400 to-sky-600 rounded-2xl flex items-center justify-center">
            <GraduationCap className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold text-slate-900" style={{ fontFamily: 'Nunito' }}>SchoolPro</h1>
            <p className="text-sm text-slate-500">Staff & Admin Login</p>
          </div>
        </div>
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <Label>Username *</Label>
            <Input data-testid="login-username" required value={username} onChange={(e) => setUsername(e.target.value)} className="rounded-xl h-12" placeholder="Enter username" />
          </div>
          <div>
            <Label>Password *</Label>
            <Input data-testid="login-password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} className="rounded-xl h-12" placeholder="Enter password" />
          </div>
          <Button data-testid="login-submit-btn" type="submit" disabled={loading} className="w-full bg-sky-500 hover:bg-sky-600 text-white font-bold rounded-xl h-12 active:scale-95 transition-transform">
            {loading ? 'Logging in...' : 'Login'}
          </Button>
        </form>
        <div className="mt-6 text-center">
          <a href="/parent" className="text-sky-600 font-bold text-sm hover:underline">Parent Portal Login</a>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
