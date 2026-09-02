import Button from "./Button";
import { ExclamationTriangleIcon } from "@heroicons/react/24/outline";

export default function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  const parts = message.split(": ");
  const title = parts.length > 1 ? parts[0] : "Data Unavailable";
  const desc = parts.length > 1 ? parts[1] : message;

  return (
    <div className="border border-negative/30 bg-[#10151C] rounded-2xl p-16 flex flex-col items-center justify-center text-center shadow-xl w-full">
      <div className="w-16 h-16 rounded-full bg-negative/10 flex items-center justify-center mb-6 border border-negative/20 shadow-inner">
        <ExclamationTriangleIcon className="w-8 h-8 text-negative" strokeWidth={1.5} />
      </div>
      <h3 className="text-xl font-heading font-bold text-white mb-2">{title}</h3>
      <p className="text-[var(--color-text-dim)] font-medium max-w-sm leading-relaxed mb-6">{desc}</p>
      {onRetry && (
        <Button onClick={onRetry} variant="ghost">
          Try Again
        </Button>
      )}
    </div>
  );
}