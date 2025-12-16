from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
from typing import Any, Callable, Iterable, Tuple
import operator
import random
import re

from chinus_tools import yaml, deep_get

__all__ = ['YmlRenderer']

# 표준 라이브러리 'operator' 및 람다를 사용하여 연산자 함수를 매핑
_OPERATOR_MAP: dict[str, Callable[[Any, Any], bool]] = {
    '>': operator.gt,
    '<': operator.lt,
    '>=': operator.ge,
    '<=': operator.le,
    '==': operator.eq,
    '!=': operator.ne,
    'in': lambda a, b: a in b,
    'not in': lambda a, b: a not in b,
}
# 연산자 우선순위를 위해 긴 연산자('not in')부터 확인하도록 정렬
_OPERATORS: list[str] = sorted(_OPERATOR_MAP.keys(), key=len, reverse=True)
# 가장 안쪽 괄호를 찾는 정규식. 미리 컴파일하여 성능 향상
_PAREN_PATTERN = re.compile(r'\(([^()]+)\)')

# and/or 분리(공백/대소문자 유연)
_OR_SPLIT = re.compile(r'\s+or\s+', flags=re.IGNORECASE)
_AND_SPLIT = re.compile(r'\s+and\s+', flags=re.IGNORECASE)


@dataclass(frozen=True)
class SourcePos:
    """
    YAML 내 소스 위치 정보를 담는 구조체.

    :param file: 파일 경로(절대 경로)
    :param line: 1-base 라인 번호
    :param column: 1-base 컬럼 번호
    """
    file: Path
    line: int
    column: int


@dataclass(frozen=True)
class RenderCtx:
    """
    렌더링 중 현재 노드의 위치 컨텍스트.

    :param stem: YAML 파일 스템명(확장자 제외 파일명)
    :param path: 현재 노드까지의 경로 튜플 (예: ('root', 'section', 0, 'key'))
    """
    stem: str
    path: Tuple[Any, ...]


