export type Mode = "strict" | "friendly";

export interface Document {
  title: string;
  content: string;
  score: number;
}

export interface ApiResponse {
  response: string;
  documents: Document[];
}

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
    throw new Error("Backend request failed");
  }

  return res.json();
}