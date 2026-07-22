"use client";

import { useState } from "react";

interface Step {
  tool: string;
  arguments: Record<string, unknown>;
  result: Record<string, unknown>;
}

interface ChatResponse {
  conversation_id: string;
  task_id: string;
  response: string;
  steps: Step[];
}

export default function Home() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<{ role: string; content: string; steps?: Step[] }[]>([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage }),
      });
      const data: ChatResponse = await res.json();

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.response, steps: data.steps },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "抱歉，發生了錯誤。請稍後再試。" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: 24, fontFamily: "system-ui" }}>
      <h1 style={{ fontSize: 24, marginBottom: 16 }}>AI Agent Platform</h1>
      <p style={{ color: "#666", marginBottom: 24 }}>新員工入職自動化 — 試試輸入：「新員工張小明明天入職市場部擔任產品經理」</p>

      <div style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16, minHeight: 400, marginBottom: 16 }}>
        {messages.map((msg, i) => (
          <div key={i} style={{ marginBottom: 16 }}>
            <div style={{ fontWeight: "bold", color: msg.role === "user" ? "#0066cc" : "#009933" }}>
              {msg.role === "user" ? "You" : "Agent"}
            </div>
            <div style={{ marginTop: 4, whiteSpace: "pre-wrap" }}>{msg.content}</div>
            {msg.steps && msg.steps.length > 0 && (
              <details style={{ marginTop: 8, color: "#666", fontSize: 14 }}>
                <summary>執行步驟 ({msg.steps.length})</summary>
                <ul style={{ marginTop: 8 }}>
                  {msg.steps.map((step, j) => (
                    <li key={j}>
                      <code>{step.tool}</code>
                    </li>
                  ))}
                </ul>
              </details>
            )}
          </div>
        ))}
        {loading && <div style={{ color: "#999" }}>Agent 正在處理中...</div>}
      </div>

      <div style={{ display: "flex", gap: 8 }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="輸入任務..."
          style={{ flex: 1, padding: 12, fontSize: 16, border: "1px solid #ddd", borderRadius: 4 }}
          disabled={loading}
        />
        <button
          onClick={sendMessage}
          disabled={loading}
          style={{ padding: "12px 24px", fontSize: 16, background: "#0066cc", color: "white", border: "none", borderRadius: 4, cursor: "pointer" }}
        >
          發送
        </button>
      </div>
    </div>
  );
}
