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
* `load-test:embed-observability`: Open dashboards with observability metrics.

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
* `--stop-timeout INTEGER`: How many seconds to wait for the load test to stop  [default: 15]
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
* `--run-once / --no-run-once`: Make each user run its render task only once.  [default: no-run-once]
* `--help`: Show this message and exit.

## `lkr load-test:embed-observability`

Open dashboards with observability metrics. The metrics are collected through Looker&#x27;s JavaScript events and logged with the specified prefix. This command will:
1. Start an embed server to host the dashboard iframe
2. Spawn multiple users that will:
   - Open the dashboard in an iframe
   - Wait for the dashboard to load
   - Track timing metrics for:
     - dashboard:loaded - Dashboard load time
     - dashboard:run:start - Query start time
     - dashboard:run:complete - Query completion time
     - dashboard:tile:start - Individual tile start time
     - dashboard:tile:complete - Individual tile completion time
3. Will also track start and end times for the whole process (looker_embed_task_start and looker_embed_task_complete)
4. Log all events with timing information to help analyze performance in a JSON format.  Events begin with &lt;log_event_prefix&gt;:*
5. Automatically stop after the specified run time

**Usage**:

```console
$ lkr load-test:embed-observability [OPTIONS]
```

**Options**:

* `--dashboard TEXT`: Dashboard ID to render  [required]
* `--users INTEGER RANGE`: Number of users to run the test with  [default: 5; 1&lt;=x&lt;=1000]
* `--spawn-rate FLOAT RANGE`: Number of users to spawn per second  [default: 1; 0&lt;=x&lt;=100]
* `--run-time INTEGER RANGE`: How many minutes to run the load test for  [default: 5; x&gt;=1]
* `--port INTEGER`: Port to run the embed server on  [default: 4000]
* `--min-wait INTEGER RANGE`: Minimum wait time between tasks  [default: 60; x&gt;=1]
* `--max-wait INTEGER RANGE`: Maximum wait time between tasks  [default: 120; x&gt;=1]
* `--model TEXT`: Model to run the test on. Specify multiple models as --model model1 --model model2
* `--completion-timeout INTEGER RANGE`: Timeout in seconds for the dashboard run complete event  [default: 120; x&gt;=1]
* `--attribute TEXT`: Looker attributes to run the test on. Specify them as attribute:value like --attribute store:value. Excepts multiple arguments --attribute store:acme --attribute team:managers. Accepts random.randint(0,1000) format
* `--log-event-prefix TEXT`: Prefix to add to the log event  [default: looker-embed-observability]
* `--open-url / --no-open-url`: Do not open the URL in the observability browser, useful for viewing a user&#x27;s embed dashboard when running locally  [default: open-url]
* `--debug`: Enable debug mode
* `--help`: Show this message and exit.
