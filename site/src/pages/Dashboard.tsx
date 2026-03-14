import { Link } from 'react-router-dom';
import { useData } from '../hooks/useData';
import WorkCard from '../components/WorkCard';
import type { Work, Stats } from '../types';

const FAMILY_LABELS: Record<string, string> = {
  ai_automation: 'AI & Automation',
  metaphysics: 'Metaphysics',
  psychology: 'Psychology',
};

export default function Dashboard() {
  const { data: works, loading: wLoading, error: wError } = useData<Work[]>('works/index.json');
  const { data: stats, loading: sLoading, error: sError } = useData<Stats>('stats.json');

  if (wLoading || sLoading) return <div className="loading">Loading corpus data...</div>;
  if (wError || sError) return <div className="error">Failed to load data: {wError || sError}</div>;

  return (
    <>
      <h1>Philip K. Dick Corpus</h1>
      <p className="subtitle">
        A scholarly exploration of Dick's fiction, essays, and exegesis
      </p>

      {stats && (
        <div className="hero-stats">
          <div className="stat-card">
            <div className="stat-value">{stats.total_works}</div>
            <div className="stat-label">Works</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.total_segments.toLocaleString()}</div>
            <div className="stat-label">Segments</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">
              {Math.round(stats.total_words / 1000).toLocaleString()}K
            </div>
            <div className="stat-label">Words</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.total_topics}</div>
            <div className="stat-label">Topics</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">
              {stats.total_topic_matches?.toLocaleString() || 0}
            </div>
            <div className="stat-label">Topic Matches</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">
              {stats.extraction_status['extracted'] || 0}/{stats.total_works}
            </div>
            <div className="stat-label">Extracted</div>
          </div>
        </div>
      )}

      {stats && stats.top_topics && stats.top_topics.length > 0 && (
        <>
          <h2>
            Top Topics{' '}
            <Link
              to="/topics"
              style={{ fontWeight: 400, fontSize: '0.85rem' }}
            >
              View all &rarr;
            </Link>
          </h2>
          <div className="top-topics-grid">
            {stats.top_topics.map((t) => (
              <Link
                key={t.topic_id}
                to={`/topics/${t.slug}`}
                className="top-topic-card"
              >
                <span className="top-topic-name">{t.canonical_name}</span>
                <span className="top-topic-count">{t.match_count}</span>
                <span className="top-topic-family">
                  {FAMILY_LABELS[t.topic_family] || t.topic_family}
                </span>
              </Link>
            ))}
          </div>
        </>
      )}

      <h2>Works in Corpus</h2>
      <div className="works-grid">
        {works &&
          works.map((w) => <WorkCard key={w.work_id} work={w} />)}
      </div>
    </>
  );
}
