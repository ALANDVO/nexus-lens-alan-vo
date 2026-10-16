import type { ScoreBand } from "../api/types";

const LABELS: Record<ScoreBand, string> = {
  excellent: "Excellent",
  good: "Good",
  needs_review: "Needs review",
  poor: "Poor",
};

const CLASSES: Record<ScoreBand, string> = {
  excellent: "badge-excellent",
  good: "badge-good",
  needs_review: "badge-needs_review",
  poor: "badge-poor",
};

interface Props {
  score: number;
  band: ScoreBand | null;
}

export default function ScoreBadge({ score, band }: Props) {
  if (band === null) {
    return <span className="badge" style={{ color: "#94a3a5" }}>Not analyzed</span>;
  }
  return (
    <span className={`badge ${CLASSES[band]}`}>
      {score} · {LABELS[band]}
    </span>
  );
}