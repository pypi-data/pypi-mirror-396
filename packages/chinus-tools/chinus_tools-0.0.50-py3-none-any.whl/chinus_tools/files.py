import json
import yaml
from pathlib import Path
from typing import Any


__all__ = ["json", "yaml"]


class FileManager:
    def __init__(self, __manager):
        self._manager = __manager

    def __getattr__(self, name):
        """정의되지 않은 속성/메서드는 내부 manager에서 위임해서 가져옵니다."""
        attr = getattr(self._manager, name)
        # 함수/메서드든 객체든 그대로 돌려주면 됩니다.
        return attr

    def loads(self, *args, **kwargs):
        return self._manager.loads(*args, **kwargs)

    def dumps(self, *args, **kwargs):
        return self._manager.dumps(*args, **kwargs)

    def load(self, file_path, **kwargs):
        with open(file_path, "r", encoding="utf-8") as f:
            return self._manager.load(f, **kwargs)

    def dump(self, obj, file_path, **kwargs):
        kwargs.setdefault('ensure_ascii', False)
        with open(file_path, "w", encoding="utf-8") as f:
            self._manager.dump(obj, f, **kwargs)

    def safe_load(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return self._manager.safe_load(f)

    def safe_dump(self, obj, file_path, **kwargs):
        kwargs.setdefault('allow_unicode', True)
        with open(file_path, "w", encoding="utf-8") as f:
            self._manager.safe_dump(obj, f, **kwargs)

    def load_tree(self, root_dir: Path) -> dict[str, Any]:
        """
        주어진 루트 디렉터리 이하의 모든 JSON/YAML 파일을 읽어
        디렉터리 구조를 반영한 중첩 딕셔너리로 반환합니다.

        예시
        ----
        a/b/c/d.json ->
        {
            "a": {
                "b": {
                    "c": {
                        "d": <d.json 또는 d.yaml 내용>
                    }
                }
            }
        }

        :param root_dir: JSON/YAML 파일들을 재귀적으로 검색할 루트 디렉터리.
        :returns: 디렉터리/파일 구조를 반영한 중첩 딕셔너리.
        :raises FileNotFoundError: 지정한 경로가 존재하지 않을 때.
        :raises NotADirectoryError: 디렉터리가 아닐 때.
        """
        if not root_dir.exists():
            raise FileNotFoundError(f"지정한 경로가 존재하지 않습니다: {root_dir}")
        if not root_dir.is_dir():
            raise NotADirectoryError(f"디렉터리가 아닙니다: {root_dir}")

        root = root_dir.resolve()
        result: dict[str, Any] = {}

        # 지원하는 확장자와 파서 매핑
        parsers: dict[str, Any] = {
            ".json": json.load,
            ".yaml": lambda f: yaml.safe_load(f),
            ".yml": lambda f: yaml.safe_load(f),
        }

        for path in root.rglob("*"):
            if not path.is_file():
                continue

            suffix = path.suffix.lower()
            data = parsers.get(suffix)
            if data is None:
                continue

            rel_path = path.resolve().relative_to(root)
            *dir_parts, file_name = rel_path.parts
            file_stem = Path(file_name).stem

            current: dict[str, Any] = result
            for part in dir_parts:
                node = current.get(part)
                if not isinstance(node, dict):
                    node = {}
                    current[part] = node
                current = node

            current[file_stem] = data

        return result


json = FileManager(json)
yaml = FileManager(yaml)
