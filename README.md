

```

cp .env.example .env

uv run --env-file=.env locust --headless --users 1000 --spawn-rate 1 --host https://localhost:8080
```