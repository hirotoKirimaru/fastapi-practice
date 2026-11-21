import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

// 2 つのプロジェクトに分ける。
//   unit: jsdom 上でコンポーネントと API クライアントを、fetch を差し替えて動かす（バックエンド不要）
//   e2e : Node から本物のバックエンドの REST / GraphQL を叩く（先にバックエンドを起動しておく）
export default defineConfig({
  plugins: [react()],
  test: {
    projects: [
      {
        extends: true,
        test: {
          name: "unit",
          environment: "jsdom",
          include: ["src/**/*.test.{ts,tsx}"],
          setupFiles: ["src/test/setup.ts"],
        },
      },
      {
        extends: true,
        test: {
          name: "e2e",
          environment: "node",
          include: ["e2e/**/*.e2e.test.ts"],
          globalSetup: ["e2e/global-setup.ts"],
          testTimeout: 15_000,
        },
      },
    ],
    coverage: {
      provider: "v8",
      include: ["src/**/*.{ts,tsx}"],
      exclude: ["src/**/*.test.{ts,tsx}", "src/test/**", "src/main.tsx"],
    },
  },
});
