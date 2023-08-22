BUNDLED_PLUGINS := xiplot/plugin_xiplot_filetypes

.PHONY: install_xiplot build_xiplot build_plugins bundle_plugins build_webdash deploy serve run all clean nuke

all: run

install_xiplot: xiplot/.gitignore

xiplot/.gitignore:
	git submodule init xiplot && \
	git submodule update --depth=1 --remote xiplot

build_xiplot:
	cd xiplot && \
	rm -rf dist && \
	pip install build toml && \
	pip install -r requirements.txt && \
	pip install . && \
	python3 -m build && \
	cp dist/xiplot-*.*.*-py3-none-any.whl ../dist/ && \
	python3 ../patches/bundle-dash-app.py && \
	cp -r xiplot/assets ../dist/ && \
	cp -r data ../dist/ &&  \
	ls ../dist/data > ../dist/assets/data.ls

build_plugins:
	pip install build
	for PLUGIN in $(BUNDLED_PLUGINS) ; do \
		cd $$PLUGIN && \
		rm -rf dist && \
		python3 -m build  ; \
	done

bundle_plugins:
	mkdir -p dist/plugins
	for PLUGIN in $(BUNDLED_PLUGINS) ; do \
		find $$PLUGIN/dist -name \*-py3-none-any.whl -exec cp {} dist/plugins \; ; \
	done
	ls dist/plugins > dist/assets/plugins.ls

build_webdash:
	npm install
	npm run build

serve:
	cd dist && \
	python3 -m http.server

deploy: install_xiplot build_xiplot build_plugins bundle_plugins build_webdash

run: deploy serve

clean:
	rm -rf dist
	mkdir dist
	rm -rf .cache
	rm -rf xiplot/dist
	rm -rf xiplot/xiplot.egg-info

nuke: clean
	rm -rf node_modules
	git submodule deinit -f xiplot
