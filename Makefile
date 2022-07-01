DASH_VERSION=2.1.0
WEDBASH_VERSION=0.0.3

install_pyodide:
	git clone https://github.com/pyodide/pyodide.git; \
	cd pyodide;

pyodide: install_pyodide
	cd pyodide; \
	git apply ../patches/webdash.patch;

install_dash:
	git clone https://github.com/plotly/dash.git; \
	cd dash; \
	git checkout tags/v$(DASH_VERSION) -b $(DASH_VERSION)

copy_build:
	mkdir -p dist; \
	cd dist; \
	cp -r ../pyodide/build/*.* .;

delete_dist:
	rm -rf dist;

webdash_patch:
	cd pyodide; \
	git diff --cached > ../patches/webdash.patch

make_dist:
	mkdir dist;

clean: delete_dist make_dist
	rm -rf .cache

webdash_build:
	npm run build;

fetch_prebuilt: 
	cd dist; \
	git clone https://github.com/ibdafna/webdash_dist; \
	cd webdash_dist; \
	git checkout webdash_$(WEDBASH_VERSION); \
	cd ..;\
	mv ./webdash_dist/*.* .; \
	rm -rf webdash_dist;

setup: webdash_build fetch_prebuilt