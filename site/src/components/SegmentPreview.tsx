import { Link } from 'react-router-dom';
import type { SegmentSummary } from '../types';
import { useState, useEffect } from 'react';

const BASE = import.meta.env.BASE_URL;

interface Props {
  segment: SegmentSummary;
}

export default function SegmentPreview({ segment }: Props) {
  const [preview, setPreview] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${BASE}data/segments/${segment.seg_id}.json`)
      .then((r) => r.json())
      .then((data) => {
        const text = data.raw_text || '';
        setPreview(text.slice(0, 300) + (text.length > 300 ? '...' : ''));
      })
      .catch(() => setPreview(null));
  }, [segment.seg_id]);

  return (
    <li className="segment-preview">
      <div className="segment-preview-header">
        <div className="segment-preview-title">
          <Link to={`/segments/${segment.seg_id}`}>
            {segment.title || `${segment.segment_type} ${segment.position}`}
          </Link>
        </div>
        <div className="segment-preview-meta">
          {segment.page_start != null && <>p. {segment.page_start}</>}
          {segment.word_count != null && <> &middot; {segment.word_count.toLocaleString()} words</>}
        </div>
      </div>
      {preview && <div className="segment-preview-text">{preview}</div>}
    </li>
  );
}
