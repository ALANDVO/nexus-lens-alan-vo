import { render, screen, waitFor } from "@testing-library/react";
import DashboardPage from "../DashboardPage";

const mockFetch = vi.fn();

beforeEach(() => {
  mockFetch.mockReset();
  global.fetch = mockFetch as unknown as typeof fetch;
});

describe("DashboardPage", () => {
  it("shows loading state, then renders the plugin list from the API", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        items: [
          {
            id: 1,
            name: "typescript-lsp",
            description: "LSP plugin for TypeScript.",
            source: "anthropics/claude-plugins-official",
            plugin_type: "lsp",
            latest_score: 100,
            latest_band: "excellent",
            created_at: "2026-01-01T00:00:00Z",
            updated_at: "2026-01-01T00:00:00Z",
          },
        ],
        total: 1,
        page: 1,
        per_page: 20,
      }),
    });

    render(<DashboardPage onViewPlugin={() => {}} onNewPlugin={() => {}} />);

    expect(screen.getByText("Loading plugins…")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("typescript-lsp")).toBeInTheDocument();
    });
    expect(screen.getByText("anthropics/claude-plugins-official")).toBeInTheDocument();
  });

  it("shows empty state when no plugins are registered", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        items: [],
        total: 0,
        page: 1,
        per_page: 20,
      }),
    });

    render(<DashboardPage onViewPlugin={() => {}} onNewPlugin={() => {}} />);

    await waitFor(() => {
      expect(screen.getByText("No plugins registered yet")).toBeInTheDocument();
    });
    expect(screen.getByRole("button", { name: "New Plugin" })).toBeInTheDocument();
  });
});