import { describe, expect, it } from "vitest";
import { getErrorMessage } from "./getErrorMessage.js";

describe("getErrorMessage", () => {
  it("usa el message del contrato del backend", () => {
    const error = {
      response: { data: { code: "INVALID_DATA", message: "Los datos enviados no son válidos" } },
    };
    expect(getErrorMessage(error)).toBe("Los datos enviados no son válidos");
  });

  it("devuelve el fallback cuando no hay detalle", () => {
    expect(getErrorMessage({}, "Error de prueba")).toBe("Error de prueba");
  });
});
