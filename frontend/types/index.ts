export interface Citation {
  chunk_index: number;
  document_name: string;
  snippet: string;
}

export interface GeneratedAnswer {
  question_id: number;
  question: string;
  answer: string;
  confidence_score: number;
  citations?: Citation[];
}

export interface Session {
  session_id: number;
  session_name: string;
  created_at: string;
}