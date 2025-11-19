export interface AskCitation {
  source_id: number;
  chunk_id: string;
  title: string | null;
  snippet: string;
  score: number;
  source_type: string | null;
  summary: string | null;
  techs: string[];
  tags: string[];
  cwes: string[];
  cves: string[];
  start_offset: number | null;
  end_offset: number | null;
}
