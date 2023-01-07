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

ゲームに引数を追加したい場合はこれを指定します  
通常の DMM を介した起動方法で使用できない隠された引数を使用することができます  
`"` で囲む必要があることに注意してください

Unity 製ゲームの引数はここに詳しく載ってます  
[PlayerCommandLineArguments](https://docs.unity3d.com/ja/2022.2/Manual/PlayerCommandLineArguments.html)

例:  
ボーダーレスフルスクリーン  
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe priconner --game-args "-popupwindow -screen-width 1920 -screen-height 1080 -screen-fullscreen 0"`  
ボーダーレス (引数が 1 個の時はエスケープするか無理やり 2 つに増やす)  
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe priconner --game-args "-popupwindow 0"`  
サブモニターで起動  
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe umamusume --game-args "-monitor 2"`

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

### 「Game path detection failed.」というエラーが出る

[game-path](#game-path)

### アンインストーラーなどの別のソフトが起動する

[game-path](#game-path)

### ゲームが起動しているのに「Game did not start. Please allow administrative privileges」というエラーが出る

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

### 「Login failed.」というエラーが出る

DMMGamePlayer を起動してログインし直して下さい

### 「"Game did not start.」というエラーが出る

ゲームにアップデートがないか確認して下さい  
管理者権限を与えてみてください  
それでも解決しなければ Issue や Twitter でバグ報告お願いします

## 不具合以外のヘルプ

### ゲームのアイコンに寄せたい

ショートカットを右クリック → プロパティ → アイコンの変更 → 参照

### ゲームに起動引数を与える

[game-args](#game-args)
