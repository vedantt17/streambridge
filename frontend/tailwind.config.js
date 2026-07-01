/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#09111f",
        panel: "#0f1d2f",
        line: "rgba(226, 232, 240, 0.14)",
        cyan: "#20d3ee"
      },
      fontFamily: {
        sans: ["Manrope", "Segoe UI", "system-ui", "sans-serif"],
        display: ["Instrument Serif", "Georgia", "serif"]
      }
    }
  },
  plugins: []
};
