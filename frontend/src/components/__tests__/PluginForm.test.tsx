import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import PluginForm from "../PluginForm";

describe("PluginForm", () => {
  it("shows validation error when required fields are empty", async () => {
    const user = userEvent.setup();
    render(<PluginForm onSubmit={() => {}} />);

    await user.click(screen.getByText("Register Plugin"));

    expect(screen.getByText("Name is required")).toBeInTheDocument();
    expect(screen.getByText("Description is required")).toBeInTheDocument();
    expect(screen.getByText("Source is required")).toBeInTheDocument();
  });

  it("shows source format error for invalid owner/repo", async () => {
    const user = userEvent.setup();
    render(<PluginForm onSubmit={() => {}} />);

    await user.type(screen.getByPlaceholderText("e.g. typescript-lsp"), "my-plugin");
    await user.type(
      screen.getByPlaceholderText("What does this plugin do?"),
      "A plugin description",
    );
    await user.type(screen.getByPlaceholderText("owner/repo"), "invalid-no-slash");
    await user.click(screen.getByText("Register Plugin"));

    expect(
      screen.getByText(/Use owner\/repo format/),
    ).toBeInTheDocument();
  });

  it("submits valid data with an auto-generated manifest", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();
    render(<PluginForm onSubmit={onSubmit} />);

    await user.type(screen.getByPlaceholderText("e.g. typescript-lsp"), "my-lsp");
    await user.type(
      screen.getByPlaceholderText("What does this plugin do?"),
      "Language server plugin for MyLang.",
    );
    await user.type(screen.getByPlaceholderText("owner/repo"), "owner/my-lsp");
    await user.click(screen.getByText("Register Plugin"));

    expect(onSubmit).toHaveBeenCalledTimes(1);
    const submitted = onSubmit.mock.calls[0][0];
    expect(submitted.name).toBe("my-lsp");
    expect(submitted.plugin_type).toBe("lsp");
    expect(submitted.source).toBe("owner/my-lsp");
    // Manifest auto-generated with lspConfig for LSP plugins.
    expect(submitted.manifest.config).toHaveProperty("lspServers");
    expect(submitted.manifest.config).toHaveProperty("lspConfig");
  });
});