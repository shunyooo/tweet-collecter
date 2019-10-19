# APIからの取得

- 正規な tweet 取得ルート
- 無料だと上限が厳しい
- トークンを取得する必要あり



#### トークン取得

[ここらへん](https://qiita.com/bakira/items/00743d10ec42993f85eb)参考に



# RUN

1. **setting config.ini**
2. **docker (or docker-compose) run**

#### docker-compose

```bash
docker-compose up tweet-crawler --build
```

#### docker

```bash
docker build -t tweet_api_crawler ./env/api_crawler
docker run --rm -d -it -v $(pwd):/app -w /app tweet_api_crawler python crawl_stream.py
```



# LINKS

- [公式ドキュメント](https://developer.twitter.com/en/docs)
- [公式ドキュメント日本語訳](http://westplain.sakuraweb.com/translate/twitter/Documentation/REST-APIs/Public-API/REST-APIs.cgi)
- モデル参考：https://github.com/qnighy/qnighy-twitter-crawler



