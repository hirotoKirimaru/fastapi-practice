import { ApiError, createApiClient } from "../src/api/client";

/** e2e が叩く本物のバックエンド。CI では uvicorn を起動してから流す */
export const E2E_API_BASE_URL: string = process.env.E2E_API_BASE_URL ?? "http://localhost:8000";

/** src/initial_data.py が作る最初の管理者（backend の FIRST_SUPERUSER / FIRST_SUPERUSER_PASSWORD） */
export const SUPERUSER = {
  email: process.env.E2E_SUPERUSER_EMAIL ?? "admin@example.com",
  password: process.env.E2E_SUPERUSER_PASSWORD ?? "changethis",
};

export const PASSWORD = "e2e-correct-horse-battery";

export function client(token?: string | null) {
  return createApiClient({ baseUrl: E2E_API_BASE_URL, getToken: () => token });
}

/** DB はテストのたびに捨てないので、メールアドレスは毎回ユニークにする */
export function uniqueEmail(label: string): string {
  return `e2e-${label}-${Date.now()}-${crypto.randomUUID().slice(0, 8)}@example.com`;
}

export async function loginAs(email: string, password: string) {
  const { access_token } = await client().auth.login(email, password);
  return { token: access_token, api: client(access_token) };
}

/** 新しいユーザを登録してログインし、トークンとユーザを返す */
export async function signupAndLogin(label: string) {
  const email = uniqueEmail(label);
  const user = await client().auth.register({ name: `e2e ${label}`, email, password: PASSWORD });
  return { user, email, ...(await loginAs(email, PASSWORD)) };
}

export const asSuperuser = () => loginAs(SUPERUSER.email, SUPERUSER.password);

/** 失敗するはずの呼び出しの ApiError を返す（成功したらテストを落とす） */
export async function apiError(promise: Promise<unknown>): Promise<ApiError> {
  const result = await promise.then(
    () => new Error("成功してしまった"),
    (e: unknown) => e,
  );
  if (!(result instanceof ApiError)) throw result;
  return result;
}
