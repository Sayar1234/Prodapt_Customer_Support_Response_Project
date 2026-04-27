export type Mode = "strict" | "friendly";

export interface Document {
  id?: string;          
  title: string;
  content: string;
  score: number;
  preview?: string;     
}

export interface ApiResponse {
  response: string;
  documents: Document[];
}

// 🔥 IMPORTANT: change this if backend URL changes
// const API_BASE = "http://localhost:8000";

export async function generateResponse(
  query: string,
  mode: Mode
): Promise<ApiResponse> {
  const res = await fetch("http://localhost:8000/generate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ query, mode })
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(errorText || "Backend request failed");
  }

  return res.json();
}