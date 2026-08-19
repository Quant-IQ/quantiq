export default function EmptyState({ message }: { message: string }) {
  return (
    <div className="border border-panelBorder bg-panel rounded-xl p-12 text-center">
      <p className="text-textMuted">{message}</p>
    </div>
  );
}