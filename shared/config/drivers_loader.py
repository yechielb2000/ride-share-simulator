from pathlib import Path

from pydantic import BaseModel


class DriverLoaderConfig(BaseModel):
    json_file: Path
