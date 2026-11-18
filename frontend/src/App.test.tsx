import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import App, { TOKEN_KEY } from "./App";
import type { User } from "./api/client";

const BASE = "http://api.test";
const PASSWORD = "correct-horse-battery";
const MEMBER: User = {
  id: 7,
  name: "テスト 花子",
  email: "hanako@example.com",
  is_active: true,
  is_superuser: false,
  is_verified: false,
};
const ADMIN: User = { ...MEMBER, id: 1, name: "admin", email: "admin@example.com", is_superuser: true };

/** バックエンドの代わり。パスワードが合えばトークンを返し、有効なトークンにだけ答える */
function fakeBackend(users: User[] = [MEMBER]) {
  const tokens = new Map<string, User>();
  return vi.fn<typeof fetch>(async (input, init) => {
    const url = new URL(String(input));
    const method = init?.method ?? "GET";
    const token = new Headers(init?.headers).get("Authorization")?.replace("Bearer ", "");
    const me = token ? tokens.get(token) : undefined;
    const json = (body: unknown, status = 200) => Response.json(body, { status });
    const unauthorized = () => json({ detail: "Unauthorized" }, 401);

    switch (`${method} ${url.pathname}`) {
      case "GET /health/":
        return json({ Hello: "World" });
      case "POST /auth/login": {
        const form = new URLSearchParams(String(init?.body));
        const user = users.find((u) => u.email === form.get("username"));
        if (!user || form.get("password") !== PASSWORD) return json({ detail: "LOGIN_BAD_CREDENTIALS" }, 400);
        const issued = `token-${user.id}-${tokens.size}`;
        tokens.set(issued, user);
        return json({ access_token: issued, token_type: "bearer" });
      }
      case "POST /auth/logout":
        if (!me) return unauthorized();
        tokens.delete(token!);
        return new Response(null, { status: 204 });
      case "GET /users/me":
        return me ? json(me) : unauthorized();
      case "PATCH /users/me":
        if (!me) return unauthorized();
        Object.assign(me, JSON.parse(String(init?.body)));
        return json(me);
      case "PATCH /users/me/password": {
        if (!me) return unauthorized();
        const body = JSON.parse(String(init?.body));
        if (body.current_password !== PASSWORD) return json({ detail: "今のパスワードが違います" }, 400);
        tokens.clear();
        return new Response(null, { status: 204 });
      }
      case "GET /users":
        if (!me?.is_superuser) return json({ detail: "Forbidden" }, 403);
        return json({ data: users, count: users.length });
      case "POST /graphql":
        return me ? json({ data: { me } }) : json({ data: null, errors: [{ message: "User is not authenticated" }] });
      default:
        return json({ detail: "Not Found" }, 404);
    }
  });
}

async function login(email: string, password = PASSWORD) {
  const user = userEvent.setup();
  const form = screen.getByRole("form", { name: "ログイン" });
  await user.type(within(form).getByLabelText("メールアドレス"), email);
  await user.type(within(form).getByLabelText("パスワード"), password);
  await user.click(within(form).getByRole("button", { name: "ログイン" }));
  return user;
}

function renderApp(users?: User[]) {
  const fetchMock = fakeBackend(users);
  vi.stubGlobal("fetch", fetchMock);
  render(<App baseUrl={BASE} />);
  return fetchMock;
}

