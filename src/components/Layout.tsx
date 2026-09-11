import React from 'react';
import { Outlet } from 'react-router-dom';
import { Navbar } from './Navbar';

export const Layout: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col bg-ivory text-ink">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
      <footer className="bg-ink text-ivory/80 border-t border-brass/20 py-8 px-4 mt-16">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4 text-xs font-sans">
          <div>
            <span className="font-serif font-bold text-sm text-ivory">Skill<span className="text-brass">Proof</span></span>
            <span className="ml-2 text-ivory/60">— Verified Problem-Solving Marketplace with Pitch Quality Gate</span>
          </div>
          <div className="flex gap-6 text-ivory/60">
            <span>Anti-Spam Quality Gate</span>
            <span>Ink & Brass Editorial</span>
            <span>V1.0 Demo</span>
          </div>
        </div>
      </footer>
    </div>
  );
};
