import platform

from pcp_serversdk_python.utils import ServerMetaInfo  # Update import as needed


def testServerMetaInfoInitialization():
    integrator = "TestIntegrator"
    meta_info = ServerMetaInfo(integrator=integrator)

    # Check platformIdentifier
    expected_platform_identifier = (
        f"{platform.system()}, Python version is: {platform.python_version()}"
    )
    assert meta_info.platformIdentifier == expected_platform_identifier

    # Check sdkIdentifier
    assert meta_info.sdkIdentifier == "PythonServerSDK/v1.5.0"

    # Check sdkCreator
    assert meta_info.sdkCreator == "PAYONE GmbH"

    # Check integrator
    assert meta_info.integrator == integrator


def testServerMetaInfoDefaults():
    meta_info = ServerMetaInfo()

    # Check platformIdentifier
    expected_platform_identifier = (
        f"{platform.system()}, Python version is: {platform.python_version()}"
    )
    assert meta_info.platformIdentifier == expected_platform_identifier

    # Check sdkIdentifier
    assert meta_info.sdkIdentifier == "PythonServerSDK/v1.5.0"

    # Check sdkCreator
    assert meta_info.sdkCreator == "PAYONE GmbH"

    # Check default integrator
    assert meta_info.integrator == ""
