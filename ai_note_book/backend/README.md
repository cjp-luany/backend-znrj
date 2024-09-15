

# 智能记录助手 - 后端

后端结构简介：

    本代码的目的是为智能助手app和web端提供后台，满足记录储存、大模型应用、多端发布和使用的需求，因此本代码仓库中包含对应的服务，app对应的是mobile服务，web对应的是web服务，大模型应用对应大模型服务，针对多用户管理对应用户和验证服务，每个服务在启动父main脚本后有各自的端口，每个服务可以使用不同的组织结构，由对应代码开发者负责。建议在服务中包含的结构是：应用(app)，资源(res)，和测试(test)，以及启动服务的子main脚本，每个服务尽量都要做到使用单元测试覆盖写好的代码，单元测试里使用控制台都没关系，提高后台代码健壮性，下面具体说代码结构内容：

## 具体

- 父main脚本：
  - 有一个数组用于定义要启动哪些服务
  - 使用python启动线程方式启动每个服务的子main脚本
  - 要在父main脚本目录下的 .env配置你的python路径，此点是针对conda或venv创建的python虚拟环境，不同版本的python和依赖库，你可以设置不同路径的python
- common：
  - 所有服务可以公用的函数、模型、缓存层、api客户端请求封装（用于大模型请求）
  - database使用了fastcrud的orm，你只需要在这里定义模型，数据库连接，它会在程序启动时自动创建数据库文件、数据库表，可以使用event拦截器在新增数据时自动加主键
  - cache希望使用redis做缓存管理，因为chat history需要设置超时，使用redis可以自带超时和设置是否持久化
  - config用于封装读取env的方法
  - security用于用户验证、注册、调用fastapi默认的outh token等
  - apiclients用于封装请求大模型的http方法
- 服务文件夹：
  - 子main脚本：设置启动fastapi或flask，在webservice中我打算使用flask挂载静态资源，其他需要接口的地方使用fastapi和fastcrud，设置跨域的cors，设置fastcrud的路由生成基础接口
  - app：编写具体函数，业务需求接口
  - res：存放json，txt，md等，用于文件资源储存，比如提示词的txt
  - test：编写单元测试方法，用于测试app中写的函数
  - .env：里面有个port记录启动子服务的端口，可以在里面添加大模型的key等
- 其他
  - docker-compose：配置docker
  - github.workflow：用于配合github仓库做 ci/cd
  - requirement：设置整个程序需要的python环境
  - sqlite：我把现在使用的sqlite目录设置为程序根目录，可以在common.database中更改，只需要改common.database一处









##### 参考结构 无关内容

```TXT
my_project/
│
├── common/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── cache.py
│   ├── security.py
│   └── api_clients.py         # API 封装层
│
├── service1/
│   ├── __init__.py
│   ├── main.py
│   ├── service1_env.env
│   └── app/
│       ├── __init__.py
│       ├── routes.py
│       └── models.py
│
├── service2/
│   ├── __init__.py
│   ├── main.py
│   ├── service2_env.env
│   └── app/
│       ├── __init__.py
│       ├── routes.py
│       └── models.py
│
├── main.py
├── docker-compose.yml
├── requirements.txt
└── README.md

my_project/
│
├── common/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── cache.py
│   └── security.py
│
├── user_service/
│   ├── __init__.py
│   ├── main.py
│   ├── user_service_env.env
│   ├── app/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── models.py
│   └── tests/
│       ├── __init__.py
│       └── test_routes.py
│
├── product_service/
│   ├── __init__.py
│   ├── main.py
│   ├── product_service_env.env
│   ├── app/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── models.py
│   └── tests/
│       ├── __init__.py
│       └── test_routes.py
│
├── main.py
├── docker-compose.yml
├── requirements.txt
├── .env
└── README.md
```
