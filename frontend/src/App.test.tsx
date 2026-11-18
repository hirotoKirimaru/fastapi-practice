import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import App from "./App";

const BASE = "http://api.test";
const USER = { id: 7, name: "テスト 花子", email: "hanako@example.com" };
const PASSWORD = "correct-horse-battery";

/** バックエンドの代わり。パスワードが合えばトークンを返し、トークンがあれば /users/me と GraphQL の me に答える */
function fakeBackend() {
  return vi.fn<typeof fetch>(async (input, init) => {
    const url = new URL(String(input));
    const authorized = new Headers(init?.headers).get("Authorization") === "Bearer good-token";
    const json = (body: unknown, status = 200) => Response.json(body, { status });

    switch (url.pathname) {
      case "/health/":
        return json({ Hello: "World" });
      case "/login/access-token": {
        const form = new URLSearchParams(String(init?.body));
        return form.get("username") === USER.email && form.get("password") === PASSWORD
          ? json({ access_token: "good-token", token_type: "bearer" })
          : json({ detail: "メールアドレスかパスワードが違います" }, 401);
      }
      case "/users/me":
        return authorized ? json(USER) : json({ detail: "Could not validate credentials" }, 401);
      case "/graphql":
        return authorized
          ? json({ data: { me: USER } })
          : json({ data: null, errors: [{ message: "User is not authenticated" }] });
      default:
        return json({ detail: "Not Found" }, 404);
    }
  });
}

async function login(email: string, password: string) {
  const user = userEvent.setup();
  await user.type(screen.getByLabelText("メールアドレス"), email);
  await user.type(screen.getByLabelText("パスワード"), password);
  await user.click(screen.getByRole("button", { name: "ログイン" }));
}

describe("App", () => {
  it("health を表示する", async () => {
    vi.stubGlobal("fetch", fakeBackend());
    render(<App baseUrl={BASE} />);
    expect(await screen.findByText('{"Hello":"World"}')).toBeInTheDocument();
  });

  it("ログインすると REST と GraphQL の両方でユーザを取って表示する", async () => {
    const fetchMock = fakeBackend();
    vi.stubGlobal("fetch", fetchMock);
    render(<App baseUrl={BASE} />);

    await login(USER.email, PASSWORD);

    expect(await screen.findByRole("heading", { name: `ようこそ、${USER.name} さん` })).toBeInTheDocument();
    const paths = fetchMock.mock.calls.map(([input]) => new URL(String(input)).pathname);
    expect(paths).toEqual(expect.arrayContaining(["/users/me", "/graphql"]));
    expect(localStorage.getItem("fastapi-practice.token")).toBe("good-token");
  });

  it("パスワードが違うとエラーを出してログインしない", async () => {
    vi.stubGlobal("fetch", fakeBackend());
    render(<App baseUrl={BASE} />);

    await login(USER.email, "wrong-password");

    expect(await screen.findByRole("alert")).toHaveTextContent("メールアドレスかパスワードが違います");
    expect(screen.getByRole("form", { name: "ログイン" })).toBeInTheDocument();
  });

  it("保存済みのトークンが無効ならログイン画面に戻す", async () => {
    localStorage.setItem("fastapi-practice.token", "expired-token");
    vi.stubGlobal("fetch", fakeBackend());
    render(<App baseUrl={BASE} />);

    expect(await screen.findByRole("alert")).toHaveTextContent("Could not validate credentials");
    expect(localStorage.getItem("fastapi-practice.token")).toBeNull();
  });

  it("ログアウトでトークンを消す", async () => {
    vi.stubGlobal("fetch", fakeBackend());
    render(<App baseUrl={BASE} />);
    await login(USER.email, PASSWORD);

    await userEvent.click(await screen.findByRole("button", { name: "ログアウト" }));

    expect(screen.getByRole("form", { name: "ログイン" })).toBeInTheDocument();
    expect(localStorage.getItem("fastapi-practice.token")).toBeNull();
  });
});
