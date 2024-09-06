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
