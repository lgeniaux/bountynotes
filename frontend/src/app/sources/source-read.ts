export interface SourceRead {
  id: number;
  title: string | null;
  source_type: string;
  status: string;
  raw_content: string;
  clean_content: string | null;
  summary: string | null;
  created_at: string;
  updated_at: string;
}
