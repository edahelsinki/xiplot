.PHONY: pyodide install_pyodide build_pyodide dashapp install_dashapp build_dashapp deploy run all clean nuke

all: run

install_pyodide: pyodide/.gitignore

pyodide/.gitignore:
	git submodule init pyodide
	git submodule update pyodide

build_pyodide: pyodide/dist/repodata.json

pyodide/dist/repodata.json: pyodide/.gitignore
ifeq (,$(wildcard pyodide/packages/dash/meta.yaml))
	cd pyodide; \
	git apply --whitespace=nowarn ../patches/pyodide.patch
endif
	cd pyodide; \
	./run_docker --non-interactive PYODIDE_PACKAGES="brotli,flask,flask-caching,cachelib,plotly,dash,dash-daq,dash-extensions,more-itertools,pandas,jinja2,markupsafe,werkzeug,click,itsdangerous,flask_compress,sklearn,scikit-learn,matplotlib" make; \
	git apply --whitespace=nowarn --reverse ../patches/pyodide.patch

pyodide: install_pyodide build_pyodide

install_dashapp: dashapp/.gitignore

dashapp/.gitignore:
	git submodule init dashapp
	git submodule update dashapp

build_dashapp: dashapp/dist/dashapp-0.1.0-py3-none-any.whl

dashapp/dist/dashapp-0.1.0-py3-none-any.whl: dashapp/.gitignore
	pip install build; \
	cd dashapp; \
	python3 -m build

dashapp: install_dashapp build_dashapp

deploy: pyodide dashapp
	rm -rf dist
	mkdir dist
	cp -r pyodide/dist/* dist/
	cp dashapp/dist/dashapp-0.1.0-py3-none-any.whl dist/
	cp -r dashapp/data dist/
	cp -r dashapp/dashapp/assets/favicon.ico dist/
	cp -r dashapp/dashapp/assets/ dist/
	cd dashapp; \
	cp ../bundle.py .; \
	pip install -r requirements.txt; \
	python3 bundle.py; \
	rm -f bundle.py
	npm install
	npm run build

run: deploy
	cd dist; \
	python3 -m http.server

clean:
	rm -rf dist
	mkdir dist
	rm -rf .cache
ifneq (,$(wildcard dashapp/bundle.py))
	rm dashapp/bundle.py
endif
ifneq (,$(wildcard pyodide/packages/dash/meta.yaml))
	cd pyodide; \
	git apply --whitespace=nowarn --reverse ../patches/pyodide.patch
endif
	rm -rf dashapp/dist
	rm -rf dashapp/dashapp.egg-info

nuke: clean
	rm -rf node_modules
	git submodule deinit -f dashapp
	git submodule deinit -f pyodide
