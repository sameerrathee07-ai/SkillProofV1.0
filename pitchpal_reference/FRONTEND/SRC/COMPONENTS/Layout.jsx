import React, { useState, useEffect } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import TopBar from "./TopBar";
import TokenPackagesModal from "./TokenPackagesModal";

export default function Layout() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [tokenModalOpen, setTokenModalOpen] = useState(false);
  const [search, setSearch] = useState("");

  // Dashboard pages use the warm cream / forest-green theme.
  useEffect(() => {
    document.body.classList.add("theme-dashboard");
    return () => document.body.classList.remove("theme-dashboard");
  }, []);

  const openTokens = () => setTokenModalOpen(true);

  return (
    <div className="db-shell">
      {mobileOpen && (
        <div className="db-backdrop" onClick={() => setMobileOpen(false)} aria-hidden="true" />
      )}

      <Sidebar
        open={mobileOpen}
        onOpenTokens={openTokens}
        onNavigate={() => setMobileOpen(false)}
      />

      <div className="db-main">
        <TopBar
          onOpenMenu={() => setMobileOpen(true)}
          onOpenTokens={openTokens}
          search={search}
          onSearch={setSearch}
        />
        <main className="db-content">
          <Outlet context={{ openTokens, search }} />
        </main>
      </div>

      <TokenPackagesModal open={tokenModalOpen} onClose={() => setTokenModalOpen(false)} />
    </div>
  );
}
