

# 智能记录助手 - 后端

后端结构简介：

* 本代码的目的是为智能助手app和web端提供后台，满足记录储存、大模型应用、多端发布和使用的需求

---

#### 帮助文档

* 本代码api开发使用fastapi和fastcrud
  * fastcrud地址：https://github.com/igorbenav/fastcrud
  * fastcrud文档地址：https://igorbenav.github.io/fastcrud/
  * 关于条件查询，看Advanced Filters这一节：https://igorbenav.github.io/fastcrud/advanced/crud/#single-parameter-filters

#### 分支管理

* #### develop：开发分支，同步最新版本代码，开发版本，未部署云端
* #### stable：稳定分支，同步支持app和web的代码，生产版本，已部署云端，部署在生产端口
  * 端口：
    * 6200：web对话页面（移动端支持）
    * 6201/docs：基础接口，日历接口，语音服务，图片识别接口
    * 6202/docs：ai对话接口，地理位置接口
* #### test：测试分支，同步用于测试后台功能的代码，测试版本，已部署云端，部署在测试端口
  * 端口：
    * 6880：页面
    * 6881/docs：所有后台接口，已分类和注释
* other：其他开发参与者自建分支