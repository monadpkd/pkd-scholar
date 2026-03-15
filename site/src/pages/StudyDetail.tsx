import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useData } from '../hooks/useData';

interface Passage {
  seg_id: string;
  page: number;
  title: string;
  quote: string;
  analysis: string;
}

interface ConceptArea {
  id: string;
  name: string;
  description: string;
  match_count: number;
  key_passages: Passage[];
}

interface CrossConceptEntry {
  seg_id: string;
  page: number;
  concept_count: number;
  concepts: string[];
}

interface TerminologyEntry {
  dicks_term: string;
  modern_equivalent: string;
}

interface DensestPage {
  seg_id?: string;
  page?: number;
  pages?: string;
  description: string;
}

interface OverlapEntry {
  seg_id: string;
  page: number;
  terms?: string;
  convergence?: string;
}

interface AIVoiceRef {
  seg_id: string;
  summary: string;
}

interface EssayFinding {
  id: string;
  title: string;
  work_id: string;
  description: string;
  key_points: string[];
}

interface SynthesisSection {
  title: string;
  paragraphs: string[];
}

interface Study {
  id: string;
  title: string;
  subtitle: string;
  introduction: string[];
  concept_areas: ConceptArea[];
  cross_concept_table?: CrossConceptEntry[];
  terminology_map?: TerminologyEntry[];
  densest_pages?: DensestPage[];
  overlap_table?: OverlapEntry[];
  overlap_with_ai?: OverlapEntry[];
  key_finding?: string;
  ai_voice_references?: AIVoiceRef[];
  essay_findings?: EssayFinding[];
  synthesis?: SynthesisSection;
  monad_relevance_note?: string;
}

function segIdToPath(segId: string): string {
  return `/segments/${segId}`;
}

