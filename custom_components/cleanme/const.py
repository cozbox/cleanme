DOMAIN = "cleanme"

PLATFORMS = ["sensor", "binary_sensor"]

CONF_NAME = "name"
CONF_CAMERA_ENTITY = "camera_entity"
CONF_PROVIDER = "provider"
CONF_MODEL = "model"
CONF_API_KEY = "api_key"
CONF_BASE_URL = "base_url"
CONF_MODE = "mode"
CONF_RUNS_PER_DAY = "runs_per_day"

MODE_MANUAL = "manual"
MODE_AUTO = "auto"

PROVIDER_OPENAI = "openai"
PROVIDER_ANTHROPIC = "anthropic"
PROVIDER_OPENROUTER = "openrouter"
PROVIDER_GEMINI = "gemini"
PROVIDER_CUSTOM = "custom"

PROVIDER_OPTIONS = {
    PROVIDER_OPENAI: "OpenAI (GPT / Vision)",
    PROVIDER_ANTHROPIC: "Anthropic (Claude Vision)",
    PROVIDER_OPENROUTER: "OpenRouter",
    PROVIDER_GEMINI: "Google Gemini",
    PROVIDER_CUSTOM: "Custom / Local HTTP endpoint",
}

DEFAULT_MODEL_OPENAI = "gpt-4.1-mini"
DEFAULT_MODEL_ANTHROPIC = "claude-3-5-sonnet-latest"
DEFAULT_MODEL_OPENROUTER = "openrouter/auto"
DEFAULT_MODEL_GEMINI = "gemini-1.5-flash-latest"

RUNS_PER_DAY_OPTIONS = [1, 2, 3, 4]

ATTR_TASKS = "tasks"
ATTR_FULL_TASKS = "full_tasks"
ATTR_COMMENT = "comment"
ATTR_LAST_ERROR = "last_error"

SERVICE_REQUEST_CHECK = "request_check"
SERVICE_SNOOZE_ZONE = "snooze_zone"
SERVICE_CLEAR_TASKS = "clear_tasks"

ATTR_ZONE = "zone"
ATTR_DURATION_MINUTES = "duration_minutes"
