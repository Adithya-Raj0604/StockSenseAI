import os
from pathlib import Path


class Settings:
    def __init__(self):
        base_dir = Path(__file__).resolve().parent.parent
        self.model_path = Path(
            os.getenv("MODEL_PATH", base_dir / "model" / "reorder_model_tuned.pkl")
        )
        self.data_path = Path(
            os.getenv("DATA_PATH", base_dir / "model" / "restaurant_inventory_with_targets.csv")
        )
        self.cors_origins = self._parse_cors_origins(os.getenv("CORS_ORIGINS", "*"))

    @staticmethod
    def _parse_cors_origins(value: str):
        origins = [origin.strip() for origin in value.split(",") if origin.strip()]
        return origins or ["*"]


settings = Settings()
