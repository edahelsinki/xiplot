.PHONY: pyodide install_pyodide patch_pyodide build_pyodide dashapp install_dashapp build_dashapp deploy all clean nuke

install_pyodide: pyodide/.gitignore

pyodide/.gitignore:
	git submodule init pyodide
	git submodule update pyodide

patch_pyodide: pyodide/packages/dash/meta.yaml

pyodide/packages/dash/meta.yaml: install_pyodide
	cd pyodide; \
	git apply ../patches/pyodide.patch

build_pyodide: pyodide/dist/repodata.json

pyodide/dist/repodata.json: install_pyodide
	cd pyodide; \
	./run_docker --non-interactive PYODIDE_PACKAGES="brotli,flask,plotly,dash,pandas,jinja2,markupsafe,werkzeug,click,itsdangerous,flask_compress,sklearn,scikit-learn,matplotlib" make

pyodide: install_pyodide patch_pyodide build_pyodide

install_dashapp: dashapp/.gitignore

dashapp/.gitignore:
	git submodule init dashapp
	git submodule update dashapp

build_dashapp: dashapp/dist/dashapp-0.1.0-py3-none-any.whl

dashapp/dist/dashapp-0.1.0-py3-none-any.whl: install_dashapp
	pip install build; \
	cd dashapp; \
	python3 -m build

dashapp: install_dashapp build_dashapp

dist/repodata.json: pyodide
	mkdir -p dist
	cp -rf pyodide/dist/* dist/

dist/dashapp-0.1.0-py3-none-any.whl: dashapp
	mkdir -p dist
	cp -f dashapp/dist/dashapp-0.1.0-py3-none-any.whl dist/

dist/data: install_dashapp
	cp -rf dashapp/data dist/

deploy: dist/repodata.json dist/dashapp-0.1.0-py3-none-any.whl dist/data

all: deploy

clean:
	rm -rf dist
	mkdir dist
	rm -rf .cache

nuke: clean
	rm -rf node_modules
	git submodule deinit dashapp
	git submodule deinit pyodide
