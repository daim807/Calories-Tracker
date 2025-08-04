/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // ✅ important!
  content: [
    
    './templates/**/*.html',
    './**/templates/**/*.html',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
