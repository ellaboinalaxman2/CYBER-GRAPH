/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: '#0a0d14',
          card: '#0f172a',
          'card-hover': '#1e293b',
          border: '#1e293b',
          'border-bright': '#334155',
          accent: '#06b6d4',
          'accent-glow': 'rgba(6, 182, 212, 0.25)',
          critical: '#ef4444',
          'critical-glow': 'rgba(239, 68, 68, 0.25)',
          high: '#f97316',
          medium: '#eab308',
          low: '#3b82f6',
          info: '#10b981',
          success: '#10b981',
          text: '#f8fafc',
          muted: '#94a3b8',
          dark: '#030712'
        }
      },
      boxShadow: {
        'cyber-glow': '0 0 15px rgba(6, 182, 212, 0.3)',
        'critical-glow': '0 0 15px rgba(239, 68, 68, 0.35)',
        'card-glow': '0 4px 20px -2px rgba(0, 0, 0, 0.5), 0 0 10px rgba(6, 182, 212, 0.1)'
      },
      fontFamily: {
        mono: ['Fira Code', 'JetBrains Mono', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif']
      }
    },
  },
  plugins: [],
}
