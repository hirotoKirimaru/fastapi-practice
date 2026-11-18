import { describe, expect, it, vi } from "vitest";

import { ApiError, createApiClient, GraphQLRequestError } from "./client";

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function setup(response: Response, token: string | null = null) {
  const fetchMock = vi.fn<typeof fetch>().mockResolvedValue(response);
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
    await api.login("a+b@example.com", "p@ss word");
    const { url, init, headers } = lastCall();
    expect(url).toBe("http://api.test/login/access-token");
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
