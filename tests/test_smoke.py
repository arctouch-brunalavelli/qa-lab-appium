def test_app_session_starts(driver):
    assert driver.session_id is not None


def test_current_package_matches_app(driver, app_config):
    assert driver.current_package == app_config.android_app_package
