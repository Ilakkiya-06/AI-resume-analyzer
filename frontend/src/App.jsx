import { useState } from "react";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);
  const [matchResult, setMatchResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [matchLoading, setMatchLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    setFile(selectedFile);
    setResult(null);
    setMatchResult(null);
    setError("");
  };

  const analyzeResume = async () => {
    if (!file) {
      setError("Please select a PDF or DOCX resume.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();

    formData.append("resume", file);

    try {
      const response = await fetch(
        "http://127.0.0.1:5000/api/analyze",
        {
          method: "POST",
          body: formData
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Analysis failed.");
      }

      setResult(data);

    } catch (err) {

      setError(err.message);

    } finally {

      setLoading(false);
    }
  };

  const matchJob = async () => {

    if (!file) {
      setError("Please select your resume first.");
      return;
    }

    if (!jobDescription.trim()) {
      setError("Please enter the job description.");
      return;
    }

    setMatchLoading(true);
    setError("");
    setMatchResult(null);

    const formData = new FormData();

    formData.append("resume", file);

    formData.append(
      "job_description",
      jobDescription
    );

    try {

      const response = await fetch(
        "http://127.0.0.1:5000/api/match",
        {
          method: "POST",
          body: formData
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error || "Matching failed."
        );
      }

      setMatchResult(data);

    } catch (err) {

      setError(err.message);

    } finally {

      setMatchLoading(false);
    }
  };

  return (
    <div className="app">

      <header className="header">

        <div>

          <h1>AI Resume Analyzer</h1>

          <p>
            Analyze your resume and improve your chances
            of getting shortlisted.
          </p>

        </div>

      </header>


      <main className="container">

        <section className="upload-card">

          <h2>Upload Your Resume</h2>

          <p>
            Supported formats: PDF and DOCX
          </p>

          <label className="upload-box">

            <input
              type="file"
              accept=".pdf,.docx"
              onChange={handleFileChange}
            />

            <span>
              {file
                ? file.name
                : "Click to choose your resume"}
            </span>

          </label>

          <button
            className="primary-button"
            onClick={analyzeResume}
            disabled={loading}
          >

            {loading
              ? "Analyzing Resume..."
              : "Analyze Resume"}

          </button>

        </section>


        {error && (

          <div className="error-box">

            {error}

          </div>

        )}


        {result && result.analysis && (

          <section className="results">

            <h2>Resume Analysis</h2>


            <div className="score-card">

              <div>

                <span>
                  Resume Score
                </span>

                <strong>
                  {result.analysis.score}
                </strong>

                <small>
                  / 100
                </small>

              </div>

            </div>


            <div className="grid">


              <div className="result-card">

                <h3>Skills Found</h3>

                <div className="tags">

                  {result.analysis.skills.length > 0

                    ? result.analysis.skills.map(
                        (skill) => (
                          <span
                            className="tag"
                            key={skill}
                          >
                            {skill}
                          </span>
                        )
                      )

                    : (
                      <p>
                        No recognized skills found.
                      </p>
                    )}

                </div>

              </div>


              <div className="result-card">

                <h3>Resume Sections</h3>

                <ul className="check-list">

                  {Object.entries(
                    result.analysis.sections
                  ).map(
                    ([section, exists]) => (

                      <li key={section}>

                        <span>
                          {section}
                        </span>

                        <strong>
                          {exists ? "✓" : "—"}
                        </strong>

                      </li>

                    )
                  )}

                </ul>

              </div>


              <div className="result-card">

                <h3>Strengths</h3>

                <ul>

                  {result.analysis.strengths.map(
                    (item, index) => (

                      <li key={index}>
                        {item}
                      </li>

                    )
                  )}

                </ul>

              </div>


              <div className="result-card">

                <h3>Weaknesses</h3>

                <ul>

                  {result.analysis.weaknesses.map(
                    (item, index) => (

                      <li key={index}>
                        {item}
                      </li>

                    )
                  )}

                </ul>

              </div>


            </div>


            <div className="result-card full">

              <h3>Suggestions</h3>

              <ul>

                {result.analysis.suggestions.map(
                  (item, index) => (

                    <li key={index}>
                      {item}
                    </li>

                  )
                )}

              </ul>

            </div>


            <div className="result-card full">

              <h3>Resume Keywords</h3>

              <div className="tags">

                {result.analysis.keywords.map(
                  (keyword) => (

                    <span
                      className="tag"
                      key={keyword}
                    >
                      {keyword}
                    </span>

                  )
                )}

              </div>

            </div>


            <details className="text-section">

              <summary>
                View Extracted Resume Text
              </summary>

              <pre>
                {result.extracted_text}
              </pre>

            </details>

          </section>

        )}


        <section className="job-section">

          <h2>Job Description Matching</h2>

          <p>
            Paste the job description to check how
            well your resume matches the role.
          </p>


          <textarea
            placeholder="Paste the job description here..."
            value={jobDescription}
            onChange={(event) =>
              setJobDescription(event.target.value)
            }
          />


          <button
            className="secondary-button"
            onClick={matchJob}
            disabled={matchLoading}
          >

            {matchLoading
              ? "Checking Match..."
              : "Check ATS Match"}

          </button>


          {matchResult && (

            <div className="match-results">


              <div className="ats-score">

                <span>
                  ATS Match Score
                </span>

                <strong>
                  {matchResult.ats_score}%
                </strong>

              </div>


              <div className="grid">


                <div className="result-card">

                  <h3>
                    Matched Skills
                  </h3>

                  <div className="tags">

                    {matchResult.matched_skills
                      .length > 0

                      ? matchResult.matched_skills.map(
                          (skill) => (

                            <span
                              className="tag success"
                              key={skill}
                            >
                              ✓ {skill}
                            </span>

                          )
                        )

                      : (
                        <p>
                          No matching skills found.
                        </p>
                      )}

                  </div>

                </div>


                <div className="result-card">

                  <h3>
                    Missing Skills
                  </h3>

                  <div className="tags">

                    {matchResult.missing_skills
                      .length > 0

                      ? matchResult.missing_skills.map(
                          (skill) => (

                            <span
                              className="tag danger"
                              key={skill}
                            >
                              ✕ {skill}
                            </span>

                          )
                        )

                      : (
                        <p>
                          No major missing skills detected.
                        </p>
                      )}

                  </div>

                </div>


                <div className="result-card full">

                  <h3>
                    Matching Keywords
                  </h3>

                  <div className="tags">

                    {matchResult.matched_keywords.map(
                      (keyword) => (

                        <span
                          className="tag"
                          key={keyword}
                        >
                          {keyword}
                        </span>

                      )
                    )}

                  </div>

                </div>


              </div>

            </div>

          )}

        </section>

      </main>


      <footer>

        <p>
          AI Resume Analyzer • Built with React
          and Flask
        </p>

      </footer>

    </div>
  );
}

export default App;