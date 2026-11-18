import { describe, expect, it } from "vitest";

import {
  HELLO_QUERY,
  USER_QUERY,
  type HelloResult,
  type UserResult,
} from "../src/api/graphql";
import { client, signupAndLogin } from "./env";

describe("GraphQL", () => {
  it("hello（ログイン不要）", async () => {
    await expect(
      client().graphql<HelloResult, { name: string }>(HELLO_QUERY, { name: "e2e" }),
    ).resolves.toEqual({ hello: "Hello, e2e!" });
  });

  it("REST で登録したユーザを GraphQL の user(id) で引ける", async () => {
    const { user } = await signupAndLogin("gql-user");
    await expect(
      client().graphql<UserResult, { id: number }>(USER_QUERY, { id: user.id }),
    ).resolves.toEqual({ user: { id: user.id, name: user.name, email: user.email } });
  });

  it("存在しない user(id) は null", async () => {
    await expect(
      client().graphql<UserResult, { id: number }>(USER_QUERY, { id: 2_147_483_647 }),
    ).resolves.toEqual({ user: null });
  });
});
