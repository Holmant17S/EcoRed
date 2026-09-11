import httpClient from "../../../shared/services/httpClient.js";
import { env } from "../../../config/env.js";
import requestsMock from "@mocks/requests.json";

const REQUESTS_ENDPOINT = "/requests/";

export async function listRequests({ signal } = {}) {
  if (env.useMocks) {
    return structuredClone(requestsMock.get);
  }
  const response = await httpClient.get(REQUESTS_ENDPOINT, { signal });
  return response.data;
}

export async function createRequest(payload) {
  if (env.useMocks) {
    return {
      ...structuredClone(requestsMock.post),
      ...payload,
      id: requestsMock.post.id ?? `mock-${Date.now()}`,
      created_at: new Date().toISOString(),
    };
  }
  const response = await httpClient.post(REQUESTS_ENDPOINT, payload);
  return response.data;
}
