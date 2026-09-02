"use client";
import { useEffect, useRef } from "react";
import { createChart, ColorType, IChartApi } from "lightweight-charts";
import { ChartPoint } from "@/lib/types";

interface Props {
  data: ChartPoint[];
  type: "area" | "candlestick";
}

export default function AdvancedChart({ data, type }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      layout: { 
        background: { type: ColorType.Solid, color: "transparent" }, 
        textColor: "#8B98A5",
        fontFamily: "'Courier New', Courier, monospace"
      },
      grid: { 
        vertLines: { color: "rgba(255, 255, 255, 0.05)" }, 
        horzLines: { color: "rgba(255, 255, 255, 0.05)" } 
      },
      rightPriceScale: {
        borderVisible: false,
      },
      timeScale: {
        borderVisible: false,
        timeVisible: true,
      },
      width: containerRef.current.clientWidth,
      height: 440,
      crosshair: {
        vertLine: { color: "rgba(255, 255, 255, 0.2)", labelBackgroundColor: "#1F2937" },
        horzLine: { color: "rgba(255, 255, 255, 0.2)", labelBackgroundColor: "#1F2937" },
      },
    });

    chartRef.current = chart;

    if (type === "area") {
      const isUp = data.length > 1 && data[data.length - 1].close >= data[0].close;
      const lineColor = isUp ? "#22C55E" : "#F0665E";
      const topColor = isUp ? "rgba(34, 197, 94, 0.4)" : "rgba(240, 102, 94, 0.4)";
      const bottomColor = isUp ? "rgba(34, 197, 94, 0.0)" : "rgba(240, 102, 94, 0.0)";

      const series = chart.addAreaSeries({
        lineColor,
        topColor,
        bottomColor,
        lineWidth: 2,
      });
      series.setData(data.map(d => ({ time: d.time as any, value: d.close })));
    } else {
      const series = chart.addCandlestickSeries({
        upColor: "#22C55E", 
        downColor: "#F0665E",
        borderVisible: false,
        wickUpColor: "#22C55E", 
        wickDownColor: "#F0665E",
      });
      series.setData(data.map(d => ({ 
        time: d.time as any, 
        open: d.open, 
        high: d.high, 
        low: d.low, 
        close: d.close 
      })));
    }

    chart.timeScale().fitContent();

    const handleResize = () => {
      if (containerRef.current) {
        chart.resize(containerRef.current.clientWidth, 440);
      }
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [data, type]);

  return <div ref={containerRef} className="w-full h-[440px]" />;
}
