import micropip

JSBEAUTIFIER_VERSION = "1.14.3"
XIPLOT_WHEEL = "xiplot-0.2.0-py3-none-any.whl"

micropip.add_mock_package("jsbeautifier", JSBEAUTIFIER_VERSION)
micropip.install(["setuptools", XIPLOT_WHEEL])
