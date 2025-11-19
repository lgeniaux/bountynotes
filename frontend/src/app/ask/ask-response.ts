import { AskCitation } from './ask-citation';

export interface AskResponse {
  answer: string;
  citations: AskCitation[];
}
