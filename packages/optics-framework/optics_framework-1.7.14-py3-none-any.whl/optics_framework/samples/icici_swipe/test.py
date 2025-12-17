from optics_framework.optics import Optics
import os
def test_icici_swipe():
    """Test case for ICICI app swipe functionality."""
    # Sample configuration for ICICI swipe test
    optics = Optics()
    os.environ["DEVICE_SERIAL_ID"] = "76e75538"

    config = {
        "driver_sources": [
            {
                "appium": {
                    "enabled": True,
                    "url": "http://127.0.0.1:4723",
                    "capabilities": {
                        "platformName": "Android",
                        "appium:automationName": "UiAutomator2",
                        "appium:deviceName": "emulator-5554",
                        "appium:platformName": "Android",
                    }
                }
            }
        ],
        "elements_sources": [
            {"appium_find_element": {"enabled": True}},
            {"appium_page_source": {"enabled": True}},
            {"appium_screenshot": {"enabled": True}},
        ],
        "execution_output_path": "/Users/dhruvmenon/Documents/optics-framework-1/optics_framework/samples/icici_swipe",
        # Optional extra keys:
        # "project_path": "/path/to/project",
        # "execution_output_path": "/tmp/optics-output",
    }

        # Configure Optics (instance method)
    optics.setup(config=config)
    # OR
    # optics = Optics.setup(config_path="path/to/your/config.yaml")
        # Launch the ICICI app with specific capabilities
    optics.launch_app(
    )
    try:
        optics.read_data( "test","ENV:DEVICE_SERIAL_ID",)

    except:
        print("An error occurred during the test.")
    finally:
        optics.quit()
        # GetI see that the code needs to use the setup function from Optics. Looking at the current code, it's directly initializing Optics with a configuration dictionary, but it should use the setup function instead.
test_icici_swipe()