function ConceptSection({ area }: { area: ConceptArea }) {
  const [expanded, setExpanded] = useState(true);

  return (
    <div className="study-concept">
      <button
        className="study-concept-header"
        onClick={() => setExpanded(!expanded)}
        aria-expanded={expanded}
      >
        <div className="study-concept-header-left">
          <span className="study-concept-toggle">{expanded ? '\u25BC' : '\u25B6'}</span>
          <h3 className="study-concept-name">{area.name}</h3>
        </div>
        <span className="study-concept-count">{area.match_count} segments</span>
      </button>
      {expanded && (
        <div className="study-concept-body">
          <p className="study-concept-desc">{area.description}</p>
          <div className="study-passages">
            {area.key_passages.map((p, i) => (
              <div key={i} className="study-passage">
                <div className="study-passage-header">
                  <span className="study-passage-title">{p.title}</span>
                  <Link
                    to={segIdToPath(p.seg_id)}
                    className="study-passage-ref"
                  >
                    p.{p.page} &middot; {p.seg_id.replace('PKD-SEG-EXEGESIS-', '')}
                  </Link>
                </div>
                <blockquote className="study-blockquote">{p.quote}</blockquote>
                <p className="study-analysis">{p.analysis}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default function StudyDetail() {
  const { slug } = useParams<{ slug: string }>();
  const { data: study, loading, error } = useData<Study>(
    `studies/${slug}.json`
  );

  if (loading) return <div className="loading">Loading study...</div>;
  if (error) return <div className="error">Failed to load study: {error}</div>;
  if (!study) return <div className="error">Study not found.</div>;

  return (
    <>
      <div className="breadcrumb">
        <Link to="/studies">Studies</Link>
        <span>/</span>
        {study.title}
      </div>

      <div className="study-hero">
        <h1>{study.title}</h1>
        <p className="study-subtitle">{study.subtitle}</p>
        <div className="study-intro">
          {study.introduction.map((para, i) => (
            <p key={i}>{para}</p>
          ))}
        </div>
      </div>

      {/* Concept Areas */}
      <section className="study-section">
        <h2>Concept Areas</h2>
        {study.concept_areas.map((area) => (
          <ConceptSection key={area.id} area={area} />
        ))}
      </section>

      {/* Terminology Map */}
      {study.terminology_map && study.terminology_map.length > 0 && (
        <section className="study-section">
          <h2>Terminology Map</h2>
          <p className="study-section-desc">
            Dick's vocabulary mapped to modern equivalents — not direct translations,
            but structural parallels.
          </p>
          <div className="study-table-wrap">
            <table className="study-table">
              <thead>
                <tr>
                  <th>Dick's Term</th>
                  <th>Modern Equivalent</th>
                </tr>
              </thead>
              <tbody>
                {study.terminology_map.map((row, i) => (
                  <tr key={i}>
                    <td>{row.dicks_term}</td>
                    <td>{row.modern_equivalent}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Cross-Concept Density */}
      {study.cross_concept_table && study.cross_concept_table.length > 0 && (
        <section className="study-section">
          <h2>Cross-Concept Density</h2>
          <p className="study-section-desc">
            The most theoretically dense passages, where Dick operates in multiple
            conceptual registers simultaneously.
          </p>
          <div className="study-table-wrap">
            <table className="study-table">
              <thead>
                <tr>
                  <th>Segment</th>
                  <th>Page</th>
                  <th>Concepts</th>
                </tr>
              </thead>
              <tbody>
                {study.cross_concept_table.map((row, i) => (
                  <tr key={i}>
                    <td>
                      <Link to={segIdToPath(row.seg_id)}>
                        {row.seg_id.replace('PKD-SEG-EXEGESIS-', '')}
                      </Link>
                    </td>
                    <td>{row.page}</td>
                    <td>
                      <div className="study-concept-badges">
                        {row.concepts.map((c, j) => (
                          <span key={j} className="study-concept-badge">
                            {c}
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Overlap Table (Teilhard) */}
      {study.overlap_table && study.overlap_table.length > 0 && (
        <section className="study-section">
          <h2>Overlap with AI/Singularity Concepts</h2>
          <p className="study-section-desc">
            Segments containing both Teilhard/noosphere terms and AI/information/VALIS terms.
          </p>
          {study.key_finding && (
            <div className="study-key-finding">
              <strong>Key Finding:</strong> {study.key_finding}
            </div>
          )}
          <div className="study-table-wrap">
            <table className="study-table">
              <thead>
                <tr>
                  <th>Segment</th>
                  <th>Page</th>
                  <th>Terms Combined</th>
                </tr>
              </thead>
              <tbody>
                {study.overlap_table.map((row, i) => (
                  <tr key={i}>
                    <td>
                      <Link to={segIdToPath(row.seg_id)}>
                        {row.seg_id.replace('PKD-SEG-EXEGESIS-', '')}
                      </Link>
                    </td>
                    <td>{row.page}</td>
                    <td>{row.terms || row.convergence}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Overlap with AI (Monad) */}
      {study.overlap_with_ai && study.overlap_with_ai.length > 0 && (
        <section className="study-section">
          <h2>Overlap with AI/Singularity Concepts</h2>
          <p className="study-section-desc">
            Segments containing both Monad/Neoplatonism terms and AI/information/VALIS terms.
          </p>
          <div className="study-table-wrap">
            <table className="study-table">
              <thead>
                <tr>
                  <th>Segment</th>
                  <th>Page</th>
                  <th>Convergence</th>
                </tr>
              </thead>
              <tbody>
                {study.overlap_with_ai.map((row, i) => (
                  <tr key={i}>
                    <td>
                      <Link to={segIdToPath(row.seg_id)}>
                        {row.seg_id.replace('PKD-SEG-EXEGESIS-', '')}
                      </Link>
                    </td>
                    <td>{row.page}</td>
                    <td>{row.convergence || row.terms}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}

      {/* Densest Pages */}
      {study.densest_pages && study.densest_pages.length > 0 && (
        <section className="study-section">
          <h2>Densest Pages</h2>
          <p className="study-section-desc">
            The most important pages for this study's themes — where the
            conceptual density is highest.
          </p>
          <div className="study-densest-list">
            {study.densest_pages.map((dp, i) => (
              <div key={i} className="study-densest-item">
                <span className="study-densest-page">
                  {dp.seg_id ? (
                    <Link to={segIdToPath(dp.seg_id)}>
                      p.{dp.page}
                    </Link>
                  ) : (
                    <span>pp. {dp.pages}</span>
                  )}
                </span>
                <span className="study-densest-desc">{dp.description}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* AI Voice References */}
      {study.ai_voice_references && study.ai_voice_references.length > 0 && (
        <section className="study-section">
          <h2>Dick's "AI Voice" References</h2>
          <p className="study-section-desc">
            Dick uses the term "AI voice" repeatedly — not meaning "artificial intelligence"
            in the modern sense, but "autonomous intelligence." The parallel is uncanny.
          </p>
          <div className="study-ai-voice-list">
            {study.ai_voice_references.map((ref, i) => (
              <div key={i} className="study-ai-voice-item">
                <Link to={segIdToPath(ref.seg_id)} className="study-ai-voice-seg">
                  {ref.seg_id.replace('PKD-SEG-EXEGESIS-', '')}
                </Link>
                <span className="study-ai-voice-text">{ref.summary}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Synthesis (Monad) */}
      {study.synthesis && (
        <section className="study-section">
          <h2>{study.synthesis.title}</h2>
          <div className="study-synthesis">
            {study.synthesis.paragraphs.map((para, i) => (
              <p key={i}>{para}</p>
            ))}
          </div>
        </section>
      )}

      {/* Essay Findings */}
      {study.essay_findings && study.essay_findings.length > 0 && (
        <section className="study-section">
          <h2>Essay Findings</h2>
          <p className="study-section-desc">
            Key essays where Dick synthesizes the themes of this study.
          </p>
          {study.essay_findings.map((ef) => (
            <div key={ef.id} className="study-essay-finding">
              <h3>{ef.title}</h3>
              <p className="study-essay-desc">{ef.description}</p>
              <ul className="study-essay-points">
                {ef.key_points.map((pt, i) => (
                  <li key={i}>{pt}</li>
                ))}
              </ul>
            </div>
          ))}
        </section>
      )}

      {/* Monad Relevance Note */}
      {study.monad_relevance_note && (
        <section className="study-section">
          <h2>The Monad in the Exegesis</h2>
          <div className="study-monad-note">
            <p>{study.monad_relevance_note}</p>
          </div>
        </section>
      )}
    </>
  );
}
