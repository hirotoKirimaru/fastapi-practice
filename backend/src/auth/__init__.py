"""認証・ユーザ管理。OSS の fastapi-users に乗せ、DB とのやり取りだけをこのパッケージで書く。

- db.py      : fastapi-users のアダプタ（SQLModel の User / AccessToken を読み書きする）
- manager.py : パスワードの規則、登録・パスワード再設定・メール確認のフック
- backend.py : Bearer トークン（DB に持つ）での認証と、FastAPI の依存（current_active_user など）
"""
