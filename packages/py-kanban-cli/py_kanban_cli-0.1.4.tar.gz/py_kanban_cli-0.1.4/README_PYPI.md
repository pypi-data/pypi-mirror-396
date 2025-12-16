# Kanban cli management

This is a command-line tool to manage simple kanban boards.

## Installation

The recommended way is to use [`pipx`](https://pypi.org/project/pipx), which installs the software in a separate Python environment automatically without you needing to worry about Python at all:

```sh
pipx install py-kanban-cli
```

You also don't need sudo privileges here.

Alternatively, if you have a specific Python environment that is active, a simple `pip install` should work as well:

```sh
pip install py-kanban-cli
```

## Usage

Notice that, despite the awkward package name `py-kanban-cli`, the cli command is simply `kanban-cli`.

For general help on the full commands, type

```sh
kanban-cli --help
```

and it will show all available options and commands.

The most commont involve management of tasks and categories, which you can get more details with the folowing:

```sh
kanban-cli tasks --help
kanban-cli categories --help
```

See the [repository page](https://github.com/fillipe-gsm/kanban-cli) for more complete examples and configuration.
