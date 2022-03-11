# DMMGamePlayerFastLauncher
DMM Game Player のゲームを高速かつセキュアに起動できるランチャー

## 特徴
- **ワンクリックでゲームを起動**
- **管理者権限不要**

## インストール
[Releases](https://github.com/fa0311/DMMGamePlayerFastLauncher/releases) から DMMGamePlayerFastLauncher.exe をダウンロード<br>
ダウンロードしたファイルをどこかに設置 ( `C:\Program Files\DMMGamePlayerFastLauncher` とかが良いかも )

## 使い方
ダウンロードした *DMMGamePlayerFastLauncher.exe* を右クリックしショートカットを作成<br>
ショートカットのプロパティのリンク先に *product_id* と起動したいゲームのexeのパスを追記<br>

例: `<DMMGamePlayerFastLauncher.exeのパス> <product_id> <ゲームのexeのパス>`<br>
ウマ娘の例: `"C:\Program Files\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe" umamusume "%UserProfile%\Umamusume\umamusume.exe"`<br>
プリコネの例: `"C:\Program Files\DMMGamePlayerFastLauncher\DMMGamePlayerFastLauncher.exe" priconner "%UserProfile%\priconner\PrincessConnectReDive.exe"`<br>

## product_id について

## product_id まとめ

## 引数

## 典拠
[Lutwidse/priconner_launch.py](https://gist.github.com/Lutwidse/82d8e7a20c96296bc0318f1cb6bf26ee)

## ライセンス
DMMGamePlayerFastLauncher is under MIT License