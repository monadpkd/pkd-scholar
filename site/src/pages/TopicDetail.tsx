import { useParams, Link } from 'react-router-dom';
import { useData } from '../hooks/useData';
import type { TopicDetail as TopicDetailType } from '../types';

const FAMILY_LABELS: Record<string, string> = {
  ai_automation: 'AI & Automation',
  metaphysics: 'Metaphysics',
  psychology: 'Psychology',
};

const RELEVANCE_LABELS: Record<string, string> = {
  central: 'Central',
  significant: 'Significant',
  mentioned: 'Mentioned',
  peripheral: 'Peripheral',
};

export default function TopicDetail() {
  const { slug } = useParams<{ slug: string }>();
  const { data: topic, loading, error } = useData<TopicDetailType>(`topics/${slug}.json`);

  if (loading) return <div className="loading">Loading topic...</div>;
  if (error) return <div className="error">Failed to load topic: {error}</div>;
  if (!topic) return <div className="error">Topic not found</div>;

  return (
    <>
      <div className="breadcrumb">
        <Link to="/">Corpus</Link>
        <span>/</span>
        <Link to="/topics">Topics</Link>
        <span>/</span>
        {topic.canonical_name}
      </div>

      <div className="work-header">
        <h1>{topic.canonical_name}</h1>
        <div className="work-meta-grid">
          <div className="meta-item">
            <div className="meta-label">Family</div>
            <div className="meta-value">
              {FAMILY_LABELS[topic.topic_family] || topic.topic_family}
            </div>
          </div>
          {topic.topic_subfamily && (
            <div className="meta-item">
              <div className="meta-label">Subfamily</div>
              <div className="meta-value">{topic.topic_subfamily.replace(/_/g, ' ')}</div>
            </div>
          )}
          <div className="meta-item">
            <div className="meta-label">Matches</div>
            <div className="meta-value">{topic.match_count}</div>
          </div>
          <div className="meta-item">
            <div className="meta-label">Works</div>
            <div className="meta-value">{topic.matched_works.length}</div>
          </div>
          <div className="meta-item">
            <div className="meta-label">Status</div>
            <div className="meta-value">{topic.status}</div>
          </div>
          <div className="meta-item">
            <div className="meta-label">ID</div>
            <div className="meta-value"><code>{topic.topic_id}</code></div>
          </div>
        </div>

        {topic.definition && (
          <div className="topic-definition">
            <strong>Definition:</strong> {topic.definition}
          </div>
        )}

        {topic.pkd_relevance && (
          <div className="topic-definition">
            <strong>PKD Relevance:</strong> {topic.pkd_relevance}
          </div>
        )}

        {topic.aliases.length > 0 && (
          <div className="topic-aliases">
            <strong>Aliases:</strong>{' '}
            {topic.aliases.map((a, i) => (
              <span key={i} className="topic-alias-tag">
                {a.alias}
              </span>
            ))}
          </div>
        )}
      </div>

      {topic.matched_works.length > 0 && (
        <>
          <h2>
            Works{' '}
            <span style={{ fontWeight: 400, fontSize: '0.9rem', color: 'var(--color-text-muted)' }}>
              ({topic.matched_works.length})
            </span>
          </h2>
          <div className="topic-works-list">
            {topic.matched_works.map((w) => (
              <Link
                key={w.work_id}
                to={`/works/${w.slug}`}
                className="topic-work-row"
              >
                <span className="topic-work-title">{w.title}</span>
                <span className="topic-work-year">{w.year_published || ''}</span>
                <span className={`topic-relevance-badge relevance-${w.relevance}`}>
                  {RELEVANCE_LABELS[w.relevance] || w.relevance}
                </span>
                <span className="topic-work-count">{w.match_count} matches</span>
              </Link>
            ))}
          </div>
        </>
      )}

      {topic.matched_segments.length > 0 && (
        <>
          <h2>
            Matched Passages{' '}
            <span style={{ fontWeight: 400, fontSize: '0.9rem', color: 'var(--color-text-muted)' }}>
              ({topic.matched_segments.length}{topic.matched_segments.length >= 100 ? '+' : ''})
            </span>
          </h2>
          <div className="topic-passages">
            {topic.matched_segments.map((seg, i) => (
              <div key={`${seg.seg_id}-${i}`} className="topic-passage">
                <div className="topic-passage-meta">
                  <Link to={`/works/${seg.work_slug}`} className="topic-passage-work">
                    {seg.work_title}
                  </Link>
                  <span className="topic-passage-location">
                    {seg.seg_title || `${seg.segment_type} ${seg.position}`}
                    {seg.page_start != null && ` (p. ${seg.page_start})`}
                  </span>
                </div>
                {seg.context_window && (
                  <div className="topic-passage-context">
                    <HighlightedContext
                      context={seg.context_window}
                      matchedText={seg.matched_text}
                    />
                  </div>
                )}
                <div className="topic-passage-actions">
                  <Link to={`/segments/${seg.seg_id}`} className="topic-passage-link">
                    View full segment
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </>
      )}
    </>
  );
}

function HighlightedContext({
  context,
  matchedText,
}: {
  context: string;
  matchedText: string;
}) {
  if (!matchedText) return <>{context}</>;

  const regex = new RegExp(`(${matchedText.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  const parts = context.split(regex);

  return (
    <>
      {parts.map((part, i) =>
        regex.test(part) ? (
          <mark key={i}>{part}</mark>
        ) : (
          <span key={i}>{part}</span>
        )
      )}
    </>
  );
}
