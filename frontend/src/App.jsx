import { useState, useEffect, useCallback } from "react";

const API_BASE = "https://tracecredit.onrender.com";

async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

const C = {
  cream: "#EEEBDD",
  tan: "#D8B6A4",
  crimson: "#630000",
  black: "#000000",
};

const sty = {
  sidebar: { width: 220, background: C.black, minHeight: "100vh", padding: "2rem 0", flexShrink: 0 },
  content: { flex: 1, padding: "2rem", background: C.cream, minHeight: "100vh" },
  card: { background: "#fff", border: `1px solid ${C.tan}`, borderRadius: 8, padding: "1.25rem", marginBottom: 16 },
  metricCard: { background: C.black, borderRadius: 8, padding: "1rem 1.25rem", flex: 1, minWidth: 120 },
  input: { width: "100%", padding: "8px 10px", border: `1px solid ${C.tan}`, borderRadius: 6, fontSize: 13, background: C.cream, color: C.black, fontFamily: "Georgia, serif", boxSizing: "border-box" },
  select: { width: "100%", padding: "8px 10px", border: `1px solid ${C.tan}`, borderRadius: 6, fontSize: 13, background: C.cream, color: C.black, fontFamily: "Georgia, serif" },
  btnPrimary: { background: C.crimson, color: "#fff", border: "none", borderRadius: 6, padding: "9px 20px", fontSize: 13, cursor: "pointer", fontFamily: "Georgia, serif" },
  btnOutline: { background: "transparent", color: C.crimson, border: `1px solid ${C.crimson}`, borderRadius: 6, padding: "8px 18px", fontSize: 13, cursor: "pointer", fontFamily: "Georgia, serif" },
  label: { fontSize: 11, color: C.tan, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 4, display: "block" },
  error: { background: "#FCEBEB", border: "1px solid #A32D2D", borderRadius: 6, padding: "10px 14px", fontSize: 13, color: "#791F1F", marginBottom: 12 },
  success: { background: "#EAF3DE", border: "1px solid #3B6D11", borderRadius: 6, padding: "10px 14px", fontSize: 13, color: "#27500A", marginBottom: 12 },
};

const PAGES = [
  { id: "new application", icon: "+" },
  { id: "limit history", icon: "~" },
  { id: "drift monitor", icon: "%" },
  { id: "model management", icon: "#" },
  { id: "alerts", icon: "!" },
];

function Badge({ label, variant = "neutral" }) {
  const styles = {
    approved: { bg: "#1a3a1a", color: "#7ecf7e", border: "1px solid #3a6a3a" },
    declined: { bg: "#3a0000", color: "#ff8080", border: "1px solid #6a0000" },
    critical: { bg: C.crimson, color: "#ffcccc", border: "1px solid #8B0000" },
    high: { bg: "#4a1a00", color: "#ffb380", border: "1px solid #7a3a00" },
    medium: { bg: "#3a2a00", color: "#ffd980", border: "1px solid #6a5000" },
    low: { bg: "#1a2a1a", color: "#a0d0a0", border: "1px solid #3a5a3a" },
    neutral: { bg: C.tan, color: C.black, border: `1px solid ${C.tan}` },
    info: { bg: "#1a1a3a", color: "#a0b0ff", border: "1px solid #3a3a6a" },
  };
  const s = styles[variant] || styles.neutral;
  return (
    <span style={{ fontSize: 11, padding: "3px 9px", borderRadius: 20, background: s.bg, color: s.color, border: s.border, fontWeight: 500, whiteSpace: "nowrap", fontFamily: "Georgia, serif" }}>
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
    <div style={{ fontSize: 10, fontWeight: 500, color: C.tan, letterSpacing: "0.1em", textTransform: "uppercase", margin: "1.25rem 0 0.75rem", borderBottom: `1px solid ${C.tan}`, paddingBottom: 6 }}>
      {children}
    </div>
  );
}

function Spinner() {
  return <span style={{ fontSize: 13, color: C.tan }}>loading...</span>;
}

function StepDot({ n, active, done }) {
  return (
    <div style={{ width: 28, height: 28, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: 500, background: done ? C.crimson : active ? C.tan : "transparent", color: done || active ? "#fff" : C.tan, border: `1px solid ${done ? C.crimson : active ? C.tan : "#444"}`, flexShrink: 0 }}>
      {done ? "✓" : n}
    </div>
  );
}

