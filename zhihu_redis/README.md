#####知乎用户scrapy_redis分布式爬取####       
选取关注者多的对象，指定知乎用户excited-vczh作为开始的爬取对象，爬取用户信息，他关注的人，关注他的人       
start_user = 'excited-vczh'     
在本机模拟分布式爬取，开启多个终端运行 scrapy crawl zhihu       
redis数据库中多了三个文件，分布式运行环境配置成功，数据保存在redis数据库。       
process_item.py将redis数据下载到本地MongoDB，也可以在setting.py中直接保存到本地，关闭上传到redis中。    
反爬：随机user-agent和proxy
![iamge](https://github.com/Abc2149/add_pic/blob/master/image/2018-05-19_140435.png)
![image](https://github.com/Abc2149/add_pic/blob/master/image/2018-05-19_140507.png)
![image](https://github.com/Abc2149/add_pic/blob/master/image/2018-05-19_140239.png)
