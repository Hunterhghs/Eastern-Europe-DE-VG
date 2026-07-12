import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: '/Eastern-Europe-DE-VG/',
  build: {
    outDir: 'docs',
    assetsDir: 'assets',
  },
});
