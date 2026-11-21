import { describe, expect, it } from "vitest";

import { apiError, asSuperuser, client, PASSWORD, signupAndLogin } from "./env";

describe("管理者: ユーザ管理", () => {
  it("一般ユーザは管理者の API を使えない（403）", async () => {
    const { user, api } = await signupAndLogin("member");
    // 呼び出しは関数で渡し、1 つずつ始める（先に全部始めると、待つ前に失敗した分が unhandled rejection になる）
    for (const call of [
      () => api.users.list(),
      () => api.users.get(user.id),
      () => api.users.update(user.id, { is_superuser: true }),
      () => api.users.remove(user.id),
    ]) {
      expect(await apiError(call())).toMatchObject({ status: 403 });
    }
  });

  it("一覧はページングでき、総数を返す", async () => {
    const { api } = await asSuperuser();
    await signupAndLogin("listed");
    const page = await api.users.list({ limit: 1 });
    expect(page.data).toHaveLength(1);
    expect(page.count).toBeGreaterThanOrEqual(2);
  });

  it("停止したユーザは入れず、再開すると入れる", async () => {
    const { api } = await asSuperuser();
    const member = await signupAndLogin("suspend");

    await expect(api.users.update(member.user.id, { is_active: false })).resolves.toMatchObject({ is_active: false });
    expect(await apiError(member.api.me())).toMatchObject({ status: 401 });
    expect(await apiError(client().auth.login(member.email, PASSWORD))).toMatchObject({ code: "LOGIN_BAD_CREDENTIALS" });

    await api.users.update(member.user.id, { is_active: true });
    await expect(member.api.me()).resolves.toMatchObject({ id: member.user.id });
  });

  it("管理者は他人のパスワードを変えられ、本人のトークンは無効になる", async () => {
    const { api } = await asSuperuser();
    const member = await signupAndLogin("admin-pw");

    await api.users.update(member.user.id, { password: "set-by-admin-123" });
    expect(await apiError(member.api.me())).toMatchObject({ status: 401 });
    await expect(client().auth.login(member.email, "set-by-admin-123")).resolves.toBeTruthy();
  });

  it("削除したユーザは見えなくなる（論理削除）", async () => {
    const { api } = await asSuperuser();
    const member = await signupAndLogin("admin-delete");

    await api.users.remove(member.user.id);
    expect(await apiError(api.users.get(member.user.id))).toMatchObject({ status: 404 });
    expect(await apiError(member.api.me())).toMatchObject({ status: 401 });
  });

  it("管理者は自分を退会させられない", async () => {
    const { api } = await asSuperuser();
    expect(await apiError(api.deleteMe())).toMatchObject({ status: 403 });
  });
});
