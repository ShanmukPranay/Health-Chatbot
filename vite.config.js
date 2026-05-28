import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',  // Allows network access - CRITICAL for sharing
    port: 5173,
    strictPort: true,  // Keeps the port fixed
    allowedHosts: [
      '10.123.26.31',  // Your IP address
      'localhost',
      '.ngrok.io',     // If you use ngrok
      '.onrender.com'  // If you deploy to render
    ]
  }
})