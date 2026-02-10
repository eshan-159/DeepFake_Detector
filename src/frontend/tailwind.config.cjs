module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Dazza Elegant Dark Palette
        void: {
          950: "#030305",
          900: "#07080c",
          850: "#0a0c12",
          800: "#0e1018",
          700: "#14161f",
        },
        surface: {
          900: "rgba(14, 16, 24, 0.85)",
          800: "rgba(20, 22, 31, 0.75)",
          700: "rgba(30, 33, 45, 0.65)",
        },
        accent: {
          violet: "#8b5cf6",
          indigo: "#6366f1",
          purple: "#a855f7",
          glow: "rgba(139, 92, 246, 0.15)",
        },
        neutral: {
          50: "#fafafa",
          100: "#f4f4f5",
          200: "#e4e4e7",
          300: "#d4d4d8",
          400: "#a1a1aa",
          500: "#71717a",
          600: "#52525b",
        },
      },
      fontFamily: {
        sans: ['"Inter"', '"SF Pro Display"', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"SF Mono"', 'Consolas', 'monospace'],
      },
      fontSize: {
        "2xs": ["0.625rem", { lineHeight: "0.875rem" }],
      },
      spacing: {
        18: "4.5rem",
        22: "5.5rem",
      },
      borderRadius: {
        "2xl": "1rem",
        "3xl": "1.5rem",
        "4xl": "2rem",
      },
      boxShadow: {
        glow: "0 0 40px -10px rgba(139, 92, 246, 0.3)",
        "glow-sm": "0 0 20px -5px rgba(139, 92, 246, 0.2)",
        "glow-lg": "0 0 60px -15px rgba(139, 92, 246, 0.4)",
        glass: "0 8px 32px rgba(0, 0, 0, 0.4)",
        "glass-lg": "0 16px 48px rgba(0, 0, 0, 0.5)",
      },
      backdropBlur: {
        xs: "2px",
      },
      animation: {
        "fade-in": "fadeIn 0.5s ease-out forwards",
        "slide-up": "slideUp 0.4s ease-out forwards",
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "glow-pulse": "glowPulse 4s ease-in-out infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        glowPulse: {
          "0%, 100%": { boxShadow: "0 0 20px -5px rgba(139, 92, 246, 0.15)" },
          "50%": { boxShadow: "0 0 30px -5px rgba(139, 92, 246, 0.25)" },
        },
      },
    },
  },
  plugins: [],
};
