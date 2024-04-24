# 開発について

## 開発
QueenBeeの制御班は4人いたので、役割分担をして開発を進めていました。Case部分 (打ち上げ前から、パラシュート降下後の着地、足部、腕の展開まで) と、Drone部分 (飛行、精密着陸まで)を2人ずつで分担し、臨機応変に対応していました。


## プログラムの概要
CaseとDrone、画像航法用のCameraでそれぞれクラスを作成しました。それらを`/queenbee_main/main/queenbee`にまとめてあります。
本番で動かしたのは`/queenbee_main/main/qb_main_daemon.py`です。

## Case部分
担当: 山城
ロケットへの収納判定、ロケットからの放出判定、パラシュート降下後の着地判定の3つを判定し、その後機体を展開するプログラムです。
光センサー、気圧センサーを使用しました。
細かい内容・アルゴリズムは実際にプログラムを読んでください。`/queenbee_main/main/queenbee/class_case.py`に置いてあります。

## Drone部分 
担当: 秀島
### ゴールまでの飛行
基本的にDrone制御は[mavsdk.System](https://github.com/mavlink/MAVSDK-Python?tab=readme-ov-file)の子クラスである`queenbee.bee`を使って制御しています。
[ライブラリ](http://mavsdk-python-docs.s3-website.eu-central-1.amazonaws.com/system.html#mavsdk.system.System)と、
`asyncio`(非同期処理)の理解がほぼ全てです。

二つある自律飛行モードの、MissionモードとGotoモードのうち、Takeoff → Goto モードで飛行しました。`/queenbee_main/main/qb_main.py`がわかりやすいと思います。

### Precision Landing
picamera ver.1.3を用いて撮影した画像を使用。撮影に用いたライブラリはpicamera2で、画像処理に用いたのはopencvです。hsv空間で閾値を決め、ゴールの場所を認識し、座標を計算してGotoでゴールに近づくという動作を繰り返しました。画像の撮影は`/queenbee_main/main/queenbee/camera2.py`、画像航法は`/queenbee_main/main/queenbee/bee.py`においてあります。

## 地上との通信
担当: 野村

地上との通信にはLoRaを用いました。詳しくは`/queenbee_main/main/queenbee/lora_queenbee.py`を見てください。

本番は使用ませんでしたが、`gc_main.py`はLoRaでダウンリンクしてきたデータをGoogleMapで追跡するスクリプトです。
時間がなくてかなりUIに頼ったコードになってるので、時間があればAPIを叩いてしっかり実装してみてもいいかもです。(秀島)