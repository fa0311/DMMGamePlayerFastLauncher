# 上級者向け

[日本語](/README.md) / [English](/README-en.md)

[詳しい使い方](/docs/README-advance.md)

## その他のインストール(上級者向け)

### 手動インストール

[Releases](https://github.com/fa0311/DMMGamePlayerFastLauncher/releases) から `DMMGamePlayerFastLauncher.exe` をダウンロード

### product_id チェッカーのみインストール

[Releases](https://github.com/fa0311/DMMGamePlayerFastLauncher/releases) から `DMMGamePlayerProductIdChecker.exe` をダウンロード  
変更のない場合はアップロードされていないので過去のバージョンの Release からダウンロードしてください

## 引数

`DMMGamePlayerFastLauncher.exe <product_id>`

| オプション          | エイリアス | デフォルト | タイプ             |
| ------------------- | ---------- | ---------- | ------------------ |
| --help              | -h         | False      | Bool               |
| --game-path         |            | None       | String &#124; None |
| --game-args         |            | None       | String &#124; None |
| --login-force       |            | Flase      | Bool               |
| --skip-exception    |            | False      | Bool               |
| --https-proxy-uri   |            | None       | String &#124; None |
| --non-request-admin |            | False      | Bool               |

### game-path

何も指定していない場合は自動で検出しますがゲームによってはうまくいかない場合があります

例:  
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe umamusume --game-path %UserProfile%/umamusume/umamusume.exe`

### game-args

ゲーム特有の引数を追加したい場合はこれを指定します  
`"` で囲む必要があることに注意してください

Unity 製ゲームの引数はここに詳しく載ってます  
[PlayerCommandLineArguments](https://docs.unity3d.com/ja/2022.2/Manual/PlayerCommandLineArguments.html)

例:  
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe umamusume --game-args "-popupwindow -screen-width 1920 -screen-height 1080 -screen-fullscreen 0"`  
引数が 1 つの時はエスケープが必要だけど適当な文字列 (0 とか) を入れればなんとかなる  
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe umamusume --game-args "-popupwindow 0"`

### login-force

ログインのキャッシュを無効にします  
ほとんどの場合、この引数は不要です

例:  
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe umamusume --login-force`

### skip-exception

エラーを出力しません  
これはあくまで応急処置で基本的には使わないで下さい  
原因不明なエラーが発生した場合は [issues](https://github.com/fa0311/DMMGamePlayerFastLauncher/issues) に報告して下さい

例:  
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe umamusume --skip-exception`

### https-proxy-uri

https プロキシを設定します  
日本国外に在住しているユーザー向けの機能です

例:  
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe umamusume --https-proxy-uri http://host:port`  
Basic 認証  
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe umamusume --https-proxy-uri http://user:pass@host:port`  
Socks5  
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe umamusume --https-proxy-uri socks5://user:pass@host:port`

詳しい使い方  
[requests.org/Proxies](https://requests-docs-ja.readthedocs.io/en/latest/user/advanced/#proxies)

### non-request-admin

このツールは管理者権限を必要なときのみ要求することがありますがそれを要求しなくなります  
ほとんどの場合、この引数は不要です

例:  
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe umamusume --non-request-admin`

## ヘルプ

### セットアップする際、「Windows によって PC が保護されました」と表示される

詳細情報をクリックして実行をクリック

### WindowsDefender がトロイの木馬と認識する

このツールはトロイの木馬ではないので誤判定です  
不安が残るようであればこのプログラムはオープンソースなので自前でビルドしてお使い下さい

### 「日本国外からのアクセスは禁止されています」というエラーが出る

[https-proxy-uri](#https-proxy-uri)

### 「ゲームのパスの検出に失敗しました」というエラーが出る

[game-path](#game-path)

### アンインストーラーなどの別のソフトが起動する

[game-path](#game-path)

### ゲームが起動しているのに「ゲームが起動しませんでした」というエラーが出る

[skip-exception](#skip-exception)

### BlueStacks を利用しているゲームだとエラーが出る

現在、BlueStacks を利用しているゲームは対応していません  
対応する予定はないです

### 「指定されたファイルが見つかりません」というエラーが出る

[game-path](#game-path) で指定したゲームのパスが間違っています

### プロキシを設定した際、ゲームは起動するがゲーム側に通信エラーが発生する

ゲーム側で国外アクセスが禁止されています  
ウマ娘とプリコネ R は禁止されていました

### 管理者権限が要求され起動しないかつエラーが出ない

そのゲームには対応していません  
Issue や Twitter でバグ報告お願いします

### 「ログインに失敗しました」というエラーが出る

DMMGamePlayer を起動してログインし直して下さい

### 「ゲームが起動しませんでした」というエラーが出る

ゲームにアップデートがないか確認して下さい  
管理者権限を与えてみてください  
それでも解決しなければ Issue や Twitter でバグ報告お願いします

### 「起動にエラーが発生したため修復プログラムを実行しました」というエラーが出る

まれに表示される場合は正常な動作です

### 「起動にエラーが発生したため修復プログラムを実行しました」と連続して何度も表示される

`%AppData%\DMMGamePlayerFastLauncher` の `cookie.bytes` を削除してみて下さい

解決しない場合、アカウントに問題がある場合が高いです  
DMMGamePlayer からゲームを起動できるか確認してみて下さい  
それでも解決しない場合はエラーの一番下の{ }で囲まれた文字列の error の右側に理由が書いているので心当たりがあればそれで解決して下さい  
心当たりがない場合は{ }で囲まれた文字列を開発者に送って下さい

### 「データが無効です」というエラーが出る

`%AppData%\DMMGamePlayerFastLauncher` の `cookie.bytes` を削除してみて下さい

### その他のエラー

`%AppData%\DMMGamePlayerFastLauncher` の `cookie.bytes` を削除してみて下さい

## 不具合以外のヘルプ

### ゲームのアイコンに寄せたい

ショートカットを右クリック → プロパティ → アイコンの変更 → 参照

### このツールを使用すると DMMGamePlayer を起動する際に毎回ログインを求められるようになった

DMMGamePlayer のバグ(仕様？)です  
どうすることも出来ないので頻繁に DMMGamePlayer を起動する方にこのツールはオススメしません

### ボーダーレスにしたい

ウマ娘の場合は  
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe umamusume --game-args "-popupwindow 0"`

詳しくは [game-args](#game-args)

### サブモニターでの起動を強制する

プリコネ R の場合は  
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe priconner --game-args "-monitor 2"`

### フルスクリーン

プリコネ R の場合は  
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe priconner --game-args "-width 1920 -screen-height 1080"`

### ボーダーレスフルスクリーン

プリコネ R の場合は  
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe priconner --game-args "-popupwindow 0 -width 1920 -screen-height 1080"`
