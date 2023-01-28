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

| オプション          | エイリアス | デフォルト   | タイプ             | note       |
| ------------------- | ---------- | ------------ | ------------------ | ---------- |
| --help              | -h         | False        | Bool               |            |
| --game-path         |            | None         | String &#124; None |            |
| --game-args         |            | None         | String &#124; None |            |
| --login-force       |            | Flase        | Bool               | deprecated |
| --skip-exception    |            | False        | Bool               |            |
| --https-proxy-uri   |            | None         | String &#124; None |            |
| --non-request-admin |            | False        | Bool               | deprecated |
| --non-bypass-uac    |            | False        | Bool               |            |
| --schtasks-path     |            | schtasks.exe | String             |            |

```mermaid
    graph TD;
        ゲームのプロセスを開始 --権限不備で起動しない--> non-bypass-uac;
        ゲームのプロセスを開始 --Start/Error--> 続行;
        non-bypass-uac --false--> 最初のリクエスト;
        最初のリクエスト --no-->ゲームに権限与える
        最初のリクエスト --yes--> non-request-admin
        non-bypass-uac --true--> non-request-admin;
        non-request-admin --true--> skip-exception;
        non-request-admin --false--> UAC;
        UAC --allow--> ゲームに権限与える
        UAC --disabled--> 続行
        skip-exception --true--> 続行
        skip-exception --false--> エラー
```

**最初のリクエスト** - 最初のリクエストは、管理者権限を要求します  
これは、タスクスケジューラーに自動的に権限を昇格させるプログラムを登録するために必要です

特にこだわりが無ければ product_id 以外の引数は不要です  
ゲームや環境によっては`game-path` `https-proxy-uri` `schtasks-path` などが必要です

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

エラーを出力しなくなります  
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

### non-bypass-uac

この引数を使用すると UAC の自動許可を行わなくなります

指定していない場合はタスクスケジューラを使った権限の自動昇格を行います  
タスクの詳細はこのコマンドで確認できます  
複雑な処理を行うため少し起動速度が遅くなります  
`schtasks.exe /query /tn \Microsoft\Windows\DMMGamePlayerFastLauncher\`

また、このコマンドで削除できます
`Get-ScheduledTask | where TaskPath -eq "\Microsoft\Windows\DMMGamePlayerFastLauncher" | Unregister-ScheduledTask -Confirm:$false`

### schtasks-path

`schtasks.exe`の起動パスです
ほとんどの場合、この引数は不要です

## ファイル階層

| ファイル名                              | 削除 | 詳細                                                                           |
| --------------------------------------- | ---- | ------------------------------------------------------------------------------ |
| DMMGamePlayerFastLauncher.exe           | x    | 本体                                                                           |
| unins000.dat                            | o    | アンインストールする際に必要                                                   |
| unins000.exe                            | x    | アンインストールする際に必要                                                   |
| cookie.bytes                            | o    | セッションのキャッシュファイル, DMM のセッションが取得できなかった際に使用する |
| tools/DMMGamePlayerProductIdChecker.exe | o    | プロダクト ID のチェッカー,左ダブルクリックで実行                              |
| tools/Task.exe                          | x    | タスクスケジューラから呼び出される                                             |
| tools/refresh.ps1                       | o    | タスクを削除する,右クリックメニューから PowerShell で実行                      |
| sample/ウマ娘.lnk                       | o    | ウマ娘の起動ショートカット,左ダブルクリックで実行                              |
| sample/プリコネ R.lnk                   | o    | プリコネ R の起動ショートカット,左ダブルクリックで実行                         |
| assets/template.xml                     | x    | タスクスケジューラのテンプレートファイル                                       |
| assets/schtasks_v1\_{username}.xml      | o    | タスクスケジューラの残骸ファイル                                               |

## ヘルプ

### セットアップする際、「Windows によって PC が保護されました」と表示される

詳細情報をクリックして実行をクリック

### WindowsDefender がトロイの木馬と認識する

このツールはトロイの木馬ではないので誤判定です  
不安が残るようであればこのプログラムはオープンソースなので自前でビルドしてお使い下さい

### 「日本国外からのアクセスは禁止されています」というエラーが出る

[https-proxy-uri](#https-proxy-uri)

### 「Game path detection failed」というエラーが出る

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

### 「Login failed」というエラーが出る

DMMGamePlayer を起動してログインし直して下さい

### 「Game did not start」というエラーが出る

ゲームにアップデートがないか確認して下さい  
管理者権限を与えてみてください  
それでも解決しなければ Issue や Twitter でバグ報告お願いします

### 「Failed to authenticate device」というエラーが出る

<img src="./img/device_auth_config.png" height="300">

## 不具合以外のヘルプ

### ゲームのアイコンに寄せたい

ショートカットを右クリック → プロパティ → アイコンの変更 → 参照

### ゲームに起動引数を与える

[game-args](#game-args)
