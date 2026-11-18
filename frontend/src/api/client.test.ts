import { describe, expect, it, vi } from "vitest";

import { ApiError, createApiClient, GraphQLRequestError } from "./client";

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function setup(response: Response, token: string | null = null) {
  const fetchMock = vi.fn<typeof fetch>(async () => response.clone());
  const api = createApiClient({
    baseUrl: "http://api.test/",
    getToken: () => token,
    fetch: fetchMock,
  });
  const lastCall = () => {
    const [url, init] = fetchMock.mock.calls.at(-1)!;
    return { url: String(url), init: init!, headers: new Headers(init!.headers) };
  };
  return { api, fetchMock, lastCall };
}

describe("createApiClient", () => {
  it("ログイン中は Authorization: Bearer を付ける", async () => {
    const { api, lastCall } = setup(jsonResponse({ id: 1, name: "a", email: "a@example.com" }), "tkn");

    await api.me();
    const { url, headers } = lastCall();
    expect(url).toBe("http://api.test/users/me");
    expect(headers.get("Authorization")).toBe("Bearer tkn");
  });

  it("トークンが無ければ Authorization を付けない", async () => {
    const { api, lastCall } = setup(jsonResponse({ Hello: "World" }));
    await expect(api.health()).resolves.toEqual({ Hello: "World" });
    expect(lastCall().headers.has("Authorization")).toBe(false);
  });

  it("login は OAuth2 のパスワードフローとしてフォームで送る", async () => {
    const { api, lastCall } = setup(jsonResponse({ access_token: "t", token_type: "bearer" }));
    await api.auth.login("a+b@example.com", "p@ss word");
    const { url, init, headers } = lastCall();
    expect(url).toBe("http://api.test/auth/login");
    expect(init.method).toBe("POST");
    expect(headers.get("Content-Type")).toBe("application/x-www-form-urlencoded");
    expect(Object.fromEntries(new URLSearchParams(String(init.body)))).toEqual({
      username: "a+b@example.com",
      password: "p@ss word",
    });
  });

  it("エラー応答は status と detail を持つ ApiError になる", async () => {
    const { api } = setup(jsonResponse({ detail: "Could not validate credentials" }, 401));
    const error = await api.me().catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ status: 401, detail: "Could not validate credentials" });
  });

  it("fastapi-users のコードと理由を code / reason に取り出す", async () => {
    const bad = await setup(jsonResponse({ detail: "LOGIN_BAD_CREDENTIALS" }, 400))
      .api.auth.login("a@example.com", "x")
      .catch((e: unknown) => e);
    expect(bad).toMatchObject({ code: "LOGIN_BAD_CREDENTIALS", reason: undefined });

    const invalid = await setup(
      jsonResponse({ detail: { code: "REGISTER_INVALID_PASSWORD", reason: "短すぎます" } }, 400),
    )
      .api.auth.register({ name: "a", email: "a@example.com", password: "x" })
      .catch((e: unknown) => e);
    expect(invalid).toMatchObject({ code: "REGISTER_INVALID_PASSWORD", reason: "短すぎます" });
  });

  it("JSON でないエラー本文でも status 付きの ApiError にする", async () => {
    const { api } = setup(new Response("<html>Bad Gateway</html>", { status: 502 }));
    await expect(api.health()).rejects.toMatchObject({ status: 502, detail: "<html>Bad Gateway</html>" });
  });

  it("204（本文なし）は null を返す", async () => {
    const { api } = setup(new Response(null, { status: 204 }), "tkn");
    await expect(api.auth.logout()).resolves.toBeNull();
  });

  it("一覧の skip / limit をクエリに載せ、未指定は付けない", async () => {
    const { api, lastCall } = setup(jsonResponse({ data: [], count: 0 }), "tkn");
    await api.users.list({ skip: 10, limit: 5 });
    expect(lastCall().url).toBe("http://api.test/users?skip=10&limit=5");
    await api.users.list();
    expect(lastCall().url).toBe("http://api.test/users");
  });

  it("graphql は query と variables を送り、data を返す", async () => {
    const { api, lastCall } = setup(jsonResponse({ data: { hello: "Hello, x!" } }));
    await expect(api.graphql("query ($n: String!) { hello(name: $n) }", { n: "x" })).resolves.toEqual({
      hello: "Hello, x!",
    });
    const { url, init } = lastCall();
    expect(url).toBe("http://api.test/graphql");
    expect(JSON.parse(String(init.body))).toEqual({
      query: "query ($n: String!) { hello(name: $n) }",
      variables: { n: "x" },
    });
  });

  it("graphql の errors は HTTP 200 でも GraphQLRequestError にする", async () => {
    const { api } = setup(
      jsonResponse({ data: null, errors: [{ message: "User is not authenticated", path: ["me"] }] }),
    );
    const error = await api.graphql("{ me { id } }").catch((e: unknown) => e);
    expect(error).toBeInstanceOf(GraphQLRequestError);
    expect((error as GraphQLRequestError).errors[0].message).toBe("User is not authenticated");
  });
});
