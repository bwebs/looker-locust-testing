Starting up

```
cp .env.example .env
gcloud builds submit -t gcr.io/looker-load-tests/lkr-test .

gcloud builds submit -t us-central1-docker.pkg.dev/lkr-dev-production/load-tests/lkr-load-test .

```

Local

```
lkr load-test:query --query=BLYyJ70e7HCeBQJrxXanHi --users=1 --run-time=5 --model=az_load_test --attribute "store:random.randint(1,7000)" --query-async
lkr load-test --dashboard=1 --users=5 --run-time=1 --attribute store:random.randint(1,7000) --model=az_load_test
lkr load-test:render --dashboard=1 --users=5 --run-time=1 --model=az_load_test

uv run --env-file=.env lkr debug looker

```

Docker

```
docker run --pull=always gcr.io/looker-load-tests/lkr-test:latest lkr load-test --dashboard=1 --users=5 --run-time=1
docker run -e LOOKERSDK_CLIENT_ID=abc -e LOOKERSDK_CLIENT_SECRET=123 -e LOOKERSDK_BASE_URL="https://autozoneloadtest.cloud.looker.com" -p 8080:8080 --pull=always us-central1-docker.pkg.dev/lkr-dev-production/load-tests/lkr-load-test lkr load-test:embed-observability --model=az_load_test --dashboard=1 --attribute="store:random.randint(0,7000)" --spawn-rate=1 --users=1 --run-time=2 --completion-timeout=45 --port=8080 --no-open-url


```

Docs

```
typer lkr/main.py utils docs --output lkr.md
```



gcloud run jobs create lkr-help-job \
    --image=us-central1-docker.pkg.dev/lkr-dev-production/load-tests/lkr-load-test \
    --command='lkr' \
    --args='load-test --dashboard=1 --users=5 --run-time=1 --model=az_load_test --run-time=1' \
    --project=your-project-id \
    --region=your-region \ 
    --set-env-vars=LOOKERSDK_CLIENT_ID=your-client-id,LOOKERSDK_CLIENT_SECRET=your-client-secret,LOOKERSDK_BASE_URL=https://your-looker-instance.com