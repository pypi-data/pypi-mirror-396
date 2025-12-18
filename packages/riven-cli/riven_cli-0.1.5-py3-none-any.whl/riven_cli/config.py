from pathlib import Path
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    TomlConfigSettingsSource,
    PydanticBaseSettingsSource,
)
from pydantic import Field

APP_NAME = "riven-cli"
CONFIG_DIR = Path.home() / ".config" / APP_NAME
CONFIG_FILE = CONFIG_DIR / "config.toml"


class Settings(BaseSettings):
    api_url: str = Field(
        default="http://localhost:8080", description="Riven Backend URL"
    )
    api_key: str | None = Field(default=None, description="Riven API Key")

    model_config = SettingsConfigDict(
        env_prefix="RIVEN_", toml_file=CONFIG_FILE, extra="ignore"
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            TomlConfigSettingsSource(settings_cls),
        )

    def save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            f.write(f'api_url = "{self.api_url}"\n')
            if self.api_key:
                f.write(f'api_key = "{self.api_key}"\n')
            else:
                f.write('# api_key = "YOUR_KEY"\n')


settings = Settings()
