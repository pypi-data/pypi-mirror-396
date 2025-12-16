import os
import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Iterable, Optional
import hashlib
import threading
import zstandard as zstd

__all__ = ["ZstDB", "compress_zst", "decompress_zst"]


def compress_zst(
    src: str | Path,
    dst: Optional[str | Path] = None,
    level: int = 3,
    chunk_size: int = 4 * 1024 * 1024,
    compressor: Optional[zstd.ZstdCompressor] = None,
    threads: Optional[int] = None,
) -> Path:
    """
    단일 파일을 Zstandard(.zst) 형식으로 압축합니다.

    :param src: 원본 파일 경로.
    :type src: str 또는 pathlib.Path
    :param dst: 출력 .zst 파일 경로.
        생략하면 ``<src>.zst`` 경로로 저장합니다.
    :type dst: str 또는 pathlib.Path 또는 None
    :param level: 압축 레벨(1–22). 값이 높을수록 압축률은 좋아지지만 속도는 느려집니다.
        ``compressor`` 인스턴스를 직접 전달하면 이 값은 무시됩니다.
    :type level: int
    :param chunk_size: 파일을 읽고 쓰는 단위 크기(바이트).
    :type chunk_size: int
    :param compressor: 재사용을 위해 미리 생성한 :class:`zstandard.ZstdCompressor` 인스턴스.
        여러 파일을 연속으로 압축할 때 유용합니다. 이 값을 지정하면 ``threads``,
        ``level`` 인자는 무시됩니다.
    :type compressor: zstandard.ZstdCompressor 또는 None
    :param threads: 압축에 사용할 스레드 수.
        ``None``이면 현재 시스템의 CPU 코어 수에서 1개를 뺀 값을 사용합니다.
        (예: 8코어 시스템이면 기본값은 7 스레드, 최소 1 이상)
        1을 지정하면 단일 스레드로 동작합니다.
    :type threads: int 또는 None
    :returns: 생성된 .zst 파일의 경로.
    :rtype: pathlib.Path
    :raises FileNotFoundError: 원본 파일이 존재하지 않을 때.
    :raises ValueError: 원본 경로가 파일이 아닐 때.
    """
    src_path = Path(src)

    if not src_path.is_file():
        if not src_path.exists():
            raise FileNotFoundError(f"Source file not found: {src_path}")
        raise ValueError(f"Source path is not a file: {src_path}")

    dst_path = Path(dst) if dst is not None else src_path.with_name(src_path.name + ".zst")

    if compressor is not None:
        cctx = compressor
    else:
        if threads is None:
            cpu_count = os.cpu_count() or 1
            # 한 코어는 남겨 두고, 최소 1 스레드는 사용
            threads = max(cpu_count - 1, 1)
        cctx = zstd.ZstdCompressor(level=level, threads=threads)

    with src_path.open("rb") as f_src, dst_path.open("wb") as f_dst:
        with cctx.stream_writer(f_dst) as writer:
            for chunk in iter(lambda: f_src.read(chunk_size), b""):
                writer.write(chunk)

    return dst_path


def decompress_zst(
    src: str | Path,
    dst: Optional[str | Path] = None,
    chunk_size: int = 4 * 1024 * 1024,
    decompressor: Optional[zstd.ZstdDecompressor] = None,
) -> Path:
    """
    Zstandard(.zst) 파일을 원본 형태로 압축 해제합니다.

    :param src: .zst 압축 파일 경로.
    :type src: str 또는 pathlib.Path
    :param dst: 압축 해제 결과를 저장할 파일 경로.
        생략하면 ``<src>``에서 끝의 ``.zst`` 확장자를 제거한 이름을 사용합니다.
        확장자가 ``.zst``가 아니면 ``<src>.out`` 형태로 저장합니다.
    :type dst: str 또는 pathlib.Path 또는 None
    :param chunk_size: 파일을 읽고 쓰는 단위 크기(바이트).
    :type chunk_size: int
    :param decompressor: 재사용을 위해 미리 생성한 :class:`zstandard.ZstdDecompressor`
        인스턴스. 여러 파일을 연속으로 해제할 때 유용합니다.
    :type decompressor: zstandard.ZstdDecompressor 또는 None
    :returns: 압축 해제된 파일의 경로.
    :rtype: pathlib.Path
    :raises FileNotFoundError: 입력 파일이 존재하지 않을 때.
    :raises ValueError: 입력 경로가 파일이 아닐 때.
    """
    src_path = Path(src)

    if not src_path.is_file():
        if not src_path.exists():
            raise FileNotFoundError(f"Source file not found: {src_path}")
        raise ValueError(f"Source path is not a file: {src_path}")

    if dst is None:
        name = src_path.name
        dst_name = name[:-4] if name.endswith(".zst") else name + ".out"
        dst_path = src_path.with_name(dst_name)
    else:
        dst_path = Path(dst)

    dctx = decompressor or zstd.ZstdDecompressor()

    with src_path.open("rb") as f_src, dst_path.open("wb") as f_dst:
        with dctx.stream_reader(f_src) as reader:
            for chunk in iter(lambda: reader.read(chunk_size), b""):
                f_dst.write(chunk)

    return dst_path


