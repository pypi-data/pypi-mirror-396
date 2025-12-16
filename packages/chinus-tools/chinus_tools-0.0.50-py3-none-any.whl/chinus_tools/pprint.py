import json
from typing import Any, Callable

__all__ = ["pprint"]


def pprint(
    data: Any,
    *,
    indent: int = 2,
    default: Callable[[Any], Any] = lambda o: o.__dict__,
    pretty: bool = True,
    max_items: int = 0,
) -> None:
    """
    JSON 직렬화 가능한 파이썬 객체를 예쁘게 출력합니다.
    """
    if not pretty:
        # pretty 출력이 아닌 경우는 json.dumps에 모두 위임
        print(
            json.dumps(
                data,
                indent=indent,
                default=default,
                ensure_ascii=False,
            )
        )
        return None

    output_buffer: list[str] = []
    append = output_buffer.append  # micro-optimization

    # 적당히 큰 캐시를 만들고, 필요 시 동적으로 확장합니다.
    indent_cache: list[str] = ["", *((" " * (i * indent)) for i in range(1, 32))]

    def _ensure_indent(level: int) -> None:
        """요청된 level까지 indent_cache를 확장합니다."""
        nonlocal indent_cache
        if level < len(indent_cache):
            return
        start = len(indent_cache)
        indent_cache.extend(" " * (i * indent) for i in range(start, level + 1))

    def _compute_limit(length: int) -> int:
        """길이와 max_items에 따라 실제 출력할 항목 수를 계산합니다."""
        if max_items <= 0:
            return length
        return min(length, max_items)

    def _format_sequence(seq: Any, level: int) -> None:
        """list/tuple 공통 포매팅."""
        _ensure_indent(level + 1)
        current_indent = indent_cache[level]
        next_indent = indent_cache[level + 1]

        length = len(seq)
        if length == 0:
            append("[]")
            return

        # 단일 원소는 max_items와 관계없이 한 줄로 처리
        if length == 1:
            append("[")
            _formatter(seq[0], level)
            append("]")
            return

        append("[\n")

        limit = _compute_limit(length)
        for i in range(limit):
            if i:
                append(",\n")
            append(next_indent)
            _formatter(seq[i], level + 1)

        # 잘린 경우 뒷부분 생략 표시
        if 0 < max_items < length:
            append(",\n")
            append(next_indent)
            append("...")

        append("\n")
        append(current_indent)
        append("]")

    def _format_mapping(mapping: dict[Any, Any], level: int) -> None:
        """dict 포매팅."""
        _ensure_indent(level + 1)
        current_indent = indent_cache[level]
        next_indent = indent_cache[level + 1]

        length = len(mapping)
        if length == 0:
            append("{}")
            return

        # 단일 원소는 max_items와 관계없이 한 줄로 처리
        if length == 1:
            (key, value), = mapping.items()
            append("{")
            append(json.dumps(key, ensure_ascii=False))
            append(": ")
            _formatter(value, level)
            append("}")
            return

        append("{\n")

        items_iter = iter(mapping.items())
        limit = _compute_limit(length)

        for i in range(limit):
            if i:
                append(",\n")
            key, value = next(items_iter)
            append(next_indent)
            append(json.dumps(key, ensure_ascii=False))
            append(": ")
            _formatter(value, level + 1)

        # 잘린 경우 뒷부분 생략 표시
        if 0 < max_items < length:
            append(",\n")
            append(next_indent)
            append('"..."')
            append(": ")
            append('"..."')

        append("\n")
        append(current_indent)
        append("}")

    def _formatter(obj: Any, level: int) -> None:
        # --- 1. 기본 타입 우선 처리 ---
        if isinstance(obj, str):
            append(json.dumps(obj, ensure_ascii=False))
            return
        if obj is True:
            append("true")
            return
        if obj is False:
            append("false")
            return
        if obj is None:
            append("null")
            return
        if isinstance(obj, (int, float)):
            append(str(obj))
            return

        # --- 2. 컬렉션 타입 확인 및 처리 ---
        if isinstance(obj, (list, tuple)):
            _format_sequence(obj, level)
            return

        if isinstance(obj, dict):
            _format_mapping(obj, level)
            return

        # --- 3. 위 모든 타입에 해당하지 않는 경우 (사용자 정의 객체 등) ---
        if default:
            _formatter(default(obj), level)
        else:
            raise TypeError(
                f"Object of type {type(obj).__name__} is not JSON serializable"
            )

    _formatter(data, 0)
    print("".join(output_buffer))
    return None
