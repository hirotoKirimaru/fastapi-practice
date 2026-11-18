/**
 * バックエンド（FastAPI）を叩くクライアント。アプリと e2e テストの両方がこれを使う。
 * REST と GraphQL の両方で、ログイン後は Authorization: Bearer <JWT> を付ける。
 */

export type Token = { access_token: string; token_type: string };

/** fastapi-users の UserRead（backend/src/schemas/auth.py） */
export type User = {
  id: number;
  name: string | null;
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  is_verified: boolean;
};
export type RegisterInput = { name: string; email: string; password: string };
export type UserUpdate = Partial<Pick<User, "name" | "email">> & { password?: string };
/** 管理者だけが変えられる項目も含む（PATCH /users/{id}） */
export type AdminUserUpdate = UserUpdate & Partial<Pick<User, "is_active" | "is_superuser" | "is_verified">>;
export type UsersPage = { data: User[]; count: number };
export type Post = { id: number; title: string; user_id: number };
export type Task = { id: number; title: string; done: boolean };
export type Page = { skip?: number; limit?: number };

/**
 * HTTP のエラー。detail はバックエンドの {"detail": ...}。
 * fastapi-users は "LOGIN_BAD_CREDENTIALS" のようなコードか {code, reason} を返すので、code に揃える
 */
export class ApiError extends Error {
  readonly status: number;
  readonly detail: unknown;
  /** detail が文字列ならそれ、{code} ならその code */
  readonly code: string | undefined;
  /** {reason} があればそれ（パスワードの規則違反の理由など） */
  readonly reason: string | undefined;

  constructor(status: number, detail: unknown) {
    super(`HTTP ${status}: ${typeof detail === "string" ? detail : JSON.stringify(detail)}`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
    const obj: Record<string, unknown> =
      typeof detail === "object" && detail !== null ? Object.fromEntries(Object.entries(detail)) : {};
    this.code = typeof detail === "string" ? detail : typeof obj.code === "string" ? obj.code : undefined;
    this.reason = typeof obj.reason === "string" ? obj.reason : undefined;
  }
}

export type GraphQLErrorItem = { message: string; path?: (string | number)[] };

/** GraphQL のエラー。HTTP は 200 で、本文の errors に入って返ってくる */
export class GraphQLRequestError extends Error {
  readonly errors: GraphQLErrorItem[];

