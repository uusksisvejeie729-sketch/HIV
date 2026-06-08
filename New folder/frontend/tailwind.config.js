/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        primary: { DEFAULT: '#7c3aed', dark: '#5b21b6', light: '#a78bfa' },
        accent: '#06b6d4',
      },
    },
  },
  plugins: [],
}
