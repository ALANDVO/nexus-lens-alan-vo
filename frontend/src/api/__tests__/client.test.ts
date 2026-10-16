import { api, ApiError } from "../client";

const mockFetch = vi.fn();

beforeEach(() => {
  mockFetch.mockReset();
  global.fetch = mockFetch as unknown as typeof fetch;
});

describe("api client", () => {
  it("listPlugins sends GET to /api/v1/plugins with query params", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ items: [], total: 0, page: 1, per_page: 20 }),
    });

    await api.listPlugins({ search: "typescript", page: 2, per_page: 10 });

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/plugins?search=typescript&page=2&per_page=10",
      expect.objectContaining({ headers: expect.any(Object) }),
    );
  });

  it("createPlugin sends POST with JSON body", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: 1, name: "test", description: "desc", source: "owner/repo",
        plugin_type: "lsp", manifest: {}, latest_score: null, latest_band: null,
        created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z",
      }),
    });

    await api.createPlugin({
      name: "test",
      description: "desc",
      source: "owner/repo",
      plugin_type: "lsp",
      manifest: { name: "test", source: "owner/repo" },
    });

    expect(mockFetch).toHaveBeenCalledWith(
      "/api/v1/plugins",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          name: "test",
          description: "desc",
          source: "owner/repo",
          plugin_type: "lsp",
          manifest: { name: "test", source: "owner/repo" },
        }),
      }),
    );
  });

  it("throws ApiError with detail on non-OK response", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 409,
      json: async () => ({ detail: "Plugin 'test' is already registered." }),
    });

    await expect(api.createPlugin({
      name: "test", description: "d", source: "o/r",
      plugin_type: "other", manifest: {},
    })).rejects.toThrow(ApiError);
  });
});