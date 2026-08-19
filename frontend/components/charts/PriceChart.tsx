"use client";
import { useEffect, useRef } from "react";
import { createChart, ColorType, IChartApi, ISeriesApi } from "lightweight-charts";
import { getPriceHistory } from "@/lib/api";
import { POLL_INTERVAL_MS } from "@/lib/constants";
import { usePolling } from "@/hooks/usePolling";

export default function PriceChart({ symbol }: { symbol: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const isLoadedRef = useRef(false);
  const { data: candles } = usePolling(() => getPriceHistory(symbol), POLL_INTERVAL_MS);

  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      layout: { background: { type: ColorType.Solid, color: "#141A21" }, textColor: "#8B98A5" },
      grid: { vertLines: { color: "#232D37" }, horzLines: { color: "#232D37" } },
      width: containerRef.current.clientWidth,
      height: 320,
    });
    const series = chart.addCandlestickSeries({
      upColor: "#22C55E", downColor: "#F0665E",
      borderVisible: false,
      wickUpColor: "#22C55E", wickDownColor: "#F0665E",
    });

    chartRef.current = chart;
    seriesRef.current = series;

    const handleResize = () => {
      if (containerRef.current) {
        chart.resize(containerRef.current.clientWidth, 320);
      }
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
      isLoadedRef.current = false;
    };
  }, [symbol]);

  useEffect(() => {
    if (candles && candles.length > 0 && seriesRef.current) {
      if (!isLoadedRef.current) {
        seriesRef.current.setData(candles);
        isLoadedRef.current = true;
      } else {
        seriesRef.current.update(candles[candles.length - 1]);
      }
    }
  }, [candles]);

  return <div ref={containerRef} className="bg-panel border border-panelBorder rounded-xl p-2" />;
}