class YmlRenderer:
    """
    YAML 파일을 로드하고, 데이터 컨텍스트에 따라 조건부 렌더링을 수행하는 클래스.

    주요 기능:
    - if/then/elif/else 조건문 처리
    - match/case 구문 처리
    - CHOICES/WEIGHT/K를 이용한 가중치 기반 랜덤 선택
    - 'conditions' 키를 이용한 렌더링 여부 제어
    - 오류 발생 시 YAML 파일의 전체 경로와 라인, 컬럼 정보를 예외 메시지에 포함
    """

    # region: Const
    _IF_KEY, _THEN_KEY, _ELIF_KEY, _ELSE_KEY = 'if', 'then', 'elif', 'else'
    _MATCH_KEY, _CASE_KEY = 'match', 'case'
    _DEFAULT_CASE_KEY = '_'
    _CONDITIONS_KEY = 'conditions'
    _TRUE_KEY, _FALSE_KEY = 'TRUE', 'FALSE'
    _CHOICES_KEY, _WEIGHT_KEY, _K_KEY = 'CHOICES', 'WEIGHT', 'K'
    # endregion

    def __init__(self, __yml_root_path: str | Path, __data: dict | None = None):
        """
        클래스 초기화.

        :param __yml_root_path: YAML 루트 디렉터리 경로
        :param __data: 렌더링에 사용할 데이터 딕셔너리
        """
        self.data: dict = {} if __data is None else dict(__data)
        root = Path(__yml_root_path).resolve()

        # 캐시: 파일 스템 → 파싱된(필터 적용된) Python 객체
        self.yml_cache: dict[str, Any] = {}
        # 파일 스템 → YAML 노드 트리(위치 정보 포함)
        self._yaml_node_roots: dict[str, Any] = {}
        # 파일 스템 → 실제 파일 전체 경로
        self._file_paths: dict[str, Path] = {}
        # 파일 스템 → 컨테이너(id(dict/list)) → 해당 노드의 경로 튜플
        self._container_path_index: dict[str, dict[int, Tuple[Any, ...]]] = {}

        self._build_yaml_cache(root)

    # region: YAML 로드/인덱스

    def _load_raw_yaml(self, file_path: Path) -> Any:
        """
        YAML 파일을 안전하게 로드하여 Python 객체를 반환합니다.

        :param file_path: YAML 파일 경로
        :return: 로드된 Python 객체
        :raises ValueError: 파일 로드/파싱 실패
        """
        try:
            return yaml.safe_load(file_path)
        except (FileNotFoundError, yaml.YAMLError) as e:
            raise ValueError(f"YAML 파일을 처리할 수 없습니다: {file_path} (원인: {e})") from e

    def _compose_yaml_node(self, file_path: Path) -> Any:
        """
        YAML 파일을 노드 트리로 파싱합니다(위치 정보 포함).

        :param file_path: YAML 파일 경로
        :return: 루트 YAML 노드
        :raises ValueError: 파싱 실패
        """
        try:
            # compose를 통해 YAML 노드 트리를 획득(각 노드에 start_mark/column 정보 포함)
            with file_path.open('r', encoding='utf-8') as f:
                # SafeLoader가 없을 경우 compose가 기본 로더를 사용
                # chinus_tools.yaml이 PyYAML을 래핑하고 있다고 가정
                return yaml.compose(f, Loader=getattr(yaml, 'SafeLoader', None))
        except Exception as e:
            raise ValueError(f"YAML 노드 파싱에 실패했습니다: {file_path} (원인: {e})") from e

    def _filter_loaded_yaml(self, loaded_data: Any) -> Any:
        """
        로드된 YAML 데이터를 규칙에 따라 필터링합니다.
        - 키가 정수이면 포함
        - 키가 문자열이면 '.'으로 시작하지 않는 경우에만 포함

        :param loaded_data: 로드된 Python 객체
        :return: 필터링된 Python 객체
        """
        if isinstance(loaded_data, dict):
            return {
                k: self._filter_loaded_yaml(v)
                for k, v in loaded_data.items()
                if isinstance(k, int) or (isinstance(k, str) and not k.startswith('.'))
            }
        elif isinstance(loaded_data, list):
            return [self._filter_loaded_yaml(v) for v in loaded_data]
        else:
            return loaded_data

    def _index_container_paths(self, stem: str, obj: Any, base_path: Tuple[Any, ...] = ()) -> None:
        """
        컨테이너(dict/list)의 id → 경로 튜플 인덱스를 생성합니다.

        :param stem: 파일 스템
        :param obj: 현재 객체
        :param base_path: 현재까지의 경로
        """
        if stem not in self._container_path_index:
            self._container_path_index[stem] = {}

        if isinstance(obj, dict):
            self._container_path_index[stem][id(obj)] = base_path
            for k, v in obj.items():
                self._index_container_paths(stem, v, base_path + (k,))
        elif isinstance(obj, list):
            self._container_path_index[stem][id(obj)] = base_path
            for i, v in enumerate(obj):
                self._index_container_paths(stem, v, base_path + (i,))

    def _build_yaml_cache(self, root_path: Path):
        """
        지정된 경로와 하위 디렉터리에서 YAML 파일을 찾아 캐시를 빌드합니다.

        :param root_path: 루트 디렉터리
        :raises FileNotFoundError: 디렉터리가 아닌 경우
        :raises KeyError: 중복 파일 스템명 발견 시
        :raises ValueError: YAML 로드/파싱 실패
        """
        if not root_path.is_dir():
            raise FileNotFoundError(f"지정된 경로 '{root_path}'가 디렉터리가 아닙니다.")

        yaml_files: Iterable[Path] = chain(root_path.rglob('*.yaml'), root_path.rglob('*.yml'))

        for file_path in yaml_files:
            file_path = file_path.resolve()
            loaded_data = self._load_raw_yaml(file_path)
            processed = self._filter_loaded_yaml(loaded_data)

            node_root = self._compose_yaml_node(file_path)

            file_stem = file_path.stem
            if file_stem in self.yml_cache:
                raise KeyError(f"경고: 중복된 파일 이름('{file_stem}')을 발견했습니다. ({file_path})")

            self.yml_cache[file_stem] = processed
            self._yaml_node_roots[file_stem] = node_root
            self._file_paths[file_stem] = file_path
            self._index_container_paths(file_stem, processed, ())

    # endregion

    # region: 위치 조회 유틸

    def _yaml_key_node_to_value(self, key_node: Any) -> Any:
        """
        YAML 키(ScalarNode)를 Python 값으로 간단 변환합니다.

        :param key_node: YAML ScalarNode
        :return: Python 값(가능한 범위에서 int/float/bool/str)
        """
        if not hasattr(key_node, 'tag') or not hasattr(key_node, 'value'):
            return None
        tag: str = key_node.tag or ''
        val: str = key_node.value
        try:
            if tag.endswith(':int'):
                return int(val)
            if tag.endswith(':float'):
                return float(val)
            if tag.endswith(':bool'):
                return val.lower() == 'true'
        except Exception:
            # 안전하게 문자열로 폴백
            pass
        return val

    def _find_yaml_node_by_path(self, stem: str, path: Tuple[Any, ...]) -> Any | None:
        """
        YAML 노드 트리에서 주어진 경로에 해당하는 노드를 찾습니다.

        :param stem: 파일 스템명
        :param path: 경로 튜플
        :return: YAML 노드 또는 None
        """
        node = self._yaml_node_roots.get(stem)
        if node is None:
            return None

        if not path:
            return node

        for seg in path:
            # 매핑 노드
            if hasattr(yaml, 'nodes') and isinstance(node, yaml.nodes.MappingNode):
                found = None
                for key_node, val_node in node.value:
                    key_val = self._yaml_key_node_to_value(key_node)
                    # 필터 규칙: 점(.)으로 시작하는 문자열 키는 스킵
                    if isinstance(key_val, str) and key_val.startswith('.'):
                        continue
                    if key_val == seg or str(key_val) == str(seg):
                        found = val_node
                        break
                if found is None:
                    return None
                node = found
                continue

            # 시퀀스 노드
            if hasattr(yaml, 'nodes') and isinstance(node, yaml.nodes.SequenceNode):
                if not isinstance(seg, int):
                    return None
                if seg < 0 or seg >= len(node.value):
                    return None
                node = node.value[seg]
                continue

            # 더 이상 내려갈 수 없음
            return None

        return node

    def _pos_from_node(self, stem: str, node: Any | None) -> SourcePos | None:
        """
        YAML 노드에서 위치 정보를 추출합니다.

        :param stem: 파일 스템명
        :param node: YAML 노드
        :return: SourcePos 또는 None
        """
        if node is None or not hasattr(node, 'start_mark'):
            return None
        mark = node.start_mark
        file_path = self._file_paths.get(stem)
        if file_path is None:
            return None
        # PyYAML은 0-base 이므로 1-base로 변환
        return SourcePos(file=file_path, line=int(mark.line) + 1, column=int(mark.column) + 1)

    def _pos_for_path(self, stem: str, path: Tuple[Any, ...]) -> SourcePos | None:
        """
        경로 튜플에 해당하는 YAML 노드 위치를 반환합니다.

        :param stem: 파일 스템명
        :param path: 경로 튜플
        :return: SourcePos 또는 None
        """
        node = self._find_yaml_node_by_path(stem, path)
        if node is None and path:
            # 값 노드를 못 찾는 경우 상위 노드 위치로 폴백
            node = self._find_yaml_node_by_path(stem, path[:-1])
        return self._pos_from_node(stem, node)

    def _fmt_pos(self, pos: SourcePos | None) -> str:
        """
        위치를 사람이 보기 쉬운 문자열로 반환합니다.

        :param pos: SourcePos
        :return: "abs/path/to/file.yaml:line:column" 또는 "위치 불명"
        """
        if pos is None:
            return "위치 불명"
        return f"{pos.file}:{pos.line}:{pos.column}"

    # endregion

    # region: 조건/평가

    def _evaluate(self, expr_str: str) -> bool:
        """
        조건문 문자열을 평가하여 True/False를 반환합니다.

        :param expr_str: 조건식 문자열
        :return: 평가 결과
        :raises TypeError: 조건문이 문자열이 아닌 경우
        """
        if not isinstance(expr_str, str):
            raise TypeError("조건문은 문자열이어야 합니다.")

        expr = expr_str
        while '(' in expr:
            expr = _PAREN_PATTERN.sub(
                lambda match: str(self._evaluate(match.group(1))),
                expr
            )

        return any(self._evaluate_and_clause(part) for part in _OR_SPLIT.split(expr))

    def _evaluate_and_clause(self, and_str: str) -> bool:
        """
        'and'로 연결된 부분 문자열을 평가합니다. 모두 참이어야 True.

        :param and_str: and 절 문자열
        :return: 평가 결과
        """
        return all(self._evaluate_atomic_expr(part) for part in _AND_SPLIT.split(and_str))

    def _evaluate_atomic_expr(self, atomic_str: str) -> bool:
        """
        'a > 10', 'role in roles' 같은 가장 작은 단위의 표현식을 평가합니다.

        :param atomic_str: 원자 표현식
        :return: 평가 결과
        """
        atomic_str = atomic_str.strip()

        if atomic_str.lower().startswith('rand '):
            # "rand 31.425%" 에서 숫자 부분 추출
            value_str = atomic_str.split(maxsplit=1)[1]
            value_str = value_str.removesuffix('%').strip()
            probability = float(value_str) / 100.0
            return random.random() < probability

        elif atomic_str.lower().startswith('not '):
            return not self._evaluate_atomic_expr(atomic_str[4:])

        for op in _OPERATORS:
            # 연산자 양옆에 공백이 없어도 분리할 수 있도록 수정
            if f' {op} ' in f' {atomic_str} ':
                var_name, value_str = [p.strip() for p in atomic_str.split(op, 1)]
                actual_value = self._parse_value(var_name)  # 변수명도 _parse_value를 통해 값 가져오기

                # var_name이 변수가 아닐 수도 있으므로 get 대신 직접 조회
                if actual_value is None and var_name not in self.data:
                    # 값을 파싱하려다 실패한 것이 아니라, 정말 없는 변수일 때만 에러 발생
                    try:
                        float(var_name)  # 숫자인지 체크
                    except (ValueError, TypeError):
                        raise NameError(f"변수 '{var_name}'를 찾을 수 없습니다.")

                target_value = self._parse_value(value_str)
                return _OPERATOR_MAP[op](actual_value, target_value)

        return bool(self._parse_value(atomic_str))

    def _parse_value(self, val_str: str) -> Any:
        """
        문자열 값을 실제 Python 타입(str, bool, int, float, list, 변수)으로 변환합니다.

        :param val_str: 원본 문자열
        :return: 파싱된 값
        """
        val_str = val_str.strip()

        # 1. 리스트 (e.g., "['warrior', 10]")
        if val_str.startswith('[') and val_str.endswith(']'):
            list_contents = val_str[1:-1].strip()
            if not list_contents:
                return []
            return [self._parse_value(item) for item in list_contents.split(',')]

        # 2. 따옴표로 묶인 문자열
        if (val_str.startswith("'") and val_str.endswith("'")) or \
                (val_str.startswith('"') and val_str.endswith('"')):
            return val_str[1:-1]

        # 3. 불리언
        val_lower = val_str.lower()
        if val_lower == 'true': return True
        if val_lower == 'false': return False

        # 4. 숫자 (정수 -> 실수 순)
        try:
            return int(val_str)
        except ValueError:
            try:
                return float(val_str)
            except ValueError:
                # 5. 변수 또는 변환 실패 시 원본 문자열
                return self.data.get(val_str, val_str)

    def _should_render(self, value: Any, ctx: RenderCtx | None = None) -> bool:
        """
        값이 렌더링되어야 하는지 여부를 결정합니다.

        :param value: 검사할 값
        :param ctx: 현재 경로 컨텍스트(오류 위치 표시에 활용)
        :return: 렌더링 여부
        """
        if value is None:
            return True
        if not isinstance(value, dict) or self._CONDITIONS_KEY not in value:
            return True
        return self._check_conditions(value[self._CONDITIONS_KEY], ctx)

    def _check_conditions(self, conditions: dict[str, Any], ctx: RenderCtx | None) -> bool:
        """
        conditions 블록을 평가합니다.

        :param conditions: 조건 딕셔너리
        :param ctx: 현재 컨텍스트(오류 위치 표시에 활용)
        :return: 모든 조건 통과 시 True
        :raises ValueError: 형식 오류
        """
        if not isinstance(conditions, dict):
            # 위치: 현재 값의 'conditions' 키
            pos = self._pos_for_path(ctx.stem, ctx.path + (self._CONDITIONS_KEY,)) if ctx else None
            where = self._fmt_pos(pos)
            raise ValueError(f"'conditions'는 딕셔너리여야 합니다. 위치: {where}")

        for cond_key, required_value in conditions.items():
            # 1. 키 파싱
            is_not_condition = isinstance(cond_key, str) and cond_key.startswith('not ')
            var_name = cond_key.removeprefix('not ') if isinstance(cond_key, str) else cond_key

            if not deep_get(self.data, var_name):
                return False

            # 원 코드의 동작을 그대로 유지
            current_value = self.data[var_name] if isinstance(var_name, str) and var_name in self.data else deep_get(self.data, var_name)

            # 2. 매치 여부(is_match) 계산 로직
            if required_value == self._TRUE_KEY:
                is_match = bool(current_value)
            elif required_value == self._FALSE_KEY:
                is_match = not bool(current_value)
            else:
                req_list = required_value if isinstance(required_value, list) else [required_value]
                is_match = current_value in req_list

            # 3. 판정
            if is_not_condition == is_match:
                return False

        return True  # 모든 조건을 통과

    # endregion

    # region: 렌더링

    def _render_if_then_else(self, cache: dict[str, Any], ctx: RenderCtx) -> Any:
        """
        'if-then-elif-else' 구조를 처리합니다.

        :param cache: 현재 블록
        :param ctx: 현재 위치 컨텍스트
        :return: 렌더링 결과
        """
        try:
            if self._evaluate(cache[self._IF_KEY]):
                return self._render(cache[self._THEN_KEY], RenderCtx(ctx.stem, ctx.path + (self._THEN_KEY,)))

            for idx, elif_block in enumerate(cache.get(self._ELIF_KEY, [])):
                if self._evaluate(elif_block[self._IF_KEY]):
                    return self._render(elif_block[self._THEN_KEY], RenderCtx(ctx.stem, ctx.path + (self._ELIF_KEY, idx, self._THEN_KEY)))

            if self._ELSE_KEY in cache:
                return self._render(cache[self._ELSE_KEY], RenderCtx(ctx.stem, ctx.path + (self._ELSE_KEY,)))

            return None  # 모든 조건 불일치 시

        except (ValueError, NameError, TypeError) as e:
            # 오류가 난 조건문의 위치를 최대한 정확히 지정
            # 우선순위: if → 해당되는 elif의 if → else는 조건이 없으므로 상위 노드
            if self._IF_KEY in cache:
                pos = self._pos_for_path(ctx.stem, ctx.path + (self._IF_KEY,))
                cond = cache.get(self._IF_KEY)
            else:
                # elif들 중 어디서 실패했는지 특정하기 어렵다면 현재 노드 위치로 폴백
                pos = self._pos_for_path(ctx.stem, ctx.path)
                cond = 'N/A'
            where = self._fmt_pos(pos)
            raise type(e)(f"조건문 '{cond}' 평가 중 오류: {e} (위치: {where})") from e

    def _render_match_case(self, cache: dict[str, Any], ctx: RenderCtx) -> Any:
        """
        'match-case' 구조를 처리합니다.

        :param cache: 현재 블록
        :param ctx: 현재 위치 컨텍스트
        :return: 렌더링 결과
        """
        try:
            match_var_name = cache[self._MATCH_KEY]
            if not isinstance(match_var_name, str):
                pos = self._pos_for_path(ctx.stem, ctx.path + (self._MATCH_KEY,))
                where = self._fmt_pos(pos)
                raise TypeError(f"'match' 값은 변수 이름(문자열)이어야 합니다: {match_var_name} (위치: {where})")

            # 딥 키 우선 조회
            value_to_match = deep_get(self.data, match_var_name)
            if value_to_match is None and match_var_name in self.data:
                value_to_match = self.data.get(match_var_name)

            cases = cache.get(self._CASE_KEY, {})
            if not isinstance(cases, dict):
                pos = self._pos_for_path(ctx.stem, ctx.path + (self._CASE_KEY,))
                where = self._fmt_pos(pos)
                raise TypeError(f"'case' 값은 딕셔너리여야 합니다: {cases} (위치: {where})")

            case = cases.get(
                value_to_match,
                cases.get(self._DEFAULT_CASE_KEY, {})
            )

            return self._render(case, RenderCtx(ctx.stem, ctx.path + (self._CASE_KEY, value_to_match if value_to_match in cases else self._DEFAULT_CASE_KEY)))
        except (TypeError, ValueError) as e:
            pos = self._pos_for_path(ctx.stem, ctx.path)
            where = self._fmt_pos(pos)
            raise type(e)(f"match/case 처리 중 오류: {e} (위치: {where})") from e

    def _render_choices(self, cache: dict[str, Any], ctx: RenderCtx) -> Any:
        """
        'CHOICES-WEIGHT-K' 구조를 처리하여 가중치 기반 랜덤 선택을 수행합니다.

        :param cache: 현재 블록
        :param ctx: 현재 위치 컨텍스트
        :return: 선택 결과
        """
        try:
            choices = self._render(cache.get(self._CHOICES_KEY), RenderCtx(ctx.stem, ctx.path + (self._CHOICES_KEY,)))
            weights = cache.get(self._WEIGHT_KEY)
            k = cache.get(self._K_KEY, 1)

            if not choices:
                return None

            if isinstance(choices, dict):
                choices = [{key: value} for key, value in choices.items()]

            if not isinstance(choices, list):
                return choices

            if not isinstance(k, int) or k < 0:
                pos = self._pos_for_path(ctx.stem, ctx.path + (self._K_KEY,))
                where = self._fmt_pos(pos)
                raise TypeError(f"'K' 값은 0 이상의 정수여야 합니다: {k} (위치: {where})")

            if weights is not None:
                if not isinstance(weights, list):
                    pos = self._pos_for_path(ctx.stem, ctx.path + (self._WEIGHT_KEY,))
                    where = self._fmt_pos(pos)
                    raise TypeError(f"'WEIGHT' 값은 리스트여야 합니다. (위치: {where})")
                if len(weights) != len(choices):
                    pos = self._pos_for_path(ctx.stem, ctx.path + (self._WEIGHT_KEY,))
                    where = self._fmt_pos(pos)
                    raise ValueError(f"CHOICES와 WEIGHT의 길이가 일치해야 합니다. (위치: {where})")

            results = random.choices(choices, weights=weights, k=k)
            return results[0] if k == 1 else results

        except (TypeError, ValueError) as e:
            pos = self._pos_for_path(ctx.stem, ctx.path)
            where = self._fmt_pos(pos)
            raise type(e)(f"가중치 선택 처리 중 오류: {e} (위치: {where})") from e

    def _render(self, node: Any, ctx: RenderCtx) -> Any:
        """
        YAML 노드를 재귀적으로 처리합니다.

        :param node: 처리 대상 노드(dict/list/단일 값)
        :param ctx: 현재 위치 컨텍스트
        :return: 렌더링 결과
        """
        if isinstance(node, list):
            return [self._render(item, RenderCtx(ctx.stem, ctx.path + (i,))) for i, item in enumerate(node)]

        if isinstance(node, dict):
            if self._IF_KEY in node and self._THEN_KEY in node:
                return self._render_if_then_else(node, ctx)
            if self._MATCH_KEY in node and self._CASE_KEY in node:
                return self._render_match_case(node, ctx)
            if self._CHOICES_KEY in node:
                return self._render_choices(node, ctx)

            # 일반 딕셔너리: 조건 필터 후 재귀 렌더
            rendered: dict = {}
            for key, value in node.items():
                child_ctx = RenderCtx(ctx.stem, ctx.path + (key,))
                if self._should_render(value, child_ctx):
                    rendered[key] = self._render(value, child_ctx)
            return rendered

        return node

    # endregion

    # region: 컨텍스트 데이터

    @contextmanager
    def _temporary_data(self, new_data: dict | None):
        """
        임시로 self.data를 변경하고, 끝나면 자동으로 복원하는 컨텍스트 매니저.

        :param new_data: 임시로 적용할 데이터 딕셔너리
        """
        if new_data is None:
            yield
            return

        original_data = self.data
        self.data = new_data
        try:
            yield
        finally:
            self.data = original_data

    # endregion

    # region: 퍼블릭 API

    def render(self, key_path: str, temp_data: dict | None = None):
        """
        주어진 키 경로에 해당하는 YAML 데이터를 렌더링합니다.

        :param key_path: 딥 키 경로(예: "fileStem.section.key")
        :param temp_data: 임시 데이터 컨텍스트
        :return: 렌더링 결과
        """
        with self._temporary_data(temp_data):
            # key_path의 최상위 세그먼트를 파일 스템으로 간주
            stem = key_path.split('.', 1)[0]
            base = deep_get(self.yml_cache, key_path, {})
            # 컨테이너 경로 인덱스에서 현재 노드의 경로를 찾아 컨텍스트 생성(없으면 루트로 간주)
            base_path = self._container_path_index.get(stem, {}).get(id(base), ())
            rendering = self._render(base, RenderCtx(stem=stem, path=base_path))
        return rendering

    def random_render(self, key_path: str, temp_data: dict | None = None):
        """
        YAML 데이터를 렌더링하고, 결과 타입에 따라 무작위 요소를 반환합니다.

        :param key_path: 딥 키 경로
        :param temp_data: 임시 데이터 컨텍스트
        :return: 무작위 선택 결과
        """
        rendering = self.render(key_path, temp_data=temp_data)

        match rendering:
            case dict() as d:
                if not d:
                    return d
                key = random.choice(list(d.keys()))
                return {key: d.get(key)}
            case list() | tuple() as seq:
                if not seq:
                    return None
                return random.choice(seq)
            case _:
                return rendering

    # endregion