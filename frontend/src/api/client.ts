/**
 * バックエンド（FastAPI）を叩くクライアント。アプリと e2e テストの両方がこれを使う。
 * REST と GraphQL の両方で、ログイン後は Authorization: Bearer <JWT> を付ける。
 */

export type Token = { access_token: string; token_type: string };
export type UserPublic = { id: number; name: string; email: string };
export type SignupInput = { name: string; email: string; password: string };

/** HTTP のエラー。detail はバックエンドの {"detail": ...} */
export class ApiError extends Error {
  readonly status: number;
  readonly detail: unknown;

  constructor(status: number, detail: unknown) {
    super(`HTTP ${status}: ${typeof detail === "string" ? detail : JSON.stringify(detail)}`);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
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
    const body: unknown = text ? JSON.parse(text) : null;
    if (!res.ok) {
      const detail =
        body !== null && typeof body === "object" && "detail" in body ? body.detail : body;
      throw new ApiError(res.status, detail);
    }
    return body as T;
  }

  function json(method: string, body: unknown): RequestInit {
    return {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    };
  }

  return {
    health: () => request<{ Hello: string }>("/health/"),
    healthCheck: () => request<boolean>("/health-check/"),

    signup: (input: SignupInput) => request<UserPublic>("/signup", json("POST", input)),

    /** OAuth2 のパスワードフロー。username にメールアドレスを入れ、フォーム形式で送る */
    login: (email: string, password: string) =>
      request<Token>("/login/access-token", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username: email, password }).toString(),
      }),

    me: () => request<UserPublic>("/users/me"),

    tasks: {
      list: () => request<{ id: number; title: string; done: boolean }[]>("/tasks"),
      create: (title: string) =>
        request<{ id: number; title: string }>("/tasks", json("POST", { title })),
      remove: (id: number) => request<null>(`/tasks/${id}`, { method: "DELETE" }),
    },

    /** errors があれば GraphQLRequestError を投げ、無ければ data を返す */
    async graphql<TData, TVariables extends Record<string, unknown> = Record<string, never>>(
      query: string,
      variables?: TVariables,
    ): Promise<TData> {
      const body = await request<{ data?: TData | null; errors?: GraphQLErrorItem[] }>(
        "/graphql",
        json("POST", { query, variables: variables ?? {} }),
      );
      if (body.errors?.length) throw new GraphQLRequestError(body.errors);
      return body.data as TData;
    },
  };
}

export type ApiClient = ReturnType<typeof createApiClient>;
