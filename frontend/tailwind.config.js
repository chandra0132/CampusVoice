/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        monsoon: {
          ivory: '#F3EFE5',      // Primary background
          ink: '#171B1A',        // Primary text
          forest: '#174B43',     // Brand colour
          marigold: '#E8B44A',   // Primary accent
          terracotta: '#C86F55', // Secondary accent
          sage: '#DCE5DB',       // Secondary surface
          card: '#FFFFFF',       // Card background
          grey: '#77766F',       // Muted text
          stone: '#DED9CE',      // Borders
          forestDark: '#0F342E',
          forestLight: '#1E5E54',
          marigoldHover: '#D49E34',
          terracottaDark: '#B25A42',
        }
      },
      fontFamily: {
        serif: ['"DM Serif Display"', '"Playfair Display"', 'Georgia', 'serif'],
        sans: ['Manrope', 'Inter', '"Noto Sans Devanagari"', '"Noto Sans Telugu"', 'sans-serif'],
        devanagari: ['"Noto Sans Devanagari"', 'sans-serif'],
        telugu: ['"Noto Sans Telugu"', 'sans-serif'],
      },
      boxShadow: {
        'editorial': '0 4px 20px -2px rgba(23, 75, 67, 0.08), 0 2px 6px -1px rgba(23, 75, 67, 0.04)',
        'editorial-lg': '0 12px 32px -4px rgba(23, 75, 67, 0.12), 0 4px 12px -2px rgba(23, 75, 67, 0.06)',
        'marigold-glow': '0 0 24px rgba(232, 180, 74, 0.35)',
      }
    },
  },
  plugins: [],
}
