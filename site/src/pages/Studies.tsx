import { Link } from 'react-router-dom';
import { useData } from '../hooks/useData';

interface StudySummary {
  id: string;
  title: string;
  subtitle: string;
  concept_count: number;
  total_matches: number;
  slug: string;
}

export default function Studies() {
  const { data: studies, loading, error } = useData<StudySummary[]>('studies/index.json');

  if (loading) return <div className="loading">Loading studies...</div>;
  if (error) return <div className="error">Failed to load studies: {error}</div>;

  return (
    <>
      <h1>Studies</h1>
      <p className="subtitle">
        Curated analytical explorations of the Exegesis, tracing Dick's engagement
        with AI, consciousness, and the philosophical traditions that shaped his metaphysics.
      </p>

      <div className="studies-grid">
        {studies &&
          studies.map((s) => (
            <Link
              key={s.id}
              to={`/studies/${s.slug}`}
              className="study-card"
            >
              <h2 className="study-card-title">{s.title}</h2>
              <p className="study-card-subtitle">{s.subtitle}</p>
              <div className="study-card-stats">
                <span className="study-stat">
                  <span className="study-stat-value">{s.concept_count}</span>
                  <span className="study-stat-label">Concept Areas</span>
                </span>
                <span className="study-stat">
                  <span className="study-stat-value">
                    {s.total_matches.toLocaleString()}
                  </span>
                  <span className="study-stat-label">Matching Segments</span>
                </span>
              </div>
            </Link>
          ))}
      </div>
    </>
  );
}
