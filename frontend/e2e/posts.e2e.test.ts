import { describe, expect, it } from "vitest";

import { apiError, asSuperuser, client, signupAndLogin } from "./env";

describe("投稿: 自分のものだけ触れる", () => {
  it("作成・一覧・更新・削除", async () => {
    const { user, api } = await signupAndLogin("posts");
    const post = await api.posts.create("最初の投稿");
    expect(post).toMatchObject({ title: "最初の投稿", user_id: user.id });

    await expect(api.posts.list()).resolves.toEqual([post]);
    await expect(api.posts.update(post.id, "書き換え")).resolves.toEqual({ ...post, title: "書き換え" });
    await api.posts.remove(post.id);
    expect(await apiError(api.posts.get(post.id))).toMatchObject({ status: 404 });
  });

  it("他人の投稿は見えず、触れない（403）", async () => {
    const alice = await signupAndLogin("alice");
    const bob = await signupAndLogin("bob");
    const post = await alice.api.posts.create("alice の投稿");

    await expect(bob.api.posts.list()).resolves.toEqual([]);
    for (const call of [
      () => bob.api.posts.get(post.id),
      () => bob.api.posts.update(post.id, "x"),
      () => bob.api.posts.remove(post.id),
    ]) {
      expect(await apiError(call())).toMatchObject({ status: 403 });
    }
  });

  it("管理者は全員の投稿を見て直せる", async () => {
    const alice = await signupAndLogin("alice-admin");
    const post = await alice.api.posts.create("alice の投稿");
    const { api } = await asSuperuser();

    expect(await api.posts.list({ limit: 100, skip: 0 })).toBeInstanceOf(Array);
    await expect(api.posts.update(post.id, "管理者が直した")).resolves.toMatchObject({ title: "管理者が直した" });
  });

  it("ログインしていなければ 401", async () => {
    expect(await apiError(client().posts.list())).toMatchObject({ status: 401 });
  });
});
