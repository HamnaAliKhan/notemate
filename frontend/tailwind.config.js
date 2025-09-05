/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class', // ✅ toggle dark mode with 'class'
  theme: {
    extend: {
      fontFamily: {
        poppins: ['Poppins', 'sans-serif'], // 👈 added here
      },
      animation: {
        "gradient-x": "gradient-x 10s ease infinite",
      },
      keyframes: {
        "gradient-x": {
          "0%, 100%": { "background-position": "0% 50%" },
          "50%": { "background-position": "100% 50%" },
        },
      },
    },
  },
  plugins: [],
};
