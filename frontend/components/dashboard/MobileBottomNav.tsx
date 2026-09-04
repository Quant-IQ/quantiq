"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  HomeIcon, 
  FunnelIcon, 
  ChartBarIcon, 
  BoltIcon
} from "@heroicons/react/24/outline";
import { 
  HomeIcon as HomeSolid, 
  FunnelIcon as FunnelSolid, 
  ChartBarIcon as ChartSolid, 
  BoltIcon as BoltSolid
} from "@heroicons/react/24/solid";

export default function MobileBottomNav() {
  const pathname = usePathname();

  const navItems = [
    { name: "Dashboard", href: "/", icon: HomeIcon, activeIcon: HomeSolid },
    { name: "Screener", href: "/screener", icon: FunnelIcon, activeIcon: FunnelSolid },
    { name: "Backtest", href: "/backtest", icon: ChartBarIcon, activeIcon: ChartSolid },
    { name: "Live", href: "/live", icon: BoltIcon, activeIcon: BoltSolid },
  ];

  return (
    <div className="md:hidden fixed bottom-0 left-0 w-full h-[64px] bg-[var(--color-bg-dark)] border-t border-[var(--color-panel-border)] z-50 flex items-center justify-around px-2 pb-safe">
      {/* Background blur overlay */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-xl pointer-events-none" />
      
      {navItems.map((item) => {
        const isActive = pathname === item.href;
        const Icon = isActive ? item.activeIcon : item.icon;
        
        return (
          <Link
            key={item.name}
            href={item.href}
            className="relative z-10 flex flex-col items-center justify-center w-16 h-full gap-1"
          >
            <div className={`relative flex items-center justify-center w-8 h-8 rounded-full transition-all duration-300 ${isActive ? "text-[var(--color-accent-green)]" : "text-[var(--color-text-dim)]"}`}>
              {isActive && (
                <div className="absolute inset-0 bg-[var(--color-accent-green)]/15 rounded-full blur-md" />
              )}
              <Icon className="w-5 h-5 relative z-10" />
            </div>
            <span className={`text-[10px] font-semibold tracking-wide transition-colors duration-300 ${isActive ? "text-white" : "text-[var(--color-text-dim)]"}`}>
              {item.name}
            </span>
          </Link>
        );
      })}
    </div>
  );
}
