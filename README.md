# MARINE TRASHART －アート製作を通じた海洋ごみ処理－
第33回高専プロコン 自由部門 応募作品

## ソースコード
このリポジトリはサーバー（バックエンド）のソースコードを管理しています。

[Webアプリ（フロントエンド）のリポジトリはこちらから](https://github.com/ezaki-lab/2022-trashart)

## URL
```https://ezaki-lab.cloud/~trashart/api/```

## システム概要
「MARINE TRASHART」はアート作品を作るために浜辺のごみを拾うことによって、ごみ問題解決に繋げることを支援します。

## 起動コマンド
```gunicorn -b 0.0.0.0:{PORT} -k eventlet main:app --reload```
