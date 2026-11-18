import { describe, expect, it } from "vitest";

import { ApiError, GraphQLRequestError } from "../src/api/client";
import {
  CREATE_POST_MUTATION,
  ME_QUERY,
  POSTS_QUERY,
  type CreatePostResult,
  type MeResult,
  type PostsResult,
} from "../src/api/graphql";
import { client, PASSWORD, signupAndLogin, uniqueEmail } from "./env";

async function errorOf(promise: Promise<unknown>) {
  return promise.then(
    () => expect.fail("成功してしまった"),
    (e: unknown) => e,
  );
}

describe("認証: REST", () => {
  it("signup -> login -> GET /users/me", async () => {
    const { user, email, token, api } = await signupAndLogin("rest-me");
    expect(user).toMatchObject({ email });
    expect(user).not.toHaveProperty("hashed_password");
    expect(token.split(".")).toHaveLength(3); // JWT

    await expect(api.me()).resolves.toEqual(user);
  });

  it("同じメールアドレスでは登録できない（409）", async () => {
    const { email } = await signupAndLogin("dup");
    const error = await errorOf(client().signup({ name: "dup", email, password: PASSWORD }));
    expect(error).toMatchObject({ status: 409 });
  });

  it("短すぎるパスワードは 400", async () => {
    const error = await errorOf(
      client().signup({ name: "short", email: uniqueEmail("short"), password: "short" }),
    );
    expect(error).toMatchObject({ status: 400 });
  });

  it("パスワード違い・未登録のメールアドレスは同じ 401", async () => {
    const { email } = await signupAndLogin("wrong-pw");
    const wrongPassword = await errorOf(client().login(email, "wrong-password"));
    const unknownUser = await errorOf(client().login(uniqueEmail("nobody"), PASSWORD));

    for (const error of [wrongPassword, unknownUser]) {
      expect(error).toBeInstanceOf(ApiError);
      expect(error).toMatchObject({ status: 401, detail: "メールアドレスかパスワードが違います" });
    }
  });

  it.each([
    ["トークン無し", null],
    ["形式不正", "not-a-jwt"],
    ["署名不正", "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIn0.invalid-signature"],
  ])("GET /users/me は %s だと 401", async (_label, token) => {
    const error = await errorOf(client(token).me());
    expect(error).toMatchObject({ status: 401, detail: "Could not validate credentials" });
  });
});

describe("認証: GraphQL", () => {
  it("同じトークンで me が引ける（REST の /users/me と一致）", async () => {
    const { api } = await signupAndLogin("gql-me");
    const rest = await api.me();
    await expect(api.graphql<MeResult>(ME_QUERY)).resolves.toEqual({ me: rest });
  });

  it("createPost はログイン中のユーザの投稿になり、posts に出る", async () => {
    const { user, api } = await signupAndLogin("gql-post");
    const title = `e2e post ${crypto.randomUUID()}`;

    const { createPost } = await api.graphql<CreatePostResult, { title: string }>(
      CREATE_POST_MUTATION,
      { title },
    );
    expect(createPost).toMatchObject({ title, userId: user.id });

    const { posts } = await client().graphql<PostsResult>(POSTS_QUERY);
    expect(posts).toContainEqual(createPost);
  });

  it.each([
    ["トークン無し", null],
    ["形式不正", "not-a-jwt"],
  ])("me / createPost は %s だとエラー", async (_label, token) => {
    const api = client(token);
    for (const call of [
      api.graphql<MeResult>(ME_QUERY),
      api.graphql<CreatePostResult, { title: string }>(CREATE_POST_MUTATION, { title: "x" }),
    ]) {
      const error = await errorOf(call);
      expect(error).toBeInstanceOf(GraphQLRequestError);
      expect((error as GraphQLRequestError).errors[0].message).toBe("User is not authenticated");
    }
  });
});
