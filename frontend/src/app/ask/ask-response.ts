import { AskCitation } from './ask-citation';

export interface AskResponse {
  answer: string | null;
  citations: AskCitation[];
}
