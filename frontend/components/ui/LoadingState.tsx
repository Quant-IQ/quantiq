export default function LoadingState({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-16 w-full text-center">
      <div className="w-10 h-10 border-4 border-white/10 border-t-[var(--color-accent-green)] rounded-full animate-spin mb-6 shadow-lg"></div>
      <p className="text-[var(--color-text-dim)] font-medium tracking-wide animate-pulse">{message}</p>
    </div>
  );
}