import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';


// eslint-disable-next-line no-underscore-dangle
const __dirname = dirname(fileURLToPath(import.meta.url));

export default defineConfig(({ mode }) => {
  const isProduction = mode === 'production';

  return ({
    base: '/static/uni_bot/',
    plugins: [
      react(),
    ],
    build: {
      outDir: 'dist/uni_bot',
      sourcemap: !isProduction,
      rollupOptions: {
        output: {
          entryFileNames: 'bundle.js',
          assetFileNames: '[name][extname]',
        },
      },
    },
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
        '@components': resolve(__dirname, 'src/components'),
        '@assets': resolve(__dirname, 'src/assets'),
        '@routes': resolve(__dirname, 'src/routes'),
        '@hooks': resolve(__dirname, 'src/hooks'),
        '@api': resolve(__dirname, 'src/api'),
        '@context': resolve(__dirname, 'src/context'),
      },
    },
    cacheDir: 'node_modules/.vite_cache',
  });
});
