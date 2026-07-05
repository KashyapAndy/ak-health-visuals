import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        cream: "#FAF7F2",
        "cream-dark": "#F0EBE3",
        olive: {
          DEFAULT: "#4D7C0F",
          light: "#84CC16",
          muted: "#ECFCCB",
          dark: "#3A5C09",
        },
        navy: {
          DEFAULT: "#0D1B2A",
          mid: "#1B3A5C",
          light: "#2C5282",
        },
        ink: "#1C1917",
        stone: "#78716C",
        amber: {
          soft: "#FEF3C7",
          DEFAULT: "#D97706",
        },
        danger: {
          soft: "#FEE2E2",
          DEFAULT: "#DC2626",
        },
      },
      fontFamily: {
        sans: ["Outfit", "sans-serif"],
        display: ["Satoshi", "Outfit", "sans-serif"],
        mono: ["DM Mono", "monospace"],
      },
      boxShadow: {
        card: "0 1px 4px 0 rgba(28,25,23,0.06), 0 4px 16px 0 rgba(28,25,23,0.04)",
        "card-hover": "0 4px 24px 0 rgba(28,25,23,0.10)",
      },
      backdropBlur: {
        glass: "12px",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.5s ease forwards",
        "fade-in": "fade-in 0.3s ease forwards",
      },
    },
  },
  plugins: [],
};

export default config;
