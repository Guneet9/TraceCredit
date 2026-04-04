import { useState } from "react";

const C = {
  cream: "#EEEBDD",
  tan: "#D8B6A4",
  crimson: "#630000",
  black: "#000000",
  tanLight: "#F2E8E1",
  crimsonLight: "#8B0000",
  crimsonDim: "#3D0000",
};

const sty = {
  page: {
    fontFamily: "Georgia, serif",
    background: C.cream,
    minHeight: "100vh",
    padding: 0,
    margin: 0,
  },
  sidebar: {
    width: 220,
    background: C.black,
    minHeight: "100vh",
    padding: "2rem 0",
    flexShrink: 0,
  },
  content: {
    flex: 1,
    padding: "2rem",
    background: C.cream,
    minHeight: "100vh",
    overflowY: "auto",
  },
  card: {
    background: "#fff",
    border: `1px solid ${C.tan}`,
    borderRadius: 8,
    padding: "1.25rem",
    marginBottom: 16,
  },
  metricCard: {
    background: C.black,
    borderRadius: 8,
    padding: "1rem 1.25rem",
    flex: 1,
    minWidth: 120,
  },
  input: {
    width: "100%",
    padding: "8px 10px",
    border: `1px solid ${C.tan}`,
    borderRadius: 6,
    fontSize: 13,
    background: C.cream,
    color: C.black,
    outline: "none",
    fontFamily: "Georgia, serif",
    boxSizing: "border-box",
  },
  select: {
    width: "100%",
    padding: "8px 10px",
    border: `1px solid ${C.tan}`,
    borderRadius: 6,
    fontSize: 13,
    background: C.cream,
    color: C.black,
    outline: "none",
    fontFamily: "Georgia, serif",
  },
  btnPrimary: {
    background: C.crimson,
    color: "#fff",
    border: "none",
    borderRadius: 6,
    padding: "9px 20px",
    fontSize: 13,
    cursor: "pointer",
    fontFamily: "Georgia, serif",
    letterSpacing: "0.03em",
  },
  btnOutline: {
    background: "transparent",
    color: C.crimson,
    border: `1px solid ${C.crimson}`,
    borderRadius: 6,
    padding: "8px 18px",
    fontSize: 13,
    cursor: "pointer",
    fontFamily: "Georgia, serif",
  },
  label: {
    fontSize: 11,
    color: C.tan,
    letterSpacing: "0.08em",
    textTransform: "uppercase",
    marginBottom: 4,
    display: "block",
    fontFamily: "Georgia, serif",
  },
};

const PAGES = [
  { id: "new application", icon: "+" },
  { id: "limit history", icon: "~" },
  { id: "drift monitor", icon: "%" },
  { id: "model management", icon: "#" },
  { id: "alerts", icon: "!", count: 3 },
];

function Badge({ label, variant = "neutral" }) {
  const styles = {
    approved: { bg: "#1a3a1a", color: "#7ecf7e", border: "1px solid #3a6a3a" },
    declined: { bg: "#3a0000", color: "#ff8080", border: "1px solid #6a0000" },
    critical: { bg: C.crimson, color: "#ffcccc", border: `1px solid ${C.crimsonLight}` },
    high: { bg: "#4a1a00", color: "#ffb380", border: "1px solid #7a3a00" },
    medium: { bg: "#3a2a00", color: "#ffd980", border: "1px solid #6a5000" },
    low: { bg: "#1a2a1a", color: "#a0d0a0", border: "1px solid #3a5a3a" },
    neutral: { bg: C.tan, color: C.black, border: `1px solid ${C.tan}` },
    info: { bg: "#1a1a3a", color: "#a0b0ff", border: "1px solid #3a3a6a" },
  };
  const s = styles[variant] || styles.neutral;
  return (
    <span style={{
      fontSize: 11, padding: "3px 9px", borderRadius: 20,
      background: s.bg, color: s.color, border: s.border,
      fontWeight: 500, whiteSpace: "nowrap", letterSpacing: "0.03em",
      fontFamily: "Georgia, serif",
    }}>
      {label}
    </span>
  );
}

