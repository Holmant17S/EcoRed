import httpClient from "../../../shared/services/httpClient.js";
import { env } from "../../../config/env.js";
import companiesMock from "@mocks/companies.json";

const COMPANIES_ENDPOINT = "/companies/";

/**
 * Consulta las empresas visibles para el usuario autenticado.
 */
export async function listCompanies({ signal } = {}) {
  if (env.useMocks) {
    return structuredClone(companiesMock.get);
  }
  const response = await httpClient.get(COMPANIES_ENDPOINT, { signal });
  return response.data;
}

/**
 * Crea una empresa mediante el contrato actual del backend.
 */
export async function createCompany(company) {
  if (env.useMocks) {
    return {
      ...structuredClone(companiesMock.post),
      ...company,
      id: companiesMock.post.id ?? `mock-${Date.now()}`,
      created_at: new Date().toISOString(),
    };
  }
  const response = await httpClient.post(COMPANIES_ENDPOINT, company);
  return response.data;
}
