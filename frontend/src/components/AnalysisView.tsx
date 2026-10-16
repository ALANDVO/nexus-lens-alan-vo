import type { Analysis } from "../api/types";
import ScoreBadge from "./ScoreBadge";
import SeverityBadge from "./SeverityBadge";

interface Props {
  analysis: Analysis;
}

const SEVERITY_ORDER: Record<string, number> = { fail: 0, warn: 1, pass: 2 };

export default function AnalysisView({ analysis }: Props) {
  const sorted = [...analysis.findings].sort(
    (a, b) => SEVERITY_ORDER[a.severity] - SEVERITY_ORDER[b.severity],
  );

  return (
    <div className="card">
      <div className="header">
        <div>
          <div className="score">{analysis.score}</div>
          <ScoreBadge score={analysis.score} band={analysis.band} />
        </div>
        <div style={{ fontSize: "0.8rem", color: "var(--text-dim)" }}>
          {analysis.findings.length} finding{analysis.findings.length !== 1 ? "s" : ""}
        </div>
      </div>

      {sorted.length === 0 ? (
        <div className="state">
          <div className="icon">✓</div>
          <p>No issues found. This plugin passed all conformance checks.</p>
        </div>
      ) : (
        <ul className="findings-list">
          {sorted.map((f, i) => (
            <li key={`${f.check_id}-${i}`} className={`finding-item ${f.severity}`}>
              <div className="finding-header">
                <code className="finding-check">{f.check_id}</code>
                <SeverityBadge severity={f.severity} />
              </div>
              <p className="finding-message">{f.message}</p>
              {Object.keys(f.evidence).length > 0 && (
                <pre className="finding-evidence">
                  {JSON.stringify(f.evidence, null, 2)}
                </pre>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}