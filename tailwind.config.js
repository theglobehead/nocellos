/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./apps/**/*.{js,jsx,ts,tsx}', './libs/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        'blue-dark-500': '#02050D',
        'blue-dark-400': '#10131C',
        'blue-dark-300': '#202B49',
        'blue-light-100': '#DCDCE4',
        'green-light-100': '#A9EA3E',
        'red-light-100': '#EA3E3E',
        'orange-200': '#EA7644',
      },
      fontFamily: {
        poppins: 'Poppins',
        inter: 'Inter',
      },
    },
  },
  plugins: [],
};
