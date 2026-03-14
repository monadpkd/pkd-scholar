import { useParams, Link } from 'react-router-dom';
import { useData } from '../hooks/useData';
import type { Segment } from '../types';

export default function SegmentDetail() {
  const { segId } = useParams<{ segId: string }>();
  const { data: segment, loading, error } = useData<Segment>(`segments/${segId}.json`);

  if (loading) return <div className="loading">Loading segment...</div>;
  if (error) return <div className="error">Failed to load segment: {error}</div>;
  if (!segment) return <div className="error">Segment not found</div>;

  return (
    <>
      <div className="breadcrumb">
        <Link to="/">Corpus</Link>
        <span>/</span>
        <Link to={`/works/${segment.work_slug}`}>{segment.work_title}</Link>
        <span>/</span>
        {segment.title || `${segment.segment_type} ${segment.position}`}
      </div>

      <div className="segment-nav">
        {segment.prev_seg_id ? (
          <Link to={`/segments/${segment.prev_seg_id}`}>&larr; Previous</Link>
        ) : (
          <span>&larr; Previous</span>
        )}
        <Link to={`/works/${segment.work_slug}`}>Back to Work</Link>
        {segment.next_seg_id ? (
          <Link to={`/segments/${segment.next_seg_id}`}>Next &rarr;</Link>
        ) : (
          <span>Next &rarr;</span>
        )}
      </div>

      <h1>{segment.title || `${segment.segment_type} ${segment.position}`}</h1>
      <p className="subtitle">
        {segment.work_title}
        {segment.page_start != null && <> &middot; Page {segment.page_start}</>}
        {segment.page_end != null && segment.page_end !== segment.page_start && (
          <>&ndash;{segment.page_end}</>
        )}
        {segment.word_count != null && <> &middot; {segment.word_count.toLocaleString()} words</>}
      </p>

      <div className="segment-content">{segment.raw_text || '(No text available)'}</div>

      <div className="segment-footer">
        Segment ID: <code>{segment.seg_id}</code> &middot; Type:{' '}
        {segment.segment_type.replace('_', ' ')} &middot; Position: {segment.position}
      </div>

      <div className="segment-nav" style={{ marginTop: '1.5rem' }}>
        {segment.prev_seg_id ? (
          <Link to={`/segments/${segment.prev_seg_id}`}>&larr; Previous</Link>
        ) : (
          <span>&larr; Previous</span>
        )}
        <Link to={`/works/${segment.work_slug}`}>Back to Work</Link>
        {segment.next_seg_id ? (
          <Link to={`/segments/${segment.next_seg_id}`}>Next &rarr;</Link>
        ) : (
          <span>Next &rarr;</span>
        )}
      </div>
    </>
  );
}
