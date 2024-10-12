

# 🚀🚀🚀青马易战自动刷题

可以实现高速的自动刷题，自动AI对战，自动爬取题库，仅供学习交流，严禁用于商业用途


### 上手指南


##### 开发前的配置要求

1. python
2. requests
3. Crypto

##### 程序说明 

**old**开头的是旧版刷题程序，适配旧版题库。

qmauto是自动刷题程序。

get_timu是自动爬取题库程序，推荐使用fight爬，可以获得更高的积分。

old_fight是ai对战程序。

qmyz存放旧版题库，使用old程序运行

new_qmyz存放新版题库

默认题库不一定最新，用户可以在此基础上爬取新题目

JSESSIONID通过cookie获取

通过get_timu爬取题目转换为CSV，使用qmauto读取CSV实现自动刷题。

fight是AI对战功能，可以自动添加题库找不到的题目。推荐使用fight来爬取题目。




### 作者

shibig



### 版权说明



该项目签署了GPLv3授权许可，详情请参阅 LICENSE.txt





