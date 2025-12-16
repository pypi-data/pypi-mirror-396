import inspect
from typing import Any
import random

__all__ = ['deep_get', 'rand_key_chain', 'get_attrs']


def deep_get(data, target_path, default=None):
    """
    중첩된 데이터 구조에서 경로와 일치하는 첫 번째 값을 재귀적으로 찾습니다.

    예를 들어, target_path가 'a/b'이면 데이터 내의 어느 깊이에서든
    {'a': {'b': value}} 구조를 찾아 value를 반환합니다.
    단일 키 'a'는 길이가 1인 경로로 취급됩니다.

    :param data: 검색할 데이터 구조입니다.
    :param target_path: 찾을 키 또는 슬래시('/')로 구분된 경로입니다.
    :param default: 값을 찾지 못했을 때 반환할 기본값입니다.
    """
    path_keys = target_path.split('/')

    def _search(current_data):
        # 1단계: 현재 위치(current_data)에서 경로가 시작되는지 확인
        temp = current_data
        try:
            for key in path_keys:
                temp = temp[key]
            # 예외 없이 모든 경로를 통과했다면 값을 찾은 것이므로 즉시 반환
            return temp
        except (KeyError, TypeError, IndexError):
            # 현재 위치에서는 경로가 시작되지 않음. 계속해서 더 깊이 탐색.
            pass

        # 2단계: 현재 위치에서 경로를 못 찾았다면, 하위 요소들을 재귀적으로 탐색
        if isinstance(current_data, dict):
            for value in current_data.values():
                found = _search(value)
                if found is not None:
                    return found
        elif isinstance(current_data, list):
            for item in current_data:
                found = _search(item)
                if found is not None:
                    return found

        # 모든 탐색을 마쳤지만 현재 경로에서 값을 찾지 못함
        return None

    result = _search(data)

    return result if result is not None else default


def rand_key_chain(d: dict, depth: int = None) -> list[Any]:
    """
    딕셔셔리에서 랜덤한 키 체인(경로)을 반환합니다

    - depth가 정수면, 지정된 깊이까지 탐색합니다.
    - depth가 None이면, 딕셔너리가 아닌 값을 만날 때까지 (최하위) 탐색합니다.

    :param d: 탐색할 딕셔너리.
    :param depth: 탐색할 깊이. None이면 최하위까지.

    :returns: 랜덤하게 선택된 key들의 리스트 (키 체인).

    :raises ValueError: 유효한 경로를 찾지 못했거나, 지정된 깊이에 도달할 수 없는 경우.
    """
    if depth is not None and depth < 1:
        raise ValueError("depth는 1 이상이어야 합니다.")

    chain = []
    current = d

    while True:
        # --- 루프 종료 조건 ---
        # 1. 지정된 깊이에 도달한 경우
        if depth is not None and len(chain) == depth:
            break
        # 2. 더 이상 탐색할 수 없는 경우 (딕셔너리가 아니거나 비어있음)
        if not isinstance(current, dict) or not current:
            break

        # --- 핵심 로직: 키 선택 및 다음 단계로 이동 ---
        key = random.choice(list(current.keys()))
        chain.append(key)
        current = current[key]

    # --- 최종 결과 검증 ---
    # depth가 지정되었는데, 그 깊이에 도달하지 못하고 루프가 끝난 경우
    if depth is not None and len(chain) < depth:
        raise ValueError(f"지정한 깊이({depth})까지 탐색할 수 없습니다. (실패 지점: 깊이 {len(chain) + 1})")

    # 경로가 전혀 만들어지지 않은 경우 (예: 입력 딕셔너리가 비어있음)
    if not chain:
        raise ValueError("유효한 경로를 찾을 수 없습니다 (입력 딕셔너리가 비어있을 수 있습니다).")

    return chain


def get_attrs(obj: Any, instance_vars: bool = True) -> dict[str, Any]:
    """
    클래스 또는 인스턴스에서 '_'로 시작하지 않는 속성을 필터링하여 반환합니다.

    :param obj: 속성을 가져올 클래스 또는 인스턴스 객체.
    :param instance_vars: True일 경우 인스턴스 변수도 포함합니다. obj가 클래스일 경우 이 값은 무시됩니다.

    :returns: 필터링된 속성 딕셔너리.
    """
    # 1. 대상이 클래스인지 인스턴스인지 확인하여 기준 클래스를 정합니다.
    cls = obj if inspect.isclass(obj) else type(obj)

    # 2. 클래스의 public 속성을 가져옵니다.
    class_attributes = {k: v for k, v in vars(cls).items() if not k.startswith('_')}

    # 3. 인스턴스 변수를 포함해야 하는 경우, 인스턴스의 public 속성을 가져와 합칩니다.
    if instance_vars and not inspect.isclass(obj):
        instance_attributes = {k: v for k, v in vars(obj).items() if not k.startswith('_')}
        # 클래스 속성 위에 인스턴스 속성을 덮어씁니다 (Python의 기본 동작과 동일).
        return {**class_attributes, **instance_attributes}

    # 4. 클래스 변수만 반환하는 경우
    return class_attributes
