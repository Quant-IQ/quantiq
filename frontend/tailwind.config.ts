import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#0A0E13",
        panel: "#141A21",
        panelBorder: "#232D37",
        accent: "#22C55E",
        textPrimary: "#E8EDF2",
        textMuted: "#8B98A5",
        info: "#4C8DFF",
        warn: "#F5934C",
        negative: "#F0665E",
      },
      fontFamily: {
        heading: ["Sora", "sans-serif"],
        body: ["Inter", "sans-serif"],
        mono: ["'Courier New'", "monospace"],
      },
    },
  },
  plugins: [],
};
export default config;
