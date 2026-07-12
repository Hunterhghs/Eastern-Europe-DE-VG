/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#0f172a',
        surface: '#1e293b',
        border: '#334155',
        accent: '#38bdf8',
        gold: '#f59e0b',
        warn: '#ef4444',
        green: '#22c55e',
        muted: '#94a3b8',
        text: '#e2e8f0',
      },
      fontFamily: {
        sans: ['system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
};
