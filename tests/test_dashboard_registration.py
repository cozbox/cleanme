"""Test that dashboard auto-registration constants and function signatures are valid."""
from pathlib import Path


INIT_PATH = Path(__file__).resolve().parent.parent / "custom_components" / "cleanme" / "__init__.py"


def test_auto_register_dashboard_function_exists():
    """Test that the auto-register dashboard function is defined in the source."""
    source = INIT_PATH.read_text(encoding="utf-8")
    assert "async def _auto_register_dashboard(" in source, (
        "_auto_register_dashboard function should be defined in __init__.py"
    )


def test_regenerate_dashboard_function_exists():
    """Test that the regenerate dashboard function is defined in the source."""
    source = INIT_PATH.read_text(encoding="utf-8")
    assert "async def _regenerate_dashboard_yaml(" in source, (
        "_regenerate_dashboard_yaml function should be defined in __init__.py"
    )


def test_dashboard_state_helper_exists():
    """Test that the dashboard state helper function is defined in the source."""
    source = INIT_PATH.read_text(encoding="utf-8")
    assert "def _get_dashboard_state(" in source, (
        "_get_dashboard_state function should be defined in __init__.py"
    )


def test_yaml_available_constant():
    """Test that YAML_AVAILABLE constant is defined in the source."""
    source = INIT_PATH.read_text(encoding="utf-8")
    assert "YAML_AVAILABLE" in source, (
        "YAML_AVAILABLE constant should be defined in __init__.py"
    )


def test_no_manual_notification():
    """Test that the manual dashboard notification was removed."""
    source = INIT_PATH.read_text(encoding="utf-8")
    # Verify the persistent_notification import is not present
    assert "from homeassistant.components.persistent_notification import async_create" not in source, (
        "persistent_notification import should be removed - dashboard should auto-register"
    )


def test_lovelace_imports_present():
    """Test that lovelace imports are present for auto-registration."""
    source = INIT_PATH.read_text(encoding="utf-8")
    assert "lovelace_const" in source, (
        "lovelace_const should be imported for dashboard auto-registration"
    )
    assert "lovelace_dashboard" in source, (
        "lovelace_dashboard should be imported for dashboard auto-registration"
    )


def test_frontend_panel_registration():
    """Test that frontend panel registration is present."""
    source = INIT_PATH.read_text(encoding="utf-8")
    assert "async_register_built_in_panel" in source, (
        "async_register_built_in_panel should be called for sidebar registration"
    )


def test_event_component_loaded_imported():
    """Test that EVENT_COMPONENT_LOADED is imported for dashboard registration."""
    source = INIT_PATH.read_text(encoding="utf-8")
    assert "EVENT_COMPONENT_LOADED" in source, (
        "EVENT_COMPONENT_LOADED should be imported for delayed registration"
    )
