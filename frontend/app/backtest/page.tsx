"use client";
import { useBacktest } from "@/hooks/useBacktest";
import StatCard from "@/components/ui/StatCard";
import EquityCurveChart from "@/components/charts/EquityCurveChart";
import LoadingState from "@/components/ui/LoadingState";
import ErrorState from "@/components/ui/ErrorState";

export default function BacktestPage() {
  const { data, error, loading, refetch } = useBacktest();

  if (loading) return <LoadingState message="Loading backtest results..." />;
  if (error) return <ErrorState message="Couldn't load backtest results." onRetry={refetch} />;
  if (!data) return null;

  return (
    <div className="py-8 space-y-6">
      <h1 className="text-3xl font-bold font-heading text-textPrimary">Backtest Report</h1>
      <div className="grid grid-cols-3 gap-4">
        <StatCard label="Sharpe Ratio" value={data.sharpe_ratio.toFixed(2)} accentClass="text-accent" />
        <StatCard label="Max Drawdown" value={`${data.max_drawdown}%`} accentClass="text-negative" />
        <StatCard label="Win Rate" value={`${data.win_rate}%`} accentClass="text-info" />
      </div>
      <EquityCurveChart data={data.equity_curve} />
    </div>
  );
}