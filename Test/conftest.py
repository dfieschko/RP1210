def pytest_addoption(parser):
    parser.addoption(
        "--apiname",
        action="store",
        default=None,
        help="Name of API",
    )


def pytest_generate_tests(metafunc):
    if "apiname" in metafunc.fixturenames:
        metafunc.parametrize("apiname", metafunc.config.getoption("apiname"))