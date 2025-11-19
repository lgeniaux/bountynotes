import { AskFilters } from './ask-filters';

export interface AskRequest {
  query: string;
  filters: AskFilters;
}
