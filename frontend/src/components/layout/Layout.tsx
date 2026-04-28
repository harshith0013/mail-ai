import { useState } from "react";
import { Navbar } from "./Navbar";
import { Sidebar } from "./Sidebar";
import { ToastContainer } from "../ui/Toast";

export function Layout({ children }: { children: React.ReactNode }) {
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar
        isMobileOpen={isMobileOpen}
        onMobileClose={() => setIsMobileOpen(false)}
        isCollapsed={isCollapsed}
        onToggleCollapse={() => setIsCollapsed(!isCollapsed)}
      />
      
      <div className="flex flex-1 flex-col overflow-hidden">
        <Navbar onMenuClick={() => setIsMobileOpen(true)} />
        <main className="flex-1 overflow-y-auto w-full relative">
          <div className="container mx-auto max-w-7xl px-4 py-8 sm:px-8">
            {children}
          </div>
        </main>
      </div>
      
      <ToastContainer />
    </div>
  );
}
