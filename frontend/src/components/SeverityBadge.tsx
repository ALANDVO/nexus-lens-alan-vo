import type { Severity } from "../api/types";

const LABELS: Record<Severity, string> = {
  pass: "Pass",
  warn: "Warning",
  fail: "Fail",
};

const CLASSES: Record<Severity, string> = {
  pass: "badge-pass",
  warn: "badge-warn",
  fail: "badge-fail",
};

export default function SeverityBadge({ severity }: { severity: Severity }) {
  return <span className={`badge ${CLASSES[severity]}`}>{LABELS[severity]}</span>;
}