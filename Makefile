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

xiplot: install_xiplot build_xiplot

deploy: xiplot
	rm -rf dist
	mkdir dist
	cp -r xiplot/data dist/
	cp -r xiplot/xiplot/assets dist/
	cp xiplot/dist/xiplot-*.*.*-py3-none-any.whl dist/
	ls dist/data > dist/assets/data.ls
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
