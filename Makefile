.PHONY: pyodide install_pyodide build_pyodide xiplot install_xiplot build_xiplot deploy run all clean nuke xiplot2 deploy2

all: run

install_pyodide: pyodide/.gitignore

pyodide/.gitignore:
	git submodule init pyodide
	git submodule update --depth=1 pyodide

build_pyodide: pyodide/dist/repodata.json

pyodide/dist/repodata.json: pyodide/.gitignore
ifeq (,$(wildcard pyodide/packages/dash/meta.yaml))
	cd pyodide && \
	git apply --whitespace=nowarn ../patches/pyodide.patch
endif
	cd pyodide && \
	./run_docker --non-interactive PYODIDE_PACKAGES="brotli,jsonschema,flask,flask-caching,cachelib,plotly,dash,dash-daq,dash-extensions,dash-mantine-components,more-itertools,pandas,jinja2,markupsafe,werkzeug,click,itsdangerous,flask_compress,sklearn,scikit-learn,matplotlib" make check dist/pyodide.asm.js dist/pyodide.js dist/distutils.tar dist/repodata.json dist/pyodide_py.tar && \
	git apply --whitespace=nowarn --reverse ../patches/pyodide.patch

pyodide: install_pyodide build_pyodide

install_xiplot: xiplot/.gitignore

xiplot/.gitignore:
	git submodule init xiplot
	git submodule update --depth=1 xiplot

build_xiplot: xiplot/.gitignore
	pip install build && \
	cd xiplot && \
	python3 -m build

xiplot: install_xiplot build_xiplot

deploy: pyodide xiplot
	rm -rf dist
	mkdir dist
	cp -r pyodide/dist/* dist/
	rm -rf dist/*-tests.tar
	rm -f dist/tsconfig.tsbuildinfo
	cp xiplot/dist/xiplot-*.*.*-py3-none-any.whl dist/
	cp -r xiplot/data dist/
	cp -r xiplot/xiplot/assets dist/
	ls dist/data > dist/assets/data.ls
	cd xiplot && \
	pip install . && \
	pip install toml && \
	cp ../patches/bundle-dash-app.py . && \
	python3 bundle-dash-app.py && \
	rm -f bundle-dash-app.py
	cp patches/bootstrap.py dist/
	npm install
	npm run build

run: deploy
	cd dist && \
	python3 -m http.server

clean:
	rm -rf dist
	mkdir dist
	rm -rf .cache
ifneq (,$(wildcard xiplot/bundle-dash-app.py))
	rm xiplot/bundle-dash-app.py
endif
ifneq (,$(wildcard pyodide/packages/dash/meta.yaml))
	cd pyodide && \
	git apply --whitespace=nowarn --reverse ../patches/pyodide.patch
endif
	rm -rf xiplot/dist
	rm -rf xiplot/xiplot.egg-info

nuke: clean
	rm -rf node_modules
	git submodule deinit -f xiplot
	git submodule deinit -f pyodide

xiplot2: install_xiplot
	# Apply pull request 29 (remove the dependency on dash-daq, and allow a pandas version that has a pyodide wheel)
	curl https://patch-diff.githubusercontent.com/raw/edahelsinki/xiplot/pull/29.patch -o /tmp/xiplot.patch
	cd xiplot && \
	git apply --whitespace=nowarn /tmp/xiplot.patch && \
	pip install build && \
	python3 -m build && \
	git apply --whitespace=nowarn --reverse /tmp/xiplot.patch

deploy2: xiplot2
	rm -rf dist
	mkdir dist
	cp -r xiplot/data dist/
	cp -r xiplot/xiplot/assets dist/
	cp patches/bootstrap.py dist/
	cp xiplot/dist/xiplot-*.*.*-py3-none-any.whl dist/
	ls dist/data > dist/assets/data.ls
	echo '{"packages": {}}' > dist/repodata.json
	cd xiplot && \
	pip install toml . && \
	cp ../patches/bundle-dash-app.py . && \
	python3 bundle-dash-app.py && \
	rm -f bundle-dash-app.py ../dist/repodata.json
	npm install
	npm run build
