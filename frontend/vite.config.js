import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

/**
 * Configuración de Vite.
 *
 * El plugin oficial de React habilita la transformación de JSX y la
 * actualización rápida de componentes durante el desarrollo.
 * `@mocks` apunta a la carpeta raíz `mocks/` (rúbrica + json-server).
 */
export default defineConfig({
  plugins: [react()],
  esbuild: {
    jsx: "automatic",
  },
  resolve: {
    alias: {
      "@mocks": fileURLToPath(new URL("../mocks", import.meta.url)),
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
  },
});
