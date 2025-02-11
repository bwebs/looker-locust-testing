

```

cp .env.example .env

gcloud builds submit -t gcr.io/looker-load-tests/locust-test .

uv run --env-file=.env locust --web-port 8080 --users 1000 --spawn-rate 1 --host https://localhost:8080


```