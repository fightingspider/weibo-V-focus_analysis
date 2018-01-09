# weibo-V-focus_analysis

通过个人账号模拟登录微博,递归爬取关注列表(根据需求设定爬取深度吧,数据量指数增长)

微博的反爬很厉害,模拟登录需要分析模拟浏览器的请求过程,PhantomJs不可行,似乎被ban掉了

![img_text](https://github.com/fightingspider/weibo-V-focus_analysis/raw/master/screen_img/V_focus_network.png)

图中分析了粉丝数大于500万的大V关注列表网络图,实际分析结果与登录账号和爬取深度有关,小项目仅作学习用
