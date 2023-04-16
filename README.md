# Lambda GPU CLI (`lambda`)

Decided to make a CLI for the Lambda GPU. WIP, but works for me, hope it works for you!
Made mainly with [Typer](https://github.com/tiangolo/typer) and [Bullet](https://github.com/bchao1/bullet).

## Installation

```
poetry build
pip install --user ./dist/lambda_cli-0.1.0-py3-none-any.whl
```

**Usage**:

```console
$ lambda [OPTIONS] COMMAND [ARGS]...
```

**Options**:

-   `--install-completion`: Install completion for the current shell.
-   `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
-   `--help`: Show this message and exit.

**Commands**:

-   `ls`: List running instances.
-   `new`: Provision a new GPU instance.
-   `stop`: Terminate a running instance.

## `lambda ls`

List running instances.

**Usage**:

```console
$ lambda ls [OPTIONS]
```

**Options**:

-   `--help`: Show this message and exit.

## `lambda new`

Provision a new GPU instance.

**Usage**:

```console
$ lambda new [OPTIONS]
```

**Options**:

-   `--ssh / --no-ssh`: Append an entry to ssh config at ~/.ssh/config [default: no-ssh]
-   `--help`: Show this message and exit.

## `lambda stop`

Terminate a running instance.

**Usage**:

```console
$ lambda stop [OPTIONS]
```

**Options**:

-   `--help`: Show this message and exit.
