module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:react/jsx-runtime',
    'plugin:react-hooks/recommended',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parserOptions: { ecmaVersion: 'latest', sourceType: 'module' },
  settings: { react: { version: '18.2' } },
  plugins: ['react-refresh'],
  rules: {
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
    'react/prop-types': 'off',
  },
  overrides: [
    {
      // Les fichiers de configuration tournent sous Node, pas dans le
      // navigateur : `__dirname` et `process` y sont légitimes.
      files: ['vite.config.js', '*.config.js'],
      env: { node: true, browser: false },
    },
    {
      // `globals: true` dans la config Vitest rend `describe`/`it`/`expect`
      // disponibles sans import ; ESLint ne le sait pas tout seul.
      files: ['**/*.test.js', '**/*.test.jsx', 'src/test/**'],
      globals: {
        describe: 'readonly',
        it: 'readonly',
        expect: 'readonly',
        vi: 'readonly',
        beforeEach: 'readonly',
        afterEach: 'readonly',
        beforeAll: 'readonly',
        afterAll: 'readonly',
      },
    },
  ],
}