  constructor(errors: GraphQLErrorItem[]) {
    super(errors.map((e) => e.message).join("; "));
    this.name = "GraphQLRequestError";
    this.errors = errors;
  }
}

export type ApiClientOptions = {
  baseUrl: string;
  /** 毎回のリクエストの直前に呼ぶ。返したトークンを Bearer で付ける */
  getToken?: () => string | null | undefined;
  fetch?: typeof fetch;
  signal?: AbortSignal;
};

function json(method: string, body: unknown): RequestInit {
  return {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  };
}

/** 一覧の skip / limit をクエリ文字列にする（未指定のものは付けない） */
function pageQuery(page: Page = {}): string {
  const params = new URLSearchParams();
  for (const [k, v] of Object.entries(page)) if (v !== undefined) params.set(k, String(v));
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

export function createApiClient(options: ApiClientOptions) {
  const baseUrl = options.baseUrl.replace(/\/+$/, "");
  const doFetch = options.fetch ?? ((...args: Parameters<typeof fetch>) => fetch(...args));

  async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
    const headers = new Headers(init.headers);
    headers.set("Accept", "application/json");
    const token = options.getToken?.();
    if (token) headers.set("Authorization", `Bearer ${token}`);

    const res = await doFetch(`${baseUrl}${path}`, {
      ...init,
      headers,
      signal: init.signal ?? options.signal,
    });
    const text = await res.text();
    let body: unknown = null;
    if (text) {
      try {
        body = JSON.parse(text);
      } catch {
        // JSON でない本文（プロキシの HTML のエラーページなど）は文字列のまま detail にする
        if (res.ok) throw new ApiError(res.status, `JSON ではない応答: ${text.slice(0, 200)}`);
        body = text;
      }
    }
    if (!res.ok) {
      const detail =
        body !== null && typeof body === "object" && "detail" in body ? body.detail : body;
      throw new ApiError(res.status, detail);
    }
    // 本文の形はバックエンドの OpenAPI に合わせた呼び出し側の型を信じる（実行時の検証はしない）
    // oxlint-disable-next-line typescript/no-unsafe-type-assertion
    return body as T;
  }

  return {
    health: () => request<{ Hello: string }>("/health/"),
    healthCheck: () => request<boolean>("/health-check/"),

    // ---- 認証（fastapi-users）
    auth: {
      register: (input: RegisterInput) => request<User>("/auth/register", json("POST", input)),
      /** OAuth2 のパスワードフロー。username にメールアドレスを入れ、フォーム形式で送る */
      login: (email: string, password: string) =>
        request<Token>("/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: new URLSearchParams({ username: email, password }).toString(),
        }),
      /** このトークンだけを無効にする（他の端末はログインしたまま） */
      logout: () => request<null>("/auth/logout", { method: "POST" }),
      /** 登録の有無に関わらず 202（メールでトークンが届く） */
      forgotPassword: (email: string) => request<null>("/auth/forgot-password", json("POST", { email })),
      resetPassword: (token: string, password: string) =>
        request<null>("/auth/reset-password", json("POST", { token, password })),
      requestVerifyToken: (email: string) =>
        request<null>("/auth/request-verify-token", json("POST", { email })),
      verify: (token: string) => request<User>("/auth/verify", json("POST", { token })),
    },

    // ---- 自分
    me: () => request<User>("/users/me"),
    updateMe: (patch: UserUpdate) => request<User>("/users/me", json("PATCH", patch)),
    /** 変えると全端末のトークンが無効になる（このトークンも） */
    changePassword: (currentPassword: string, newPassword: string) =>
      request<null>(
        "/users/me/password",
        json("PATCH", { current_password: currentPassword, new_password: newPassword }),
      ),
    /** 退会（論理削除） */
    deleteMe: () => request<null>("/users/me", { method: "DELETE" }),

    // ---- 管理者
    users: {
      list: (page?: Page) => request<UsersPage>(`/users${pageQuery(page)}`),
      get: (id: number) => request<User>(`/users/${id}`),
      update: (id: number, patch: AdminUserUpdate) => request<User>(`/users/${id}`, json("PATCH", patch)),
      remove: (id: number) => request<null>(`/users/${id}`, { method: "DELETE" }),
    },

    // ---- 投稿（自分のものだけ。管理者は全部）
    posts: {
      list: (page?: Page) => request<Post[]>(`/posts${pageQuery(page)}`),
      create: (title: string) => request<Post>("/posts", json("POST", { title })),
      get: (id: number) => request<Post>(`/posts/${id}`),
      update: (id: number, title: string) => request<Post>(`/posts/${id}`, json("PATCH", { title })),
      remove: (id: number) => request<null>(`/posts/${id}`, { method: "DELETE" }),
    },

    tasks: {
      list: () => request<Task[]>("/tasks"),
      create: (title: string) => request<{ id: number; title: string }>("/tasks", json("POST", { title })),
      remove: (id: number) => request<null>(`/tasks/${id}`, { method: "DELETE" }),
    },

    /** errors があれば GraphQLRequestError を投げ、無ければ data を返す */
    async graphql<TData>(query: string, variables?: Record<string, unknown>): Promise<TData> {
      const body = await request<{ data?: TData | null; errors?: GraphQLErrorItem[] }>(
        "/graphql",
        json("POST", { query, variables: variables ?? {} }),
      );
      if (body.errors?.length) throw new GraphQLRequestError(body.errors);
      // errors が無ければ data がある（GraphQL の仕様）
      // oxlint-disable-next-line typescript/no-unsafe-type-assertion
      return body.data as TData;
    },
  };
}

export type ApiClient = ReturnType<typeof createApiClient>;
