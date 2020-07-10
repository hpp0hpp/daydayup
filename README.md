.
最近想建个网站,借鉴了Hopetree/izone的代码,从对django一无所知,到熟练应用,添加了一些小功能,最终部署在自己的小站上,欢迎大家访问 
博客效果： https://www.daydayupclub.co/

## 新增功能
- 增加投稿功能(Markdown编辑器),投稿需要审核才能在首页展示
- 增加分类的父子分类功能
- 修改文章分类为树形结构(tree view),适合有大量分类的网站
- 修改下一篇文章为按照发布日期排列的上一篇文章,方便用户右手操作从最新的文章一直往之前的文章浏览
- 增加右下角回到首页小按钮,方便手机操作,从详情页直接返回首页
- 增加爬虫功能,便于爬取一些内容增加到文章
- 降低上下页的按钮,方便手机单手操作
- 增加详情页的切换主题按钮
- 还有好多其他的,后面再补充

## 功能介绍
- Django 自带的后台管理系统，方便对于文章、用户及其他动态内容的管理
- 文章分类、标签、浏览量统计以及规范的 SEO 设置
- 用户认证系统，在 Django 自带的用户系统的基础上扩展 Oauth 认证，支持微博、Github 等第三方认证
- 文章评论系统，炫酷的输入框特效，支持 markdown 语法，二级评论结构和回复功能
- 信息提醒功能，登录和退出提醒，收到评论和回复提醒，信息管理
- 强大的全文搜索功能，只需要输入关键词就能展现全站与之关联的文章
- RSS 博客订阅功能及规范的 Sitemap 网站地图
- 实用的在线工具
- 友情链接和推荐工具网站的展示
- 缓存系统，遵循缓存原则，加速网站打开速度
- RESTful API 风格的 API 接口

## 博客页面效果（响应式）
- PC 页面效果

![pc](https://user-images.githubusercontent.com/30201215/60588842-93321b80-9dca-11e9-93f2-50e34b2c4b3f.jpg)

- PC 暗色主题效果

![tendcode_2019-11-22_23-18-55](https://user-images.githubusercontent.com/30201215/69438380-e576d780-0d7f-11ea-9ea5-c182caa3a2a8.png)

- ipad 效果

![ipad](https://user-images.githubusercontent.com/30201215/60588800-7e558800-9dca-11e9-8beb-5d2dcf01b869.jpg)

- 手机效果

![iphone](https://user-images.githubusercontent.com/30201215/60588832-8e6d6780-9dca-11e9-84fa-f1d71510c81e.jpg)

## 运行指导
- 由于本项目分为几个不同的分支，每个分支的功能是一样的，但是运行的方式不同，所以需要根据分支查看对应的运行wiki
- 指导 wiki：https://github.com/Hopetree/izone/wiki
