import { useEffect, useMemo, useState, type FormEvent } from "react";

import { createApiClient, type ApiClient, type User } from "./api/client";
import { API_BASE_URL } from "./api/config";
import { ME_QUERY, type MeResult } from "./api/graphql";
import { errorMessage } from "./api/messages";

export const TOKEN_KEY = "fastapi-practice.token";

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

const field = (form: FormData, name: string) => String(form.get(name) ?? "");

export default function App({ baseUrl = API_BASE_URL }: { baseUrl?: string }) {
  const [token, setTokenState] = useState<string | null>(readToken);
  const api = useMemo(() => createApiClient({ baseUrl, getToken: () => token }), [baseUrl, token]);

  const [health, setHealth] = useState("loading...");
  const [me, setMe] = useState<User | null>(null);
  const [gqlEmail, setGqlEmail] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  function setToken(next: string | null) {
    writeToken(next);
    setTokenState(next);
  }

  /** 失敗したらエラーを出す。成功時のお知らせは notice */
  async function run(action: () => Promise<unknown>, done?: string) {
    setError(null);
    setNotice(null);
    try {
      await action();
      if (done) setNotice(done);
    } catch (e) {
      setError(errorMessage(e));
    }
  }

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

  // トークンがあれば REST（/users/me）と GraphQL（me）の両方でログイン中のユーザを取る
  useEffect(() => {
    if (!token) {
      setMe(null);
      setGqlEmail(null);
      return;
    }
    let cancelled = false;
    Promise.all([api.me(), api.graphql<MeResult>(ME_QUERY)]).then(
      ([rest, gql]) => {
        if (cancelled) return;
        setMe(rest);
        setGqlEmail(gql.me.email);
      },
      (e: unknown) => {
        if (cancelled) return;
        setError(errorMessage(e)); // 期限切れ・ログアウト済み等。ログイン画面に戻す
        setToken(null);
      },
    );
    return () => {
      cancelled = true;
    };
  }, [api, token]);

  return (
    <main style={{ fontFamily: "system-ui, sans-serif", padding: "2rem", maxWidth: 720, margin: "0 auto" }}>
      <h1>fastapi-practice frontend sample</h1>
      <p>
        Backend: <code>{baseUrl}</code> / GET <code>/health/</code>: <code data-testid="health">{health}</code>
      </p>

      {error && (
        <p role="alert" style={{ color: "crimson" }}>
          {error}
        </p>
      )}
      {notice && <p role="status">{notice}</p>}

      {me ? (
        <SignedIn
          api={api}
          me={me}
          gqlEmail={gqlEmail}
          run={run}
          onUpdated={setMe}
          onSignedOut={() => setToken(null)}
        />
      ) : (
        <SignedOut api={api} run={run} onSignedIn={setToken} />
      )}
    </main>
  );
}

type Run = (action: () => Promise<unknown>, done?: string) => Promise<void>;

function SignedOut({ api, run, onSignedIn }: { api: ApiClient; run: Run; onSignedIn: (token: string) => void }) {
  const [mode, setMode] = useState<"login" | "register" | "forgot">("login");
  const title = { login: "ログイン", register: "新規登録", forgot: "パスワードを忘れた" }[mode];

  function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    const email = field(form, "email");
    const password = field(form, "password");
    if (mode === "forgot") {
      void run(() => api.auth.forgotPassword(email), "登録済みなら、再設定のメールを送りました");
      return;
    }
    void run(async () => {
      if (mode === "register") await api.auth.register({ name: field(form, "name"), email, password });
      onSignedIn((await api.auth.login(email, password)).access_token);
    });
  }

  return (
    <form onSubmit={onSubmit} aria-label={title}>
      <h2>{title}</h2>
      {mode === "register" && (
        <label>
          名前 <input name="name" required />
        </label>
      )}
      <label>
        メールアドレス <input name="email" type="email" required />
      </label>
      {mode !== "forgot" && (
        <label>
          パスワード <input name="password" type="password" minLength={8} required />
        </label>
      )}
      <button type="submit">{{ login: "ログイン", register: "登録してログイン", forgot: "再設定メールを送る" }[mode]}</button>
      <nav>
        {mode !== "login" && (
          <button type="button" onClick={() => setMode("login")}>
            ログインへ
          </button>
        )}
        {mode !== "register" && (
          <button type="button" onClick={() => setMode("register")}>
            新規登録へ
          </button>
        )}
        {mode !== "forgot" && (
          <button type="button" onClick={() => setMode("forgot")}>
            パスワードを忘れた
          </button>
        )}
      </nav>
    </form>
  );
}

function SignedIn(props: {
  api: ApiClient;
  me: User;
  gqlEmail: string | null;
  run: Run;
  onUpdated: (user: User) => void;
  onSignedOut: () => void;
}) {
  const { api, me, gqlEmail, run, onUpdated, onSignedOut } = props;

  function onRename(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const name = field(new FormData(e.currentTarget), "name");
    void run(async () => onUpdated(await api.updateMe({ name })), "名前を変えました");
  }

  function onChangePassword(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = new FormData(e.currentTarget);
    void run(async () => {
      await api.changePassword(field(form, "current"), field(form, "next"));
      onSignedOut(); // 全端末のトークンが無効になるので、ログインし直してもらう
    }, "パスワードを変えました。新しいパスワードでログインしてください");
  }

  return (
    <section aria-label="ログイン中">
      <h2>ようこそ、{me.name ?? me.email} さん</h2>
      <p>
        REST <code>GET /users/me</code>: <code>{me.email}</code> / GraphQL <code>{"{ me { email } }"}</code>:{" "}
        <code>{gqlEmail}</code>
        {me.is_superuser && <strong>（管理者）</strong>}
      </p>
      <button
        type="button"
        onClick={() =>
          // サーバ側の無効化に失敗しても（期限切れ等）、手元のトークンは必ず捨てる
          void run(() => api.auth.logout().finally(onSignedOut))
        }
      >
        ログアウト
      </button>

      <form onSubmit={onRename} aria-label="名前の変更">
        <label>
          名前 <input name="name" defaultValue={me.name ?? ""} required />
        </label>
        <button type="submit">名前を変える</button>
      </form>

      <form onSubmit={onChangePassword} aria-label="パスワードの変更">
        <label>
          今のパスワード <input name="current" type="password" required />
        </label>
        <label>
          新しいパスワード <input name="next" type="password" minLength={8} required />
        </label>
        <button type="submit">パスワードを変える</button>
      </form>

      {me.is_superuser ? (
        <AdminUsers api={api} run={run} />
      ) : (
        <button
          type="button"
          onClick={() => {
            if (!confirm("退会しますか？")) return;
            void run(async () => (await api.deleteMe(), onSignedOut()), "退会しました");
          }}
        >
          退会する
        </button>
      )}
    </section>
  );
}

function AdminUsers({ api, run }: { api: ApiClient; run: Run }) {
  const [users, setUsers] = useState<User[] | null>(null);
  const load = () => run(async () => setUsers((await api.users.list()).data));

  return (
    <section aria-label="ユーザ管理">
      <h3>ユーザ管理</h3>
      <button type="button" onClick={() => void load()}>
        一覧を読む
      </button>
      {users && (
        <table>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.id}</td>
                <td>{u.email}</td>
                <td>{u.is_active ? "有効" : "停止中"}</td>
                <td>
                  <button
                    type="button"
                    onClick={() => void run(async () => (await api.users.update(u.id, { is_active: !u.is_active }), load()))}
                  >
                    {u.is_active ? "停止" : "再開"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
