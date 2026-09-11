import httpClient from "../../../shared/services/httpClient.js";
import { env } from "../../../config/env.js";
import materialsMock from "@mocks/materials.json";

const MATERIALS_ENDPOINT = "/materials/";

/**
 * Consulta las publicaciones de materiales disponibles.
 */
export async function listMaterials({ signal } = {}) {
  if (env.useMocks) {
    return structuredClone(materialsMock.get);
  }
  const response = await httpClient.get(MATERIALS_ENDPOINT, { signal });
  return response.data;
}

/**
 * Crea una publicación de material.
 */
export async function createMaterial(material) {
  if (env.useMocks) {
    return {
      ...structuredClone(materialsMock.post),
      ...material,
      id: materialsMock.post.id ?? `mock-${Date.now()}`,
      created_at: new Date().toISOString(),
    };
  }
  const response = await httpClient.post(MATERIALS_ENDPOINT, material);
  return response.data;
}
