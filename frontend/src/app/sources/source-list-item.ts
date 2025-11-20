import { SourceStatus } from './source-status';

export interface SourceListItem {
  id: number;
  title: string | null;
  source_type: string;
  status: SourceStatus;
  error_message: string | null;
  processed_at: string | null;
  created_at: string;
  updated_at: string;
}
