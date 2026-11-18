import { E2E_API_BASE_URL } from "./env";

/** バックエンドが起動するまで待つ（最大 30 秒）。起動していなければ分かるように落とす */
export default async function waitForBackend() {
  const deadline = Date.now() + 30_000;
  let lastError: unknown;
  while (Date.now() < deadline) {
    try {
      const res = await fetch(`${E2E_API_BASE_URL}/health-check/`);
      if (res.ok) return;
      lastError = new Error(`HTTP ${res.status}`);
    } catch (e) {
      lastError = e;
    }
    await new Promise((r) => setTimeout(r, 500));
  }
  throw new Error(
    `バックエンド（${E2E_API_BASE_URL}）につながりません。backend で ` +
      "`uv run alembic upgrade head && uv run poe start` を起動してから流してください" +
      `（接続先は E2E_API_BASE_URL で変えられます）: ${String(lastError)}`,
  );
}