function NewApplicationPage() {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [auditTrail, setAuditTrail] = useState(null);

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

  const f = (k, v) => setForm(p => ({ ...p, [k]: v }));

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        user_id: parseInt(form.user_id),
        age: parseInt(form.age),
        gender: parseInt(form.gender),
        education: parseInt(form.education),
        marital_status: parseInt(form.marital_status),
        current_credit_limit: parseFloat(form.current_credit_limit),
        pay_status_m1: parseFloat(form.pay_status_m1),
        pay_status_m2: parseFloat(form.pay_status_m2),
        pay_status_m3: parseFloat(form.pay_status_m3),
        pay_status_m4: parseFloat(form.pay_status_m4),
        pay_status_m5: parseFloat(form.pay_status_m5),
        pay_status_m6: parseFloat(form.pay_status_m6),
        bill_amt_m1: parseFloat(form.bill_amt_m1),
        bill_amt_m2: parseFloat(form.bill_amt_m2),
        bill_amt_m3: parseFloat(form.bill_amt_m3),
        bill_amt_m4: parseFloat(form.bill_amt_m4),
        bill_amt_m5: parseFloat(form.bill_amt_m5),
        bill_amt_m6: parseFloat(form.bill_amt_m6),
        pay_amt_m1: parseFloat(form.pay_amt_m1),
        pay_amt_m2: parseFloat(form.pay_amt_m2),
        pay_amt_m3: parseFloat(form.pay_amt_m3),
        pay_amt_m4: parseFloat(form.pay_amt_m4),
        pay_amt_m5: parseFloat(form.pay_amt_m5),
        pay_amt_m6: parseFloat(form.pay_amt_m6),
      };
      const data = await api("/api/predict", { method: "POST", body: JSON.stringify(payload) });
      setResult(data);
      setStep(3);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const loadAuditTrail = async (decisionId) => {
    try {
      const data = await api(`/api/audit-trail/${decisionId}`);
      setAuditTrail(data);
    } catch (e) {
      setError(e.message);
    }
  };

  const steps = ["applicant profile", "payment history", "decision"];

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: "2rem" }}>
        {steps.map((s, i) => (
          <div key={s} style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <StepDot n={i + 1} active={step === i + 1} done={step > i + 1} />
            <span style={{ fontSize: 13, color: step === i + 1 ? C.black : C.tan }}>{s}</span>
            {i < 2 && <div style={{ width: 32, height: 1, background: step > i + 1 ? C.crimson : "#444" }} />}
          </div>
        ))}
      </div>

      {error && <div style={sty.error}>{error}</div>}

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
                <tr>
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
          <div style={{ fontSize: 11, color: C.tan, marginTop: 10 }}>pay status: -1 = paid on time · 1+ = months delayed</div>
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 16 }}>
            <button style={sty.btnOutline} onClick={() => setStep(1)}>← back</button>
            <button style={sty.btnPrimary} onClick={handleSubmit} disabled={loading}>
              {loading ? "submitting..." : "submit application →"}
            </button>
          </div>
        </div>
      )}

      {step === 3 && result && (
        <div>
          <div style={{ background: C.crimson, borderRadius: 8, padding: "1.5rem", marginBottom: 16, display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div>
              <div style={{ fontSize: 11, color: C.tan, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 4 }}>recommended credit limit</div>
              <div style={{ fontSize: 36, fontWeight: 500, color: "#fff" }}>${result.recommended_limit?.toLocaleString() ?? "—"}</div>
              <div style={{ fontSize: 12, color: C.tan, marginTop: 4 }}>model {result.model_version}</div>
            </div>
            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: 11, color: C.tan, marginBottom: 4 }}>risk probability</div>
              <div style={{ fontSize: 28, fontWeight: 500, color: "#fff" }}>{result.risk_probability != null ? (result.risk_probability * 100).toFixed(1) + "%" : "—"}</div>
            </div>
          </div>

          <div style={sty.card}>
            <SectionLabel>decision summary</SectionLabel>
            <table style={{ width: "100%", fontSize: 13, borderCollapse: "collapse" }}>
              {[
                ["risk probability", result.risk_probability != null ? (result.risk_probability * 100).toFixed(2) + "%" : "—"],
                ["recommended limit", result.recommended_limit != null ? "$" + result.recommended_limit.toLocaleString() : "—"],
                ["model version", result.model_version ?? "—"],
                ["assessed at", result.prediction_made_at ? new Date(result.prediction_made_at).toLocaleString() : "—"],
              ].map(([k, v]) => (
                <tr key={k} style={{ borderBottom: `1px solid ${C.cream}` }}>
                  <td style={{ padding: "8px 0", color: "#666" }}>{k}</td>
                  <td style={{ padding: "8px 0", fontWeight: 500, textAlign: "right" }}>{v}</td>
                </tr>
              ))}
            </table>
          </div>

          {auditTrail && (
            <div style={sty.card}>
              <SectionLabel>audit trail — decision #{auditTrail.decision_id}</SectionLabel>
              <div style={{ fontSize: 13, color: "#444", lineHeight: 1.7 }}>
                <div style={{ marginBottom: 8 }}><strong>features submitted:</strong></div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 4 }}>
                  {auditTrail.features && Object.entries(auditTrail.features).map(([k, v]) => (
                    <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "3px 0", borderBottom: `1px solid ${C.cream}` }}>
                      <span style={{ color: "#666", fontFamily: "monospace", fontSize: 12 }}>{k}</span>
                      <span style={{ fontWeight: 500 }}>{v ?? "—"}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          <div style={{ display: "flex", gap: 10 }}>
            <button style={sty.btnOutline} onClick={() => { setStep(1); setResult(null); setAuditTrail(null); setError(null); }}>new application</button>
          </div>
        </div>
      )}
    </div>
  );
}