class ZstCache:
    """
    Zstandard로 압축된 SQLite DB를 한 번만 압축 해제해서
    캐시 디렉터리에 .db 파일로 저장하고 재사용하는 캐시입니다.
    """

    __slots__ = ("dir", "_lock")

    def __init__(self, dir: str | Path | None = None) -> None:
        """
        :param dir: 캐시 디렉터리 경로. None이면 시스템 임시 디렉터리 하위의
                    ``zst_sqlite_cache``를 사용합니다.
        """
        if dir is None:
            root = Path(tempfile.gettempdir())
            dir = root / "zst_sqlite_cache"

        self.dir = Path(dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _key(self, zst: Path) -> str:
        """
        경로 + 파일 크기 + mtime을 이용해 캐시 키를 만듭니다.
        """
        zst = zst.resolve()
        st = zst.stat()
        h = hashlib.sha256()
        h.update(str(zst).encode("utf-8"))
        h.update(str(st.st_size).encode("utf-8"))
        h.update(str(int(st.st_mtime)).encode("utf-8"))
        return h.hexdigest()

    def _db_path(self, key: str) -> Path:
        return self.dir / f"{key}.db"

    def get(self, zst: str | Path, *, buf: int = 1 << 20) -> Path:
        """
        압축된 zst 파일을 해제한 .db 경로를 반환합니다.

        - 이미 캐시에 있으면 그대로 반환
        - 없으면 해제 후 캐시에 저장하고 경로 반환
        """
        zst = Path(zst)
        key = self._key(zst)
        db = self._db_path(key)

        if db.exists():
            return db

        with self._lock:
            if db.exists():
                return db

            fd, tmp_name = tempfile.mkstemp(
                dir=self.dir,
                suffix=".db.tmp",
            )
            tmp = Path(tmp_name)

            try:
                dec = zstd.ZstdDecompressor()
                with zst.open("rb", buffering=buf) as src, open(
                        fd,
                        "wb",
                        buffering=buf,
                ) as dst:
                    dec.copy_stream(src, dst)

                tmp.replace(db)
            finally:
                if tmp.exists() and not db.exists():
                    try:
                        tmp.unlink()
                    except OSError:
                        pass

        return db


class ZstDB:
    """
    ZstCache를 이용해 압축된 SQLite DB를 열어 쿼리하는 헬퍼입니다.
    """

    __slots__ = ("zst", "cache", "conn", "_c")

    def __init__(self, zst: str | Path, cache: ZstCache | None = None) -> None:
        """
        :param zst: Zstandard로 압축된 SQLite DB 파일 경로.
        :param cache: 캐시 인스턴스. None이면 기본 캐시 디렉터리를 사용합니다.
        """
        self.zst = Path(zst)
        self.cache = cache or ZstCache()
        self.conn: Optional[sqlite3.Connection] = None
        self._c: Optional[sqlite3.Cursor] = None

    def __enter__(self) -> "ZstDB":
        self._open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._close()

    # ---------------- 내부 유틸 ---------------- #

    def _open(self) -> None:
        """
        캐시된 .db를 열어 SQLite 연결을 생성합니다.
        """
        try:
            db = self.cache.get(self.zst)

            self.conn = sqlite3.connect(
                db,
                isolation_level=None,
                check_same_thread=False,
            )
            self.conn.row_factory = sqlite3.Row

            # 윈도우에서 확인된 안전 범위 내 최적화
            self.conn.executescript(
                """
                PRAGMA temp_store = MEMORY;
                PRAGMA cache_size = -20000;
                PRAGMA synchronous = OFF;
                """
            )

            self._c = self.conn.cursor()
        except Exception:
            self._close()
            raise

    def _close(self) -> None:
        """
        SQLite 연결을 정리합니다. (캐시 파일은 남깁니다.)
        """
        if self._c is not None:
            try:
                self._c.close()
            except Exception:
                pass
            self._c = None

        if self.conn is not None:
            try:
                self.conn.close()
            except Exception:
                pass
            self.conn = None

    def _conn(self) -> sqlite3.Connection:
        if self.conn is None:
            raise ConnectionError("SQLite 연결이 없습니다.")
        return self.conn

    def _cur(self) -> sqlite3.Cursor:
        conn = self._conn()
        if self._c is None:
            self._c = conn.cursor()
        return self._c

    # ---------------- 쿼리 헬퍼 ---------------- #

    def q(
        self,
        sql: str,
        params: Iterable[Any] | dict[str, Any] = (),
    ) -> list[sqlite3.Row]:
        """
        SQL을 실행하고 모든 결과 행을 반환합니다.
        """
        c = self._cur()
        c.execute(sql, params)
        return c.fetchall()

    def sel(
        self,
        table: str,
        cols: str | Iterable[str] = "*",
        where: Optional[str | Iterable[str] | dict[str, Any]] = None,
        params: Iterable[Any] | dict[str, Any] = (),
        limit: Optional[int] = None,
    ) -> list[sqlite3.Row]:
        """
        간단한 SELECT 헬퍼입니다.
        """
        if isinstance(cols, str):
            col_str = cols
        else:
            col_str = ", ".join(cols)

        where_sql = ""
        q_params: Iterable[Any] | dict[str, Any] = params

        if isinstance(where, dict):
            keys = list(where.keys())
            where_sql = " AND ".join(f"{k} = ?" for k in keys)
            q_params = tuple(where[k] for k in keys)
        elif isinstance(where, (list, tuple, set)):
            parts = list(where)
            if parts:
                where_sql = " AND ".join(parts)
        elif isinstance(where, str):
            where_sql = where

        sql_parts = [f"SELECT {col_str} FROM {table}"]
        if where_sql:
            sql_parts.append(f"WHERE {where_sql}")
        if limit is not None:
            sql_parts.append(f"LIMIT {limit}")

        sql = " ".join(sql_parts)
        return self.q(sql, q_params)
