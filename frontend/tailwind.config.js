/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        aviation: {
          dark: '#0B132B',
          navy: '#1C2541',
          slate: '#3A506B',
          accent: '#0072CE',
          cyan: '#5BC0BE',
          warning: '#F59E0B',
          danger: '#EF4444',
          success: '#10B981',
          card: '#131D38',
          cardHover: '#1B2A50',
          border: '#2A3B60'
        }
      }
    },
  },
  plugins: [],
}
