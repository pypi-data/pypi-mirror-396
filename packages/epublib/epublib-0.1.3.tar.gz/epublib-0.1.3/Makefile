venv=[ -d .venv ] && . .venv/bin/activate

test:
	@$(venv); EPUBLIB_TEST_FULL="" pytest -n auto

test_full:
	$(MAKE) docs SPHINXOPTS=-W
	$(venv); basedpyright src;
	$(venv); EPUBLIB_EPUB_SAMPLE=$$(pwd)/src/tests/samples/big.epub EPUBLIB_TEST_FULL=1 pytest -n auto

shell:
	@cat "src/.startup.py"
	@$(venv); PYTHONSTARTUP="src/.startup.py" python

cover:
	@$(venv); pytest --cov=epublib --cov-report html
	@xdg-open htmlcov/index.html

docs_generate:
	$(venv); SPHINX_APIDOC_OPTIONS=members,show-inheritance sphinx-apidoc \
		--module-first --no-toc --separate \
	 	-f src/epublib -o docs/source/
	sed -i "1s/.*/API/" docs/source/epublib.rst
	sed -i "2s/.*/===/" docs/source/epublib.rst

docs: docs_generate
	$(venv); $(MAKE) -C docs/ html

docs_view:
	xdg-open docs/_build/html/index.html

docs_clean:
	$(venv); $(MAKE) -C docs/ clean
	rm -f docs/source/epublib*.rst

sigil_plugin:
	$(venv); $(MAKE) -C sigil/

update_requirements:
	$(venv); uv pip compile pyproject.toml -o requirements.txt
	$(venv); uv pip compile --group dev -o dev.requirements.txt

bump:
	@git add CHANGELOG.md
	@if ! git status --porcelain | grep -P '^(M |A ) CHANGELOG.md'; then \
		echo "Expected CHANGELOG.md as modified"; false; fi
	@latest_tag=$$(git describe --tags $(git rev-list --tags --max-count=1)); \
	  if [ "$$latest_tag" = "v$$(uv version --short)" ]; then \
		echo "Bumping project version (patch)..."; \
		uv version --bump patch; \
		fi
	git add pyproject.toml uv.lock CHANGELOG.md
	git commit -m "Version $$(uv version --short)"
	git tag "v$$(uv version --short)"



publish:
	uv build
	. ./.env; export UV_PUBLISH_TOKEN; uv publish ./dist/*-$$(uv version --short)*

.PHONY: test shell cover docs sigil_plugin docs_view docs_generate publish
