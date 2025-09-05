import React, { useState, useEffect } from "react";
import Splash from "./Splash"; 

export default function TranscriptApp() {
  const [showSplash, setShowSplash] = useState(true);
  const [url, setUrl] = useState("");
  const [transcript, setTranscript] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("full");
  const [aiBullets, setAiBullets] = useState(null);
  const [aiSummary, setAiSummary] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [copyFeedback, setCopyFeedback] = useState("");

  // 🔹 Update document title depending on screen
  useEffect(() => {
    if (showSplash) {
      document.title = "Welcome | NoteMate";
    } else {
      document.title = "NoteMate";
    }
  }, [showSplash]);

  // Copy to clipboard function
  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopyFeedback("✅ Copied!");
      setTimeout(() => setCopyFeedback(""), 2000);
    } catch (err) {
      setCopyFeedback("❌ Copy failed");
      setTimeout(() => setCopyFeedback(""), 2000);
    }
  };

  // Download as text file function
  const downloadAsText = (content, filename) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Get current content based on active tab
  const getCurrentContent = () => {
    if (!transcript) return "";
    
    switch (activeTab) {
      case "full":
        return transcript.full_text;
      case "bullets":
        return transcript.bullet_points?.join('\n• ') || "";
      case "timestamps":
        return transcript.timestamps?.map(t => `${t.time} — ${t.text}`).join('\n') || "";
      case "ai-bullets":
        return aiBullets?.join('\n• ') || "";
      case "ai-summary":
        return aiSummary || "";
      default:
        return "";
    }
  };

  // Get filename based on active tab
  const getFilename = () => {
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    switch (activeTab) {
      case "full":
        return `transcript-full-${timestamp}.txt`;
      case "bullets":
        return `transcript-bullets-${timestamp}.txt`;
      case "timestamps":
        return `transcript-timestamps-${timestamp}.txt`;
      case "ai-bullets":
        return `transcript-ai-bullets-${timestamp}.txt`;
      case "ai-summary":
        return `transcript-ai-summary-${timestamp}.txt`;
      default:
        return `transcript-${timestamp}.txt`;
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setTranscript(null);

    try {
      const response = await fetch("http://127.0.0.1:5000/transcribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch transcription.");
      }

      const data = await response.json();
      setTranscript(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAiBullets = async () => {
    if (!transcript?.full_text) return;
    
    setAiLoading(true);
    setError(null);
    
    try {
      const response = await fetch("http://127.0.0.1:5000/ai-bullets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: transcript.full_text }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate AI bullets.");
      }

      const data = await response.json();
      setAiBullets(data.ai_bullets);
    } catch (err) {
      setError(err.message);
    } finally {
      setAiLoading(false);
    }
  };

  const handleAiSummary = async () => {
    if (!transcript?.full_text) return;
    
    setAiLoading(true);
    setError(null);
    
    try {
      const response = await fetch("http://127.0.0.1:5000/ai-summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: transcript.full_text }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate AI summary.");
      }

      const data = await response.json();
      setAiSummary(data.ai_summary);
    } catch (err) {
      setError(err.message);
    } finally {
      setAiLoading(false);
    }
  };

  // 🔹 Show splash first, then main app
  if (showSplash) {
    return <Splash onFinish={() => setShowSplash(false)} />;
  }

  return (
    <div className="relative min-h-screen flex items-center justify-center overflow-hidden font-poppins">
      {/* Background gradient animation */}
      <div className="absolute inset-0 bg-gradient-to-r from-purple-500 via-pink-500 to-yellow-500 animate-gradient-x opacity-90"></div>

      {/* Content Card */}
      <div className="relative z-10 max-w-3xl w-full bg-white/90 rounded-3xl shadow-2xl p-10 backdrop-blur-lg">
        <h1 className="text-5xl font-extrabold text-center text-gray-900 mb-8 tracking-tight drop-shadow-lg">
          NoteMate
        </h1>

        {/* Input Form */}
        <form
          onSubmit={handleSubmit}
          className="flex flex-col sm:flex-row gap-4 mb-8"
        >
          <input
            type="text"
            placeholder="Paste YouTube link..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            className="flex-1 p-4 border border-gray-300 rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-4 bg-purple-600 text-white font-semibold rounded-xl shadow-lg hover:bg-purple-700 transition disabled:opacity-50"
          >
            {loading ? "Transcribing..." : "Transcribe"}
          </button>
        </form>

        {/* Error Message */}
        {error && (
          <p className="text-red-600 text-center mb-6 font-medium">{error}</p>
        )}

        {/* Transcript Result */}
        {transcript && (
          <>
            {/* Tabs */}
            <div className="flex justify-center gap-4 mb-6">
              <button
                onClick={() => setActiveTab("full")}
                className={`px-5 py-2 rounded-xl font-medium ${
                  activeTab === "full"
                    ? "bg-purple-600 text-white shadow-md"
                    : "bg-gray-200 text-gray-800"
                }`}
              >
                📜 Full Transcript
              </button>
              <button
                onClick={() => setActiveTab("bullets")}
                className={`px-5 py-2 rounded-xl font-medium ${
                  activeTab === "bullets"
                    ? "bg-purple-600 text-white shadow-md"
                    : "bg-gray-200 text-gray-800"
                }`}
              >
                🔘 Bullet Points
              </button>
              <button
                onClick={() => setActiveTab("timestamps")}
                className={`px-5 py-2 rounded-xl font-medium ${
                  activeTab === "timestamps"
                    ? "bg-purple-600 text-white shadow-md"
                    : "bg-gray-200 text-gray-800"
                }`}
              >
                ⏱️ Timestamped
              </button>
              <button
                onClick={() => {
                  setActiveTab("ai-bullets");
                  if (!aiBullets) handleAiBullets();
                }}
                className={`px-5 py-2 rounded-xl font-medium ${
                  activeTab === "ai-bullets"
                    ? "bg-purple-600 text-white shadow-md"
                    : "bg-gray-200 text-gray-800"
                }`}
              >
                🤖 AI Bullets
              </button>
              <button
                onClick={() => {
                  setActiveTab("ai-summary");
                  if (!aiSummary) handleAiSummary();
                }}
                className={`px-5 py-2 rounded-xl font-medium ${
                  activeTab === "ai-summary"
                    ? "bg-purple-600 text-white shadow-md"
                    : "bg-gray-200 text-gray-800"
                }`}
              >
                📝 AI Summary
              </button>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-center gap-3 mb-4">
              <button
                onClick={() => copyToClipboard(getCurrentContent())}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition flex items-center gap-2"
              >
                📋 Copy
              </button>
              <button
                onClick={() => downloadAsText(getCurrentContent(), getFilename())}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition flex items-center gap-2"
              >
                💾 Download
              </button>
            </div>

            {/* Copy Feedback */}
            {copyFeedback && (
              <div className="text-center mb-4">
                <span className="text-sm font-medium text-gray-700">{copyFeedback}</span>
              </div>
            )}

            {/* Transcript Output */}
            <div className="p-5 bg-gray-50 rounded-2xl shadow-inner max-h-[450px] overflow-y-auto">
              {activeTab === "full" && (
                <pre className="whitespace-pre-wrap text-gray-900 text-lg leading-relaxed">
                  {transcript.full_text}
                </pre>
              )}
              {activeTab === "bullets" && (
                <ul className="list-disc pl-6 space-y-2 text-gray-900 text-lg">
                  {transcript.bullet_points?.map((point, i) => (
                    <li key={i}>{point}</li>
                  ))}
                </ul>
              )}
              {activeTab === "timestamps" && (
                <ul className="space-y-2 text-gray-900 text-lg">
                  {transcript.timestamps?.map((t, i) => (
                    <li key={i}>
                      <span className="font-bold text-purple-700">
                        {t.time}
                      </span>{" "}
                      — {t.text}
                    </li>
                  ))}
                </ul>
              )}
              {activeTab === "ai-bullets" && (
                <div>
                  {aiLoading ? (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto mb-4"></div>
                      <p className="text-gray-600">Generating AI bullets...</p>
                    </div>
                  ) : aiBullets ? (
                    <ul className="list-disc pl-6 space-y-2 text-gray-900 text-lg">
                      {aiBullets.map((point, i) => (
                        <li key={i}>{point}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-gray-600 text-center py-8">Click the AI Bullets tab to generate intelligent bullet points</p>
                  )}
                </div>
              )}
              {activeTab === "ai-summary" && (
                <div>
                  {aiLoading ? (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto mb-4"></div>
                      <p className="text-gray-600">Generating AI summary...</p>
                    </div>
                  ) : aiSummary ? (
                    <pre className="whitespace-pre-wrap text-gray-900 text-lg leading-relaxed">
                      {aiSummary}
                    </pre>
                  ) : (
                    <p className="text-gray-600 text-center py-8">Click the AI Summary tab to generate a comprehensive summary</p>
                  )}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
