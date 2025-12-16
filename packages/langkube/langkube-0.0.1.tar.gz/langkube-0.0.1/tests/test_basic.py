from langkube import version
def test_version():
    assert version() == "0.0.1"
