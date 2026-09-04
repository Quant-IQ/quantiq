"use client";

import { useState } from "react";
import WatchlistSidebar from "@/components/dashboard/WatchlistSidebar";
import WatchlistView from "@/components/dashboard/WatchlistView";
import MarketOverview from "@/components/dashboard/MarketOverview";
import MobileWatchlistSelector from "@/components/dashboard/MobileWatchlistSelector";

export default function Home() {
  const [activeWatchlist, setActiveWatchlist] = useState<string | null>(null);

  return (
    <div className="w-full flex flex-col h-full bg-[var(--color-bg-dark)] relative overflow-hidden">
      {/* Ambient glows */}
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-[var(--color-accent-green)]/10 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-blue-500/10 blur-[120px] rounded-full pointer-events-none" />
      
      <div className="flex flex-col md:flex-row flex-1 overflow-hidden relative z-10">
        <MobileWatchlistSelector activeWatchlist={activeWatchlist} onSelect={setActiveWatchlist} />
        <WatchlistSidebar activeWatchlist={activeWatchlist} onSelect={setActiveWatchlist} />
        {activeWatchlist ? (
          <WatchlistView watchlistName={activeWatchlist} />
        ) : (
          <MarketOverview />
        )}
      </div>
    </div>
  );
}