function LimitHistoryPage() {
  const [userId, setUserId] = useState("1");
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api(`/api/limit-history/${userId}?limit=20`);
      setHistory(data);
    } catch (e) {
      setError(e.message);
      setHistory(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={sty.card}>
        <div style={{ display: "flex", gap: 10, alignItems: "flex-end" }}>
          <div style={{ flex: 1 }}>
            <label style={sty.label}>user id</label>
            <input style={sty.input} value={userId} onChange={e => setUserId(e.target.value)} placeholder="enter user id" />
          </div>
          <button style={sty.btnPrimary} onClick={fetchHistory} disabled={loading}>
            {loading ? "loading..." : "fetch history"}
          </button>
        </div>
      </div>

      {error && <div style={sty.error}>{error}</div>}

      {history && (
        <>
          <div style={{ display: "flex", gap: 12, marginBottom: 16, flexWrap: "wrap" }}>
            <MetricCard label="user id" value={history.user_id} />
            <MetricCard label="total decisions" value={history.history_count} />
            <MetricCard label="drift events" value={history.history?.filter(h => h.drift_detected).length ?? 0} accent />
          </div>

          <div style={sty.card}>
            <SectionLabel>credit limit history</SectionLabel>
            {history.history?.length === 0 ? (
              <div style={{ color: C.tan, fontSize: 13 }}>no decisions found</div>
            ) : (
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                <thead>
                  <tr>
                    {["date", "limit", "change ($)", "drift", "model"].map(h => (
                      <th key={h} style={{ textAlign: "left", padding: "8px 10px", fontWeight: 500, color: C.tan, fontSize: 11, letterSpacing: "0.07em", textTransform: "uppercase", borderBottom: `1px solid ${C.tan}` }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {history.history?.map((h, i) => (
                    <tr key={h.decision_id} style={{ background: i % 2 === 0 ? "#fff" : C.cream, borderBottom: `1px solid ${C.cream}` }}>
                      <td style={{ padding: "10px", color: "#666" }}>{new Date(h.created_at).toLocaleDateString()}</td>
                      <td style={{ padding: "10px", fontWeight: 500 }}>${h.predicted_limit?.toLocaleString() ?? "—"}</td>
                      <td style={{ padding: "10px" }}>
                        {h.delta != null ? (
                          <span style={{ color: h.delta > 0 ? "#2d6a2d" : h.delta < 0 ? C.crimson : "#999", fontWeight: 500 }}>
                            {h.delta > 0 ? "+" : ""}{h.delta !== 0 ? h.delta.toLocaleString() : "—"}
                          </span>
                        ) : "—"}
                      </td>
                      <td style={{ padding: "10px" }}>
                        {h.drift_detected ? <Badge label="detected" variant="high" /> : <span style={{ color: "#999", fontSize: 12 }}>none</span>}
                      </td>
                      <td style={{ padding: "10px" }}><Badge label={h.model_version ?? "—"} variant="info" /></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </div>
  );
}

function DriftMonitorPage() {
  const [events, setEvents] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [severity, setSeverity] = useState("");

  const fetchEvents = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = severity ? `?severity=${severity}&limit=50` : "?limit=50";
      const data = await api(`/api/drift-events${params}`);
      setEvents(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [severity]);

  useEffect(() => { fetchEvents(); }, [fetchEvents]);

  const sevBg = { high: "#4a1a00", medium: "#3a2a00", low: "#1a2a1a", critical: C.crimson };

  return (
    <div>
      <div style={{ display: "flex", gap: 12, marginBottom: 16, flexWrap: "wrap" }}>
        <MetricCard label="total events" value={events?.event_count ?? "—"} />
        <MetricCard label="high severity" value={events?.events?.filter(e => e.severity === "high" || e.severity === "critical").length ?? "—"} accent />
        <MetricCard label="medium" value={events?.events?.filter(e => e.severity === "medium").length ?? "—"} />
      </div>

      <div style={{ ...sty.card, display: "flex", gap: 10, alignItems: "flex-end" }}>
        <div style={{ flex: 1 }}>
          <label style={sty.label}>filter by severity</label>
          <select style={sty.select} value={severity} onChange={e => setSeverity(e.target.value)}>
            <option value="">all</option>
            <option value="low">low</option>
            <option value="medium">medium</option>
            <option value="high">high</option>
            <option value="critical">critical</option>
          </select>
        </div>
        <button style={sty.btnPrimary} onClick={fetchEvents} disabled={loading}>
          {loading ? "loading..." : "refresh"}
        </button>
      </div>

      {error && <div style={sty.error}>{error}</div>}

      <div style={sty.card}>
        <SectionLabel>drift events</SectionLabel>
        {loading && <Spinner />}
        {!loading && events?.events?.length === 0 && (
          <div style={{ color: C.tan, fontSize: 13 }}>no drift events detected</div>
        )}
        {!loading && events?.events?.length > 0 && (
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13, tableLayout: "fixed" }}>
            <thead>
              <tr>
                {["feature", "drift score", "threshold", "severity", "detected at"].map(h => (
                  <th key={h} style={{ textAlign: "left", padding: "8px 10px", fontWeight: 500, color: C.tan, fontSize: 11, letterSpacing: "0.07em", textTransform: "uppercase", borderBottom: `1px solid ${C.tan}` }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {events.events.map((e, i) => (
                <tr key={e.event_id} style={{ background: i % 2 === 0 ? "#fff" : C.cream, borderBottom: `1px solid ${C.cream}` }}>
                  <td style={{ padding: "10px", fontFamily: "monospace", fontSize: 12 }}>{e.feature_name}</td>
                  <td style={{ padding: "10px", fontWeight: 500 }}>{e.drift_score?.toFixed(2) ?? "—"}</td>
                  <td style={{ padding: "10px", color: "#666" }}>{e.threshold?.toFixed(2) ?? "—"}</td>
                  <td style={{ padding: "10px" }}><Badge label={e.severity} variant={e.severity} /></td>
                  <td style={{ padding: "10px", color: "#666", fontSize: 12 }}>{new Date(e.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

function ModelManagementPage() {
  const [models, setModels] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activating, setActivating] = useState(null);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  const fetchModels = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api("/api/models");
      setModels(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchComparison = async () => {
    try {
      const data = await api("/api/models/compare");
      setComparison(data);
    } catch (e) {
      // comparison requires 2+ models — silently skip if not available
    }
  };

  useEffect(() => { fetchModels(); fetchComparison(); }, [fetchModels]);

  const handleActivate = async (version) => {
    setActivating(version);
    setError(null);
    setSuccessMsg(null);
    try {
      await api(`/api/models/${version}/activate`, { method: "POST" });
      setSuccessMsg(`Model ${version} is now active`);
      fetchModels();
    } catch (e) {
      setError(e.message);
    } finally {
      setActivating(null);
    }
  };

  const activeModel = models?.models?.find(m => m.is_active);

  return (
    <div>
      <div style={{ display: "flex", gap: 12, marginBottom: 16, flexWrap: "wrap" }}>
        <MetricCard label="registered" value={models?.total_models ?? "—"} sub="model versions" />
        <MetricCard label="active model" value={activeModel?.version ?? "—"} sub="currently serving" />
        <MetricCard label="accuracy" value={activeModel ? (activeModel.metrics?.test?.accuracy != null ? (activeModel.metrics.test.accuracy * 100).toFixed(1) + "%" : "—") : "—"} accent />
      </div>

      {error && <div style={sty.error}>{error}</div>}
      {successMsg && <div style={sty.success}>{successMsg}</div>}

      {loading && <Spinner />}

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        {models?.models?.map(m => {
          const testMetrics = m.metrics?.test || {};
          return (
            <div key={m.version} style={{ ...sty.card, marginBottom: 0, borderColor: m.is_active ? C.crimson : C.tan, borderWidth: m.is_active ? 2 : 1 }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
                <div style={{ fontSize: 18, fontWeight: 500 }}>{m.version}</div>
                {m.is_active && <Badge label="active" variant="approved" />}
              </div>
              <div style={{ fontSize: 12, color: C.tan, marginBottom: 12 }}>{m.description}</div>
              {[
                ["accuracy", testMetrics.accuracy != null ? (testMetrics.accuracy * 100).toFixed(1) + "%" : "—"],
                ["roc-auc", testMetrics.roc_auc?.toFixed(4) ?? "—"],
                ["f1 score", testMetrics.f1?.toFixed(4) ?? "—"],
                ["created", m.created_at ? new Date(m.created_at).toLocaleDateString() : "—"],
              ].map(([k, v]) => (
                <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "6px 0", borderBottom: `1px solid ${C.cream}`, fontSize: 13 }}>
                  <span style={{ color: "#666" }}>{k}</span>
                  <span style={{ fontWeight: 500 }}>{v}</span>
                </div>
              ))}
              {!m.is_active && (
                <button style={{ ...sty.btnPrimary, width: "100%", marginTop: 14 }} onClick={() => handleActivate(m.version)} disabled={activating === m.version}>
                  {activating === m.version ? "activating..." : `activate ${m.version}`}
                </button>
              )}
              {m.is_active && (
                <div style={{ marginTop: 14, padding: "8px 12px", background: C.cream, borderRadius: 6, fontSize: 12, color: C.tan, textAlign: "center" }}>
                  serving live traffic
                </div>
              )}
            </div>
          );
        })}
      </div>

      {comparison?.comparison && (
        <div style={sty.card}>
          <SectionLabel>metric comparison</SectionLabel>
          {[["accuracy", "test_accuracy"], ["roc-auc", "test_roc_auc"], ["f1 score", "test_f1"]].map(([label, key]) => {
            const values = comparison.comparison.map(m => ({ version: m.version, val: m[key] || 0 }));
            const max = Math.max(...values.map(v => v.val)) || 1;
            return (
              <div key={key} style={{ marginBottom: 14 }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 6 }}>
                  <span style={{ color: "#444" }}>{label}</span>
                  <span style={{ color: C.tan }}>{values.map(v => `${v.version}: ${v.val.toFixed(4)}`).join(" · ")}</span>
                </div>
                {values.map((v, i) => (
                  <div key={v.version} style={{ position: "relative", height: 10, background: C.cream, borderRadius: 5, border: `1px solid ${C.tan}`, marginBottom: 4 }}>
                    <div style={{ position: "absolute", width: `${(v.val / max) * 100}%`, height: "100%", background: i === 0 ? C.tan : C.crimson, borderRadius: 5, opacity: 0.85 }} />
                  </div>
                ))}
              </div>
            );
          })}
          <div style={{ fontSize: 11, color: C.tan }}>best model: {comparison.best_model}</div>
        </div>
      )}
    </div>
  );
}

function AlertsPage() {
  const [alertsData, setAlertsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [resolving, setResolving] = useState(null);

  const fetchAlerts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api("/api/alerts");
      setAlertsData(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchAlerts(); }, [fetchAlerts]);

  const sevBorder = { critical: C.crimson, high: "#7a3a00", medium: "#6a5000", low: "#3a5a3a" };

  return (
    <div>
      <div style={{ display: "flex", gap: 12, marginBottom: 16, flexWrap: "wrap" }}>
        <MetricCard label="active alerts" value={alertsData?.summary?.total_active ?? "—"} />
        <MetricCard label="critical" value={alertsData?.summary?.by_severity?.critical ?? 0} accent sub="needs action" />
        <MetricCard label="high" value={alertsData?.summary?.by_severity?.high ?? 0} sub="review soon" />
        <MetricCard label="drift" value={alertsData?.summary?.by_type?.drift ?? 0} sub="limit changes" />
      </div>

      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 12 }}>
        <button style={sty.btnOutline} onClick={fetchAlerts} disabled={loading}>
          {loading ? "loading..." : "refresh"}
        </button>
      </div>

      {error && <div style={sty.error}>{error}</div>}

      {!loading && alertsData?.alerts?.length === 0 && (
        <div style={{ ...sty.card, textAlign: "center", padding: "3rem", color: C.tan }}>
          no active alerts
        </div>
      )}

      {alertsData?.alerts?.map(a => (
        <div key={a.alert_id} style={{ ...sty.card, borderLeft: `4px solid ${sevBorder[a.severity] || C.tan}`, borderRadius: "0 8px 8px 0", display: "flex", alignItems: "flex-start", gap: 14 }}>
          <div style={{ paddingTop: 2 }}><Badge label={a.severity || a.type} variant={a.severity || "neutral"} /></div>
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: 13, color: C.black, lineHeight: 1.6, marginBottom: 4 }}>{a.message}</div>
            <div style={{ fontSize: 11, color: C.tan }}>{a.type} · {new Date(a.timestamp).toLocaleString()}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

export default function App() {
  const [page, setPage] = useState("new application");
  const [apiStatus, setApiStatus] = useState("checking...");

  useEffect(() => {
    api("/health")
      .then(d => setApiStatus(d.status === "healthy" ? "connected" : "degraded"))
      .catch(() => setApiStatus("unreachable"));
  }, []);

  const pageMap = {
    "new application": <NewApplicationPage />,
    "limit history": <LimitHistoryPage />,
    "drift monitor": <DriftMonitorPage />,
    "model management": <ModelManagementPage />,
    "alerts": <AlertsPage />,
  };

  const titles = {
    "new application": { title: "new application", sub: "submit a credit limit request" },
    "limit history": { title: "limit history", sub: "track changes over time for a user" },
    "drift monitor": { title: "drift monitor", sub: "statistical distribution checks and fairness" },
    "model management": { title: "model management", sub: "versions, metrics, activation" },
    "alerts": { title: "alerts", sub: "active violations and drift events" },
  };

  const t = titles[page];
  const statusColor = apiStatus === "connected" ? "#2d6a2d" : apiStatus === "checking..." ? "#666" : C.crimson;

  return (
    <div style={{ display: "flex", minHeight: "100vh", fontFamily: "Georgia, serif" }}>
      <div style={sty.sidebar}>
        <div style={{ padding: "0 1.5rem 2rem", borderBottom: "1px solid #222" }}>
          <div style={{ fontSize: 16, fontWeight: 500, color: "#fff", letterSpacing: "0.05em" }}>TraceCredit</div>
          <div style={{ fontSize: 11, color: "#555", marginTop: 2 }}>credit monitoring</div>
        </div>

        <nav style={{ padding: "1rem 0" }}>
          {PAGES.map(p => {
            const isActive = page === p.id;
            return (
              <div key={p.id} onClick={() => setPage(p.id)} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 1.5rem", cursor: "pointer", background: isActive ? C.crimson : "transparent", borderLeft: isActive ? `3px solid ${C.tan}` : "3px solid transparent" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <span style={{ fontSize: 13, color: isActive ? "#fff" : "#666", width: 16, textAlign: "center" }}>{p.icon}</span>
                  <span style={{ fontSize: 13, color: isActive ? "#fff" : "#888" }}>{p.id}</span>
                </div>
              </div>
            );
          })}
        </nav>

        <div style={{ position: "absolute", bottom: "1.5rem", left: "1.5rem", right: "1.5rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "10px 12px", background: "#111", borderRadius: 8 }}>
            <div style={{ width: 7, height: 7, borderRadius: "50%", background: statusColor, flexShrink: 0 }} />
            <div>
              <div style={{ fontSize: 11, color: "#aaa" }}>api {apiStatus}</div>
              <div style={{ fontSize: 10, color: "#555", wordBreak: "break-all" }}>tracecredit.onrender.com</div>
            </div>
          </div>
        </div>
      </div>

      <div style={sty.content}>
        <div style={{ marginBottom: "1.75rem" }}>
          <h1 style={{ fontSize: 22, fontWeight: 500, color: C.black, margin: 0 }}>{t.title}</h1>
          <p style={{ fontSize: 13, color: C.tan, margin: "4px 0 0" }}>{t.sub}</p>
        </div>
        {pageMap[page]}
      </div>
    </div>
  );
}
