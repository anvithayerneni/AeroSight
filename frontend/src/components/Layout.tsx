import React from 'react';
import { Sidebar, PageId } from './Sidebar';
import { Navbar } from './Navbar';

interface LayoutProps {
  activePage: PageId;
  onSelectPage: (page: PageId) => void;
  onRefresh?: () => void;
  isRefreshing?: boolean;
  children: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({
  activePage,
  onSelectPage,
  onRefresh,
  isRefreshing,
  children
}) => {
  return (
    <div className="flex h-screen w-full bg-aviation-dark overflow-hidden">
      <Sidebar activePage={activePage} onSelectPage={onSelectPage} />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Navbar onRefresh={onRefresh} isRefreshing={isRefreshing} />
        <main className="flex-1 overflow-y-auto p-6 lg:p-8 space-y-6">
          {children}
        </main>
      </div>
    </div>
  );
};
