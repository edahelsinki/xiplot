.PHONY: install_xiplot setup_build build_xiplot setup_plugins build_test_plugin bundle_plugins build_webdash deploy serve run all clean nuke

all: run

install_xiplot: xiplot/.gitignore

xiplot/.gitignore:
	git submodule init xiplot && \
	git submodule update --depth=1 --remote xiplot

setup_build:
	rm -rf dist && \
	mkdir dist

build_xiplot:
	cd xiplot && \
	rm -rf dist && \
	pip install build toml && \
	pip install -r requirements.txt && \
	pip install . && \
	python3 -m build && \
	python3 ../patches/bundle-dash-app.py && \
	cp -r xiplot/assets ../dist/ && \
	cp dist/xiplot-*.*.*-py3-none-any.whl ../dist/ && \
	cp -r data ../dist/ &&  \
	ls ../dist/data > ../dist/assets/data.ls

setup_plugins:
	cd xiplot && \
	mkdir -p plugins && \
	rm -f plugins/*.whl

build_test_plugin:
	cd xiplot/test_plugin && \
	rm -rf dist && \
	pip install build && \
	python3 -m build && \
	cp dist/xiplot_test_plugin-*.*.*-py3-none-any.whl ../plugins

bundle_plugins:
	mkdir dist/plugins
	find xiplot/plugins -name \*.whl -exec cp {} dist/plugins \;
	ls dist/plugins > dist/assets/plugins.ls

build_webdash:
	npm install
	npm run build

serve:
	cd dist && \
	python3 -m http.server

deploy: install_xiplot build_xiplot setup_plugins bundle_plugins build_webdash

run: install_xiplot build_xiplot setup_plugins build_test_plugin bundle_plugins build_webdash serve

clean:
	rm -rf dist
	mkdir dist
	rm -rf .cache
	rm -rf xiplot/dist
	rm -rf xiplot/xiplot.egg-info

nuke: clean
	rm -rf node_modules
	git submodule deinit -f xiplot
