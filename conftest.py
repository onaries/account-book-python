import os


def pytest_sessionfinish(session, exitstatus):
    print("\n*** test run reporting finishing", exitstatus)
    print("*** test run reporting finished")

    os.remove(os.path.join(os.getcwd(), "test.db"))
