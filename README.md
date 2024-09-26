# backend-znrj

backend znrj python

#### 新的backend在backend文件夹，在重构中

---

#### 帮助文档

* 本代码api开发使用fastapi和fastcrud
  * fastcrud地址：https://github.com/igorbenav/fastcrud
  * fastcrud文档地址：https://igorbenav.github.io/fastcrud/
  * 关于条件查询，看Advanced Filters这一节：https://igorbenav.github.io/fastcrud/advanced/crud/#single-parameter-filters

#### 分支管理

* develop：开发分支，同步最新版本代码，开发版本，未部署云端
* stable：稳定分支，同步支持app和web的代码，生产版本，已部署云端，部署在生产端口
  * 端口：
    * 6200：web对话页面（移动端支持）
    * 6201：基础接口，日历接口，语音服务，图片识别接口
    * 6202：ai对话接口，地理位置接口
* test：测试分支，同步用于测试后台功能的代码，测试版本，已部署云端，部署在测试端口
  * 端口：
    * 6201：所有后台接口，已分类和注释
* other：其他开发参与者自建分支

#### 功能清单、测试地址、测试覆盖率

* 对话服务
  * 思维链
  * Function Call 和 Agent
  * 数据操作
  * 提示词
  * 对话历史
  * RAG
  * 辅助功能
* 数据服务
  * 日历服务
  * 记录服务
* 地理服务
  * 位置获取/记录
  * 位置感知
* 多用户服务
  * 对话隔离
  * 对话历史隔离
  * 数据隔离
  * 注册登录
* 缓存服务
  * 配置/初始化
  * 对话跟踪
  * 数据持久化
* 多模态服务
  * 图像识别
  * 语音识别
  * 语音生成
* Web服务
  * 发布页
  * 帮助文档
  * 线上体验
  * 公众号

#### 部署和开发前置

* 后端
  * python
    * conda->虚拟环境 py3.9
    * requirement
    * docker
    * 异步和多线程
    * redis、mq和分布式
  * 服务器
    * ssh、注册服务、容器等
    * frp大模型机器、数据库机器
    * nginx、load balance
    * 服务器申请、备案、运维、安全策略等
  * 数据库
    * sqlite
    * pg
  * 大语言模型
    * Openai：CoT、RAG、MLLM、Prompt、FC、Agent、Workflow、微调
    * 第三方：Dify、AnythingLLM、
    * 模型：Gpt、Glm、Claude（代替llava）
    * 部署：HF、Ollama、Kaggle
* 前端
  * flutter
    * 环境部署
    * 拉取代码->创建该环境新项目->覆盖代码
    * websim原型构建
  * ios
    * xcode环境部署
    * ipa
    * app store
  * web
    * vue->NaiveUI ? tailwind
    * markdown语法->生成文档
    * uniapp ？wx-gongzhonghao

#### weekly问题汇总

1. 2024-09-19
   * 问题：如何实现多用户对话隔离？
   * 解决：使用fastapi的依赖注入，每个用户的对话都是一个独立的对象，通过依赖注入的方式，将用户的对话对象注入到对话服务中，实现对话隔离。
2.
