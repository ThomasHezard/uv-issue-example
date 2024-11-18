# Example

This project is an illustration of the `uv` issue described [here](https://github.com/astral-sh/uv/issues/9211).

## Steps to reproduce the issue

1. Sync the env and build the wheel:
    ```bash
    uv sync
    uv build
    ```

2. Run the tests with the `--no-project` command for Python 3.8 to 3.12, it should work fine:
    ```bash
    uv run --link-mode=copy --python "3.8" --no-project --with "tomli~=2.0" --with dist/*.whl python tests/tests.py
    uv run --link-mode=copy --python "3.9" --no-project --with "tomli~=2.0" --with dist/*.whl python tests/tests.py
    uv run --link-mode=copy --python "3.10" --no-project --with "tomli~=2.0" --with dist/*.whl python tests/tests.py
    uv run --link-mode=copy --python "3.11" --no-project --with "tomli~=2.0" --with dist/*.whl python tests/tests.py
    uv run --link-mode=copy --python "3.12" --no-project --with "tomli~=2.0" --with dist/*.whl python tests/tests.py
    ```

3. Run the tests with the `--only-dev` command for Python 3.8 to 3.12, it should work for all except 3.12:
    ```bash
    uv run --link-mode=copy --python "3.8" --only-dev --with dist/*.whl python tests/tests.py
    uv run --link-mode=copy --python "3.9" --only-dev --with dist/*.whl python tests/tests.py
    uv run --link-mode=copy --python "3.10" --only-dev --with dist/*.whl python tests/tests.py
    uv run --link-mode=copy --python "3.11" --only-dev --with dist/*.whl python tests/tests.py
    uv run --link-mode=copy --python "3.12" --only-dev --with dist/*.whl python tests/tests.py
    ```


## What I understand

- `uv run --link-mode=copy --python "3.12" --no-project --with "tomli~=2.0" [...]` chooses the numpy version according the wheel dependencies. With Python 3.12, this leads to numpy 2.1.3:
  ```bash
  >>> uv run --link-mode=copy --python "3.12" --no-project --with "tomli~=2.0" --with dist/*.whl python -c "import numpy; print(numpy.__version__)"
  Installed 93 packages in 2.82s
  2.1.3
  ```
- `uv run --link-mode=copy --python "3.12" --only-dev [...]` chooses the numpy version according from lock file, even though numpy is NOT a dev dependency. With Python 3.12, this lead to 1.24.4, which fails to install under Python 3.12
  ```bash
  ❯❯❯ uv run --no-project --python 3.12 --with "numpy==1.24.4"                                                                             
    × Failed to download and build `numpy==1.24.4`
    ├─▶ Build backend failed to determine requirements with `build_wheel()` (exit status: 1)
  
    │   [stderr]
    │   Traceback (most recent call last):
    │     File "<string>", line 8, in <module>
    │     File "/Users/thomashezard/.cache/uv/builds-v0/.tmp5hnK0H/lib/python3.12/site-packages/setuptools/__init__.py", line 10, in <module>
    │       import distutils.core
    │   ModuleNotFoundError: No module named 'distutils'
  
    ╰─▶ distutils was removed from the standard library in Python 3.12. Consider adding a constraint (like `numpy >1.24.4`) to avoid building a version of numpy that depends on distutils.
  ```
- This can be verified with the following command:
  ```bash
  ❯❯❯ uv run --no-project --python 3.12 --with "numpy==1.24.4"                                                                             
    × Failed to download and build `numpy==1.24.4`
    ├─▶ Build backend failed to determine requirements with `build_wheel()` (exit status: 1)
  
    │   [stderr]
    │   Traceback (most recent call last):
    │     File "<string>", line 8, in <module>
    │     File "/Users/thomashezard/.cache/uv/builds-v0/.tmp5hnK0H/lib/python3.12/site-packages/setuptools/__init__.py", line 10, in <module>
    │       import distutils.core
    │   ModuleNotFoundError: No module named 'distutils'
  
    ╰─▶ distutils was removed from the standard library in Python 3.12. Consider adding a constraint (like `numpy >1.24.4`) to avoid building a version of numpy that depends on distutils.
  ```

## My question

Why does `uv run --only-dev [...]` look up the version in the `uv.lock` file for packages that are not in the dev group?