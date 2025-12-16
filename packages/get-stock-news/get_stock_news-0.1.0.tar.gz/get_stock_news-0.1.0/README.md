# GetStockNews PyPI packaging

`newscraper-pypi` holds the metadata needed to build and publish the `get-stock-news` distribution. The actual application source lives in `../NewScraper`, which is why the `pyproject.toml` maps the package directory back to that folder.

## Layout
- `pyproject.toml` declares the project metadata, dependencies, and the `get-stock-news` console script.
- `README.md` is bundled into the sdist/wheel as the long description.
- `LICENSE` mirrors the MIT license used by the code in `NewScraper`.

## Building locally
1. Switch into this directory: `cd newscraper-pypi`.
2. Prepare the build tools (only required once per environment):
   ```bash
   python -m pip install --upgrade build twine
   ```
3. Build the distributables:
   ```bash
   python -m build
   ```
4. (Optional) Verify the CLI by reinstalling the wheel:
   ```bash
   python -m pip install --force-reinstall dist/get_stock_news-*.whl
   get-stock-news --help
   ```
5. Run `python -m twine check dist/*` before publishing.

## Publishing checklist
- Ensure `../NewScraper/README.md` and `NewScraper/RELEASE_GUIDE.md` (or other docs you refer to) align with the `pyproject.toml` version.
- Tag the git repository (if that workflow applies) before uploading.
- Upload with `python -m twine upload dist/*` once sign-off is received. Do not publish until you have explicit confirmation from the release owner.
