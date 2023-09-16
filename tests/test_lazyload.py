import multiprocessing
import sys


def check_loaded(queue, modules):
    import xiplot  # noqa: F401
    import xiplot.setup  # noqa: F401

    queue.put([mod in sys.modules for mod in modules])


def test_ensure_lazyload():
    # This tests that the following packages are not imported when xiplot is
    # imported, so that they can be lazily loaded in the WASM version.
    # This test starts a new Python (multi-)process using "spawn" to check the
    # imports in a clean environment.
    modules = ["sklearn", "jsonschema", "plotly.figure_factory"]
    ctx = multiprocessing.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=check_loaded, args=(q, modules))
    p.start()
    for mod, loaded in zip(modules, q.get()):
        assert not loaded, f"{mod} should be lazily loaded"
    p.join()
