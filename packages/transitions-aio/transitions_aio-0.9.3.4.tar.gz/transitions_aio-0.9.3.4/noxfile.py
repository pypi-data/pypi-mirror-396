import nox


python = ["3.8", "3.9", "3.10", "3.11", "3.12", "3.13"]
nox.options.stop_on_first_error = True


@nox.session(python=python[-1])
def test_mypy(session):
    session.install(".")
    session.install(".[dev]")
    session.install(".[diagrams]")
    session.install(".[mypy]")
    session.run("pytest", "-sxv", "--doctest-modules", "tests/")


@nox.session(python=python[-1])
def test(session):
    session.install(".")
    session.install(".[dev]")
    session.install(".[diagrams]")
    session.run("pytest", "-sxv", "tests/")


@nox.session(python=python)
def test_no_gv(session):
    session.install(".")
    session.install(".[dev]")
    session.run("pytest", "-sxv", "tests/")
