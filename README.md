# DMMGamePlayerFastLauncher
DMM Game Player のゲームを高速かつセキュアに起動できるランチャー

## 特徴
- **ワンクリックでゲームを起動**
- **管理者権限不要**

## インストール
[Releases](https://github.com/fa0311/DMMGamePlayerFastLauncher/releases) から DMMGamePlayerFastLauncher-Setup.exe をダウンロード<br>
実行してセットアップする

## 使い方
エクスプローラーやデスクトップで右クリックし**新規作成**、**ショートカットの作成**を選択<br>
**項目の場所を入力して下さい**にダウンロードした**DMMGamePlayerFastLauncherのパス**と**product_id**を入力<br>
ショートカットの名前は何でも良いです<br>

例<br>
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe umamusume`<br>
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe priconner`<br>

## product_idって？
ゲームに割り当てられているidです<br>
`%AppData%\DMMGamePlayerFastLauncher\tools` にある `DMMGamePlayerProductIdChecker.exe` を実行することで確認できます


## 引数
`DMMGamePlayerFastLauncher.exe <product_id>`

| オプション           | エイリアス | デフォルト                                       | 備考                                    | タイプ |
|----------------------|------------|--------------------------------------------------|-----------------------------------------|--------|
| --help               | -h         | False                                            |                                         | bool   |
| --game-path          |            | False                                            | ゲームのパス Falseにすると自動           |        |
| --login-force        |            | False                                            | ログインを強制する                      | bool   |
| --skip-exception     |            | False                                            | エラーをスキップ                       | bool   |
| --proxy-uri          |            | None                                             | HTTPプロクシを指定                   | string |

### プロクシ

`--proxy-uri`を指定することで、DMMへのリクエストがすべてプロクシーサーバーに通されます。

フォーマット：
`http://<ip>:<port>`

認証が必要の場合(Basic認証のみ)：
`http://<username>:<password>@<ip>:<port>`

## ヘルプ

### インストールするとき
> **セットアップする際、WindowsによってPCが保護されましたと表示される**<br>
> 詳細情報をクリックして実行をクリック<br>

> **WindowsDefenderがトロイの木馬判定を出す**<br>
> このツールはトロイの木馬ではないので誤判定です<br>
> 不安が残るようであればプログラムのコードを公開しているのでビルドしてお使い下さい

### 全てのゲームに起こる症状

> **「要求された操作には管理者特権が必要です」というエラーが出る**<br>
> DMMGamePlayerが管理者権限でインストールされています<br>
> DMMGamePlayerから管理者権限を外して下さい<br>
> (このツールのv4.0以降このエラーは出ないと思いますが)

### 特定のゲームに起こる症状

> **「ゲームのパスの検出に失敗しました」というエラーが出る**<br>
> **アンインストーラーなどの別のソフトが起動する**<br>
> 自動でゲームのパスを探す機能のバグです<br>
> `--game-path <ゲームのパス>` を指定してください<br>
例<br>
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe umamusume --game-path %UserProfile%/umamusume/umamusume.exe`<br>

> **「ゲームが起動しませんでした」というエラーが出る**<br>
> `--game-path <ゲームのパス>` を指定してください<br>
例<br>
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe umamusume --game-path %UserProfile%/umamusume/umamusume.exe`<br>

> **ゲームが起動しているのに「ゲームが起動しませんでした」というエラーが出る**<br>
> `--skip-exception` を指定することでエラーをスキップ出来ますがオススメしません<br>
> 別の解決方法を探すので発生するゲームがあれば報告して下さい<br>
> 例<br>
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe umamusume --skip-exception`<br>

> **BlueStacksを利用しているゲームだとエラーが出る**<br>
> 現在、BlueStacksを利用しているゲームは対応していません<br>
> 対応する予定はないです

> **「要求された操作には管理者特権が必要です」というエラーが出る**<br>
> ゲームが管理者権限でインストールされています<br>
> ゲームから管理者権限を外して下さい<br>

> **「指定されたファイルが見つかりません」というエラーが出る**<br>
> `--game-path` で指定したゲームのパスが間違っています<br>

### 何もしてないのに壊れた！！ってとき

> **「ログインに失敗しました」というエラーが出る**<br>
> DMMGamePlayerを起動してログインして下さい<br>
> DMMGamePlayerを起動しているなら終了させて下さい<br>

> **「ゲームが起動しませんでした」というエラーが出る**<br>
> ゲームにアップデートがないか確認して下さい<br>

> **「起動にエラーが発生したため修復プログラムを実行しました」というエラーが出る**<br>
> まれに表示される場合は正常な動作です<br>

> **「起動にエラーが発生したため修復プログラムを実行しました」と連続して何度も表示される**<br>
> `%AppData%\DMMGamePlayerFastLauncher` の `cookie.bytes` を削除してみて下さい<br>
> 解決しない場合、アカウントに問題がある場合が高いです<br>
> DMMGamePlayerからゲームを起動できるか確認してみて下さい<br>
> それでも解決しない場合はエラーの一番下の{ }で囲まれた文字列のerrorの右側に理由が書いているので心当たりがあればそれで解決して下さい<br>
> 心当たりがない場合は{ }で囲まれた文字列を開発者に送って下さい<br>

> **「データが無効です」というエラーが出る**<br>
> `%AppData%\DMMGamePlayerFastLauncher` の `cookie.bytes` を削除してみて下さい<br>

> **その他のエラー**<br>
> `%AppData%\DMMGamePlayerFastLauncher` の `cookie.bytes` を削除してみて下さい<br>

> **解決しない**<br>
> ツールが対策された可能性があります<br>

### 不具合以外

> **ゲームのアイコンに寄せたい**<br>
> ショートカットを右クリック→プロパティ→アイコンの変更→参照

> **このツールを使用するとDMMGamePlayerを起動する際に毎回ログインを求められるようになった**<br>
> DMMGamePlayerのバグ(仕様？)です<br>
> どうすることも出来ないので頻繁にDMMGamePlayerを起動する方にこのツールはオススメしません<br>

## 典拠
[Lutwidse/priconner_launch.py](https://gist.github.com/Lutwidse/82d8e7a20c96296bc0318f1cb6bf26ee)

## ライセンス
DMMGamePlayerFastLauncher is under MIT License
