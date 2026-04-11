import { defineConfig } from 'eslint'
import typescriptParser from '@typescript-eslint/parser'
import reactPlugin from 'eslint-plugin-react'
import reactHooksPlugin from 'eslint-plugin-react-hooks'
import jsxA11yPlugin from 'eslint-plugin-jsx-a11y'
import typescriptPlugin from '@typescript-eslint/eslint-plugin'

export default defineConfig({
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  parser: typescriptParser,
  parserOptions: {
    ecmaFeatures: {
      jsx: true,
    },
    ecmaVersion: 'latest',
    sourceType: 'module',
  },
  plugins: {
    '@typescript-eslint': typescriptPlugin,
    react: reactPlugin,
    'react-hooks': reactHooksPlugin,
    'jsx-a11y': jsxA11yPlugin,
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
  rules: {
    'react/react-in-jsx-scope': 'off',
    'react/prop-types': 'off',
    '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
    'no-console': ['warn', { allow: ['warn', 'error'] }],
    'jsx-a11y/no-autofocus': 'off',
    '@typescript-eslint/no-explicit-any': 'off',
  },
  ignores: ['node_modules', 'dist', 'build'],
})
