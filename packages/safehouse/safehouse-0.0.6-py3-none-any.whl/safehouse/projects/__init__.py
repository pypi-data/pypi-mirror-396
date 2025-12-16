import json
from pathlib import Path
from typing import Optional

from safehouse.services import local
from safehouse.types import JsonBlob
from . import exceptions


MODES = (
    'live',
    'local',
    'standalone',
)


class Project:
    def __init__(
        self,
        *,
        filepath: Path, 
        mode: Optional[str]='local',
        name: str,
        org_name: str,
    ):
        self.filepath = filepath
        self.mode = mode.lower()
        self.name = name.lower()
        self.org_name = org_name.lower()
        self.validate()

    def __str__(self) -> str:
        return f"{self.org_name}.{self.name} ({self.filepath})"

    @property
    def json(self) -> JsonBlob:
        return {
            'organization': self.org_name,
            'mode': self.mode,
            'name': self.name,
        }

    @property
    def is_local(self) -> bool:
        return self.mode == 'local'

    @property
    def json_file(self) -> Path:
        return self.filepath / 'project.json'

    def save(self):
        with open(self.json_file, 'w') as f:
            json.dump(self.json, f, indent=4)

    def validate(self):
        assert self.filepath is not None
        assert self.name is not None
        assert self.org_name is not None
        if self.mode not in MODES:
            raise Exception(f"unsupported mode: '{self.mode}'")
        if self.is_local and not local.is_running():
            raise exceptions.ProjectError(f"{self} needs safehouse services to be running locally")


def from_safehouse_dir(safehouse_dir: Path) -> Project:
    project_json_file = str(safehouse_dir / "project.json")
    with open(project_json_file, 'r', encoding='utf-8') as f:
        project_dict: JsonBlob = json.load(f)
        mode = project_dict.get('mode', 'local')
        name = project_dict.get('name')
        org_name = project_dict.get('organization')
        return Project(filepath=safehouse_dir, name=name, org_name=org_name)
