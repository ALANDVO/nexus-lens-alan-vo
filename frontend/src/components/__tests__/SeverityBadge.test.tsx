import { render, screen } from "@testing-library/react";
import SeverityBadge from "../SeverityBadge";

describe("SeverityBadge", () => {
  it("renders 'Pass' with the green class for pass severity", () => {
    render(<SeverityBadge severity="pass" />);
    const badge = screen.getByText("Pass");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass("badge-pass");
  });

  it("renders 'Warning' with the amber class for warn severity", () => {
    render(<SeverityBadge severity="warn" />);
    const badge = screen.getByText("Warning");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass("badge-warn");
  });

  it("renders 'Fail' with the red class for fail severity", () => {
    render(<SeverityBadge severity="fail" />);
    const badge = screen.getByText("Fail");
    expect(badge).toBeInTheDocument();
    expect(badge).toHaveClass("badge-fail");
  });
});