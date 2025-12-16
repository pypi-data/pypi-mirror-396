from pathlib import Path
import os

__all__ = ['get_project_root', 'which']


def get_project_root(start_path: str, root_markers: str | list[str] = None) -> Path | None:
    """
    주어진 경로에서부터 상위로 올라가며 프로젝트 루트를 찾습니다.

    - `root_markers`가 지정되지 않으면 기본값 ['.idea', '.git'] 중 하나를 찾습니다.
    - `root_markers`가 문자열이나 리스트로 지정되면 해당 마커만 찾습니다.

    :param start_path: 탐색을 시작할 파일의 경로 (__file__을 전달하세요).
    :param root_markers: 루트를 식별할 파일/폴더 이름 (문자열 또는 리스트).
    :return: 프로젝트 루트의 Path 객체. 찾지 못하면 None.
    """
    if root_markers is None:
        # 매개변수가 없으면 기본 마커 목록을 사용합니다.
        markers_to_check = ['.idea', '.git']
    elif isinstance(root_markers, str):
        # 매개변수가 문자열이면, 검색을 위해 리스트로 만듭니다.
        markers_to_check = [root_markers]
    else:
        # 매개변수가 리스트이면 그대로 사용합니다.
        markers_to_check = root_markers

    current_path = Path(start_path).resolve()
    for parent in current_path.parents:
        # any()와 제너레이터 표현식을 사용하여 마커 목록 중 하나라도 존재하는지 효율적으로 확인합니다.
        if any((parent / marker).exists() for marker in markers_to_check):
            return parent

    return None


def which(name: str, path: str):
    result = []
    for root, dirs, files in os.walk(os.path.join(get_project_root(__file__), path)):
        if name in files + dirs:
            result.append(os.path.join(root, name))
    return result
