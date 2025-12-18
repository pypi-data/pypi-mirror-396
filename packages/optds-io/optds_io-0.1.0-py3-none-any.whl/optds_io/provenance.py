import subprocess
import json
from hashlib import sha256
from datetime import datetime, timezone
from pydantic import BaseModel, Field

def get_git_revision() -> str:
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    except Exception:
        return "unknown"
    
# def get_git_revision_hash() -> str:
#     try:
#         return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
#     except Exception:
#         return "unknown"

class TransformSpec(BaseModel):
    spec_version: str = "1.0"
    created_at_utc: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    git_commit: str = Field(default_factory=get_git_revision)
    source_vendor: str
    filters: dict
    
    @property
    def spec_hash(self) -> str:
        return sha256(self.model_dump_json().encode("utf-8")).hexdigest()
