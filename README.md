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

目的のゲームの**product_id**が分からない場合、**product_id**を適当なものにするとインストールしているゲームの**product_id**が一覧で表示されます<br>
*%AppData%\DMMGamePlayerFastLauncher\sample* にサンプル用のショートカットを置いています<br>

## 引数
`DMMGamePlayerFastLauncher.exe <product_id>`

| オプション           | エイリアス | デフォルト                                       | 備考                              | タイプ |
|----------------------|------------|--------------------------------------------------|-----------------------------------|--------|
| --help               | -h         | False                                            |                                   | bool   |
| --game-path          |            | False                                            | Falseにすると自動                 |        |
| --dmmgameplayer-path | -dgp-path  | C:/Program Files/DMMGamePlayer/DMMGamePlayer.exe |                                   |        |
| --non-kill           |            | False                                            | DMMGamePlayerが起動したままになる | bool   |
| --debug              |            | False                                            | デバッグモード                    | bool   |
| --login-force        |            | False                                            | ログインを強制する                | bool   |

## ヘルプ

> **セットアップする際、WindowsによってPCが保護されましたと表示される**<br>
> 詳細情報をクリックして実行をクリック

> **ゲームのアイコンに寄せたい**<br>
> ショートカットを右クリック→プロパティ→アイコンの変更→参照

> **ゲームのパスの検出に失敗しましたというエラーが出るまたは起動しない**<br>
> --game-path <ゲームのパス> を指定する<br>
例<br>
`%AppData%\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe umamusume --game-path %UserProfile%/umamusume/umamusume.exe`<br>

## 典拠
[Lutwidse/priconner_launch.py](https://gist.github.com/Lutwidse/82d8e7a20c96296bc0318f1cb6bf26ee)

## ライセンス
DMMGamePlayerFastLauncher is under MIT License