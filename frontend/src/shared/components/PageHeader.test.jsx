import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import PageHeader from "./PageHeader.jsx";

describe("PageHeader", () => {
  it("renderiza el título principal", () => {
    render(
      <PageHeader
        id="companies-title"
        title="Empresas"
        subtitle="Listado del usuario"
      />,
    );

    expect(screen.getByRole("heading", { name: "Empresas" })).toBeTruthy();
    expect(screen.getByText("Listado del usuario")).toBeTruthy();
  });
});
