module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'airbnb',
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:react/jsx-runtime',
    'plugin:react-hooks/recommended',
    'plugin:jsx-a11y/recommended',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs'],
  parserOptions: { ecmaVersion: 'latest', sourceType: 'module' },
  settings: {
    react: { version: '18.2' },
    'import/resolver': {
      alias: {
        map: [
          ['@', './src'],
          ['@components', './src/components'],
          ['@assets', './src/assets'],
          ['@routes', './src/routes'],
          ['@hooks', './src/hooks'],
          ['@api', './src/api'],
          ['@context', './src/context'],
        ],
        extensions: ['.js', '.jsx']
      },
    }
  },
  plugins: ['import', 'react-refresh', 'jsx-a11y'],
  rules: {
    'no-multiple-empty-lines': ['error', { max: 2 }],
    quotes: ['error', 'single'],
    curly: ['error', 'all'],
    strict: 'off',
    'arrow-parens': 'off',
    'no-plusplus': 'off',
    'class-methods-use-this': 'off',
    'max-len': ['error', 120, 2, {
      ignoreUrls: true,
      ignoreComments: false,
      ignoreRegExpLiterals: true,
      ignoreStrings: true,
      ignoreTemplateLiterals: true,
    }],
    'import/newline-after-import': ['error', { count: 2 }],
    'import/no-extraneous-dependencies': ['error', {
      devDependencies: [ 'vite.config.js' ],
    }],
    'react/jsx-no-target-blank': 'off',
    'react/jsx-props-no-spreading': 'off',
    'react/react-in-jsx-scope': 'off',
    'react/jsx-one-expression-per-line': 'off',
    'react/destructuring-assignment': 'off',
    'jsx-a11y/anchor-is-valid': ['error', {
      components: ['Link'],
      specialLink: ['to'],
    }],
    'jsx-a11y/label-has-associated-control': ['error', {
      labelComponents: [],
      labelAttributes: [],
      controlComponents: [],
      assert: 'htmlFor',
      depth: 25,
    }],
  },
};
