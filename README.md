any-notify: クロス環境向け通知CLI
=================================

概要
----
`any-notify` は Codex-CLI 等から呼び出せる簡易通知コマンドです。GNOME (libnotify) を優先し、WSL2 では PowerShell のポップアップにフォールバックします。

インストール/実行方法
----------------------
- リポ内から直接実行:
  - `python -m any_notify --help`
  - `python -m any_notify -t "タイトル" "本文"`
- パスへ公開したい場合は、`pip install -e .` 後に `any-notify` コマンドが利用できます。

使用例
------
- 標準: `any-notify -t "Build" "完了しました"`
- 重要度: `any-notify -u critical -t "警告" "ディスク残容量が少ない"`
- タイムアウト(ms): `any-notify -T 5000 -t "情報" "自動クリーン完了"`
- 明示バックエンド: `any-notify -b gdbus -t "タイトル" "本文"`

バックエンド選択
----------------
1. `notify-send` があれば使用
2. それ以外は `gdbus` (org.freedesktop.Notifications)
3. WSL2の場合は PowerShell の COM Popup
4. 最後に stdout 出力

注意
----
- `notify-send`/`gdbus` は `libnotify`/`glib2` に含まれます。Arch/Ubuntuで導入してください。
- WSL2 での PowerShell ポップアップはトーストではなく簡易ダイアログです。
