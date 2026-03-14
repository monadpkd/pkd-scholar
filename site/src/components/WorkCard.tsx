import { Link } from 'react-router-dom';
import type { Work } from '../types';

function formatNumber(n: number): string {
  if (n >= 1000) return `${(n / 1000).toFixed(n >= 10000 ? 0 : 1)}K`;
  return n.toString();
}

export default function WorkCard({ work }: { work: Work }) {
  return (
    <div className="work-card">
      <Link to={`/works/${work.slug}`}>
        <div className="work-card-title">{work.title}</div>
        <div className="work-card-meta">
          <span className="tag tag-type">{work.work_type.replace('_', ' ')}</span>
          {work.year_published && (
            <span className="tag tag-year">{work.year_published}</span>
          )}
          <span className={`tag tag-status-${work.extraction_status}`}>
            {work.extraction_status.replace('_', ' ')}
          </span>
        </div>
        <div className="work-card-stats">
          {work.page_count && <>{work.page_count} pages &middot; </>}
          {work.segment_count} segments &middot;{' '}
          {formatNumber(work.total_word_count)} words
        </div>
      </Link>
    </div>
  );
}
