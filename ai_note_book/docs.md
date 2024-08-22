# 开发日历服务功能
---
### 简单描述日历流程：
* 1. app发送信息到日历服务api 如 { "message" : "我今晚8点在家吃饭" }
* 2. api返回信息 如 { "data" : "好的，已经帮您记下来了", code:200 }
* 3. app在每日显示事项页面查询，能够看到晚上8点有 "在家吃饭" 事项
* 4. app在按月显示页面能看到今天有一个事项，点击今天能看到 "在家吃饭" 事项
* 备注：
  * 以上从自然语言，到api返回记下来这件事需要用 大语言模型（未完成）、数据库记录接口（已有）完成
  * 以上查询接口未有
  * 以上app ui界面参考下面的git连接
  * 以上日历服务api也参考ui界面思考要实现哪些api
  * 日历服务api最后以 fastapi docs形式给出
  * 日历服务api最基础要实现按日查询0点到24点事项功能
  * 本代码api开发使用fastapi和fastcrud
    * fastcrud地址：https://github.com/igorbenav/fastcrud
    * fastcrud文档地址：https://igorbenav.github.io/fastcrud/
    * 关于条件查询，看Advanced Filters这一节：https://igorbenav.github.io/fastcrud/advanced/crud/#single-parameter-filters
  * 如fastcrud无法实现，请使用fastapi和sqlalchemy实现，参考代码文件下 sqlalchemy-demo.py.bak
  * 将main里对query_during_chat()调用的注释去掉可以测试对话中rag查询功能
    

### 日历ui界面git连接
* 日历按日显示界面参考：https://github.com/Jamalianpour/time_planner
* 日历按月显示界面参考：https://github.com/aleksanderwozniak/table_calendar

