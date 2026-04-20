from utils.driver_factory import create_driver


def test_app_launch():
    driver = create_driver()

    # Basic validation: app launched
    current_package = driver.current_package
    print("Current package:", current_package)

    assert current_package is not None

    driver.quit()