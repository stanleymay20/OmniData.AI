/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        scroll: {
          light: '#E9E6F0',    // Breath White
          gold: '#FAD643',      // Rain Gold
          blue: '#5AC8FA',      // Breath Blue
          purple: '#6B47DC',    // Scroll Purple
          black: '#1B1B1F',     // Scroll Night
          crimson: '#D72638',   // Scroll Flame
        }
      },
      animation: {
        'scroll-spin': 'scroll-spin 2s linear infinite',
        'scroll-pulse': 'scroll-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        'scroll-spin': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        'scroll-pulse': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
      },
    },
  },
  plugins: [],
} 