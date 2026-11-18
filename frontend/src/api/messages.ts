import { ApiError, GraphQLRequestError } from "./client";

/** バックエンドのエラーコード（主に fastapi-users のもの）を画面に出す文言にする */
const MESSAGES: Record<string, string> = {
  LOGIN_BAD_CREDENTIALS: "メールアドレスかパスワードが違います",
  LOGIN_USER_NOT_VERIFIED: "メールアドレスが確認されていません",
  REGISTER_USER_ALREADY_EXISTS: "このメールアドレスは登録済みです",
  UPDATE_USER_EMAIL_ALREADY_EXISTS: "このメールアドレスは使われています",
  RESET_PASSWORD_BAD_TOKEN: "再設定のリンクが無効か、期限が切れています",
  VERIFY_USER_BAD_TOKEN: "確認のリンクが無効か、期限が切れています",
  Unauthorized: "ログインし直してください",
};

export function errorMessage(e: unknown): string {
  if (e instanceof ApiError) {
    if (e.reason) return e.reason; // パスワードの規則違反など、理由が付いているもの
    if (e.code) return MESSAGES[e.code] ?? e.code;
    if (e.status === 400) return "入力内容を確かめてください";
  }
  if (e instanceof GraphQLRequestError) return e.message;
  return e instanceof Error ? e.message : String(e);
}
