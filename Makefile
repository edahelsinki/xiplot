.PHONY: pyodide install_pyodide patch_pyodide build_pyodide dashapp install_dashapp patch_dashapp build_dashapp deploy run all clean nuke

all: run

install_pyodide: pyodide/.gitignore

pyodide/.gitignore:
	git submodule init pyodide
	git submodule update pyodide

patch_pyodide: pyodide/packages/dash/meta.yaml

pyodide/packages/dash/meta.yaml: pyodide/.gitignore
	cd pyodide; \
	git apply ../patches/pyodide.patch

build_pyodide: pyodide/dist/repodata.json

pyodide/dist/repodata.json: pyodide/.gitignore
	cd pyodide; \
	./run_docker --non-interactive PYODIDE_PACKAGES="brotli,flask,flask-caching,cachelib,plotly,dash,dash-extensions,more-itertools,pandas,jinja2,markupsafe,werkzeug,click,itsdangerous,flask_compress,sklearn,scikit-learn,matplotlib" make

pyodide: install_pyodide patch_pyodide build_pyodide

install_dashapp: dashapp/.gitignore

dashapp/.gitignore:
	git submodule init dashapp
	git submodule update dashapp

patch_dashapp: dashapp/patch.marker

dashapp/patch.marker: dashapp/.gitignore
	cd dashapp; \
	git apply ../patches/dashapp.patch

build_dashapp: dashapp/dist/dashapp-0.1.0-py3-none-any.whl

dashapp/dist/dashapp-0.1.0-py3-none-any.whl: dashapp/.gitignore
	pip install build; \
	cd dashapp; \
	python3 -m build

dashapp: install_dashapp patch_dashapp build_dashapp

deploy: pyodide dashapp
	rm -rf dist
	mkdir dist
	cp -r pyodide/dist/* dist/
	cp dashapp/dist/dashapp-0.1.0-py3-none-any.whl dist/
	cp -r dashapp/data dist/
	cp -r dashapp/dashapp/assets/* dist/
	cp bundle.py dashapp/
	cd dashapp; \
	pip install -r requirements.txt; \
	python3 bundle.py
	npm run build

run: deploy
	cd dist; \
	python3 -m http.server

clean:
	rm -rf dist
	mkdir dist
	rm -rf .cache
	rm -rf dashapp/dist

nuke: clean
	rm -rf node_modules
	git submodule deinit -f dashapp
	git submodule deinit -f pyodide
