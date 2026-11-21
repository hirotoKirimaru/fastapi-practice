/** テストで fetch の引数を読むための小さな道具 */

export function urlOf(input: RequestInfo | URL): string {
  return input instanceof Request ? input.url : input.toString();
}

/** 本文は文字列で送っている（JSON.stringify / URLSearchParams#toString）。それ以外は空にする */
export function bodyText(init: RequestInit | undefined): string {
  return typeof init?.body === "string" ? init.body : "";
}
