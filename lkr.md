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

* `hello`: Say hello, world!
* `debug`: Check that the environment variables are...
* `load-test`
* `test-qid`

## `lkr hello`

Say hello, world!

**Usage**:

```console
$ lkr hello [OPTIONS]
```

**Options**:

* `--hidden TEXT`: [default: True]
* `--help`: Show this message and exit.

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
* `--spawn-rate FLOAT RANGE`: Number of users to spawn per second  [default: 1; 1&lt;=x&lt;=100]
* `--run-time INTEGER RANGE`: How many minutes to run the load test for  [default: 5; x&gt;=1]
* `--dashboard TEXT`: Dashboard ID to run the test on. Keeps dashboard open for user, turn on auto-refresh to keep dashboard updated
* `--qid TEXT`: Query ID (from explore url) to run the test on
* `--model TEXT`: Model to run the test on. Specify multiple models as --model model1 --model model2
* `--attribute TEXT`: Looker attributes to run the test on. Specify them as attribute:value like --attribute store:value. Excepts multiple arguments --attribute store:acme --attribute team:managers
* `--help`: Show this message and exit.

## `lkr test-qid`

**Usage**:

```console
$ lkr test-qid [OPTIONS] USER_ID QID
```

**Arguments**:

* `USER_ID`: User ID to run the test on  [required]
* `QID`: Query ID (from explore url) to run the test on  [required]

**Options**:

* `--help`: Show this message and exit.

