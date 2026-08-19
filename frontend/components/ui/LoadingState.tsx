export default function LoadingState({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="py-24 text-center">
      <p className="text-textMuted">{message}</p>
    </div>
  );
}