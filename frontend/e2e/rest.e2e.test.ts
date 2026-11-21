import { describe, expect, it } from "vitest";

import { ApiError } from "../src/api/client";
import { client } from "./env";

describe("REST", () => {
  it("GET /health/", async () => {
    await expect(client().health()).resolves.toEqual({ Hello: "World" });
  });

  it("GET /health-check/", async () => {
    await expect(client().healthCheck()).resolves.toBe(true);
  });

  it("タスクを作って一覧に出し、消す", async () => {
    const api = client();
    const title = `e2e task ${crypto.randomUUID()}`;

    const created = await api.tasks.create(title);
    expect(created.title).toBe(title);

    const tasks = await api.tasks.list();
    expect(tasks).toContainEqual(expect.objectContaining({ id: created.id, title, done: false }));

    await api.tasks.remove(created.id);
    expect((await api.tasks.list()).map((t) => t.id)).not.toContain(created.id);
  });

  it("存在しないタスクの削除は 404", async () => {
    const error = await client()
      .tasks.remove(2_147_483_647)
      .catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ status: 404, detail: "Task not found" });
  });
});
