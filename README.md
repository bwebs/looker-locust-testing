

Starting up
```
cp .env.example .env
gcloud builds submit -t gcr.io/looker-load-tests/lkr-test .

```

Local
```
lkr load-test --dashboard=1 --users=5 --run-time=1
```

Docker
```
docker run --pull=always gcr.io/looker-load-tests/lkr-test:latest lkr load-test --dashboard=1 --users=5 --run-time=1
```


