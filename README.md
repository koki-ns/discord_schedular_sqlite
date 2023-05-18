# discord_schedular
discordからスラッシュコマンドでsqliteに予定を追加し、朝と前日の夜に通知してくれるbot  
個人用  
タスクの状態（完了/未完了）を設定できるようにした
  
~~本番環境かつプライベートで運用しながらGoogleカレンダーのapiを使うにはGCPに課金しなきゃいけないみたいだったのでsqliteに移行しました~~  
GCEとサービスアカウントをうまく使えば無料で運用できるとわかったのでやっぱりGoogleカレンダーで管理することにしました→[discord_schedular](https://github.com/koki-ns/discord_schedular)
