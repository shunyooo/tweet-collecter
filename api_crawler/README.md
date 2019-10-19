# APIからの取得

- 正規な tweet 取得ルート
- 無料だと上限が厳しい
- トークンを取得する必要あり



# RUN

1. **(optional) get twitter app token** [参考](https://qiita.com/bakira/items/00743d10ec42993f85eb) 
2. **setting config.ini**
3. **docker (or docker-compose) run**

#### docker-compose

```bash
docker-compose up tweet-crawler --build
```

#### docker

```bash
docker build -t tweet_api_crawler ./env/api_crawler
docker run --rm -d -it -v $(pwd):/app -w /app tweet_api_crawler python crawl_stream.py
```



# TODO

- [x] Docker 環境構 築
- [x] Docker 起動だけでStreamをDBに追加していく機構
- [x] 並列実行の考慮（docker run を非同期で回すだけで良いかも）
  - [ ] 並列実行の検証
- [ ] ログのクラウド化（StackDriver）
- [ ] 実行プロセスやマシンIDのログ（今何台で取得していて、何件とれているかを知りたい）
- [ ] 集計ビューの作成
  - [ ] UI, UX, アプリ構成 練る
  - [ ] Backend 実装（データの集計等, 別で集計DB立てる？, Django REST APIで実装）
  - [ ] Frontend 実装（React or Vue)



# LINKS

- [公式ドキュメント](https://developer.twitter.com/en/docs)
- [公式ドキュメント日本語訳](http://westplain.sakuraweb.com/translate/twitter/Documentation/REST-APIs/Public-API/REST-APIs.cgi)
- モデル参考：https://github.com/qnighy/qnighy-twitter-crawler



