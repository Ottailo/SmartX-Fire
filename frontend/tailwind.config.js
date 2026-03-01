/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        background: '#000000',
        terminalPanel: '#040404',
        terminalSurface: '#0B1015',
        terminalBorder: '#1A2129',
        terminalActive: '#00F2FE',
        textPrimary: '#F0F4F8',
        textSecondary: '#52667A',
        neonGreen: '#39FF14',
        neonOrange: '#FF7A00',
        neonRed: '#FF003C',
        neonPurple: '#B026FF',
        neonCyan: '#00F2FE',
      },
      fontFamily: {
        mono: ['"Space Mono"', 'monospace'],
        display: ['"Space Grotesk"', 'sans-serif'],
      },
      backgroundImage: {
        'grid-pattern': "radial-gradient(circle, #1A2129 1px, transparent 1px)",
      },
      backgroundSize: {
        'grid-size': '20px 20px',
      }
    },
  },
  plugins: [],
};
