import Button from "./Button";

export default function ErrorState({
  message,
  onRetry,
}: {
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="border border-negative/40 bg-negative/10 rounded-xl p-8 text-center space-y-4">
      <p className="text-negative">{message}</p>
      {onRetry && <Button onClick={onRetry}>Retry</Button>}
    </div>
  );
}