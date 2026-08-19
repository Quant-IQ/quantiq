"use client";
import { usePolling } from "@/hooks/usePolling";
import { getTrades } from "@/lib/api";
import SignalsTable from "@/components/signals/SignalsTable";
import PriceChart from "@/components/charts/PriceChart";
import LoadingState from "@/components/ui/LoadingState";
import ErrorState from "@/components/ui/ErrorState";
import EmptyState from "@/components/ui/EmptyState";
import { POLL_INTERVAL_MS } from "@/lib/constants";

export default function LivePage() {
  const { data, error, loading, refetch } = usePolling(getTrades, POLL_INTERVAL_MS);

  if (loading) return <LoadingState message="Loading live signals..." />;
  if (error) return <ErrorState message="Couldn't load live signals." onRetry={refetch} />;

  const trades = data?.trades ?? [];

  return (
    <div className="py-8 space-y-6">
      <h1 className="text-3xl font-bold font-heading text-textPrimary">Live Signals</h1>
      <PriceChart symbol="NIFTY" />
      {trades.length === 0 ? (
        <EmptyState message="No signals yet — check back once the bot is running." />
      ) : (
        <SignalsTable trades={trades} />
      )}
    </div>
  );
}