import { useEffect, useState } from "react";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

type FetchState =
  | { status: "loading" }
  | { status: "ok"; data: unknown }
  | { status: "error"; message: string };

export default function App() {
  const [state, setState] = useState<FetchState>({ status: "loading" });

  useEffect(() => {
    const controller = new AbortController();
    fetch(`${API_BASE_URL}/health/`, { signal: controller.signal })
      .then(async (res) => {
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }
        const data = await res.json();
        setState({ status: "ok", data });
      })
      .catch((e: unknown) => {
        if (e instanceof DOMException && e.name === "AbortError") return;
        setState({
          status: "error",
          message: e instanceof Error ? e.message : String(e),
        });
      });
    return () => controller.abort();
  }, []);

  return (
    <main
      style={{
        fontFamily: "system-ui, sans-serif",
        padding: "2rem",
        maxWidth: 720,
        margin: "0 auto",
      }}
    >
      <h1>fastapi-practice frontend sample</h1>
      <p>
        Backend: <code>{API_BASE_URL}</code>
      </p>
      <h2>
        GET <code>/health/</code>
      </h2>
      {state.status === "loading" && <p>loading...</p>}
      {state.status === "ok" && (
        <pre style={{ background: "#f4f4f4", padding: "1rem" }}>
          {JSON.stringify(state.data, null, 2)}
        </pre>
      )}
      {state.status === "error" && (
        <p style={{ color: "crimson" }}>error: {state.message}</p>
      )}
    </main>
  );
}
