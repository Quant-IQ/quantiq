export default function Button({
  children,
  onClick,
  variant = "primary",
}: {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: "primary" | "ghost";
}) {
  const base = "px-4 py-2 rounded-lg text-sm font-semibold transition-colors";
  const styles =
    variant === "primary"
      ? `${base} bg-accent text-black hover:opacity-90`
      : `${base} border border-panelBorder text-textPrimary hover:bg-panel`;
  return (
    <button onClick={onClick} className={styles}>
      {children}
    </button>
  );
}