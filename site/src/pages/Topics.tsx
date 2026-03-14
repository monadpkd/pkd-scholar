import { useState, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { useData } from '../hooks/useData';
import type { TopicSummary } from '../types';

const FAMILY_LABELS: Record<string, string> = {
  ai_automation: 'AI & Automation',
  metaphysics: 'Metaphysics',
  psychology: 'Psychology',
};

const SUBFAMILY_COLORS: Record<string, string> = {
  machine_role: '#e74c3c',
  human_response: '#e67e22',
  core_concepts: '#3498db',
  android_identity: '#9b59b6',
  artificial_intelligence: '#2980b9',
  automation_and_labor: '#f39c12',
  economic_systems: '#e74c3c',
  psychological_regulation: '#1abc9c',
  reality_instability: '#8e44ad',
  surveillance_and_control: '#c0392b',
  cybernetics_general: '#2c3e50',
  political_systems: '#d35400',
  reality: '#8e44ad',
  consciousness: '#2ecc71',
  altered_states: '#e91e63',
  mortality: '#607d8b',
  clinical_descriptive: '#00bcd4',
};

export default function Topics() {
  const { data: topics, loading, error } = useData<TopicSummary[]>('topics/index.json');
  const [familyFilter, setFamilyFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const families = useMemo(() => {
    if (!topics) return [];
    const fams = new Set(topics.map((t) => t.topic_family));
    return Array.from(fams).sort();
  }, [topics]);

  const filtered = useMemo(() => {
    if (!topics) return [];
    let result = topics;
    if (familyFilter !== 'all') {
      result = result.filter((t) => t.topic_family === familyFilter);
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      result = result.filter(
        (t) =>
          t.canonical_name.toLowerCase().includes(q) ||
          (t.definition && t.definition.toLowerCase().includes(q))
      );
    }
    return result;
  }, [topics, familyFilter, searchQuery]);

  if (loading) return <div className="loading">Loading topics...</div>;
  if (error) return <div className="error">Failed to load topics: {error}</div>;

  const withMatches = filtered.filter((t) => t.match_count > 0);
  const withoutMatches = filtered.filter((t) => t.match_count === 0);

  return (
    <>
      <h1>Topics</h1>
      <p className="subtitle">
        {topics?.length} controlled vocabulary terms across {families.length} topic families.{' '}
        {topics?.filter((t) => t.match_count > 0).length} topics with matches in the corpus.
      </p>

      <div className="topics-controls">
        <div className="search-input-wrapper">
          <input
            className="search-input"
            type="text"
            placeholder="Filter topics by name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="filter-buttons">
          <button
            className={`filter-btn ${familyFilter === 'all' ? 'active' : ''}`}
            onClick={() => setFamilyFilter('all')}
          >
            All ({topics?.length})
          </button>
          {families.map((fam) => (
            <button
              key={fam}
              className={`filter-btn ${familyFilter === fam ? 'active' : ''}`}
              onClick={() => setFamilyFilter(fam)}
            >
              {FAMILY_LABELS[fam] || fam} ({topics?.filter((t) => t.topic_family === fam).length})
            </button>
          ))}
        </div>
      </div>

      {withMatches.length > 0 && (
        <>
          <h2>
            Topics with Matches{' '}
            <span style={{ fontWeight: 400, fontSize: '0.9rem', color: 'var(--color-text-muted)' }}>
              ({withMatches.length})
            </span>
          </h2>
          <div className="topics-grid">
            {withMatches.map((topic) => (
              <TopicCard key={topic.topic_id} topic={topic} />
            ))}
          </div>
        </>
      )}

      {withoutMatches.length > 0 && (
        <>
          <h2>
            Unmatched Topics{' '}
            <span style={{ fontWeight: 400, fontSize: '0.9rem', color: 'var(--color-text-muted)' }}>
              ({withoutMatches.length})
            </span>
          </h2>
          <div className="topics-grid">
            {withoutMatches.map((topic) => (
              <TopicCard key={topic.topic_id} topic={topic} />
            ))}
          </div>
        </>
      )}
    </>
  );
}

function TopicCard({ topic }: { topic: TopicSummary }) {
  const badgeColor = topic.topic_subfamily
    ? SUBFAMILY_COLORS[topic.topic_subfamily] || '#95a5a6'
    : '#95a5a6';

  return (
    <Link to={`/topics/${topic.slug}`} className="topic-card">
      <div className="topic-card-header">
        <span className="topic-name">{topic.canonical_name}</span>
        {topic.match_count > 0 && (
          <span className="topic-match-count">{topic.match_count}</span>
        )}
      </div>
      <div className="topic-card-badges">
        <span className="topic-family-badge">
          {FAMILY_LABELS[topic.topic_family] || topic.topic_family}
        </span>
        {topic.topic_subfamily && (
          <span
            className="topic-subfamily-badge"
            style={{ backgroundColor: badgeColor }}
          >
            {topic.topic_subfamily.replace(/_/g, ' ')}
          </span>
        )}
      </div>
      {topic.definition && (
        <div className="topic-card-def">
          {topic.definition.length > 120
            ? topic.definition.slice(0, 120) + '...'
            : topic.definition}
        </div>
      )}
    </Link>
  );
}
