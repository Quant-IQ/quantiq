import Link from "next/link";

export default function NotFound() {
  return (
    <div className="py-24 text-center space-y-4">
      <h1 className="text-2xl font-bold text-textPrimary">Page not found</h1>
      <Link href="/backtest" className="text-accent underline">Back to Backtest Report</Link>
    </div>
  );
}