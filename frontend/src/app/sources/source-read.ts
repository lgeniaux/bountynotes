import { SourceStatus } from './source-status';

export interface SourceRead {
  id: number;
  title: string | null;
  source_type: string;
  status: SourceStatus;
  error_message: string | null;
  processed_at: string | null;
  raw_content: string;
  clean_content: string | null;
  summary: string | null;
  techs: string[];
  tags: string[];
  cwes: string[];
  cves: string[];
  created_at: string;
  updated_at: string;
}