function MetricCard({ label, value, sub, accent }) {
  return (
    <div style={sty.metricCard}>
      <div style={{ fontSize: 11, color: C.tan, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 6 }}>{label}</div>
      <div style={{ fontSize: 24, fontWeight: 500, color: accent ? C.tan : "#fff", lineHeight: 1.1 }}>{value}</div>
      {sub && <div style={{ fontSize: 11, color: "#666", marginTop: 4 }}>{sub}</div>}
    </div>
  );
}

function SectionLabel({ children }) {
  return (
    <div style={{
      fontSize: 10, fontWeight: 500, color: C.tan,
      letterSpacing: "0.1em", textTransform: "uppercase",
      margin: "1.25rem 0 0.75rem",
      borderBottom: `1px solid ${C.tan}`,
      paddingBottom: 6,
    }}>
      {children}
    </div>
  );
}

function StepDot({ n, active, done }) {
  return (
    <div style={{
      width: 28, height: 28, borderRadius: "50%",
      display: "flex", alignItems: "center", justifyContent: "center",
      fontSize: 12, fontWeight: 500,
      background: done ? C.crimson : active ? C.tan : "transparent",
      color: done || active ? "#fff" : C.tan,
      border: `1px solid ${done ? C.crimson : active ? C.tan : "#444"}`,
      flexShrink: 0,
    }}>
      {done ? "✓" : n}
    </div>
  );
}

