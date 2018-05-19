# 多线程爬取知乎用户信息

目录结构
-zhihu
    -datafile
        -1.csv
        -2.csv
        ....
    -spider
        -crawl.py
        -datafile.py
        -run.py
    -tool
        -proxy
-运行 python run.py

crawl.py
- 获取指定用户的详情信息和他关注的用户列表
- 单例模式，线程安全
- 在知乎未登录的情况下，爬取知乎的用户，注意：需要携带authorization未登录状态的授权码，不然会一直返回一些不相干的信息。
- 反爬：
    from fake_useragent import UserAgent
    get_random_proxy()  代理IP：免费代理IP不稳定，可以购买稳定的IP代理
- 爬取的方式：


datafile.py
- 将知乎用户的信息存储到csv文件
- 必要的功能：
    从已有的csv文件中提取所有已爬取的用户和待爬取的用户，防止程序意外中断，可以继续爬取
    去重
- 单例模式，线程安全
- 默认爬取10万用户

run.py 
- 多线程
    主线程：维护一个待爬取响应队列，更新待爬取和已爬取数量
    子线程：从响应队列获取用户，保存用户信息，获取新的用户，去重已爬取用户再放入任务队列。

- crawled_set 已爬取用户集合
- task_set 未爬取用户集合
- log 更新状态信息












   
        