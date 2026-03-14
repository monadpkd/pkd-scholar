import { useParams, Link } from 'react-router-dom';
import { useState } from 'react';
import { useData } from '../hooks/useData';
import SegmentPreview from '../components/SegmentPreview';
import type { WorkDetail as WorkDetailType } from '../types';

const SEGMENTS_PER_PAGE = 25;

const RELEVANCE_LABELS: Record<string, string> = {
  central: 'Central',
  significant: 'Significant',
  mentioned: 'Mentioned',
  peripheral: 'Peripheral',
};

export default function WorkDetail() {
  const { slug } = useParams<{ slug: string }>();
  const { data: work, loading, error } = useData<WorkDetailType>(`works/${slug}.json`);
  const [page, setPage] = useState(1);

  if (loading) return <div className="loading">Loading work...</div>;
  if (error) return <div className="error">Failed to load work: {error}</div>;
  if (!work) return <div className="error">Work not found</div>;

  const totalPages = Math.ceil(work.segments.length / SEGMENTS_PER_PAGE);
  const startIdx = (page - 1) * SEGMENTS_PER_PAGE;
  const visibleSegments = work.segments.slice(startIdx, startIdx + SEGMENTS_PER_PAGE);

  return (
    <>
      <div className="breadcrumb">
        <Link to="/">Corpus</Link>
        <span>/</span>
        {work.title}
      </div>

      <div className="work-header">
        <h1>{work.title}</h1>
        <div className="work-meta-grid">
          <div className="meta-item">
            <div className="meta-label">Author</div>
            <div className="meta-value">{work.author}</div>
          </div>
          <div className="meta-item">
            <div className="meta-label">Type</div>
            <div className="meta-value">{work.work_type.replace('_', ' ')}</div>
          </div>
          {work.year_published && (
            <div className="meta-item">
              <div className="meta-label">Year</div>
              <div className="meta-value">{work.year_published}</div>
            </div>
          )}
          {work.page_count && (
            <div className="meta-item">
              <div className="meta-label">Pages</div>
              <div className="meta-value">{work.page_count}</div>
            </div>
          )}
          <div className="meta-item">
            <div className="meta-label">Segments</div>
            <div className="meta-value">{work.segment_count}</div>
          </div>
          <div className="meta-item">
            <div className="meta-label">Words</div>
            <div className="meta-value">{work.total_word_count.toLocaleString()}</div>
          </div>
          <div className="meta-item">
            <div className="meta-label">Status</div>
            <div className="meta-value">{work.extraction_status.replace('_', ' ')}</div>
          </div>
          <div className="meta-item">
            <div className="meta-label">Source Lane</div>
            <div className="meta-value">Lane {work.source_lane}</div>
          </div>
        </div>
        {work.notes && (
          <div style={{ marginTop: '1rem', fontSize: '0.9rem', color: 'var(--color-text-muted)' }}>
            {work.notes}
          </div>
        )}
      </div>

      {work.topics && work.topics.length > 0 && (
        <>
          <h2>
            Topics Found{' '}
            <span style={{ fontWeight: 400, fontSize: '0.9rem', color: 'var(--color-text-muted)' }}>
              ({work.topics.length})
            </span>
          </h2>
          <div className="work-topics-list">
            {work.topics.map((t) => (
              <Link
                key={t.topic_id}
                to={`/topics/${t.slug}`}
                className="work-topic-row"
              >
                <span className="work-topic-name">{t.canonical_name}</span>
                <span className={`topic-relevance-badge relevance-${t.relevance}`}>
                  {RELEVANCE_LABELS[t.relevance] || t.relevance}
                </span>
                <span className="work-topic-count">{t.match_count} matches</span>
              </Link>
            ))}
          </div>
        </>
      )}

      <h2>
        Segments{' '}
        <span style={{ fontWeight: 400, fontSize: '0.9rem', color: 'var(--color-text-muted)' }}>
          ({work.segments.length} total)
        </span>
      </h2>

      <ul className="segment-list">
        {visibleSegments.map((seg) => (
          <SegmentPreview key={seg.seg_id} segment={seg} />
        ))}
      </ul>

      {totalPages > 1 && (
        <div className="pagination">
          <button disabled={page <= 1} onClick={() => setPage(page - 1)}>
            Previous
          </button>
          <span className="pagination-info">
            Page {page} of {totalPages}
          </span>
          <button disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
            Next
          </button>
        </div>
      )}
    </>
  );
}
