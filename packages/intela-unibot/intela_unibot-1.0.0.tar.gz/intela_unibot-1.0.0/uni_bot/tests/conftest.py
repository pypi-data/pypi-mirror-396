"""
Configurations and fixtures for tests.
"""
from pytest_stub.toolbox import stub_global

stub_global({
    'openedx.core.djangoapps.plugins.constants': '[mock]',
})
