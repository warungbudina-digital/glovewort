# File Tree

```text
glovewort/
├── README.md
├── .env.example
├── docker-compose.yml
├── docs/
│   ├── ARCHITECTURE.md
│   ├── SPEC.md
│   ├── FILE_TREE.md
│   ├── DEPLOYMENT.md
│   ├── TELEGRAM.md
│   ├── SECURITY.md
│   └── TROUBLESHOOTING.md
├── deploy/
│   └── ollama-fastapi/
│       ├── .env.example
│       ├── README.md
│       ├── docker-compose.yml
│       ├── openclaw.config.example.yaml
│       └── api/
│           ├── Dockerfile
│           ├── main.py
│           └── requirements.txt
├── openclaw/
│   ├── Dockerfile
│   ├── config/
│   │   ├── openclaw.config.yaml
│   │   ├── model-routing.yaml
│   │   └── permissions.yaml
│   └── scripts/
│       ├── entrypoint.sh
│       ├── wait-for-bridge.sh
│       └── healthcheck.sh
├── ollama/
│   ├── Modelfile
│   ├── scripts/
│   │   ├── pull-model.sh
│   │   └── healthcheck.sh
│   └── data/
├── logs/
└── state/
```
