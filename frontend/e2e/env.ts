import { createApiClient } from "../src/api/client";

/** e2e が叩く本物のバックエンド。CI では uvicorn を起動してから流す */
export const E2E_API_BASE_URL: string =
  process.env.E2E_API_BASE_URL ?? "http://localhost:8000";

export function client(token?: string | null) {
  return createApiClient({ baseUrl: E2E_API_BASE_URL, getToken: () => token });
}

/** DB はテストのたびに捨てないので、メールアドレスは毎回ユニークにする */
export function uniqueEmail(label: string): string {
  return `e2e-${label}-${Date.now()}-${crypto.randomUUID().slice(0, 8)}@example.com`;
}

export const PASSWORD = "e2e-correct-horse-battery";

/** 新しいユーザを登録してログインし、トークンとユーザを返す */
export async function signupAndLogin(label: string) {
  const email = uniqueEmail(label);
  const user = await client().signup({ name: `e2e ${label}`, email, password: PASSWORD });
  const { access_token } = await client().login(email, PASSWORD);
  return { user, email, token: access_token, api: client(access_token) };
}
