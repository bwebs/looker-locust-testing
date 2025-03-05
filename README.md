Starting up

```
cp .env.example .env
gcloud builds submit -t gcr.io/looker-load-tests/lkr-test .

```

Local

```
lkr load-test:query --query=BLYyJ70e7HCeBQJrxXanHi --users=1 --run-time=5 --model=az_load_test --attribute "store:random.randint(1,7000)" --query-async
lkr load-test --dashboard=1 --users=5 --run-time=1 --attribute store:random.randint(1,7000) --model=az_load_test

```

Docker

```
docker run --pull=always gcr.io/looker-load-tests/lkr-test:latest lkr load-test --dashboard=1 --users=5 --run-time=1
```
