# tweet-crawler

ツイッターをスクレイプするやつ。[GetOldTweets3](https://github.com/Mottl/GetOldTweets3)を使用。

# 実行

## DB挿入先指定

`config/config.ini`

```ini
[db]
  DBMS :mysql+mysqldb
  HOST :*****
  USER :wsl-user
  PASS :*****
  DB   :arb
  POOL_RECYCLE:300
```

## 実行

#### docker build & run crawl

```bash
. scripts/build-docker.sh
. scripts/run-docker-crawl.sh ダンジョン飯 --since 2019-06-10 --until 2019-06-11
```

#### ローカル → GCE

```bash
gcloud compute --project "machinelearning-219614" ssh --zone "us-central1-a" "syunyooo@arb-tweet-crawler-1" --command "docker run -d -v /home/syunyooo/auto-ranking-blog/crawler/tweet-crawler/:/app tweet-crawler_jupyter python main.py ダンジョン飯 --since 2019-06-10 --until 2019-06-11"
```

```bash
gcloud compute --project "machinelearning-219614" ssh --zone "us-central1-a" "syunyooo@arb-tweet-crawler-18" --command "docker run -d -v /home/syunyooo/auto-ranking-blog/crawler/tweet-crawler/:/app tweet-crawler_jupyter python main.py ダンジョン飯 --since 2019-06-10 --until 2019-06-11"
```





# 参考

- ~~[twitterscraper](https://github.com/taspinar/twitterscraper)~~
  - ~~クロールの核部分のスクリプト。~~
  - ~~ロガーの組み込みや取得時のコールバック等を導入した~~
- [GetOldTweets3](https://github.com/Mottl/GetOldTweets3)
  - 漏れやBANがなさそうなのでこっちを採用









