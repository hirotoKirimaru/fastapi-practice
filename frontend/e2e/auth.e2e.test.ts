import { describe, expect, it } from "vitest";

import { GraphQLRequestError } from "../src/api/client";
import {
  CREATE_POST_MUTATION,
  ME_QUERY,
  type CreatePostResult,
  type MeResult,
} from "../src/api/graphql";
import { apiError, client, E2E_API_BASE_URL, loginAs, PASSWORD, signupAndLogin, uniqueEmail } from "./env";

describe("認証: 登録・ログイン", () => {
  it("register -> login -> GET /users/me", async () => {
    const { user, email, api } = await signupAndLogin("me");
    expect(user).toMatchObject({ email, is_active: true, is_superuser: false, is_verified: false });
    expect(user).not.toHaveProperty("hashed_password");
    await expect(api.me()).resolves.toEqual(user);
  });

  it("登録時に is_superuser を送っても管理者にならない", async () => {
    // クライアントの型（RegisterInput）では送れない項目なので、素の fetch で送る
    const res = await fetch(`${E2E_API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: "evil", email: uniqueEmail("evil"), password: PASSWORD, is_superuser: true }),
    });
    expect(await res.json()).toMatchObject({ is_superuser: false });
  });

  it.each([
    ["重複", "dup", PASSWORD, "REGISTER_USER_ALREADY_EXISTS"],
    ["短いパスワード", "new", "short", "REGISTER_INVALID_PASSWORD"],
  ])("登録できない: %s", async (_label, which, password, code) => {
    const { email } = await signupAndLogin("dup-src");
    const target = which === "dup" ? email.toUpperCase() : uniqueEmail("new"); // 大文字小文字は区別しない
    const error = await apiError(client().auth.register({ name: "x", email: target, password }));
    expect(error).toMatchObject({ status: 400, code });
  });

  it("パスワード違い・未登録は同じエラー（登録の有無を漏らさない）", async () => {
    const { email } = await signupAndLogin("bad-cred");
    for (const call of [
      () => client().auth.login(email, "wrong-password"),
      () => client().auth.login(uniqueEmail("x"), PASSWORD),
    ]) {
      expect(await apiError(call())).toMatchObject({ status: 400, code: "LOGIN_BAD_CREDENTIALS" });
    }
  });

  it.each([
    ["トークン無し", null],
    ["不正なトークン", "not-a-token"],
  ])("GET /users/me は %s だと 401", async (_label, token) => {
    expect(await apiError(client(token).me())).toMatchObject({ status: 401 });
  });

  it("ログアウトはその端末のトークンだけを無効にする", async () => {
    const { email, api } = await signupAndLogin("logout");
    const other = await loginAs(email, PASSWORD);

    await api.auth.logout();
    expect(await apiError(api.me())).toMatchObject({ status: 401 });
    await expect(other.api.me()).resolves.toMatchObject({ email });
  });
});

describe("認証: 自分の情報の更新", () => {
  it("名前とメールアドレスを変えられる。管理者には自分でなれない", async () => {
    const { user, api } = await signupAndLogin("update");
    const email = uniqueEmail("updated");
    const updated = await api.updateMe({ name: "改名", email, ...({ is_superuser: true } as object) });
    expect(updated).toEqual({ ...user, name: "改名", email, is_verified: false });
  });

  it("他人のメールアドレスには変えられない", async () => {
    const other = await signupAndLogin("taken");
    const { api } = await signupAndLogin("taker");
    expect(await apiError(api.updateMe({ email: other.email }))).toMatchObject({
      code: "UPDATE_USER_EMAIL_ALREADY_EXISTS",
    });
  });

  it("パスワード変更: 今のパスワードが違うと 400", async () => {
    const { api } = await signupAndLogin("pw-wrong");
    expect(await apiError(api.changePassword("wrong-password", "brand-new-password"))).toMatchObject({
      status: 400,
      detail: "今のパスワードが違います",
    });
  });

  it("パスワード変更: 全端末のトークンが無効になり、新しいパスワードでだけ入れる", async () => {
    const { email, api } = await signupAndLogin("pw-change");
    const other = await loginAs(email, PASSWORD);

    await api.changePassword(PASSWORD, "brand-new-password");

    for (const session of [api, other.api]) expect(await apiError(session.me())).toMatchObject({ status: 401 });
    expect(await apiError(client().auth.login(email, PASSWORD))).toMatchObject({ code: "LOGIN_BAD_CREDENTIALS" });
    await expect(loginAs(email, "brand-new-password")).resolves.toBeTruthy();
  });

  it("退会すると入れなくなり、同じメールアドレスで登録し直せる", async () => {
    const { email, api } = await signupAndLogin("leave");
    await api.deleteMe();

    expect(await apiError(api.me())).toMatchObject({ status: 401 });
    expect(await apiError(client().auth.login(email, PASSWORD))).toMatchObject({ code: "LOGIN_BAD_CREDENTIALS" });
    await expect(client().auth.register({ name: "again", email, password: PASSWORD })).resolves.toMatchObject({
      email,
    });
  });
});

describe("認証: パスワード再設定・メール確認", () => {
  // トークンはメールで届くので、e2e では「受け付けること」と「不正なトークンを拒むこと」まで。
  // トークンを使った再設定・確認の成功は backend の tests/scenario/test_auth.py で見ている
  it("forgot-password は登録の有無に関わらず受け付ける（202）", async () => {
    const { email } = await signupAndLogin("forgot");
    await expect(client().auth.forgotPassword(email)).resolves.toBeNull();
    await expect(client().auth.forgotPassword(uniqueEmail("nobody"))).resolves.toBeNull();
  });

  it("不正なトークンでの再設定・確認は拒む", async () => {
    expect(await apiError(client().auth.resetPassword("bad-token", "brand-new-password"))).toMatchObject({
      code: "RESET_PASSWORD_BAD_TOKEN",
    });
    expect(await apiError(client().auth.verify("bad-token"))).toMatchObject({ code: "VERIFY_USER_BAD_TOKEN" });
  });
});

describe("認証: GraphQL", () => {
  it("同じトークンで me が引ける（REST の /users/me と一致）", async () => {
    const { user, api } = await signupAndLogin("gql-me");
    await expect(api.graphql<MeResult>(ME_QUERY)).resolves.toEqual({
      me: { id: user.id, name: user.name, email: user.email },
    });
  });

  it("createPost はログイン中のユーザの投稿になり、REST の /posts にも出る", async () => {
    const { user, api } = await signupAndLogin("gql-post");
    const title = `e2e post ${crypto.randomUUID()}`;
    const { createPost } = await api.graphql<CreatePostResult>(CREATE_POST_MUTATION, { title });
    expect(createPost).toMatchObject({ title, userId: user.id });
    await expect(api.posts.list()).resolves.toEqual([{ id: createPost.id, title, user_id: user.id }]);
  });

  it("ログアウト後のトークンでは me が引けない", async () => {
    const { api } = await signupAndLogin("gql-logout");
    await api.auth.logout();
    await expect(api.graphql<MeResult>(ME_QUERY)).rejects.toThrow("User is not authenticated");
  });

  it.each([
    ["トークン無し", null],
    ["不正なトークン", "not-a-token"],
  ])("me / createPost は %s だとエラー", async (_label, token) => {
    const api = client(token);
    for (const call of [
      () => api.graphql<MeResult>(ME_QUERY),
      () => api.graphql<CreatePostResult>(CREATE_POST_MUTATION, { title: "x" }),
    ]) {
      const error = await call().catch((e: unknown) => e);
      if (!(error instanceof GraphQLRequestError)) throw error;
      expect(error.errors[0].message).toBe("User is not authenticated");
    }
  });
});
