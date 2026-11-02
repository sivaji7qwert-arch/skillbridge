/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef4ff",
          100: "#d9e6ff",
          500: "#2f5fdd",
          600: "#254dc0",
          700: "#1d3d9a",
          900: "#122764",
        },
      },
    },
  },
  plugins: [],
}
