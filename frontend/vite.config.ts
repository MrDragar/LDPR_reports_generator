import path from 'path';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
		const env  = loadEnv(mode, process.cwd(), '')
    return {
      server: {
        port: 5174, // Порт для dev-сервера
        host: '0.0.0.0' // Доступ с других устройств в сети
      },
      preview: {
        port: 4173 // Порт для preview-сервера (npm run preview)
      },
      define: {
				'process.env.SERVER_URL': JSON.stringify(env.SERVER_URL)
      },
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '.'),
        }
      }
    };
});
