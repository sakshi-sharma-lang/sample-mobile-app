def handle_initial_flow(driver):
    try:
        driver.find_element(
            "id",
            "com.android.permissioncontroller:id/permission_allow_button"
        ).click()
    except:
        pass

    try:
        driver.find_element(
            "id",
            "com.android.permissioncontroller:id/permission_allow_foreground_only_button"
        ).click()
    except:
        pass

    try:
        driver.find_element(
            "xpath",
            "//android.widget.Button[@text='Skip']"
        ).click()
    except:
        pass