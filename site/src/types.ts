export interface Work {
  work_id: string;
  title: string;
  slug: string;
  work_type: string;
  source_lane: string;
  author: string;
  year_published: number | null;
  page_count: number | null;
  extraction_status: string;
  notes: string | null;
  segment_count: number;
  total_word_count: number;
}

export interface WorkTopic {
  topic_id: string;
  canonical_name: string;
  slug: string;
  topic_family: string;
  topic_subfamily: string | null;
  relevance: string;
  match_count: number;
}

export interface WorkDetail extends Work {
  segments: SegmentSummary[];
  topics: WorkTopic[];
}

export interface SegmentSummary {
  seg_id: string;
  title: string | null;
  segment_type: string;
  position: number;
  page_start: number | null;
  page_end: number | null;
  word_count: number | null;
}

export interface Segment {
  seg_id: string;
  work_id: string;
  title: string | null;
  segment_type: string;
  position: number;
  page_start: number | null;
  page_end: number | null;
  raw_text: string | null;
  word_count: number | null;
  work_title: string;
  work_slug: string;
  prev_seg_id: string | null;
  next_seg_id: string | null;
}

export interface SearchEntry {
  seg_id: string;
  work_id: string;
  title: string | null;
  preview: string | null;
  work_title: string;
  work_slug: string;
}

export interface TopicSummary {
  topic_id: string;
  canonical_name: string;
  slug: string;
  topic_family: string;
  topic_subfamily: string | null;
  definition: string | null;
  pkd_relevance: string | null;
  status: string;
  match_count: number;
}

export interface TopicMatchedSegment {
  seg_id: string;
  match_type: string;
  matched_text: string;
  context_window: string | null;
  seg_title: string | null;
  segment_type: string;
  position: number;
  page_start: number | null;
  page_end: number | null;
  work_title: string;
  work_slug: string;
  work_id: string;
}

export interface TopicMatchedWork {
  work_id: string;
  title: string;
  slug: string;
  year_published: number | null;
  relevance: string;
  match_count: number;
}

export interface TopicAlias {
  alias: string;
  alias_type: string;
}

export interface TopicDetail {
  topic_id: string;
  canonical_name: string;
  slug: string;
  topic_family: string;
  topic_subfamily: string | null;
  definition: string | null;
  pkd_relevance: string | null;
  status: string;
  match_count: number;
  aliases: TopicAlias[];
  matched_works: TopicMatchedWork[];
  matched_segments: TopicMatchedSegment[];
}

export interface Stats {
  total_works: number;
  total_segments: number;
  total_words: number;
  total_topics: number;
  total_topic_matches: number;
  extraction_status: Record<string, number>;
  work_types: Record<string, number>;
  segment_types: Record<string, number>;
  top_topics: TopicSummary[];
}
