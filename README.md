# DMMGamePlayerFastLauncher
DMM Game Player のゲームを高速かつセキュアに起動できるランチャー

## 特徴
- **ワンクリックでゲームを起動**
- **管理者権限不要**

## インストール
[Releases](https://github.com/fa0311/DMMGamePlayerFastLauncher/releases) から DMMGamePlayerFastLauncher-Setup.exe をダウンロード<br>
実行してセットアップする

## 使い方
ダウンロードした *C:\Program Files (x86)\DMMGamePlayerFastLauncher* にある *DMMGamePlayerFastLauncher.exe* を右クリックしショートカットを作成<br>
作成したショートカットのプロパティのリンク先に *product_id* を追記<br>

例: `C:\Program Files (x86)\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe <product_id>`<br>

product_idは存在しないproduct_idが指定された際のエラーにダウンロードされているソフトのproduct_idが表示されるのでそれを参考にして下さい<br>
*C:\Program Files (x86)\DMMGamePlayerFastLauncher\sample* にサンプル用のショートカットを置いています<br>

## 引数
`DMMGamePlayerFastLauncher.exe <product_id>`

| オプション           | エイリアス | デフォルト                                       | 備考                              | タイプ |
|----------------------|------------|--------------------------------------------------|-----------------------------------|--------|
| --help               | -h         | False                                            |                                   | bool   |
| --game-path          |            | False                                            | Falseにすると自動                 |        |
| --dmmgameplayer-path | -dgp-path  | C:/Program Files/DMMGamePlayer/DMMGamePlayer.exe |                                   |        |
| --non-kill           |            | False                                            | DMMGamePlayerが起動したままになる | bool   |
| --debug              |            | False                                            | デバッグモード                    | bool   |

## 典拠
[Lutwidse/priconner_launch.py](https://gist.github.com/Lutwidse/82d8e7a20c96296bc0318f1cb6bf26ee)

## ライセンス
DMMGamePlayerFastLauncher is under MIT License