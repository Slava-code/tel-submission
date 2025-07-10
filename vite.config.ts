import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: {
        main: './index.html',
        'youtube-filter': './src/youtube-filter.ts'
      },
      output: {
        entryFileNames: (chunkInfo) => {
          return chunkInfo.name === 'youtube-filter' ? 'src/youtube-filter.js' : 'assets/[name]-[hash].js'
        }
      }
    }
  }
})
