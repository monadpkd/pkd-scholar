import { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import Fuse from 'fuse.js';
import { useData } from '../hooks/useData';
import type { SearchEntry } from '../types';

const MAX_RESULTS = 50;

export default function Search() {
  const { data: index, loading, error } = useData<SearchEntry[]>('search_index.json');
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchEntry[]>([]);

  const fuse = useMemo(() => {
    if (!index) return null;
    return new Fuse(index, {
      keys: [
        { name: 'title', weight: 2 },
        { name: 'preview', weight: 1 },
        { name: 'work_title', weight: 0.5 },
      ],
      threshold: 0.4,
      includeScore: true,
      ignoreLocation: true,
      minMatchCharLength: 2,
    });
  }, [index]);

  useEffect(() => {
    if (!fuse || !query.trim()) {
      setResults([]);
      return;
    }
    const hits = fuse.search(query.trim(), { limit: MAX_RESULTS });
    setResults(hits.map((h) => h.item));
  }, [fuse, query]);

  if (loading) return <div className="loading">Loading search index...</div>;
  if (error) return <div className="error">Failed to load search index: {error}</div>;

  return (
    <>
      <h1>Search Corpus</h1>
      <p className="subtitle">Fuzzy search across {index?.length.toLocaleString()} segments</p>

      <div className="search-input-wrapper">
        <input
          className="search-input"
          type="text"
          placeholder="Search by title, text content, or work name..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          autoFocus
        />
      </div>

      {query.trim() && (
        <div className="search-meta">
          {results.length === 0
            ? 'No results found.'
            : `${results.length} result${results.length !== 1 ? 's' : ''} found`}
        </div>
      )}

      <div>
        {results.map((r) => (
          <div key={r.seg_id} className="search-result">
            <div className="search-result-title">
              <Link to={`/segments/${r.seg_id}`}>
                {r.title || r.seg_id}
              </Link>
            </div>
            <div className="search-result-work">
              <Link to={`/works/${r.work_slug}`}>{r.work_title}</Link>
            </div>
            {r.preview && (
              <div className="search-result-preview">
                {r.preview.slice(0, 200)}
                {r.preview.length >= 200 ? '...' : ''}
              </div>
            )}
          </div>
        ))}
      </div>
    </>
  );
}
