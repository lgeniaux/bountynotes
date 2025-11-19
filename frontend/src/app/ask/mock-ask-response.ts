import { AskResponse } from './ask-response';

export const MOCK_ASK_RESPONSE: AskResponse = {
  answer:
    'This is a temporary frontend mock response. Replace it with the live POST /ask call once the backend endpoint is ready.',
  citations: [
    {
      source_id: 1,
      chunk_id: '1-0',
      title: 'Example write-up',
      snippet: 'Matched text from a prepared source chunk appears here.',
      score: 0.82,
    },
  ],
};
