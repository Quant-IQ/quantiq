"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { getWatchlists } from "@/lib/api";
import LoadingState from "@/components/ui/LoadingState";
import Sparkline from "@/components/ui/Sparkline";
import { 
  HomeIcon, 
  FunnelIcon, 
  ChartBarIcon, 
  BoltIcon,
  ListBulletIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon
} from "@heroicons/react/24/outline";
import { 
  HomeIcon as HomeSolid, 
  FunnelIcon as FunnelSolid, 
  ChartBarIcon as ChartSolid, 
  BoltIcon as BoltSolid
} from "@heroicons/react/24/solid";

export default function WatchlistSidebar({ 
  activeWatchlist, 
  onSelect 
}: { 
  activeWatchlist: string | null; 
  onSelect: (name: string | null) => void;
}) {
  const pathname = usePathname();
  const [watchlists, setWatchlists] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getWatchlists().then(res => {
      setWatchlists(res.watchlists);
    }).finally(() => setLoading(false));
  }, []);

  const navItems = [
    { name: "Dashboard", href: "/", icon: HomeIcon, activeIcon: HomeSolid },
    { name: "Screener", href: "/screener", icon: FunnelIcon, activeIcon: FunnelSolid },
    { name: "Backtest", href: "/backtest", icon: ChartBarIcon, activeIcon: ChartSolid },
    { name: "Live Signals", href: "/live", icon: BoltIcon, activeIcon: BoltSolid },
  ];

  return (
    <div className="w-[300px] border-r border-[var(--color-panel-border)] flex flex-col glass-panel h-full shadow-2xl">
      {/* Brand */}
      <div className="p-6 border-b border-[var(--color-panel-border)] flex items-center gap-1">
        <h1 className="font-heading font-extrabold text-3xl tracking-tight leading-none">
          <span className="text-white">Quant</span>
          <span className="text-[var(--color-accent-green)]">IQ</span>
        </h1>
      </div>

      {/* Main Navigation */}
      <div className="p-3 border-b border-[var(--color-panel-border)] space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = isActive ? item.activeIcon : item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              onClick={() => {
                if (item.href === "/") {
                  onSelect(null);
                }
              }}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 ${
                isActive && !activeWatchlist
                  ? "bg-white/10 text-white font-semibold" 
                  : "text-[var(--color-text-dim)] hover:bg-white/5 hover:text-white"
              }`}
            >
              <Icon className="w-5 h-5" />
              {item.name}
            </Link>
          );
        })}
      </div>

      {/* Watchlists */}
      <div className="p-4 flex items-center justify-between">
        <div className="flex items-center gap-2 text-[var(--color-text-dim)] text-xs font-semibold tracking-wider uppercase">
          <ListBulletIcon className="w-4 h-4" />
          <span>Watchlists</span>
        </div>
      </div>
      
      <div className="flex-1 overflow-y-auto px-3 pb-4 space-y-1 custom-scrollbar">
        {loading ? (
          <div className="p-4"><LoadingState message="Loading..." /></div>
        ) : (
          watchlists.map((name, i) => {
            // Determine a pseudo-random trend direction for the watchlist
            const isPos = (name.length + i) % 2 === 0;
            
            return (
              <button
                key={name}
                onClick={() => onSelect(name)}
                className={`w-full flex items-center justify-between px-4 py-3 rounded-lg text-sm transition-all duration-200 ${
                  activeWatchlist === name 
                    ? "bg-gradient-to-r from-[var(--color-accent-green)]/10 to-transparent border-l-2 border-[var(--color-accent-green)] text-white font-medium shadow-sm" 
                    : "border-l-2 border-transparent text-[var(--color-text-dim)] hover:bg-white/5 hover:text-white"
                }`}
              >
                <span>{name.replace(/_/g, " ")}</span>
                <div className={`flex items-center justify-center w-6 h-6 rounded-md shadow-sm ${isPos ? 'bg-[var(--color-accent-green)]/10 text-[var(--color-accent-green)]' : 'bg-[#F0665E]/10 text-[#F0665E]'}`}>
                  {isPos ? (
                    <ArrowTrendingUpIcon className="w-4 h-4" strokeWidth={2.5} />
                  ) : (
                    <ArrowTrendingDownIcon className="w-4 h-4" strokeWidth={2.5} />
                  )}
                </div>
              </button>
            );
          })
        )}
      </div>
    </div>
  );
}
