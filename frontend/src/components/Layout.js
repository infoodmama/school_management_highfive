import React from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { GraduationCap, Users, ClipboardCheck, DollarSign, ShoppingCart, Settings, BookOpen, Package, CalendarDays, BookOpenCheck, UserCog, LogOut } from 'lucide-react';
import { useAuth, canAccess } from '../lib/AuthContext';

const allNavItems = [
  { path: '/', label: 'Dashboard', icon: GraduationCap },
  { path: '/classes', label: 'Classes', icon: BookOpen },
  { path: '/students', label: 'Students', icon: Users },
  { path: '/attendance', label: 'Attendance', icon: ClipboardCheck },
  { path: '/fees', label: 'Fees', icon: DollarSign },
  { path: '/expenses', label: 'Expenses', icon: ShoppingCart },
  { path: '/inventory', label: 'Inventory', icon: Package },
  { path: '/calendar', label: 'Calendar', icon: CalendarDays },
  { path: '/homework', label: 'Homework', icon: BookOpenCheck },
  { path: '/staff', label: 'Staff', icon: UserCog },
  { path: '/settings', label: 'Settings', icon: Settings },
];

const Layout = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, role, logout } = useAuth();

  const navItems = allNavItems.filter((item) => canAccess(role, item.path));

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const getRoleLabel = () => {
    if (role === 'admin') return 'Administrator';
    if (role === 'teacher') return 'Teacher';
    if (role === 'office_staff') return 'Office Staff';
    return '';
  };

  return (
    <div className="flex min-h-screen bg-slate-50">
      <div className="w-64 bg-white border-r border-slate-200 fixed h-full flex flex-col">
        <div className="p-6 flex-1">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-12 h-12 bg-gradient-to-br from-sky-400 to-sky-600 rounded-2xl flex items-center justify-center">
              <GraduationCap className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-extrabold text-slate-900" style={{ fontFamily: 'Nunito' }}>SchoolPro</h1>
              <p className="text-xs text-slate-500 font-medium">Management System</p>
            </div>
          </div>
          <nav className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  data-testid={`nav-${item.label.toLowerCase()}`}
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl font-bold text-sm transition-all duration-200 active:scale-95 ${
                    isActive ? 'bg-sky-500 text-white shadow-lg' : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
        {/* User info & Logout */}
        <div className="p-4 border-t border-slate-200">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-9 h-9 bg-slate-200 rounded-full flex items-center justify-center">
              <span className="text-sm font-bold text-slate-600">{(user?.name || user?.username || '?')[0].toUpperCase()}</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-bold text-slate-900 truncate">{user?.name || user?.username}</p>
              <p className="text-xs text-slate-500">{getRoleLabel()}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            data-testid="logout-btn"
            className="flex items-center gap-2 w-full px-4 py-2.5 text-rose-600 hover:bg-rose-50 rounded-xl font-bold text-sm transition-all"
          >
            <LogOut className="w-4 h-4" />
            Logout
          </button>
        </div>
      </div>

      <div className="ml-64 flex-1">
        <div className="p-6 sm:p-8">
          <Outlet />
        </div>
      </div>
    </div>
  );
};

export default Layout;