describe("App", () => {
  it("health を表示する", async () => {
    renderApp();
    expect(await screen.findByText('{"Hello":"World"}')).toBeInTheDocument();
  });

  it("ログインすると REST と GraphQL の両方でユーザを取って表示する", async () => {
    const fetchMock = renderApp();
    await login(MEMBER.email);

    expect(await screen.findByRole("heading", { name: `ようこそ、${MEMBER.name} さん` })).toBeInTheDocument();
    const calls = fetchMock.mock.calls.map(([input]) => new URL(String(input)).pathname);
    expect(calls).toEqual(expect.arrayContaining(["/users/me", "/graphql"]));
    expect(localStorage.getItem(TOKEN_KEY)).toMatch(/^token-7-/);
  });

  it("パスワードが違うと、コードを日本語にして出す", async () => {
    renderApp();
    await login(MEMBER.email, "wrong-password");
    expect(await screen.findByRole("alert")).toHaveTextContent("メールアドレスかパスワードが違います");
    expect(screen.getByRole("form", { name: "ログイン" })).toBeInTheDocument();
  });

  it("保存済みのトークンが無効ならログイン画面に戻す", async () => {
    localStorage.setItem(TOKEN_KEY, "expired-token");
    renderApp();
    expect(await screen.findByRole("alert")).toHaveTextContent("ログインし直してください");
    expect(localStorage.getItem(TOKEN_KEY)).toBeNull();
  });

  it("ログアウトでサーバ側のトークンも消す", async () => {
    const fetchMock = renderApp();
    const user = await login(MEMBER.email);
    await user.click(await screen.findByRole("button", { name: "ログアウト" }));

    expect(await screen.findByRole("form", { name: "ログイン" })).toBeInTheDocument();
    expect(localStorage.getItem(TOKEN_KEY)).toBeNull();
    expect(fetchMock.mock.calls.some(([input]) => String(input).endsWith("/auth/logout"))).toBe(true);
  });

  it("サーバ側のログアウトに失敗しても、手元ではログアウトする", async () => {
    const fetchMock = renderApp();
    const user = await login(MEMBER.email);
    await screen.findByRole("button", { name: "ログアウト" });
    const original = fetchMock.getMockImplementation()!;
    fetchMock.mockImplementation(async (input, init) =>
      String(input).endsWith("/auth/logout") ? Response.json({ detail: "Unauthorized" }, { status: 401 }) : original(input, init),
    );

    await user.click(screen.getByRole("button", { name: "ログアウト" }));
    expect(await screen.findByRole("form", { name: "ログイン" })).toBeInTheDocument();
    expect(localStorage.getItem(TOKEN_KEY)).toBeNull();
  });

  it("名前を変える", async () => {
    renderApp([{ ...MEMBER }]);
    const user = await login(MEMBER.email);
    const form = await screen.findByRole("form", { name: "名前の変更" });
    await user.clear(within(form).getByLabelText("名前"));
    await user.type(within(form).getByLabelText("名前"), "改名 花子");
    await user.click(within(form).getByRole("button"));

    expect(await screen.findByRole("heading", { name: "ようこそ、改名 花子 さん" })).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent("名前を変えました");
  });

  it("パスワードを変えるとログインし直しになる", async () => {
    renderApp();
    const user = await login(MEMBER.email);
    const form = await screen.findByRole("form", { name: "パスワードの変更" });
    await user.type(within(form).getByLabelText("今のパスワード"), PASSWORD);
    await user.type(within(form).getByLabelText("新しいパスワード"), "brand-new-password");
    await user.click(within(form).getByRole("button"));

    expect(await screen.findByRole("form", { name: "ログイン" })).toBeInTheDocument();
    expect(screen.getByRole("status")).toHaveTextContent("新しいパスワードでログインしてください");
  });

  it("管理者にだけユーザ管理を出す", async () => {
    renderApp([MEMBER, ADMIN]);
    const user = await login(ADMIN.email);
    const admin = await screen.findByRole("region", { name: "ユーザ管理" });
    await user.click(within(admin).getByRole("button", { name: "一覧を読む" }));
    expect(await within(admin).findByText(MEMBER.email)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "退会する" })).not.toBeInTheDocument();
  });

  it("一般ユーザにはユーザ管理を出さない", async () => {
    renderApp();
    await login(MEMBER.email);
    expect(await screen.findByRole("button", { name: "退会する" })).toBeInTheDocument();
    expect(screen.queryByRole("region", { name: "ユーザ管理" })).not.toBeInTheDocument();
  });
});
