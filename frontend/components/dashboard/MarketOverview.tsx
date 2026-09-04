"use client";

import { useEffect, useState } from "react";
import { ScreenerData, ChartPoint, Trade } from "@/lib/types";
import { getScreener, getStockChart, getTrades, getLiveSignals } from "@/lib/api";
import LoadingState from "@/components/ui/LoadingState";
import { ArrowTrendingUpIcon, ArrowTrendingDownIcon, FireIcon } from "@heroicons/react/24/solid";
import { MagnifyingGlassIcon, BellIcon, UserIcon } from "@heroicons/react/24/outline";
import AdvancedChart from "@/components/charts/AdvancedChart";
import { useRouter } from "next/navigation";

export default function MarketOverview() {
  const router = useRouter();
  const [data, setData] = useState<ScreenerData[]>([]);
  const [niftyChart, setNiftyChart] = useState<ChartPoint[]>([]);
  const [recentTrades, setRecentTrades] = useState<Trade[]>([]);
  const [liveSignals, setLiveSignals] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedIndex, setSelectedIndex] = useState("^NSEI");

  useEffect(() => {
    Promise.all([
      getScreener(),
      getStockChart(selectedIndex, "1d").catch(() => ({ data: [] })),
      getTrades().catch(() => ({ trades: [] })),
      getLiveSignals().catch(() => ({ signals: [] }))
    ]).then(([screenerRes, chartRes, tradesRes, signalsRes]) => {
      setData(screenerRes.data);
      setNiftyChart(chartRes.data);
      setRecentTrades(tradesRes.trades);
      setLiveSignals(signalsRes.signals);
    }).finally(() => setLoading(false));
  }, []);

  // Effect specifically for when the index changes after initial load
  useEffect(() => {
    if (loading) return; // Skip initial load as it's handled above
    getStockChart(selectedIndex, "1d")
      .then(res => setNiftyChart(res.data))
      .catch(() => setNiftyChart([]));
  }, [selectedIndex]);

  if (loading) return <div className="p-12 flex-1"><LoadingState message="Analyzing market overview..." /></div>;

  const sortedByChange = [...data].sort((a, b) => b.change_pct - a.change_pct);
  const gainers = sortedByChange.slice(0, 4);
  const losers = sortedByChange.slice(-4).reverse();
  
  const sortedByVolume = [...data].sort((a, b) => b.volume - a.volume);
  const active = sortedByVolume.slice(0, 4);

  const advances = data.filter(d => d.change_pct > 0).length;
  const declines = data.filter(d => d.change_pct < 0).length;
  const unchanged = data.length - advances - declines;
  
  const total = advances + declines + unchanged;
  const advPct = total ? (advances / total) * 100 : 0;
  const decPct = total ? (declines / total) * 100 : 0;
  const unchangedPct = total ? (unchanged / total) * 100 : 0;

  const latestNifty = niftyChart.length > 0 ? niftyChart[niftyChart.length - 1].close : 0;
  const topGainer = gainers[0];
  const totalVolume = data.reduce((acc, stock) => acc + stock.volume, 0);

  const renderStockRow = (stock: ScreenerData) => {
    const isPos = stock.change_pct >= 0;
    const initial = stock.symbol.substring(0, 1);
    
    return (
      <div 
        key={stock.symbol} 
        onClick={() => router.push(`/stock/${stock.symbol}`)}
        className="flex items-center justify-between p-3 -mx-3 rounded-xl hover:bg-white/5 transition-all duration-300 hover:translate-x-1 cursor-pointer group"
      >
        <div className="flex items-center gap-3">
          <span className="font-bold text-sm text-white transition-colors">{stock.symbol}</span>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="text-white font-mono font-medium text-[14px] tabular-nums text-right min-w-[75px]">
            ₹{stock.ltp.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className={`flex items-center justify-center min-w-[68px] px-2 py-1 rounded-md text-right font-mono text-xs font-bold tabular-nums shadow-sm ${isPos ? 'bg-[var(--color-accent-green)]/10 text-[var(--color-accent-green)] border border-[var(--color-accent-green)]/20' : 'bg-[#F0665E]/10 text-[#F0665E] border border-[#F0665E]/20'}`}>
            {isPos ? '+' : ''}{stock.change_pct.toFixed(2)}%
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex-1 flex flex-col p-6 overflow-y-auto custom-scrollbar gap-6">
      
      {/* Top KPI Banner (Styled to match screenshot) */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 w-full">
        {/* KPI 1 */}
        <div className="bg-[#161B22] border border-white/5 rounded-lg p-4 flex flex-col justify-between shadow-sm h-[90px]">
           <span className="text-[var(--color-text-dim)] text-[10px] uppercase tracking-widest font-bold mb-1">Selected Index Close</span>
           <span className="text-white text-[22px] font-mono font-bold tabular-nums">
             {latestNifty > 0 ? `₹${latestNifty.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '...'}
           </span>
        </div>
        
        {/* KPI 2 */}
        <div className="bg-[#161B22] border border-white/5 rounded-lg p-4 flex flex-col justify-between shadow-sm h-[90px]">
           <span className="text-[var(--color-text-dim)] text-[10px] uppercase tracking-widest font-bold mb-1">Adv / Dec Ratio</span>
           <div className="flex items-center gap-3">
             <span className="text-[var(--color-accent-green)] text-[22px] font-mono font-bold tabular-nums">
               {declines > 0 ? (advances / declines).toFixed(2) : advances}x
             </span>
             <span className="text-[var(--color-accent-green)] text-[10px] font-bold bg-[var(--color-accent-green)]/10 px-1.5 py-0.5 rounded">
               {advances >= declines ? 'Bullish' : 'Bearish'}
             </span>
           </div>
        </div>

        {/* KPI 3 */}
        <div className="bg-[#161B22] border border-white/5 rounded-lg p-4 flex flex-col justify-between shadow-sm h-[90px]">
           <span className="text-[var(--color-text-dim)] text-[10px] uppercase tracking-widest font-bold mb-1">Screener Volume</span>
           <span className="text-white text-[22px] font-mono font-bold tabular-nums">
             {(totalVolume / 1000000).toFixed(2)}M
           </span>
        </div>

        {/* KPI 4 */}
        <div className="bg-[#161B22] border border-white/5 rounded-lg p-4 flex flex-col justify-between shadow-sm h-[90px]">
           <span className="text-[var(--color-text-dim)] text-[10px] uppercase tracking-widest font-bold mb-1">Market Breadth</span>
           <div className="w-full flex h-1.5 rounded-full overflow-hidden mt-1 mb-2">
             <div style={{ width: `${advPct}%` }} className="h-full bg-[var(--color-accent-green)]" />
             <div style={{ width: `${unchangedPct}%` }} className="h-full bg-blue-500/50" />
             <div style={{ width: `${decPct}%` }} className="h-full bg-[#F0665E]" />
           </div>
           <div className="flex justify-between text-[9px] text-[var(--color-text-dim)] uppercase font-bold tracking-wider mt-auto">
             <span>Adv {advPct.toFixed(0)}%</span>
             <span>Unc {unchangedPct.toFixed(0)}%</span>
             <span>Dec {decPct.toFixed(0)}%</span>
           </div>
        </div>
      </div>

      {/* Header Container */}
      <div className="flex items-center justify-between mt-2 mb-1">
        <h2 className="text-xl font-bold text-white tracking-tight">Market Overview</h2>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        
        {/* Left Col: Chart & Breadth */}
        <div className="xl:col-span-2 flex flex-col gap-8">
           
           {/* Market Chart */}
           <div className="glass-panel p-6 rounded-2xl shadow-xl flex flex-col gap-4">
             <div className="flex items-center justify-between">
               <div>
                  <h3 className="text-lg font-heading font-bold text-white tracking-tight">Market Intraday</h3>
                  <p className="text-xs text-[var(--color-text-dim)] uppercase tracking-wider font-semibold mt-1">1D Trend</p>
               </div>
               <select
                 value={selectedIndex}
                 onChange={(e) => setSelectedIndex(e.target.value)}
                 className="bg-black/40 border border-[var(--color-panel-border)] rounded-lg px-3 py-1.5 text-sm font-semibold text-white focus:outline-none focus:border-[var(--color-accent-green)] transition-colors cursor-pointer"
               >
                 <option value="^NSEI" className="bg-[var(--color-bg-dark)]">NIFTY 50</option>
                 <option value="^NSEBANK" className="bg-[var(--color-bg-dark)]">BANKNIFTY</option>
                 <option value="^BSESN" className="bg-[var(--color-bg-dark)]">SENSEX</option>
                 <option value="^CNXIT" className="bg-[var(--color-bg-dark)]">NIFTY IT</option>
               </select>
             </div>
             {/* Note: AdvancedChart defaults to 440px height, we can wrap it in a flex container if needed, but it handles its own height internally if we don't override. Let's just let it be its default height */}
             <div className="w-full relative">
                {niftyChart.length > 0 ? (
                  <AdvancedChart data={niftyChart} type="area" />
                ) : (
                  <div className="absolute inset-0 flex items-center justify-center text-[var(--color-text-dim)] text-sm min-h-[440px]">Chart data unavailable</div>
                )}
             </div>
           </div>

           {/* Bottom Row of Left Column */}
           <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mt-2">
             {/* Market Breadth Panel */}
             <div className="bg-[#161B22] border border-white/5 rounded-2xl p-5 flex flex-col justify-between shadow-xl">
                <div className="flex items-center justify-between mb-6">
                  <span className="text-white text-xs uppercase tracking-wider font-bold">Market Breadth (Universe)</span>
                  <span className="text-[var(--color-text-dim)] text-[10px] font-bold uppercase">Adv/Dec: {(advances / (declines || 1)).toFixed(2)}</span>
                </div>
                
                <div className="flex items-center justify-between font-semibold mb-3">
                   <div className="text-[var(--color-accent-green)] text-[13px] font-bold">{advances} Adv</div>
                   <div className="text-white text-[13px] font-bold">{unchanged} Unc</div>
                   <div className="text-[#F0665E] text-[13px] font-bold text-right">{declines} Dec</div>
                </div>
                
                <div className="w-full flex h-2.5 rounded-full overflow-hidden">
                   <div style={{ width: `${advPct}%` }} className="h-full bg-[var(--color-accent-green)]" />
                   <div style={{ width: `${unchangedPct}%` }} className="h-full bg-[#FCA5A5]" />
                   <div style={{ width: `${decPct}%` }} className="h-full bg-[#F0665E]" />
                </div>
             </div>

             {/* Recent Activity Panel */}
             <div className="bg-[#161B22] border border-white/5 rounded-2xl p-5 flex flex-col shadow-xl">
                <div className="flex items-center gap-2 mb-5">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4 text-white">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-white text-xs uppercase tracking-wider font-bold">Recent Activity</span>
                </div>
                <div className="space-y-4 flex-1">
                  {recentTrades.slice(0, 2).map((trade) => (
                    <div key={trade.id} className="flex justify-between items-center">
                      <div>
                        <div className="text-[11px] font-bold text-white uppercase tracking-wider">{trade.signal} {trade.quantity || 100} {trade.symbol}</div>
                        <div className="text-[10px] text-[var(--color-text-dim)] mt-0.5">Market @ {trade.price.toFixed(2)}</div>
                      </div>
                      <div className="bg-[var(--color-accent-green)]/10 text-[var(--color-accent-green)] border border-[var(--color-accent-green)]/20 px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider">
                        Executed
                      </div>
                    </div>
                  ))}
                  {recentTrades.length === 0 && <div className="text-xs text-[var(--color-text-dim)]">No recent activity</div>}
                </div>
             </div>
           </div>

        </div>

        {/* Right Col: Top Movers & Signals */}
        <div className="flex flex-col gap-6">
           
           {/* Top Gainers */}
           <div className="glass-panel p-5 rounded-2xl shadow-xl">
             <div className="flex items-center gap-2 mb-4">
               <ArrowTrendingUpIcon className="w-5 h-5 text-[var(--color-accent-green)]" />
               <h3 className="text-sm font-bold text-white uppercase tracking-wider">Top Gainers</h3>
             </div>
             <div className="space-y-2">
               {gainers.map(renderStockRow)}
             </div>
           </div>

           {/* Top Losers */}
           <div className="glass-panel p-5 rounded-2xl shadow-xl">
             <div className="flex items-center gap-2 mb-4">
               <ArrowTrendingDownIcon className="w-5 h-5 text-[var(--color-accent-red)]" />
               <h3 className="text-sm font-bold text-white uppercase tracking-wider">Top Losers</h3>
             </div>
             <div className="space-y-2">
               {losers.map(renderStockRow)}
             </div>
           </div>

           {/* Live Signals */}
           <div className="bg-[#161B22] border border-white/5 p-5 rounded-2xl shadow-xl">
             <div className="flex items-center gap-2 mb-4">
               <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-4 h-4 text-[#F0665E]">
                 <path strokeLinecap="round" strokeLinejoin="round" d="M9.348 14.651a3.75 3.75 0 010-5.303m5.304 0a3.75 3.75 0 010 5.303m-7.425 2.122a6.75 6.75 0 010-9.546m9.546 0a6.75 6.75 0 010 9.546M5.106 18.894c-3.808-3.808-3.808-9.98 0-13.789m13.788 0c3.808 3.808 3.808 9.98 0 13.789M12 12.75a.75.75 0 110-1.5.75.75 0 010 1.5z" />
               </svg>
               <h3 className="text-xs font-bold text-white uppercase tracking-wider">Live Signals</h3>
             </div>
             <div className="space-y-4">
               {liveSignals.slice(0, 4).map((signal, i) => (
                 <div key={i} className="flex items-start gap-3">
                   <div className={`w-1.5 h-1.5 rounded-full mt-1.5 shadow-sm ${signal.signal === 'BUY' ? 'bg-[var(--color-accent-green)] shadow-[var(--color-accent-green)]' : 'bg-[#F0665E] shadow-[#F0665E]'}`} />
                   <div>
                     <div className="text-[11px] font-bold text-white uppercase tracking-wider">{signal.symbol} - {signal.signal === 'BUY' ? 'Breakout' : 'RSI Oversold'} @ {signal.price}</div>
                     <div className="text-[10px] text-[var(--color-text-dim)] mt-0.5">{i === 0 ? '2 mins ago' : i === 1 ? '15 mins ago' : '1 hour ago'}</div>
                   </div>
                 </div>
               ))}
               {liveSignals.length === 0 && <div className="text-xs text-[var(--color-text-dim)]">No live signals</div>}
             </div>
           </div>

        </div>
      </div>
    </div>
  );
}
