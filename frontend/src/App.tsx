import { useEffect, useMemo, useState, type FormEvent } from "react";

import { ApiError, createApiClient, type UserPublic } from "./api/client";
import { API_BASE_URL } from "./api/config";
import { ME_QUERY, type MeResult } from "./api/graphql";

const TOKEN_KEY = "fastapi-practice.token";

function readToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

function writeToken(token: string | null) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    // プライベートウィンドウ等で使えないときはメモリ上だけで持つ
  }
}

function errorMessage(e: unknown): string {
  if (e instanceof ApiError && typeof e.detail === "string") return e.detail;
  return e instanceof Error ? e.message : String(e);
}

type Me = { rest: UserPublic; graphql: MeResult["me"] };

export default function App({ baseUrl = API_BASE_URL }: { baseUrl?: string }) {
  const [token, setToken] = useState<string | null>(readToken);
  const api = useMemo(() => createApiClient({ baseUrl, getToken: () => token }), [baseUrl, token]);

  const [health, setHealth] = useState<string>("loading...");
  const [me, setMe] = useState<Me | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [mode, setMode] = useState<"login" | "signup">("login");

  useEffect(() => {
    const controller = new AbortController();
    createApiClient({ baseUrl, signal: controller.signal })
      .health()
      .then(
        (data) => setHealth(JSON.stringify(data)),
        (e: unknown) => {
          if (e instanceof DOMException && e.name === "AbortError") return;
          setHealth(`error: ${errorMessage(e)}`);
        },
      );
    return () => controller.abort();
  }, [baseUrl]);

  // トークンがあれば REST と GraphQL の両方でログイン中のユーザを取る
  useEffect(() => {
    if (!token) {
      setMe(null);
      return;
    }
    let cancelled = false;
    Promise.all([api.me(), api.graphql<MeResult>(ME_QUERY)]).then(
      ([rest, gql]) => {
        if (!cancelled) setMe({ rest, graphql: gql.me });
      },
      (e: unknown) => {
        if (cancelled) return;
        // 期限切れ等。トークンを捨ててログイン画面に戻す
        setError(errorMessage(e));
        setToken(null);
        writeToken(null);
      },
    );
    return () => {
      cancelled = true;
    };
  }, [api, token]);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const email = String(form.get("email"));
    const password = String(form.get("password"));
    setError(null);
    try {
      if (mode === "signup") {
        await api.signup({ name: String(form.get("name")), email, password });
      }
      const { access_token } = await api.login(email, password);
      writeToken(access_token);
      setToken(access_token);
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  function logout() {
    writeToken(null);
    setToken(null);
  }

  return (
    <main style={{ fontFamily: "system-ui, sans-serif", padding: "2rem", maxWidth: 720, margin: "0 auto" }}>
      <h1>fastapi-practice frontend sample</h1>
      <p>
        Backend: <code>{baseUrl}</code>
      </p>
      <p>
        GET <code>/health/</code>: <code data-testid="health">{health}</code>
      </p>

      {error && (
        <p role="alert" style={{ color: "crimson" }}>
          {error}
        </p>
      )}

      {me ? (
        <section aria-label="ログイン中">
          <h2>ようこそ、{me.rest.name} さん</h2>
          <p>
            REST <code>GET /users/me</code>: <code>{me.rest.email}</code>
          </p>
          <p>
            GraphQL <code>{"{ me { email } }"}</code>: <code>{me.graphql.email}</code>
          </p>
          <button type="button" onClick={logout}>
            ログアウト
          </button>
        </section>
      ) : (
        <form onSubmit={onSubmit} aria-label={mode === "login" ? "ログイン" : "新規登録"}>
          <h2>{mode === "login" ? "ログイン" : "新規登録"}</h2>
          {mode === "signup" && (
            <label>
              名前 <input name="name" required />
            </label>
          )}
          <label>
            メールアドレス <input name="email" type="email" required />
          </label>
          <label>
            パスワード <input name="password" type="password" minLength={8} required />
          </label>
          <button type="submit">{mode === "login" ? "ログイン" : "登録してログイン"}</button>
          <button type="button" onClick={() => setMode(mode === "login" ? "signup" : "login")}>
            {mode === "login" ? "新規登録へ" : "ログインへ"}
          </button>
        </form>
      )}
    </main>
  );
}
