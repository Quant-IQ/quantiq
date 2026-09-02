import { ExclamationCircleIcon, BoltIcon, ChartBarIcon } from "@heroicons/react/24/outline";

export default function EmptyState({ message, icon }: { message: string, icon?: "bolt" | "chart" }) {
  const parts = message.split(": ");
  const title = parts.length > 1 ? parts[0] : "Nothing to see here";
  const desc = parts.length > 1 ? parts[1] : message;

  return (
    <div className="border border-[var(--color-panel-border)] bg-[#10151C] rounded-2xl p-16 flex flex-col items-center justify-center text-center shadow-xl w-full">
      <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mb-6 border border-white/5 shadow-inner">
        {icon === "bolt" ? (
          <BoltIcon className="w-8 h-8 text-[var(--color-text-dim)]" strokeWidth={1.5} />
        ) : icon === "chart" ? (
          <ChartBarIcon className="w-8 h-8 text-[var(--color-text-dim)]" strokeWidth={1.5} />
        ) : (
          <ExclamationCircleIcon className="w-8 h-8 text-[var(--color-text-dim)]" strokeWidth={1.5} />
        )}
      </div>
      <h3 className="text-xl font-heading font-bold text-white mb-2">{title}</h3>
      <p className="text-[var(--color-text-dim)] font-medium max-w-sm leading-relaxed">{desc}</p>
    </div>
  );
}