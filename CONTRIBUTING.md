# Contributing

## Development

- The 3rd version of the
  [Python](https://en.wikipedia.org/wiki/Python_(programming_language))
  programming language is used mainly in this project.
- Dependencies managment is handled using [requirements files](requirements)
  with [uv](https://github.com/astral-sh/uv).
  - `requirements.in` contain requirements for running the application and
    `requirements-dev.in` contain requirements for development.
  - `.txt` files are locked requirements with hashes generated using `uv` to
    provide a reproducible environment.
  - For development you will need to use both files, while users just need to
    use the `requirements.txt` file.

> `pre-commit` will take care about generating `.txt` files. You should just
> edit `.in` files or use `uv` to upgrade locked requirements.

### Create a virtual environment and install dependencies

First clone the git repository:

```
git clone https://github.com/zefr0x/cys403_project.git
```

For development you are recommended to use [uv](https://github.com/astral-sh/uv)
for reproducing the same environment.

1. Create a virtual environment and activate it

```shell
uv venv

source .venv/bin/activate
```

2. Run the following command in the project's root directory to install all the
   dependencies for development

```shell
uv pip sync requirements/{requirements,requirements-dev}.txt
```

3. Then you can run the application as a python module

```shell
python3 -m cys403_project
```

> You can use the [`justfile`](justfile) with
> [just](https://github.com/casey/just) for the last two steps if you want to.

### Style

- You should [type hint](https://docs.python.org/3/library/typing.html) every
  thing as possible.
- You should comment every thing to keep the code easy to read. Every file,
  every class, every function, and any line that need a comment.

You should use:

- [mypy](http://www.mypy-lang.org/) `(Static Type Checker)`
- [ruff](https://astral.sh/ruff) `(Style Enforcer & Code Formatter)`

You can also use any tool that you want as long as it's compatible with the
required style.

#### Installing `pre-commit`

To make every thing easy [**`pre-commit`**](https://pre-commit.com/) is used in
this project, it should run in every commit, so you shouldn't commit any thing
without checking it first.

First install it:

```shell
uv pip install pre-commit
```

> You can use another way to install it, maybe from your OS's package manager.

Then add it as a git hook while you are inside the repository:

```shell
pre-commit install
```

### Testing

Unit tests are managed using [`pytest`](https://docs.pytest.org/en/stable/)
under [`tests/`](tests).
