/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        'parkinsans': ['Parkinsans', 'system-ui', '-apple-system', 'sans-serif'],
      },
      colors: {
        quilt: {
          primary: '#6366f1',
          secondary: '#8b5cf6',
          accent: '#06b6d4',
        },
      },
    },
  },
  plugins: [],
}
