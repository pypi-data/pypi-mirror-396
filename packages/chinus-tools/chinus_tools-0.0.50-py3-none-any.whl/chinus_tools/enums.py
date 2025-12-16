from __future__ import annotations

from typing import Any, Iterable, Mapping, get_args, get_origin, Literal
import copy

__all__ = ["Enum"]


class _ImmutableWrapper:
    """Enum 속성의 내부 변경을 막기 위한 유틸 베이스 클래스."""

    __slots__ = ("_attr_name",)

    def __init__(self, attr_name: str) -> None:
        self._attr_name = attr_name

    @property
    def attr_name(self) -> str:
        """해당 래퍼가 보호하는 Enum 속성 이름입니다."""
        return self._attr_name

    def raise_error(self) -> None:
        """불변 컨테이너의 쓰기 연산 시 예외를 발생시킵니다."""
        raise AttributeError(f"Enum의 속성 '{self._attr_name}'의 내부는 수정할 수 없습니다.")


class ImmutableDict(dict):
    """내부 값 수정을 막고 커스텀 에러를 발생시키는 딕셔너리입니다."""

    __slots__ = ("_wrapper",)

    def __init__(self, attr_name: str, initial_data: Mapping | None = None) -> None:
        super().__init__({} if initial_data is None else initial_data)
        self._wrapper = _ImmutableWrapper(attr_name)

    # --- 불변화: 쓰기 관련 메서드 모두 막기 ---

    def __setitem__(self, key: Any, value: Any) -> None:
        self._wrapper.raise_error()

    def __delitem__(self, key: Any) -> None:
        self._wrapper.raise_error()

    def clear(self) -> None:
        self._wrapper.raise_error()

    def pop(self, *args: Any, **kwargs: Any) -> Any:
        self._wrapper.raise_error()

    def popitem(self) -> Any:
        self._wrapper.raise_error()

    def setdefault(self, *args: Any, **kwargs: Any) -> Any:
        self._wrapper.raise_error()

    def update(self, *args: Any, **kwargs: Any) -> None:
        self._wrapper.raise_error()

    # --- deepcopy 시에는 일반 dict로 풀어주기 ---

    def __deepcopy__(self, memo: dict[int, Any]) -> dict:
        """deepcopy 시, 불변 래퍼를 벗기고 일반 dict로 복사합니다."""
        obj_id = id(self)
        if obj_id in memo:
            return memo[obj_id]

        new_dict: dict[Any, Any] = {}
        memo[obj_id] = new_dict

        for k, v in self.items():
            new_dict[copy.deepcopy(k, memo)] = copy.deepcopy(v, memo)

        return new_dict


class ImmutableList(list):
    """내부 값 수정을 막고 커스텀 에러를 발생시키는 리스트입니다."""

    __slots__ = ("_wrapper",)

    def __init__(self, attr_name: str, initial_data: Iterable | None = None) -> None:
        super().__init__([] if initial_data is None else initial_data)
        self._wrapper = _ImmutableWrapper(attr_name)

    # --- 불변화: 쓰기 관련 메서드 모두 막기 ---

    def __setitem__(self, index, value) -> None:
        self._wrapper.raise_error()

    def __delitem__(self, index) -> None:
        self._wrapper.raise_error()

    def append(self, *args: Any, **kwargs: Any) -> None:
        self._wrapper.raise_error()

    def clear(self) -> None:
        self._wrapper.raise_error()

    def extend(self, *args: Any, **kwargs: Any) -> None:
        self._wrapper.raise_error()

    def insert(self, *args: Any, **kwargs: Any) -> None:
        self._wrapper.raise_error()

    def pop(self, *args: Any, **kwargs: Any) -> Any:
        self._wrapper.raise_error()

    def remove(self, *args: Any, **kwargs: Any) -> None:
        self._wrapper.raise_error()

    def reverse(self) -> None:
        self._wrapper.raise_error()

    def sort(self, *args: Any, **kwargs: Any) -> None:
        self._wrapper.raise_error()

    # --- deepcopy 시에는 일반 list로 풀어주기 ---

    def __deepcopy__(self, memo: dict[int, Any]) -> list:
        """deepcopy 시, 불변 래퍼를 벗기고 일반 list로 복사합니다."""
        obj_id = id(self)
        if obj_id in memo:
            return memo[obj_id]

        new_list: list[Any] = []
        memo[obj_id] = new_list

        append = new_list.append
        for item in self:
            append(copy.deepcopy(item, memo))

        return new_list


# --- 컨테이너 불변 변환 함수 ---

def _make_immutable_custom(obj: Any, attr_name: str) -> Any:
    """dict / list (및 기타 컨테이너)를 불변 래퍼로 감쌉니다."""

    # 이미 우리의 래퍼라면 다시 감싸지 않습니다.
    if isinstance(obj, (ImmutableDict, ImmutableList)):
        return obj

    if isinstance(obj, dict):
        processed = {k: _make_immutable_custom(v, attr_name) for k, v in obj.items()}
        return ImmutableDict(attr_name, processed)

    if isinstance(obj, list):
        processed = [_make_immutable_custom(v, attr_name) for v in obj]
        return ImmutableList(attr_name, processed)

    # 필요 시 tuple / set 등도 내부만 재귀적으로 처리해서 재구성
    if isinstance(obj, tuple):
        return tuple(_make_immutable_custom(v, attr_name) for v in obj)

    if isinstance(obj, set):
        return frozenset(_make_immutable_custom(v, attr_name) for v in obj)

    return obj


# --- 메타클래스 ---

class NoReassign(type):
    """Enum 전용 메타클래스: 재할당 방지 및 컨테이너 불변 래핑을 담당합니다."""

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        attrs: dict[str, Any],
    ) -> type:
        immutable_attrs: dict[str, Any] = {}

        for k, v in attrs.items():
            if k.startswith("__") and k.endswith("__"):
                # 매직 메서드는 있는 그대로 둡니다.
                immutable_attrs[k] = v
            else:
                immutable_attrs[k] = _make_immutable_custom(v, k)

        return super().__new__(mcs, name, bases, immutable_attrs)

    def __setattr__(cls, k: str, v: Any) -> None:
        """클래스 속성 재할당을 막습니다."""
        raise AttributeError(f"Enum의 속성 '{k}'는 재할당할 수 없습니다.")

    def __getattribute__(cls, item: str) -> Any:
        """Literal 속성은 값 리스트로 반환하고, 나머지는 그대로 반환합니다."""
        attr = object.__getattribute__(cls, item)
        if get_origin(attr) is Literal:
            return list(get_args(attr))
        return attr


class Enum(metaclass=NoReassign):
    """열거형 베이스 클래스입니다.

    - 클래스 속성 재할당 방지
    - dict / list / tuple / set 속성은 불변 컨테이너로 래핑
    - Literal 타입 속성은 `list`로 풀어서 반환
    """
    pass