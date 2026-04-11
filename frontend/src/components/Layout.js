import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { GraduationCap, Users, ClipboardCheck, DollarSign, ShoppingCart, Settings, BookOpen } from 'lucide-react';

const Layout = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Dashboard', icon: GraduationCap },
    { path: '/classes', label: 'Classes', icon: BookOpen },
    { path: '/students', label: 'Students', icon: Users },
    { path: '/attendance', label: 'Attendance', icon: ClipboardCheck },
    { path: '/fees', label: 'Fees', icon: DollarSign },
    { path: '/expenses', label: 'Expenses', icon: ShoppingCart },
    { path: '/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-slate-200 fixed h-full">
        <div className="p-6">
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
                    isActive
                      ? 'bg-sky-500 text-white shadow-lg'
                      : 'text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="ml-64 flex-1">
        <div className="p-6 sm:p-8">
          <Outlet />
        </div>
      </div>
    </div>
  );
};

export default Layout;