function NewApplicationPage() {
  const [step, setStep] = useState(1);
  const [form, setForm] = useState({
    user_id: "1001", age: "35", gender: "2", education: "2", marital_status: "1",
    current_credit_limit: "50000",
    pay_status_m1: "0", pay_status_m2: "0", pay_status_m3: "0",
    pay_status_m4: "0", pay_status_m5: "0", pay_status_m6: "0",
    bill_amt_m1: "5000", bill_amt_m2: "4500", bill_amt_m3: "5500",
    bill_amt_m4: "6000", bill_amt_m5: "5200", bill_amt_m6: "4800",
    pay_amt_m1: "2500", pay_amt_m2: "2300", pay_amt_m3: "2800",
    pay_amt_m4: "3000", pay_amt_m5: "2600", pay_amt_m6: "2400",
  });
  const [result, setResult] = useState(null);
  const f = (k, v) => setForm(p => ({ ...p, [k]: v }));

  const mockResult = {
    risk_probability: 0.18,
    recommended_limit: 61200,
    model_version: "v1",
    decision_id: 42,
    explanation: "Account shows low default risk, low card usage, clean payment history, mostly on-time payments.",
    shap: [
      { feature: "pay_status_m1", value: 0.31, dir: 1 },
      { feature: "payment_to_bill_ratio", value: 0.24, dir: 1 },
      { feature: "default_status_count", value: 0.18, dir: -1 },
      { feature: "utilization_ratio", value: 0.15, dir: -1 },
      { feature: "avg_bill_6m", value: 0.08, dir: 1 },
      { feature: "credit_limit", value: 0.04, dir: 1 },
    ],
  };

  const steps = ["applicant profile", "payment history", "decision"];

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: "2rem" }}>
        {steps.map((s, i) => (
          <div key={s} style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <StepDot n={i + 1} active={step === i + 1} done={step > i + 1} />
            <span style={{ fontSize: 13, color: step === i + 1 ? C.black : C.tan, letterSpacing: "0.02em" }}>{s}</span>
            {i < 2 && <div style={{ width: 32, height: 1, background: step > i + 1 ? C.crimson : "#444" }} />}
          </div>
        ))}
      </div>

      {step === 1 && (
        <div style={sty.card}>
          <SectionLabel>applicant profile</SectionLabel>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14, marginBottom: 16 }}>
            {[["user id", "user_id"], ["age", "age"], ["current credit limit ($)", "current_credit_limit"]].map(([label, key]) => (
              <div key={key}>
                <label style={sty.label}>{label}</label>
                <input style={sty.input} value={form[key]} onChange={e => f(key, e.target.value)} />
              </div>
            ))}
            <div>
              <label style={sty.label}>gender</label>
              <select style={sty.select} value={form.gender} onChange={e => f("gender", e.target.value)}>
                <option value="1">male</option>
                <option value="2">female</option>
              </select>
            </div>
            <div>
              <label style={sty.label}>education</label>
              <select style={sty.select} value={form.education} onChange={e => f("education", e.target.value)}>
                <option value="1">graduate school</option>
                <option value="2">university</option>
                <option value="3">high school</option>
              </select>
            </div>
            <div>
              <label style={sty.label}>marital status</label>
              <select style={sty.select} value={form.marital_status} onChange={e => f("marital_status", e.target.value)}>
                <option value="1">married</option>
                <option value="2">single</option>
                <option value="3">other</option>
              </select>
            </div>
          </div>
          <div style={{ display: "flex", justifyContent: "flex-end" }}>
            <button style={sty.btnPrimary} onClick={() => setStep(2)}>next step →</button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div style={sty.card}>
          <SectionLabel>6-month payment history</SectionLabel>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
              <thead>
                <tr style={{ background: C.cream }}>
                  {["month", "pay status", "bill amount ($)", "payment ($)"].map(h => (
                    <th key={h} style={{ textAlign: "left", padding: "8px 10px", fontWeight: 500, color: C.tan, fontSize: 11, letterSpacing: "0.07em", textTransform: "uppercase", borderBottom: `1px solid ${C.tan}` }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {[1, 2, 3, 4, 5, 6].map(m => (
                  <tr key={m} style={{ borderBottom: `1px solid ${C.cream}` }}>
                    <td style={{ padding: "6px 10px", color: C.tan, fontWeight: 500 }}>month {m}</td>
                    {[`pay_status_m${m}`, `bill_amt_m${m}`, `pay_amt_m${m}`].map(k => (
                      <td key={k} style={{ padding: "4px 10px" }}>
                        <input value={form[k]} onChange={e => f(k, e.target.value)} style={{ ...sty.input, width: 100 }} />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div style={{ fontSize: 11, color: C.tan, marginTop: 10, letterSpacing: "0.03em" }}>
            pay status: -1 = paid on time · 1+ = months delayed
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 16 }}>
            <button style={sty.btnOutline} onClick={() => setStep(1)}>← back</button>
            <button style={sty.btnPrimary} onClick={() => { setResult(mockResult); setStep(3); }}>submit application →</button>
          </div>
        </div>
      )}

      {step === 3 && result && (
        <div>
          <div style={{ background: C.crimson, borderRadius: 8, padding: "1.5rem", marginBottom: 16, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div>
              <div style={{ fontSize: 11, color: C.tan, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 4 }}>recommended credit limit</div>
              <div style={{ fontSize: 36, fontWeight: 500, color: "#fff" }}>${result.recommended_limit.toLocaleString()}</div>
              <div style={{ fontSize: 12, color: C.tan, marginTop: 4 }}>decision #{result.decision_id} · model {result.model_version}</div>
            </div>
            <div style={{ textAlign: "right" }}>
              <Badge label="approved" variant="approved" />
              <div style={{ fontSize: 11, color: C.tan, marginTop: 8 }}>risk probability</div>
              <div style={{ fontSize: 28, fontWeight: 500, color: "#fff" }}>{(result.risk_probability * 100).toFixed(1)}%</div>
            </div>
          </div>

          <div style={sty.card}>
            <SectionLabel>decision rationale</SectionLabel>
            <p style={{ fontSize: 13, color: "#444", lineHeight: 1.7, margin: 0 }}>{result.explanation}</p>
          </div>

          <div style={sty.card}>
            <SectionLabel>feature importance (SHAP)</SectionLabel>
            {result.shap.map(({ feature, value, dir }) => (
              <div key={feature} style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 10 }}>
                <div style={{ fontSize: 12, color: "#444", width: 200, flexShrink: 0, fontFamily: "monospace" }}>{feature}</div>
                <div style={{ flex: 1, height: 10, background: C.cream, borderRadius: 5, overflow: "hidden", border: `1px solid ${C.tan}` }}>
                  <div style={{
                    width: `${value * 100 / 0.31 * 100}%`,
                    height: "100%",
                    background: dir > 0 ? "#2d6a2d" : C.crimson,
                    borderRadius: 5,
                  }} />
                </div>
                <div style={{ fontSize: 12, fontWeight: 500, color: dir > 0 ? "#2d6a2d" : C.crimson, width: 40, textAlign: "right" }}>
                  {dir > 0 ? "+" : "-"}{value.toFixed(2)}
                </div>
              </div>
            ))}
          </div>

          <div style={{ display: "flex", gap: 10 }}>
            <button style={sty.btnOutline} onClick={() => { setStep(1); setResult(null); }}>new application</button>
            <button style={sty.btnPrimary}>view full audit trail →</button>
          </div>
        </div>
      )}
    </div>
  );
}

function LimitHistoryPage() {
  const history = [
    { id: 38, date: "2026-03-01", limit: 58400, prev: 52000, delta: 6400, drift: false, model: "v1" },
    { id: 29, date: "2026-02-01", limit: 52000, prev: 55000, delta: -3000, drift: true, model: "v1" },
    { id: 21, date: "2026-01-01", limit: 55000, prev: 55000, delta: 0, drift: false, model: "v1" },
    { id: 14, date: "2025-12-01", limit: 55000, prev: null, delta: null, drift: false, model: "v1" },
  ];

  return (
    <div>
      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
        <MetricCard label="current limit" value="$58,400" sub="as of march 2026" />
        <MetricCard label="total decisions" value="4" sub="since dec 2025" />
        <MetricCard label="drift events" value="1" accent sub="feb 2026" />
      </div>

      <div style={sty.card}>
        <SectionLabel>credit limit history — user 1001</SectionLabel>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr>
              {["date", "limit", "change ($)", "drift", "model", "audit"].map(h => (
                <th key={h} style={{ textAlign: "left", padding: "8px 10px", fontWeight: 500, color: C.tan, fontSize: 11, letterSpacing: "0.07em", textTransform: "uppercase", borderBottom: `1px solid ${C.tan}` }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {history.map((h, i) => (
              <tr key={h.id} style={{ background: i % 2 === 0 ? "#fff" : C.cream, borderBottom: `1px solid ${C.cream}` }}>
                <td style={{ padding: "12px 10px", color: "#666" }}>{h.date}</td>
                <td style={{ padding: "12px 10px", fontWeight: 500, color: C.black }}>${h.limit.toLocaleString()}</td>
                <td style={{ padding: "12px 10px" }}>
                  {h.delta !== null ? (
                    <span style={{ color: h.delta > 0 ? "#2d6a2d" : h.delta < 0 ? C.crimson : "#999", fontWeight: 500 }}>
                      {h.delta > 0 ? "+" : ""}{h.delta !== 0 ? h.delta.toLocaleString() : "—"}
                    </span>
                  ) : "—"}
                </td>
                <td style={{ padding: "12px 10px" }}>
                  {h.drift ? <Badge label="detected" variant="high" /> : <span style={{ color: "#999", fontSize: 12 }}>none</span>}
                </td>
                <td style={{ padding: "12px 10px" }}><Badge label={h.model} variant="info" /></td>
                <td style={{ padding: "12px 10px" }}>
                  <button style={{ ...sty.btnOutline, padding: "4px 10px", fontSize: 11 }}>view →</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function DriftMonitorPage() {
  const features = [
    { name: "credit_limit", psi: 0.04, ks_p: 0.31, mean_diff: 8.2, severity: "low", drifted: false },
    { name: "pay_status_m1", psi: 0.14, ks_p: 0.02, mean_diff: 24.1, severity: "medium", drifted: true },
    { name: "bill_amt_m1", psi: 0.07, ks_p: 0.18, mean_diff: 12.4, severity: "low", drifted: false },
    { name: "pay_amt_m1", psi: 0.28, ks_p: 0.01, mean_diff: 31.7, severity: "high", drifted: true },
    { name: "age", psi: 0.02, ks_p: 0.61, mean_diff: 3.1, severity: "low", drifted: false },
  ];

  return (
    <div>
      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
        <MetricCard label="features monitored" value="5" />
        <MetricCard label="drifted" value="2" accent sub="pay_status, pay_amt" />
        <MetricCard label="last scan" value="today" sub="monthly batch" />
      </div>

      <div style={sty.card}>
        <SectionLabel>feature drift — three-method detection</SectionLabel>
        <div style={{ fontSize: 11, color: C.tan, marginBottom: 12, letterSpacing: "0.03em" }}>
          KS test (p &lt; 0.05) · PSI (&gt; 0.10) · mean difference (&gt; 20%) — any one triggers drift
        </div>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13, tableLayout: "fixed" }}>
          <thead>
            <tr>
              {["feature", "psi", "ks p-value", "mean diff", "severity", "status"].map(h => (
                <th key={h} style={{ textAlign: "left", padding: "8px 10px", fontWeight: 500, color: C.tan, fontSize: 11, letterSpacing: "0.07em", textTransform: "uppercase", borderBottom: `1px solid ${C.tan}` }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {features.map((feat, i) => (
              <tr key={feat.name} style={{ background: i % 2 === 0 ? "#fff" : C.cream }}>
                <td style={{ padding: "12px 10px", fontFamily: "monospace", fontSize: 12, color: C.black }}>{feat.name}</td>
                <td style={{ padding: "12px 10px", color: feat.psi > 0.1 ? C.crimson : "#666", fontWeight: feat.psi > 0.1 ? 500 : 400 }}>{feat.psi.toFixed(2)}</td>
                <td style={{ padding: "12px 10px", color: feat.ks_p < 0.05 ? C.crimson : "#666", fontWeight: feat.ks_p < 0.05 ? 500 : 400 }}>{feat.ks_p.toFixed(2)}</td>
                <td style={{ padding: "12px 10px", color: feat.mean_diff > 20 ? C.crimson : "#666", fontWeight: feat.mean_diff > 20 ? 500 : 400 }}>{feat.mean_diff.toFixed(1)}%</td>
                <td style={{ padding: "12px 10px" }}><Badge label={feat.severity} variant={feat.severity} /></td>
                <td style={{ padding: "12px 10px" }}>
                  {feat.drifted ? <Badge label="drifted" variant="high" /> : <span style={{ fontSize: 12, color: "#999" }}>stable</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={sty.card}>
        <SectionLabel>fairness — cohort comparison</SectionLabel>
        {[
          { c1: "income_low", c2: "income_high", gap: 18400, threshold: 2000, sev: "critical" },
          { c1: "age_20-30", c2: "age_50-60", gap: 3200, threshold: 2000, sev: "medium" },
        ].map((v, i) => (
          <div key={i} style={{
            display: "flex", alignItems: "center", gap: 12, padding: "14px 0",
            borderBottom: i === 0 ? `1px solid ${C.cream}` : "none"
          }}>
            <Badge label={v.sev} variant={v.sev} />
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: 13, color: C.black, fontWeight: 500, marginBottom: 2 }}>
                {v.c1} vs {v.c2}
              </div>
              <div style={{ fontSize: 11, color: C.tan }}>
                avg limit gap: ${v.gap.toLocaleString()} · threshold ${v.threshold.toLocaleString()}
              </div>
            </div>
            <div style={{ fontSize: 16, fontWeight: 500, color: C.crimson }}>${v.gap.toLocaleString()}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ModelManagementPage() {
  const [active, setActive] = useState("v1");
  const models = [
    { version: "v1", type: "LogisticRegression", accuracy: 0.7461, roc_auc: 0.755, f1: 0.8039, created: "2025-12-15" },
    { version: "v2", type: "RandomForest (150)", accuracy: 0.9814, roc_auc: 0.9978, f1: 0.9806, created: "2026-01-20" },
  ];

  return (
    <div>
      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
        <MetricCard label="registered" value="2" sub="model versions" />
        <MetricCard label="active model" value={active} sub="currently serving" />
        <MetricCard label="accuracy" value={active === "v1" ? "74.6%" : "98.1%"} accent sub="on test set" />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        {models.map(m => (
          <div key={m.version} style={{
            ...sty.card,
            marginBottom: 0,
            borderColor: m.version === active ? C.crimson : C.tan,
            borderWidth: m.version === active ? 2 : 1,
          }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
              <div style={{ fontSize: 18, fontWeight: 500, color: C.black }}>{m.version}</div>
              <div style={{ display: "flex", gap: 6 }}>
                {m.version === active && <Badge label="active" variant="approved" />}
              </div>
            </div>
            <div style={{ fontSize: 12, color: C.tan, marginBottom: 12, letterSpacing: "0.03em" }}>{m.type}</div>
            {[["accuracy", `${(m.accuracy * 100).toFixed(1)}%`], ["roc-auc", m.roc_auc.toFixed(4)], ["f1 score", m.f1.toFixed(4)], ["trained", m.created]].map(([k, v]) => (
              <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "6px 0", borderBottom: `1px solid ${C.cream}`, fontSize: 13 }}>
                <span style={{ color: "#666" }}>{k}</span>
                <span style={{ fontWeight: 500, color: C.black }}>{v}</span>
              </div>
            ))}
            {m.version !== active && (
              <button style={{ ...sty.btnPrimary, width: "100%", marginTop: 14 }} onClick={() => setActive(m.version)}>
                activate {m.version}
              </button>
            )}
            {m.version === active && (
              <div style={{ marginTop: 14, padding: "8px 12px", background: C.cream, borderRadius: 6, fontSize: 12, color: C.tan, textAlign: "center" }}>
                serving live traffic
              </div>
            )}
          </div>
        ))}
      </div>

      <div style={sty.card}>
        <SectionLabel>metric comparison</SectionLabel>
        {[["accuracy", 0.7461, 0.9814], ["roc-auc", 0.755, 0.9978], ["f1 score", 0.8039, 0.9806]].map(([metric, v1, v2]) => (
          <div key={metric} style={{ marginBottom: 14 }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 6 }}>
              <span style={{ color: "#444", letterSpacing: "0.03em" }}>{metric}</span>
              <span style={{ color: C.tan }}>v1: {v1.toFixed(4)} · v2: {v2.toFixed(4)}</span>
            </div>
            <div style={{ position: "relative", height: 10, background: C.cream, borderRadius: 5, border: `1px solid ${C.tan}` }}>
              <div style={{ position: "absolute", width: `${v1 * 100}%`, height: "100%", background: C.tan, borderRadius: 5 }} />
              <div style={{ position: "absolute", width: `${v2 * 100}%`, height: "100%", background: C.crimson, borderRadius: 5, opacity: 0.85 }} />
            </div>
          </div>
        ))}
        <div style={{ fontSize: 11, color: C.tan, letterSpacing: "0.03em" }}>tan = v1 · crimson = v2</div>
      </div>
    </div>
  );
}

function AlertsPage() {
  const [alerts, setAlerts] = useState([
    { id: 3, type: "fairness", severity: "critical", message: "Fairness violation: income_low vs income_high on avg_limit (gap=$18,400, threshold=$2,000)", time: "2 hours ago" },
    { id: 2, type: "drift", severity: "high", message: "Credit limit drift for user 892: $42,000 → $61,000 (delta=$19,000)", time: "5 hours ago" },
    { id: 1, type: "drift", severity: "medium", message: "Feature drift detected: pay_amt_m1 (PSI=0.28, KS p=0.01)", time: "1 day ago" },
  ]);

  const resolve = (id) => setAlerts(a => a.filter(x => x.id !== id));

  const sevBorder = { critical: C.crimson, high: "#7a3a00", medium: "#6a5000", low: "#3a5a3a" };

  return (
    <div>
      <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap" }}>
        <MetricCard label="active alerts" value={alerts.length} />
        <MetricCard label="critical" value={alerts.filter(a => a.severity === "critical").length} accent sub="needs action" />
        <MetricCard label="high" value={alerts.filter(a => a.severity === "high").length} sub="review soon" />
        <MetricCard label="medium" value={alerts.filter(a => a.severity === "medium").length} sub="monitor" />
      </div>

      {alerts.length === 0 && (
        <div style={{ ...sty.card, textAlign: "center", padding: "3rem", color: C.tan }}>
          no active alerts
        </div>
      )}

      {alerts.map(a => (
        <div key={a.id} style={{
          ...sty.card,
          borderLeft: `4px solid ${sevBorder[a.severity] || C.tan}`,
          borderRadius: "0 8px 8px 0",
          display: "flex", alignItems: "flex-start", gap: 14,
        }}>
          <div style={{ paddingTop: 2 }}><Badge label={a.severity} variant={a.severity} /></div>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 13, color: C.black, lineHeight: 1.6, marginBottom: 4 }}>{a.message}</div>
            <div style={{ fontSize: 11, color: C.tan, letterSpacing: "0.03em" }}>
              {a.type} · {a.time}
            </div>
          </div>
          <button style={{ ...sty.btnOutline, padding: "5px 12px", fontSize: 11, flexShrink: 0 }} onClick={() => resolve(a.id)}>
            resolve
          </button>
        </div>
      ))}
    </div>
  );
}

export default function App() {
  const [page, setPage] = useState("new application");

  const pageMap = {
    "new application": <NewApplicationPage />,
    "limit history": <LimitHistoryPage />,
    "drift monitor": <DriftMonitorPage />,
    "model management": <ModelManagementPage />,
    "alerts": <AlertsPage />,
  };

  const titles = {
    "new application": { title: "new application", sub: "submit a credit limit request" },
    "limit history": { title: "limit history", sub: "track changes over time" },
    "drift monitor": { title: "drift monitor", sub: "statistical distribution checks" },
    "model management": { title: "model management", sub: "versions, metrics, activation" },
    "alerts": { title: "alerts", sub: "active violations and drift events" },
  };

  const t = titles[page];

  return (
    <div style={{ display: "flex", minHeight: "100vh", fontFamily: "Georgia, serif" }}>
      <div style={sty.sidebar}>
        <div style={{ padding: "0 1.5rem 2rem", borderBottom: "1px solid #222" }}>
          <div style={{ fontSize: 16, fontWeight: 500, color: "#fff", letterSpacing: "0.05em" }}>TraceCredit</div>
          <div style={{ fontSize: 11, color: "#555", marginTop: 2, letterSpacing: "0.05em" }}>credit monitoring</div>
        </div>

        <nav style={{ padding: "1rem 0" }}>
          {PAGES.map(p => {
            const isActive = page === p.id;
            return (
              <div
                key={p.id}
                onClick={() => setPage(p.id)}
                style={{
                  display: "flex", alignItems: "center", justifyContent: "space-between",
                  padding: "10px 1.5rem",
                  cursor: "pointer",
                  background: isActive ? C.crimson : "transparent",
                  borderLeft: isActive ? `3px solid ${C.tan}` : "3px solid transparent",
                  transition: "background 0.15s",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <span style={{ fontSize: 13, color: isActive ? "#fff" : "#666", width: 16, textAlign: "center" }}>{p.icon}</span>
                  <span style={{ fontSize: 13, color: isActive ? "#fff" : "#888", letterSpacing: "0.03em" }}>{p.id}</span>
                </div>
                {p.count && (
                  <span style={{ fontSize: 10, background: C.crimson, color: "#fff", padding: "2px 6px", borderRadius: 10, border: isActive ? "1px solid rgba(255,255,255,0.3)" : "none" }}>
                    {p.count}
                  </span>
                )}
              </div>
            );
          })}
        </nav>

        <div style={{ position: "absolute", bottom: "1.5rem", left: "1.5rem", right: "1.5rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "10px 12px", background: "#111", borderRadius: 8 }}>
            <div style={{ width: 7, height: 7, borderRadius: "50%", background: "#2d6a2d", flexShrink: 0 }} />
            <div>
              <div style={{ fontSize: 11, color: "#aaa" }}>api connected</div>
              <div style={{ fontSize: 10, color: "#555" }}>model v1 active</div>
            </div>
          </div>
        </div>
      </div>

      <div style={sty.content}>
        <div style={{ marginBottom: "1.75rem" }}>
          <h1 style={{ fontSize: 22, fontWeight: 500, color: C.black, margin: 0, letterSpacing: "0.02em" }}>{t.title}</h1>
          <p style={{ fontSize: 13, color: C.tan, margin: "4px 0 0", letterSpacing: "0.03em" }}>{t.sub}</p>
        </div>

        {pageMap[page]}
      </div>
    </div>
  );
}
