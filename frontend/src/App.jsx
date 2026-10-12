
import { useState } from "react";
import "./App.css";

const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function askQuestion(event) {
    event.preventDefault();

    const cleanedQuestion = question.trim();
    if (cleanedQuestion.length < 3) {
      setError("Please enter a health question of at least 3 characters.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: cleanedQuestion }),
      });

      if (!response.ok) {
        throw new Error(
          response.status === 422
            ? "Please enter a question between 3 and 1,000 characters."
            : `The server returned an error (${response.status}).`
        );
      }

      setResult(await response.json());
    } catch (err) {
      setError(
        err instanceof TypeError
          ? "Cannot connect to MedEvidence AI. Check that the backend is running at http://127.0.0.1:8000."
          : err.message
      );
    } finally {
      setLoading(false);
    }
  }

  const statusLabels = {
    evidence_found: "Evidence found",
    no_evidence: "Insufficient evidence",
    evidence_unavailable: "Evidence unavailable",
    possible_emergency: "Urgent safety guidance",
    personalized_medication: "Medication safety guidance",
    not_verified: "Source check warning",
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#home" aria-label="MedEvidence AI home">
          <span className="brand-icon">✳</span>
          <span>MedEvidence <b>AI</b></span>
        </a>
        <span className="topbar-label">
          <span className="live-dot" /> Evidence-first health education
        </span>
      </header>

      <main id="home">
        <section className="hero">
          <div className="eyebrow">
            <span>✦</span> YOUR HEALTH, BETTER INFORMED
          </div>
          <h1>
            Understand health
            <br />
            with <span>evidence.</span>
          </h1>
          <p className="hero-copy">
            Ask a general health question and explore answers grounded in
            published health guidance, with source links you can check yourself.
          </p>

          <div className="trust-row">
            <span>✓ Traceable sources</span>
            <span>✓ Safety-aware responses</span>
            <span>✓ Transparent limitations</span>
          </div>
        </section>

        <section className="workspace">
          <div className="section-heading">
            <div>
              <span className="step-label">01 / ASK</span>
              <h2>What would you like to understand?</h2>
            </div>
            <span className="general-tag">General health education</span>
          </div>

          <form className="question-form" onSubmit={askQuestion}>
            <label htmlFor="question">Your health question</label>
            <textarea
              id="question"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="e.g. What are the risk factors for high blood pressure?"
              maxLength={1000}
              rows={4}
              disabled={loading}
            />
            <div className="form-bottom">
              <span>{question.length}/1000 characters</span>
              <button type="submit" disabled={loading || question.trim().length < 3}>
                {loading ? "Researching…" : "Explore evidence"} <span>→</span>
              </button>
            </div>
          </form>

          {!result && !loading && !error && (
            <div className="suggestions">
              <span>TRY ASKING</span>
              {[
                "What are the risk factors for high blood pressure?",
                "What makes a diet healthy?",
                "What are common risk factors for diabetes?",
              ].map((item) => (
                <button
                  type="button"
                  className="suggestion"
                  key={item}
                  onClick={() => {
                    setQuestion(item);
                    setError("");
                  }}
                >
                  {item} <span>↗</span>
                </button>
              ))}
            </div>
          )}

          {loading && (
            <div className="loading-panel" role="status">
              <div className="loader" />
              <div>
                <strong>Reviewing available evidence</strong>
                <p>Searching the local evidence library and checking source links…</p>
              </div>
            </div>
          )}

          {error && (
            <div className="error-panel" role="alert">
              <strong>We couldn’t complete your request.</strong>
              <p>{error}</p>
              <button type="button" onClick={askQuestion} disabled={loading}>
                Try again
              </button>
            </div>
          )}

          {result && (
            <section className="results" aria-live="polite">
              <div className="result-heading">
                <div>
                  <span className="step-label">02 / RESPONSE</span>
                  <h2>Evidence summary</h2>
                </div>
                <span className={`status-pill status-${result.status}`}>
                  {statusLabels[result.status] || result.status.replaceAll("_", " ")}
                </span>
              </div>

              <div className="answer-card">
                <div className="answer-mark">✳</div>
                <div>
                  <h3>
                    {["possible_emergency", "personalized_medication"].includes(result.status)
                      ? "Safety guidance"
                      : "What the evidence says"}
                  </h3>
                  <p className="answer-text">{result.answer}</p>
                </div>
              </div>

              <div className="sources-heading">
                <div>
                  <span className="step-label">03 / TRACEABILITY</span>
                  <h2>Explore the sources</h2>
                </div>
                <span className="source-count">
                  {result.sources?.length || 0} source
                  {result.sources?.length === 1 ? "" : "s"}
                </span>
              </div>

              {result.verification?.length > 0 && (
                <div className="verification-note">
                  <strong>Source-link checks</strong>
                  <p>
                    {result.verification.filter((item) => item.traceable).length}
                    {" of "}
                    {result.verification.length} claim link(s) point to a
                    retrieved source passage. This checks traceability, not
                    independent medical accuracy.
                  </p>
                </div>
              )}

              {result.sources?.length > 0 ? (
                <div className="source-list">
                  {result.sources.map((source) => (
                    <article className="source-card" key={source.passage_id}>
                      <div className="source-topline">
                        <span className="source-type">PUBLISHED GUIDANCE</span>
                        <span className="source-id">{source.passage_id}</span>
                      </div>
                      <h3>{source.title}</h3>
                      <p className="publisher">{source.publisher}</p>
                      <p className="excerpt">{source.excerpt}</p>
                      <a href={source.url} target="_blank" rel="noreferrer">
                        Read original source <span>↗</span>
                      </a>
                    </article>
                  ))}
                </div>
              ) : (
                <div className="empty-sources">
                  No supporting sources were returned for this response.
                </div>
              )}

              <button
                className="ask-another"
                onClick={() => {
                  setResult(null);
                  setQuestion("");
                  setError("");
                }}
              >
                Ask another question <span>↗</span>
              </button>
            </section>
          )}
        </section>

        <section className="safety-banner">
          <span className="safety-icon">i</span>
          <div>
            <strong>A note about your health</strong>
            <p>
              MedEvidence AI provides general health education, not diagnosis
              or treatment. It does not replace advice from a qualified
              healthcare professional. If you may be experiencing a medical
              emergency, contact local emergency services immediately.
            </p>
          </div>
        </section>
      </main>

      <footer>
        <a className="footer-brand" href="#home">MedEvidence AI</a>
        <span>Evidence matters. Your wellbeing matters more.</span>
        <span>UnivaBio Hackathon · 2026</span>
      </footer>
    </div>
  );
}

export default App;