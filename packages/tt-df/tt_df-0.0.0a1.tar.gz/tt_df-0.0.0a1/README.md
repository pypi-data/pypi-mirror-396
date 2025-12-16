# test-time-dataframes

Table with features across pandas and pyspark

*DF Lib* | **Native Mocks** | **Pytest Fixture** | File IO Mocking | Call Comparison
--- | --- | --- | --- | --- |
pandas | ✅ | ✅ | ✅ | ✅
pyspark | ⏳ | ⏳ | ⏳ | ⏳

Note that there are good testing utilities inside of each of these data processing libraries, this is just an extension to make various things easier. Please make full use of these in addition to this library:

- [pandas.testing](https://pandas.pydata.org/docs/reference/testing.html)

## Development Setup

Create and activate the Conda environment
```bash
conda create -n tt-df python=3.11
conda activate tt-df
```

Install this package in editable mode
```bash
python -m pip install -e ".[dev,pandas]"
```

Install pre-commit hooks
```bash
pre-commit install
```

```bash
python -m pytest tests
```

## Releasing

Update the version in `pyproject.toml`
```
version='X.Y.Z'
```

Create a git tag and push
```
git tag vX.Y.Z
git push --tags
```

Then create a release via github.

#### If you mess up and need to edit things

Remove old tag and re-tag
```
git tag -d vX.Y.Z
git tag vX.Y.Z

git push -f --tags
```

Delete previous github release and re-create.