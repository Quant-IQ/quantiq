export default function Badge({ signal }: { signal: "BUY" | "SELL" }) {
  const isBuy = signal === "BUY";
  return (
    <span
      className={`px-2 py-0.5 rounded-full text-xs font-bold ${
        isBuy ? "bg-accent/20 text-accent" : "bg-negative/20 text-negative"
      }`}
    >
      {signal}
    </span>
  );
}