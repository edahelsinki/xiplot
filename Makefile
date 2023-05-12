.PHONY: xiplot install_xiplot build_xiplot deploy run all clean nuke

all: run

install_xiplot: xiplot/.gitignore

xiplot/.gitignore:
	git submodule init xiplot
	git submodule update --depth=1 --remote xiplot

build_xiplot: xiplot/.gitignore
	cd xiplot && \
	rm -rf dist && \
	pip install build toml && \
	pip install -r requirements.txt && \
	pip install . && \
	python3 -m build

build_plugins: xiplot/.gitignore
	cd xiplot && \
	rm -f plugins/*.whl && \
	cd test_plugin && \
	rm -rf dist && \
	pip install build && \
	python3 -m build && \
	cp dist/xiplot_test_plugin-*.*.*-py3-none-any.whl ../plugins

xiplot: install_xiplot build_xiplot build_plugins

deploy: xiplot
	rm -rf dist
	mkdir dist
	cp -r xiplot/xiplot/assets dist/
	cp xiplot/dist/xiplot-*.*.*-py3-none-any.whl dist/
	cp -r xiplot/data dist/
	ls dist/data > dist/assets/data.ls
	cp -r xiplot/plugins dist/
	rm dist/plugins/.gitignore
	ls dist/plugins > dist/assets/plugins.ls
	python3 patches/bundle-dash-app.py
	npm install
	npm run build

run: deploy
	cd dist && \
	python3 -m http.server

clean:
	rm -rf dist
	mkdir dist
	rm -rf .cache
	rm -rf xiplot/dist
	rm -rf xiplot/xiplot.egg-info

nuke: clean
	rm -rf node_modules
	git submodule deinit -f xiplot
