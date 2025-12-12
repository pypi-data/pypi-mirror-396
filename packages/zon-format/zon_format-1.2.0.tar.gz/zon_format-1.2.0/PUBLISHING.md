*** Begin Minimal Publishing Guide ***

1) Prepare environment

```zsh
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install build wheel twine
```

2) Clean

```zsh
cd zon-format
rm -rf build/ dist/ ./*.egg-info
```

3) Build

```zsh
python -m build
ls -lh dist/
```

4) Check

```zsh
python -m twine check dist/*
```

5) Upload to TestPyPI

```zsh
python -m twine upload --repository testpypi dist/*
# username: __token__
# password: <TestPyPI token>
```

6) Test install from TestPyPI

```zsh
python -m venv test_env
source test_env/bin/activate
pip install --upgrade pip
pip install --index-url https://test.pypi.org/simple/ zon-format
python -c "import zon; print('import OK')"
deactivate
rm -rf test_env
```

7) Upload to PyPI

```zsh
python -m twine upload dist/*
# username: __token__
# password: <PyPI token>
```

8) Verify production install

```zsh
pip install --upgrade pip
pip install zon-format
python -c "import zon; print('import OK')"
```

Notes
- If `python -m build` fails, ensure `build` is installed in the active venv.
- Prefer installing the wheel directly for local tests: `python -m pip install dist/*.whl`.
- If PyPI rejects an upload with "File already exists", bump the version in `pyproject.toml`, rebuild, and re-upload.