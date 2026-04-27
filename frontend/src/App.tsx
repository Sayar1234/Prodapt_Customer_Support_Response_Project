import { useState } from "react";
import { generateResponse} from "./api"
import type {Mode, Document } from "./api";

export default function App() {
  const [query, setQuery] = useState<string>("");
  const [mode, setMode] = useState<Mode>("strict");
  const [loading, setLoading] = useState<boolean>(false);

  const [response, setResponse] = useState<string>("");
  const [docs, setDocs] = useState<Document[]>([]);

  const handleGenerate = async () => {
  if (!query.trim()) return;

  setLoading(true);
  setResponse("");
  setDocs([]);

  try {
    const data = await generateResponse(query, mode);

    setResponse(data.response ?? "No response returned");
    setDocs(data.documents ?? []);
  } catch (err: any) {
    setResponse(
      err.name === "AbortError"
        ? "Request timed out. Backend is slow or not responding."
        : `Failed to connect to backend: ${err.message || err}`
    );
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="min-h-screen flex flex-col">

      {/* HEADER */}
      <header className="bg-white border-b px-6 py-4 flex justify-between">
        <h1 className="text-xl font-bold">
          AI Support Assistant
        </h1>

        <span className="text-sm text-gray-500">
          FastAPI + OpenRouter + PineconeDB
        </span>
      </header>

      {/* MAIN */}
      <main className="flex flex-1 gap-6 p-6">

        {/* LEFT PANEL */}
        <section className="w-1/2 bg-white rounded-xl shadow p-5">

          <h2 className="font-semibold mb-3">
            Customer Query
          </h2>

          <textarea
            className="w-full h-40 border rounded-lg p-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Enter customer complaint..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />

          <div className="flex justify-between items-center mt-4">

            <select
              className="border rounded-lg px-3 py-2"
              value={mode}
              onChange={(e) => setMode(e.target.value as Mode)}
            >
              <option value="strict">Strict Mode</option>
              <option value="friendly">Friendly Mode</option>
            </select>

            <button
              onClick={handleGenerate}
              className="bg-blue-600 text-white px-5 py-2 rounded-lg hover:bg-blue-700 transition"
            >
              Generate
            </button>

          </div>

          {loading && (
            <p className="mt-4 text-blue-500 animate-pulse">
              Generating response...
            </p>
          )}
        </section>

        {/* RIGHT PANEL */}
        <section className="w-1/2 flex flex-col gap-4">

          {/* RESPONSE */}
          <div className="bg-white rounded-xl shadow p-5 flex-1">
            <h2 className="font-semibold mb-2">
              AI Response
            </h2>

            <div className="bg-gray-50 rounded-lg p-3 h-full overflow-auto text-sm">
              {response || (
                <span className="text-gray-400">
                  Response will appear here...
                </span>
              )}
            </div>
          </div>

          {/* DOCUMENTS */}
          <div className="bg-white rounded-xl shadow p-5 flex-1">
            <h2 className="font-semibold mb-2">
              Retrieved Policies
            </h2>

            <div className="space-y-3 overflow-auto h-full">

              {docs.length === 0 && (
                <p className="text-gray-400 text-sm">
                  No documents yet
                </p>
              )}

              {docs.map((doc, i) => (
                <div
                  key={doc.id || i}
                  className="border rounded-xl p-3 bg-gray-50 hover:bg-gray-100 transition"
                >
                  {/* Header */}
                  <div className="flex justify-between items-center mb-2">
                    <p className="font-semibold text-sm text-gray-800">
                      {doc.title}
                    </p>

                    <span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-600">
                      {(doc.score * 100).toFixed(0)}%
                    </span>
                  </div>

                  {/* Content */}
                  <p className="text-sm text-gray-600">
                    {doc.preview || doc.content.slice(0, 180) + "..."}
                  </p>
                </div>
              ))}

            </div>
          </div>

        </section>
      </main>
    </div>
  );
}