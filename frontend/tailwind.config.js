/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: ['selector', '[data-theme="dark"]'],
  theme: {
    extend: {
      colors: {
        gray: {
          50: 'var(--surface-2)',
          100: 'var(--surface-2)',
          200: 'var(--border)',
          300: 'var(--border-strong)',
          400: 'var(--ink-faint)',
          500: 'var(--ink-faint)',
          600: 'var(--ink-soft)',
          700: 'var(--ink-soft)',
          800: 'var(--ink)',
          900: 'var(--ink)',
        },
        blue: {
          50: 'var(--brand-soft)',
          200: 'color-mix(in srgb, var(--brand) 30%, transparent)',
          500: 'var(--brand)',
          600: 'var(--brand-strong)',
        },
        indigo: {
          50: 'var(--brand-soft)',
          200: 'color-mix(in srgb, var(--brand) 30%, transparent)',
          500: 'var(--brand)',
          600: 'var(--brand-strong)',
        },
        green: {
          50: 'var(--ok-soft)',
          200: 'color-mix(in srgb, var(--ok) 30%, transparent)',
          500: 'var(--ok)',
          600: 'var(--ok-text)',
        },
        red: {
          50: 'var(--danger-soft)',
          200: 'color-mix(in srgb, var(--danger) 30%, transparent)',
          800: 'var(--danger)',
        },
        purple: {
          50: 'var(--quiz-soft)',
          200: 'color-mix(in srgb, var(--quiz) 30%, transparent)',
          600: 'var(--quiz)',
        },
        yellow: {
          50: 'var(--warn-soft)',
          200: 'color-mix(in srgb, var(--warn) 30%, transparent)',
        },
      },
      backgroundColor: {
        white: 'var(--surface)',
      },
      textColor: {
        white: '#ffffff',
      },
      borderColor: {
        DEFAULT: 'var(--border)',
      },
    },
  },
  plugins: [],
};
