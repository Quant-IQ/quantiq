"use client";

import { useEffect, useState, use } from "react";
import { getStockInfo, getStockChart } from "@/lib/api";
import { StockInfo, ChartPoint } from "@/lib/types";
import AdvancedChart from "@/components/charts/AdvancedChart";
import LoadingState from "@/components/ui/LoadingState";
import ErrorState from "@/components/ui/ErrorState";
import { useRouter } from "next/navigation";
import { ArrowLeftIcon } from "@heroicons/react/24/outline";

export default function StockDetailPage({ params }: { params: Promise<{ symbol: string }> }) {
  const router = useRouter();
  const unwrappedParams = use(params);
  const symbol = decodeURIComponent(unwrappedParams.symbol).toUpperCase();
  
  const [info, setInfo] = useState<StockInfo | null>(null);
  const [chartData, setChartData] = useState<ChartPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  
  const [range, setRange] = useState("1y");
  const [chartType, setChartType] = useState<"area" | "candlestick">("area");

  const fetchData = () => {
    setLoading(true);
    setError(false);
    
    Promise.all([getStockInfo(symbol), getStockChart(symbol, range)])
      .then(([infoRes, chartRes]) => {
        setInfo(infoRes);
        setChartData(chartRes.data);
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchData();
  }, [symbol, range]); 

  if (loading && !info) return <div className="flex-1 bg-[var(--color-bg-dark)]"><LoadingState message={`Loading ${symbol}...`} /></div>;
  if (error) return <div className="flex-1 bg-[var(--color-bg-dark)]"><ErrorState message="Could not load stock data." onRetry={fetchData} /></div>;
  
  if (!info) return null;

  const isPos = info.current_price && info.previous_close 
    ? info.current_price >= info.previous_close 
    : true;
    
  const changeAmt = info.current_price && info.previous_close 
    ? info.current_price - info.previous_close 
    : 0;
    
  const changePct = info.current_price && info.previous_close 
    ? (changeAmt / info.previous_close) * 100 
    : 0;

  return (
    <div className="flex-1 flex flex-col bg-[var(--color-bg-dark)] h-full overflow-y-auto custom-scrollbar">
      {/* Top Header Navigation */}
      <div className="px-8 py-6 glass-header sticky top-0 z-20 flex items-center gap-6 border-b border-[var(--color-panel-border)]">
        <button 
          onClick={() => router.back()}
          className="flex items-center justify-center w-10 h-10 rounded-full bg-white/5 border border-[var(--color-panel-border)] text-[var(--color-text-dim)] hover:text-white hover:bg-white/10 transition-colors"
        >
          <ArrowLeftIcon className="w-5 h-5" />
        </button>
        <div className="flex flex-col">
           <h1 className="font-bold text-white text-xl tracking-tight">{info.name}</h1>
           <div className="flex items-center gap-2 text-xs text-[var(--color-text-dim)] uppercase tracking-wider font-semibold flex-wrap">
              <span>{info.symbol}</span>
              {info.sector && (
                 <>
                   <span>•</span>
                   <span>{info.sector}</span>
                 </>
              )}
              {info.industry && (
                 <>
                   <span>•</span>
                   <span>{info.industry}</span>
                 </>
              )}
           </div>
        </div>
      </div>

      {/* Main Content Layout */}
      <div className="p-8 max-w-7xl mx-auto w-full flex flex-col lg:flex-row gap-8">
        
        {/* Left Sidebar (Scorecard / Info) */}
        <div className="w-full lg:w-[320px] flex flex-col gap-6">
          <div className="glass-panel p-6 rounded-2xl">
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-6">Stock Scorecard</h3>
            
            <div className="space-y-6">
               <div className="flex items-start justify-between border-b border-[var(--color-panel-border)] pb-6">
                 <div>
                    <div className="text-[var(--color-text-dim)] text-xs font-semibold uppercase tracking-wider mb-1">Market Cap</div>
                    <div className="text-white font-medium">{info.market_cap ? `₹${(info.market_cap / 10000000).toFixed(0)} Cr` : "N/A"}</div>
                 </div>
               </div>
               
               <div className="flex items-start justify-between border-b border-[var(--color-panel-border)] pb-6">
                 <div>
                    <div className="text-[var(--color-text-dim)] text-xs font-semibold uppercase tracking-wider mb-1">P/E Ratio</div>
                    <div className="text-white font-medium">{info.pe_ratio ? info.pe_ratio.toFixed(2) : "N/A"}</div>
                 </div>
               </div>
               
               <div className="flex items-start justify-between border-b border-[var(--color-panel-border)] pb-6">
                 <div>
                    <div className="text-[var(--color-text-dim)] text-xs font-semibold uppercase tracking-wider mb-1">Div Yield</div>
                    <div className="text-white font-medium">{info.dividend_yield ? `${(info.dividend_yield * 100).toFixed(2)}%` : "N/A"}</div>
                 </div>
               </div>

               <div className="flex items-start justify-between border-b border-[var(--color-panel-border)] pb-6">
                 <div>
                    <div className="text-[var(--color-text-dim)] text-xs font-semibold uppercase tracking-wider mb-1">52W High</div>
                    <div className="text-white font-medium">{info.fifty_two_week_high ? `₹${info.fifty_two_week_high.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : "N/A"}</div>
                 </div>
               </div>

               <div className="flex items-start justify-between pb-2">
                 <div>
                    <div className="text-[var(--color-text-dim)] text-xs font-semibold uppercase tracking-wider mb-1">52W Low</div>
                    <div className="text-white font-medium">{info.fifty_two_week_low ? `₹${info.fifty_two_week_low.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : "N/A"}</div>
                 </div>
               </div>
            </div>
          </div>
          
          {info.description && (
            <div className="glass-panel p-6 rounded-2xl">
              <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">About</h3>
              <p className="text-[var(--color-text-dim)] text-sm leading-relaxed line-clamp-6 hover:line-clamp-none transition-all">
                {info.description}
              </p>
            </div>
          )}
        </div>

        {/* Right Main Area */}
        <div className="flex-1 flex flex-col gap-6">
           
           {/* Price & Chart Header */}
           <div className="flex flex-col gap-1">
             <div className="flex items-center gap-3">
               <span className="text-4xl font-bold text-white tabular-nums">
                 ₹{info.current_price?.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
               </span>
               <div className={`flex items-center gap-1 text-lg font-semibold px-2 py-1 rounded ${isPos ? 'text-[var(--color-accent-green)] bg-[var(--color-accent-green)]/10' : 'text-[var(--color-accent-red)] bg-[var(--color-accent-red)]/10'}`}>
                  {isPos ? "+" : ""}{changePct.toFixed(2)}%
               </div>
             </div>
             <div className="text-[var(--color-text-dim)] text-sm">
               {isPos ? "+" : ""}₹{changeAmt.toFixed(2)} (1D)
             </div>
           </div>

           {/* Chart Controls */}
           <div className="glass-panel p-6 rounded-2xl flex flex-col gap-4">
              <div className="flex items-center justify-between border-b border-[var(--color-panel-border)] pb-4">
                 
                 {/* Tabs */}
                 <div className="flex items-center gap-6">
                    <button className="text-white text-sm font-semibold border-b-2 border-[var(--color-accent-green)] pb-4 -mb-[17px]">Overview</button>
                    <button className="text-[var(--color-text-dim)] hover:text-white transition-colors text-sm font-semibold pb-4 -mb-[17px]">Financials</button>
                    <button className="text-[var(--color-text-dim)] hover:text-white transition-colors text-sm font-semibold pb-4 -mb-[17px]">News</button>
                 </div>

                 {/* Chart Type Toggle */}
                 <div className="flex items-center bg-black/40 rounded-lg p-1 border border-[var(--color-panel-border)]">
                    <button 
                      onClick={() => setChartType("area")}
                      className={`px-3 py-1 text-xs font-semibold rounded-md transition-colors ${chartType === "area" ? 'bg-white/10 text-white' : 'text-[var(--color-text-dim)] hover:text-white'}`}
                    >
                      Area
                    </button>
                    <button 
                      onClick={() => setChartType("candlestick")}
                      className={`px-3 py-1 text-xs font-semibold rounded-md transition-colors ${chartType === "candlestick" ? 'bg-white/10 text-white' : 'text-[var(--color-text-dim)] hover:text-white'}`}
                    >
                      Candle
                    </button>
                 </div>
              </div>

              {/* Chart Component */}
              <div className="w-full relative min-h-[440px]">
                {loading && <div className="absolute inset-0 z-10 flex items-center justify-center bg-[var(--color-bg-dark)]/50 backdrop-blur-sm"><LoadingState message="Fetching chart..." /></div>}
                <AdvancedChart data={chartData} type={chartType} />
              </div>

              {/* Time Range Selector */}
              <div className="flex items-center justify-center gap-2 mt-2">
                 {["1d", "1w", "1m", "1y", "5y"].map((r) => (
                   <button 
                     key={r}
                     onClick={() => setRange(r)}
                     className={`px-4 py-1.5 rounded-full text-xs font-semibold uppercase tracking-wider transition-all ${
                       range === r 
                       ? 'bg-white text-black' 
                       : 'text-[var(--color-text-dim)] hover:text-white hover:bg-white/10'
                     }`}
                   >
                     {r}
                   </button>
                 ))}
              </div>
           </div>

        </div>
      </div>
    </div>
  );
}
