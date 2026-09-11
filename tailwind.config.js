/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ivory: '#F7F3EA',
        ink: {
          DEFAULT: '#1C1B19',
          light: '#2D2C2A',
          muted: '#5A5854',
          subtle: '#E8E4DA'
        },
        brass: {
          DEFAULT: '#C08A2E',
          hover: '#A67424',
          light: '#F4E8D0',
        },
        forest: {
          DEFAULT: '#2F5233',
          hover: '#244027',
          light: '#E3EBE4',
        },
        brick: {
          DEFAULT: '#A34A3E',
          hover: '#873B30',
          light: '#F7EAE8',
        }
      },
      fontFamily: {
        serif: ['"Source Serif 4"', 'Georgia', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
