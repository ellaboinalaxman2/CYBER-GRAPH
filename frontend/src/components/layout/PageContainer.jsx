import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import Footer from './Footer';
import { useAppContext } from '../../context/AppContext';

export const PageContainer = ({
  title,
  subtitle,
  actions,
  children,
  noPadding = false,
}) => {
  const { sidebarOpen } = useAppContext();

  return (
    <div className="min-h-screen bg-[#0a0d14] text-slate-100 flex">
      {/* Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div
        className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ${
          sidebarOpen ? 'lg:pl-64' : 'lg:pl-20'
        } pl-0`}
      >
        <Header />

        <main className="flex-1 flex flex-col">
          {(title || subtitle || actions) && (
            <div className="px-4 lg:px-8 pt-6 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/40 bg-slate-950/20">
              <div>
                {title && <h1 className="text-2xl font-bold text-slate-100 tracking-tight">{title}</h1>}
                {subtitle && <p className="text-xs sm:text-sm text-slate-400 mt-1 font-mono">{subtitle}</p>}
              </div>
              {actions && <div className="flex items-center gap-2.5 flex-wrap">{actions}</div>}
            </div>
          )}

          <div className={`flex-1 ${noPadding ? 'p-0' : 'p-4 lg:p-8'}`}>{children}</div>
        </main>

        <Footer />
      </div>
    </div>
  );
};

export default PageContainer;
