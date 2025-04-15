# `lkr`

**Usage**:

```console
$ lkr [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--env-file FILE`: Path to the environment file to load  [default: /Users/bryanweber/projects/load-tests/.env]
* `--client-id TEXT`: Looker API client ID
* `--client-secret TEXT`: Looker API client secret
* `--base-url TEXT`: Looker API base URL
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `debug`: Check that the environment variables are...
* `load-test`
* `load-test:query`
* `load-test:render`

## `lkr debug`

Check that the environment variables are set correctly

**Usage**:

```console
$ lkr debug [OPTIONS] TYPE:{looker}
```

**Arguments**:

* `TYPE:{looker}`: Type of debug to run (looker)  [required]

**Options**:

* `--help`: Show this message and exit.

## `lkr load-test`

**Usage**:

```console
$ lkr load-test [OPTIONS]
```

**Options**:

* `--users INTEGER RANGE`: Number of users to run the test with  [default: 25; 1&lt;=x&lt;=1000]
* `--spawn-rate FLOAT RANGE`: Number of users to spawn per second  [default: 1; 0&lt;=x&lt;=100]
* `--run-time INTEGER RANGE`: How many minutes to run the load test for  [default: 5; x&gt;=1]
* `--dashboard TEXT`: Dashboard ID to run the test on. Keeps dashboard open for user, turn on auto-refresh to keep dashboard updated
* `--model TEXT`: Model to run the test on. Specify multiple models as --model model1 --model model2
* `--attribute TEXT`: Looker attributes to run the test on. Specify them as attribute:value like --attribute store:value. Excepts multiple arguments --attribute store:acme --attribute team:managers. Accepts random.randint(0,1000) format
* `--help`: Show this message and exit.

## `lkr load-test:query`

**Usage**:

```console
$ lkr load-test:query [OPTIONS]
```

**Options**:

* `--query TEXT`: Query ID (from explore url) to run the test on  [required]
* `--users INTEGER RANGE`: Number of users to run the test with  [default: 25; 1&lt;=x&lt;=1000]
* `--spawn-rate FLOAT RANGE`: Number of users to spawn per second  [default: 1; 0&lt;=x&lt;=100]
* `--run-time INTEGER RANGE`: How many minutes to run the load test for  [default: 5; x&gt;=1]
* `--model TEXT`: Model to run the test on. Specify multiple models as --model model1 --model model2
* `--attribute TEXT`: Looker attributes to run the test on. Specify them as attribute:value like --attribute store:value. Excepts multiple arguments --attribute store:acme --attribute team:managers. Accepts random.randint(0,1000) format
* `--wait-time-min INTEGER RANGE`: User tasks have a random wait time between this and the max wait time  [default: 1; 1&lt;=x&lt;=100]
* `--wait-time-max INTEGER RANGE`: User tasks have a random wait time between this and the min wait time  [default: 15; 1&lt;=x&lt;=100]
* `--sticky-sessions / --no-sticky-sessions`: Keep the same user logged in for the duration of the test. sticky_sessions=True is currently not supported with the Looker SDKs, we are working around it in the User class.  [default: no-sticky-sessions]
* `--query-async / --no-query-async`: Run the query asynchronously  [default: no-query-async]
* `--async-bail-out INTEGER`: How many iterations to wait for the async query to complete (roughly number of seconds)  [default: 120]
* `--help`: Show this message and exit.

## `lkr load-test:render`

**Usage**:

```console
$ lkr load-test:render [OPTIONS]
```

**Options**:

* `--dashboard TEXT`: Dashboard ID to render  [required]
* `--users INTEGER RANGE`: Number of users to run the test with  [default: 25; 1&lt;=x&lt;=1000]
* `--spawn-rate FLOAT RANGE`: Number of users to spawn per second  [default: 1; 0&lt;=x&lt;=100]
* `--run-time INTEGER RANGE`: How many minutes to run the load test for  [default: 5; x&gt;=1]
* `--model TEXT`: Model to run the test on. Specify multiple models as --model model1 --model model2
* `--attribute TEXT`: Looker attributes to run the test on. Specify them as attribute:value like --attribute store:value. Excepts multiple arguments --attribute store:acme --attribute team:managers. Accepts random.randint(0,1000) format
* `--result-format TEXT`: Format of the rendered output (pdf, png, jpg)  [default: pdf]
* `--render-bail-out INTEGER`: How many iterations to wait for the render task to complete (roughly number of seconds)  [default: 120]
* `--help`: Show this message and exit.
