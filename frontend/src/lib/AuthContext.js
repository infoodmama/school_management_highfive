import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

// Role access map
// super_admin: everything
// admin_role: everything except settings
// teacher: students, attendance, calendar, homework
// office_staff: students, fees, expenses, inventory
const ROLE_ACCESS = {
  super_admin: ['/', '/classes', '/students', '/attendance', '/fees', '/expenses', '/inventory', '/calendar', '/homework', '/staff', '/settings'],
  admin_role: ['/', '/classes', '/students', '/attendance', '/fees', '/expenses', '/inventory', '/calendar', '/homework', '/staff'],
  teacher: ['/students', '/attendance', '/calendar', '/homework'],
  office_staff: ['/students', '/fees', '/expenses', '/inventory'],
};

export const getDefaultRoute = (role) => {
  if (role === 'super_admin' || role === 'admin_role') return '/';
  if (role === 'teacher') return '/students';
  if (role === 'office_staff') return '/students';
  return '/';
};

export const canAccess = (role, path) => {
  if (!role) return false;
  const allowed = ROLE_ACCESS[role] || [];
  // Allow student detail for anyone who can access students
  if (path.startsWith('/students/') && allowed.includes('/students')) return true;
  return allowed.includes(path);
};

export const getNavItems = (role) => {
  return ROLE_ACCESS[role] || [];
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [role, setRole] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem('schoolpro_auth');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setUser(parsed.user);
        setRole(parsed.role);
      } catch (e) { localStorage.removeItem('schoolpro_auth'); }
    }
    setLoading(false);
  }, []);

  const login = (userData, userRole) => {
    setUser(userData);
    setRole(userRole);
    localStorage.setItem('schoolpro_auth', JSON.stringify({ user: userData, role: userRole }));
  };

  const logout = () => {
    setUser(null);
    setRole(null);
    localStorage.removeItem('schoolpro_auth');
  };

  return (
    <AuthContext.Provider value={{ user, role, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
