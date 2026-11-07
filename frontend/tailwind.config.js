/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        campus: {
          bg: '#0a0d17',
          card: '#111726',
          border: '#1f293d',
          accent: '#6366f1',
          accentHover: '#4f46e5',
          secondary: '#8b5cf6',
        }
      }
    },
  },
  plugins: [],
}
