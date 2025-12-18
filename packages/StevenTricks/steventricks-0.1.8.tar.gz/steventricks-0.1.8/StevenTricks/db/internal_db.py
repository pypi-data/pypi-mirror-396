# -*- coding: utf-8 -*-
"""
internal_db
===========

低階 pickle 資料庫引擎：DBPkl

設計定位：
- 單純處理「一個資料夾 + 一個 table_name」的讀寫
- 管 schema（欄位 dtype / primary key / links）
- 支援：
    - write_db：主鍵合併寫入
    - write_partition：依 partition 欄位整批覆寫
    - load_db：附帶 schema 驗證與 link 解碼
    - load_raw / load_schema / save_schema / migrate_column_dtype / validate_schema

注意：
- 這一層 **不 import DataStore**，也不提供高階歷史版本管理。
- 高階功能由 StevenTricks.db.data_store.DataStore 來包，依賴方向是：
      DataStore  →  DBPkl
  反向依賴一律禁止。
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional, Union, List, Dict, Any, Tuple

import numpy as np
import pandas as pd

from StevenTricks.io.file_utils import pickleio

logger = logging.getLogger(__name__)


class DBPkl:
    """
    用 pickle 模擬簡易 DB 的工具，支援「主鍵合併」、「欄位 schema 檢查」等功能。

    參數
    ----
    db_name : str
        資料夾路徑（實際存放 <table_name>.pkl 與 <logical_table_name>_schema.pkl 的地方）
    table_name : str
        實際存檔用的 table 名（例如：'三大法人買賣超日報__2012'）
    logical_table_name : Optional[str]
        邏輯上的 table 名，用來決定 schema 檔名。
        若省略，預設 = table_name（維持舊行為）。
    """

    def __init__(
        self,
        db_name: str,
        table_name: str,
        logical_table_name: Optional[str] = None,
    ):
        self.db_name = str(db_name)
        self.table_name = str(table_name)

        self.logical_table_name = (
            str(logical_table_name) if logical_table_name else self.table_name
        )

        self.base_dir = Path(self.db_name)
        self.base_dir.mkdir(parents=True, exist_ok=True)

        # schema 檔路徑：{db_dir}/{logical_table_name}_schema.pkl
        self.schema_path = (self.base_dir / f"{self.logical_table_name}_schema").with_suffix(".pkl")

        self.schema: Optional[Dict[str, Any]] = None
        self.schema_conflict: Optional[Dict[str, Any]] = None

    # === 安全載入主檔：給「寫入端」使用（舊檔壞掉就當作沒有舊資料） ===
    def _safe_load_main(self, main_path: Path) -> Optional[pd.DataFrame]:
        """
        安全讀取主檔：
        - 主檔不存在 -> 回傳 None
        - 主檔損毀（EOFError）-> log 警告，回傳 None，讓呼叫端視為 '沒有舊資料'
        - 主檔內容不是 DataFrame -> log 警告，回傳 None
        - 其他錯誤 -> 原樣丟出（讓你知道有不尋常的壞掉）
        """
        try:
            obj = pickleio(path=str(main_path), mode="load")
        except FileNotFoundError:
            return None
        except EOFError:
            logger.warning(
                "[DBPkl] 主檔損毀（EOFError），視為無舊資料重新建立：%s",
                main_path,
            )
            return None
        except Exception as e:
            logger.error(
                "[DBPkl] 讀取主檔發生非預期錯誤（將向上拋出）：path=%s, err=%s",
                main_path,
                e,
            )
            raise

        if isinstance(obj, pd.DataFrame):
            return obj

        logger.warning(
            "[DBPkl] 主檔內容不是 DataFrame（type=%s），視為無舊資料：%s",
            type(obj).__name__,
            main_path,
        )
        return None

    # ------------------------------------------------------------------
    # 寫入：整表合併寫入
    # ------------------------------------------------------------------
    def write_db(
        self,
        df: pd.DataFrame,
        convert_mode: str,
        primary_key: Optional[Union[str, List[str]]] = None,
        update_existing: bool = True,
        overwrite_rows: bool = True,
        allow_new_columns: bool = True,
        allow_remove_columns: bool = False,
        allow_remove_rows: bool = False,
        allow_new_rows: bool = True,
        save_schema: bool = True,
        pk_policy: str = "strict",  # 'strict' | 'ignore' | 'override'
    ) -> None:
        """
        pk_policy:
            - 'strict'   ：既有 schema 有 primary_key，且與這次傳入的 primary_key 不同 → 直接視為錯誤
            - 'ignore'   ：若兩者不同，沿用既有 schema 的 primary_key，忽略本次傳入的 primary_key
            - 'override' ：若兩者不同，以本次傳入的 primary_key 為準，覆蓋 schema
        """
        if df is None or df.empty:
            return

        existing_schema = self.load_schema()

        effective_pk = self._validate_schema_conflict(
            df,
            primary_key,
            convert_mode=convert_mode,
            pk_policy=pk_policy,
        )

        df, schema_data = self._prepare_schema(df, effective_pk, existing_schema)

        main_path = self.base_dir / f"{self.table_name}.pkl"

        t0 = time.perf_counter()

        t_read0 = time.perf_counter()
        old_df = self._safe_load_main(main_path)
        t_read1 = time.perf_counter()

        t_merge0 = time.perf_counter()
        merged_df = self._merge_existing_data(
            new_df=df,
            old_df=old_df,
            schema_data=schema_data,
            update_existing=update_existing,
            overwrite_rows=overwrite_rows,
            allow_new_columns=allow_new_columns,
            allow_remove_columns=allow_remove_columns,
            allow_remove_rows=allow_remove_rows,
            allow_new_rows=allow_new_rows,
        )
        t_merge1 = time.perf_counter()

        merged_df = self._dedup_by_pk_or_raise(
            merged_df, schema_data.get("primary_key"), stage="write_db:final", keep="last"
        )

        t_write0 = time.perf_counter()
        pickleio(main_path, data=merged_df, mode="save")
        t_write1 = time.perf_counter()

        if save_schema:
            pickleio(self.schema_path, data=schema_data, mode="save")
            self.schema = schema_data

        t1 = time.perf_counter()

        logger.info(
            "[DBPkl Timer] table=%s | load=%.2fs, merge=%.2fs, write=%.2fs, total=%.2fs | "
            "rows_new=%d, rows_old=%s, rows_out=%d",
            self.table_name,
            t_read1 - t_read0,
            t_merge1 - t_merge0,
            t_write1 - t_write0,
            t1 - t0,
            len(df),
            "None" if old_df is None else len(old_df),
            len(merged_df),
        )

    # ------------------------------------------------------------------
    # 寫入：按 partition 覆寫
    # ------------------------------------------------------------------
    def write_partition(
        self,
        df: pd.DataFrame,
        convert_mode: str,
        partition_cols: Union[str, List[str]],
        primary_key: Optional[Union[str, List[str]]] = None,
        save_schema: bool = True,
        pk_policy: str = "strict",  # 'strict' | 'ignore' | 'override'
    ) -> None:
        """
        依指定 partition 欄位（例如 'date'）做「整批覆寫」。

        注意：
        - 不再對 old_df 做任何 astype() 之類的型別轉換；
          型別轉換只作用在「本次新 df」，用來符合 schema。
        - pk_policy 同 write_db() 說明。
        """
        if df is None or df.empty:
            return

        if isinstance(partition_cols, str):
            part_cols = [partition_cols]
        else:
            part_cols = list(partition_cols)

        if not part_cols:
            raise ValueError("write_partition() 需要至少一個 partition 欄位")

        missing_in_new = [c for c in part_cols if c not in df.columns]
        if missing_in_new:
            raise ValueError(
                f"Partition 欄位 {missing_in_new} 不存在於新資料 DataFrame（table={self.table_name}）。"
            )

        existing_schema = self.load_schema()
        effective_pk = self._validate_schema_conflict(
            df,
            primary_key,
            convert_mode=convert_mode,
            pk_policy=pk_policy,
        )
        df, schema_data = self._prepare_schema(df, effective_pk, existing_schema)

        main_path = self.base_dir / f"{self.table_name}.pkl"
        old_df = self._safe_load_main(main_path)

        if old_df is not None and not old_df.empty:
            missing_in_old = [c for c in part_cols if c not in old_df.columns]
            if missing_in_old:
                raise ValueError(
                    f"Partition 欄位 {missing_in_old} 不存在於既有資料表（table={self.table_name}）。"
                )

            if len(part_cols) == 1:
                col = part_cols[0]
                replace_vals = df[col].dropna().unique()
                keep_mask = ~old_df[col].isin(replace_vals)
            else:
                new_keys = pd.MultiIndex.from_frame(df[part_cols].drop_duplicates())
                old_keys = pd.MultiIndex.from_frame(old_df[part_cols])
                keep_mask = ~old_keys.isin(new_keys)

            kept_df = old_df[keep_mask].copy()
            out_df = pd.concat([kept_df, df], ignore_index=True)
        else:
            out_df = df.copy()

        ordered_cols = list(schema_data["dtypes"].keys())
        missing_in_out = [c for c in ordered_cols if c not in out_df.columns]
        if missing_in_out:
            raise ValueError(
                f"write_partition() 內部錯誤：schema 欄位 {missing_in_out} 不在合併後 DataFrame 中（table={self.table_name}）。"
            )

        out_df = out_df[ordered_cols]
        out_df = self._dedup_by_pk_or_raise(
            out_df, schema_data.get("primary_key"), stage="write_partition:final", keep="last"
        )
        pickleio(main_path, data=out_df, mode="save")

        if save_schema:
            pickleio(self.schema_path, data=schema_data, mode="save")
            self.schema = schema_data

    # ------------------------------------------------------------------
    # 內部工具：dtype 轉換 / schema 檢查
    # ------------------------------------------------------------------

    def _coerce_series_to_dtype(self, s: pd.Series, expected: str) -> Tuple[pd.Series, bool]:
        """
        嘗試把 s 轉成 expected dtype；回傳 (converted_series, ok)

        ✅ 重要修正：
        - Pandas nullable integer（例如 'Int64' / 'UInt64'）允許 NA，
          不能用「有 NaN 就失敗」這種舊邏輯。
        """
        if expected is None:
            return s, False

        exp = str(expected).strip()
        exp_l = exp.lower()

        # ---- helpers ----
        def _is_nullable_int_dtype(dtype_str: str) -> bool:
            # Pandas nullable integer: Int64 / Int32 / UInt64 ...
            return dtype_str.startswith("Int") or dtype_str.startswith("UInt")

        def _is_numpy_int_dtype(dtype_str_lower: str) -> bool:
            # numpy int64/int32...
            return dtype_str_lower.startswith("int") and not dtype_str_lower.startswith("int[")  # 粗略

        # ---- numeric (int/float) ----
        if exp_l.startswith("int") or exp_l.startswith("float") or _is_nullable_int_dtype(exp):
            try:
                out = pd.to_numeric(s, errors="coerce")

                # nullable integer: allow NA, but non-NA must be integer-like
                if _is_nullable_int_dtype(exp):
                    non_na = out.dropna()
                    if not non_na.empty:
                        # 檢查是否為整數（允許 1.0 這種）
                        frac = (non_na % 1).astype(float)
                        if not np.isclose(frac, 0.0).all():
                            return s, False
                    return out.astype(exp), True

                # numpy int: cannot hold NA
                if exp_l.startswith("int") and _is_numpy_int_dtype(exp_l):
                    if out.isna().any():
                        return s, False
                    non_na = out
                    frac = (non_na % 1).astype(float)
                    if not np.isclose(frac, 0.0).all():
                        return s, False
                    return out.astype(exp), True

                # float
                if exp_l.startswith("float"):
                    return out.astype(exp), True

                # fallback numeric cast
                return out.astype(exp), True

            except Exception:
                return s, False

        # ---- datetime ----
        if exp_l.startswith("datetime64"):
            try:
                out = pd.to_datetime(s, errors="coerce")
                if str(out.dtype) == exp:
                    return out, True
                try:
                    return out.astype(exp), True
                except Exception:
                    return s, False
            except Exception:
                return s, False

        # ---- bool / boolean ----
        if exp_l in {"bool", "boolean"}:
            try:
                tmp = s
                if (s.dtype == "O") or pd.api.types.is_string_dtype(s) or pd.api.types.is_numeric_dtype(s):
                    m = s.astype(str).str.strip().str.lower()
                    mapping = {
                        "true": True, "false": False,
                        "1": True, "0": False,
                        "是": True, "否": False,
                        "y": True, "n": False,
                        "yes": True, "no": False,
                        "t": True, "f": False,
                        "": pd.NA,
                        "nan": pd.NA,
                        "none": pd.NA,
                    }
                    mapped = m.map(mapping)
                    tmp = pd.Series(np.where(mapped.isna(), pd.NA, mapped), index=s.index)

                # boolean（nullable）比較安全
                if exp_l == "boolean":
                    return tmp.astype("boolean"), True
                # bool（numpy）不允許 NA
                if tmp.isna().any():
                    return s, False
                return tmp.astype("bool"), True
            except Exception:
                return s, False

        # ---- string / object ----
        if exp_l in {"string", "object"}:
            try:
                return (s.astype("string") if exp_l == "string" else s.astype("object")), True
            except Exception:
                return s, False

        # ---- other ----
        try:
            return s.astype(exp), True
        except Exception:
            return s, False

    def _validate_schema_conflict(
        self,
        df: pd.DataFrame,
        primary_key: Optional[Union[str, List[str]]],
        convert_mode: str = "error",
        pk_policy: str = "strict",
    ) -> Optional[List[str]]:
        """
        檢查 df 與既有表的 schema 是否相容，並依 pk_policy 處理 primary_key 衝突。
        """
        mode = (convert_mode or "error").lower().strip()
        if mode not in {"error", "coerce", "upcast"}:
            raise ValueError(f"Unknown mode: {mode!r}. Expected 'error'|'coerce'|'upcast'.")

        pk_policy = (pk_policy or "strict").lower().strip()
        if pk_policy not in {"strict", "ignore", "override"}:
            raise ValueError(f"Unknown pk_policy: {pk_policy!r}. Expected 'strict'|'ignore'|'override'.")

        # 確保 schema 有載入（load_schema() 會把 self.schema 填起來）
        if self.schema is None:
            # 沒有既有 schema：略過 dtype 比對
            return self._normalize_primary_key(primary_key)

        existing_pk_raw = self.schema.get("primary_key")
        existing_pk = self._normalize_primary_key(existing_pk_raw)
        new_pk = self._normalize_primary_key(primary_key)

        if existing_pk is None and new_pk is None:
            effective_pk = None
        elif existing_pk is None and new_pk is not None:
            effective_pk = new_pk
        elif existing_pk is not None and new_pk is None:
            effective_pk = existing_pk
        else:
            if existing_pk != new_pk:
                try:
                    old_tail = pickleio(self.base_dir / f"{self.table_name}.pkl", mode="load").tail(1)
                except Exception:
                    old_tail = None

                self.schema_conflict = {
                    "table": self.table_name,
                    "type": "primary_key_mismatch",
                    "existing_primary_key": existing_pk,
                    "new_primary_key": new_pk,
                    "old_row": old_tail,
                    "new_row": df.tail(1),
                }

                if pk_policy == "strict":
                    raise ValueError("Primary key mismatch. Please resolve manually.")

                if pk_policy == "ignore":
                    logger.warning(
                        "[DBPkl] primary_key 衝突，但依 pk_policy='ignore' 沿用既有設定：table=%s, existing=%s, new=%s",
                        self.table_name,
                        existing_pk,
                        new_pk,
                    )
                    effective_pk = existing_pk
                else:
                    logger.warning(
                        "[DBPkl] primary_key 衝突，依 pk_policy='override' 以新設定覆蓋：table=%s, old=%s, new=%s",
                        self.table_name,
                        existing_pk,
                        new_pk,
                    )
                    effective_pk = new_pk
            else:
                effective_pk = existing_pk

        expected_dtypes: Dict[str, str] = self.schema.get("dtypes", {}) or {}

        def _is_numeric_dtype_str(s_: str) -> bool:
            ls = (s_ or "").lower()
            return ls.startswith("int") or ls.startswith("float") or s_.startswith("Int") or s_.startswith("UInt")

        for col in df.columns:
            if col not in expected_dtypes:
                continue

            expected = expected_dtypes[col]
            actual = str(df[col].dtype)
            if actual == expected:
                continue

            if mode == "error":
                try:
                    old_tail = pickleio(self.base_dir / f"{self.table_name}.pkl", mode="load").tail(1)
                    old_sample = old_tail[[col]] if (old_tail is not None and col in old_tail.columns) else old_tail
                except Exception:
                    old_sample = None
                self.schema_conflict = {
                    "table": self.table_name,
                    "type": "dtype_mismatch",
                    "column": col,
                    "expected_dtype": expected,
                    "actual_dtype": actual,
                    "old_row": old_sample,
                    "new_row": df[[col]].tail(1),
                }
                raise TypeError("Column dtype mismatch. Please resolve manually.")

            both_numeric = _is_numeric_dtype_str(expected) and pd.api.types.is_numeric_dtype(df[col].dtype)

            if mode == "upcast" and both_numeric:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")
                continue

            converted, ok = self._coerce_series_to_dtype(df[col], expected)
            if ok and str(converted.dtype) == expected:
                df[col] = converted
                continue

            try:
                old_tail = pickleio(self.base_dir / f"{self.table_name}.pkl", mode="load").tail(1)
                old_sample = old_tail[[col]] if (old_tail is not None and col in old_tail.columns) else old_tail
            except Exception:
                old_sample = None

            self.schema_conflict = {
                "table": self.table_name,
                "type": "dtype_mismatch",
                "column": col,
                "expected_dtype": expected,
                "actual_dtype": actual if not ok else str(converted.dtype),
                "old_row": old_sample,
                "new_row": df[[col]].tail(1),
            }
            raise TypeError("Column dtype mismatch. Please resolve manually.")

        self.schema_conflict = None
        return effective_pk

    @staticmethod
    def _normalize_primary_key(
        primary_key: Optional[Union[str, List[str]]]
    ) -> Optional[List[str]]:
        if primary_key is None:
            return None
        if isinstance(primary_key, str):
            return [primary_key]
        if isinstance(primary_key, (list, tuple)):
            return [str(c) for c in primary_key]
        try:
            return [str(c) for c in primary_key]  # type: ignore[arg-type]
        except Exception:
            return None

    def _prepare_schema(
        self,
        df: pd.DataFrame,
        primary_key: Optional[Union[str, List[str]]],
        existing_schema: Optional[Dict],
    ) -> Tuple[pd.DataFrame, Dict]:
        schema_data = {"dtypes": {col: str(df[col].dtype) for col in df.columns}, "links": {}}

        if primary_key:
            self._check_primary_key_valid(df, primary_key)
            schema_data["primary_key"] = primary_key if isinstance(primary_key, list) else [primary_key]
        else:
            auto_pk_name = "AutoPrimaryKey_1"
            counter = 1
            while auto_pk_name in df.columns:
                counter += 1
                auto_pk_name = f"AutoPrimaryKey_{counter}"
            df.insert(0, auto_pk_name, range(1, len(df) + 1))
            schema_data["primary_key"] = [auto_pk_name]
            schema_data["dtypes"][auto_pk_name] = str(df[auto_pk_name].dtype)

        pk_list = schema_data["primary_key"]

        # 為 object 欄位建立 link table
        for col in [c for c in df.columns if c not in pk_list]:
            if df[col].dtype == object and df[col].duplicated().any():
                unique_vals = (
                    pd.Series(df[col], dtype="object")
                    .dropna()
                    .astype(str)
                    .str.strip()
                    .replace("", pd.NA)
                    .dropna()
                    .drop_duplicates()
                    .tolist()
                )
                link_df = self._generate_link_df(col, unique_vals, existing_schema)

                non_null_mapping = dict(zip(link_df[col], link_df["link_id"]))
                mapped = df[col].map(non_null_mapping)

                # ✅ link_id 欄位用 nullable integer，避免後面 dtype 不一致
                df[col] = pd.to_numeric(mapped, errors="coerce").astype("Int64")

                schema_data["links"][col] = link_df.to_dict(orient="list")
                schema_data["dtypes"][col] = str(df[col].dtype)

        return df, schema_data

    def _check_primary_key_valid(self, df: pd.DataFrame, primary_key: Union[str, List[str]]) -> None:
        if isinstance(primary_key, str):
            if primary_key not in df.columns:
                raise ValueError(f"Primary key column '{primary_key}' missing in DataFrame")
            if df[primary_key].isna().any():
                raise ValueError(f"Primary key column '{primary_key}' contains NaN")
            if df.duplicated(subset=[primary_key]).any():
                raise ValueError(f"Primary key column '{primary_key}' does not form a unique constraint")
        elif isinstance(primary_key, list):
            if not all(col in df.columns for col in primary_key):
                raise ValueError(f"Some primary key columns {primary_key} missing in DataFrame")
            if df[primary_key].isna().any().any():
                raise ValueError(f"Primary key columns {primary_key} contain NaN")
            if df.duplicated(subset=primary_key).any():
                raise ValueError(f"Primary key columns {primary_key} do not form a unique constraint")

    def _generate_link_df(
        self,
        col: str,
        unique_vals: List[str],
        existing_schema: Optional[Dict],
    ) -> pd.DataFrame:
        new_vals_raw = pd.Series(unique_vals, dtype="object")
        new_vals = new_vals_raw.dropna().astype(str).str.strip()
        new_vals = new_vals[new_vals != ""].drop_duplicates().tolist()

        if existing_schema and col in (existing_schema.get("links") or {}):
            old_link_df = pd.DataFrame(existing_schema["links"][col])

            if col not in old_link_df.columns:
                old_link_df[col] = pd.Series(dtype="string")
            if "link_id" not in old_link_df.columns:
                old_link_df["link_id"] = pd.Series(dtype="Int64")

            old_link_df[col] = old_link_df[col].astype("string").str.strip()
            old_link_df = old_link_df[old_link_df[col].notna() & (old_link_df[col] != "")].copy()

            link_id_num = pd.to_numeric(old_link_df["link_id"], errors="coerce")
            max_id = int(link_id_num.max()) if link_id_num.notna().any() else 0

            old_mapping = dict(zip(old_link_df[col].astype(str), link_id_num.astype("Int64")))
            add_vals = [v for v in new_vals if v not in old_mapping]

            if add_vals:
                start = max_id + 1
                new_ids = list(range(start, start + len(add_vals)))
                new_entries = pd.DataFrame({col: add_vals, "link_id": new_ids})
                out = pd.concat([old_link_df[[col, "link_id"]], new_entries], ignore_index=True)
            else:
                out = old_link_df[[col, "link_id"]].copy()

            out = out.drop_duplicates(subset=[col]).sort_values("link_id").reset_index(drop=True)
            out[col] = out[col].astype("string")
            out["link_id"] = pd.to_numeric(out["link_id"], errors="coerce").astype("Int64")
            return out

        if not new_vals:
            return pd.DataFrame(
                {col: pd.Series(dtype="string"), "link_id": pd.Series(dtype="Int64")}
            )

        link_df = pd.DataFrame({col: new_vals})
        link_df["link_id"] = range(1, len(link_df) + 1)
        link_df[col] = link_df[col].astype("string")
        link_df["link_id"] = link_df["link_id"].astype("Int64")
        return link_df

    def _dedup_by_pk_or_raise(
        self,
        df: pd.DataFrame,
        pk: Optional[Union[str, List[str]]],
        *,
        stage: str,
        keep: str = "last",
    ) -> pd.DataFrame:
        pk_list = self._normalize_primary_key(pk)
        if not pk_list:
            return df

        for c in pk_list:
            if c not in df.columns:
                return df

        before = len(df)
        if df.duplicated(subset=pk_list).any():
            df = df.drop_duplicates(subset=pk_list, keep=keep).copy()
            after = len(df)
            logger.warning(
                "[DBPkl] 偵測到重複 PK，已自動去重：table=%s, stage=%s, pk=%s, dropped=%d",
                self.table_name, stage, pk_list, before - after
            )

        if df.duplicated(subset=pk_list).any():
            raise ValueError(
                f"[DBPkl] 去重後仍存在重複 PK：table={self.table_name}, stage={stage}, pk={pk_list}"
            )

        return df

    def _merge_existing_data(
        self,
        new_df: pd.DataFrame,
        old_df: Optional[pd.DataFrame],
        schema_data: Dict,
        update_existing: bool,
        overwrite_rows: bool,
        allow_new_columns: bool,
        allow_remove_columns: bool,
        allow_remove_rows: bool,
        allow_new_rows: bool,
    ) -> pd.DataFrame:
        if old_df is None or old_df.empty:
            return new_df

        pk = schema_data.get("primary_key")

        old_df = self._dedup_by_pk_or_raise(old_df, pk, stage="merge:old_df", keep="last")
        new_df = self._dedup_by_pk_or_raise(new_df, pk, stage="merge:new_df", keep="last")

        old_df = old_df.set_index(pk, drop=True)
        new_df = new_df.set_index(pk, drop=True)

        if update_existing:
            if allow_new_columns:
                new_cols = [c for c in new_df.columns if c not in old_df.columns]
                if new_cols:
                    old_df = old_df.merge(
                        new_df[new_cols],
                        left_index=True,
                        right_index=True,
                        how="left",
                    )
            if allow_remove_columns:
                keep_cols = [c for c in old_df.columns if c in new_df.columns]
                old_df = old_df[keep_cols]
            new_df = new_df[[c for c in new_df.columns if c in old_df.columns]]

        if allow_remove_rows:
            old_df = old_df[old_df.index.isin(new_df.index)]

        if allow_new_rows:
            old_df = pd.concat([old_df, new_df[~new_df.index.isin(old_df.index)]])

        if overwrite_rows:
            old_df.update(new_df)

        old_df = old_df.reset_index()
        return old_df

    # ------------------------------------------------------------------
    # 讀取 / schema 操作
    # ------------------------------------------------------------------

    def load_db(self, decode_links: bool = True) -> pd.DataFrame:
        """
        正常載入資料表（套用 schema 檢查與 link 還原）。
        若主檔損毀（EOFError），會直接拋錯，避免靜默吃掉資料問題。
        """
        path = self.base_dir / f"{self.table_name}.pkl"
        if not path.exists():
            raise FileNotFoundError(f"Table '{self.table_name}' not found at {path}")

        df = pickleio(path, mode="load")

        if self.schema:
            self.validate_schema(df)

            if decode_links:
                for col, records in (self.schema.get("links", {}) or {}).items():
                    link_df = pd.DataFrame(records)
                    if "link_id" not in link_df.columns or col not in link_df.columns:
                        continue
                    mapping = dict(zip(link_df["link_id"], link_df[col]))
                    if col in df.columns:
                        df[col] = df[col].map(mapping)

            schema_cols = list((self.schema.get("dtypes", {}) or {}).keys())
            df = df[[col for col in schema_cols if col in df.columns]]

        return df

    def load_raw(self) -> pd.DataFrame:
        """
        直接載入主資料表（<table_name>.pkl），不做 schema 驗證、不還原 links。
        若主檔損毀（EOFError），會直接拋錯。
        """
        path = self.base_dir / f"{self.table_name}.pkl"
        if not path.exists():
            raise FileNotFoundError(f"Table '{self.table_name}' not found at {path}")
        return pickleio(path, mode="load")

    def load_schema(self) -> Optional[Dict]:
        """
        直接讀取 schema 檔；若檔案不存在，回傳 None。
        若 schema 檔損毀（EOFError），會 log 警告並回傳 None（讓後續當成「無 schema」重建）。
        """
        if self.schema is not None:
            return self.schema

        if self.schema_path.exists():
            try:
                self.schema = pickleio(self.schema_path, mode="load")
            except EOFError:
                logger.warning(
                    "[DBPkl] schema 檔損毀（EOFError），將視為無 schema 重新建立：%s",
                    self.schema_path,
                )
                self.schema = None
                return None
            return self.schema
        return None

    def save_schema(self, schema: Dict) -> None:
        pickleio(self.schema_path, data=schema, mode="save")
        self.schema = schema

    def migrate_column_dtype(
        self,
        col: str,
        target_dtype: str,
        *,
        coerce: bool = True,
    ) -> None:
        df = self.load_raw()
        schema = self.load_schema() or {"dtypes": {}, "links": {}, "primary_key": []}

        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in table '{self.table_name}'")

        converted, ok = self._coerce_series_to_dtype(df[col], target_dtype)

        if not ok:
            if coerce:
                raise TypeError(
                    f"Cannot safely convert column '{col}' to '{target_dtype}' "
                    f"in table '{self.table_name}'"
                )
            return

        df[col] = converted
        schema.setdefault("dtypes", {})
        schema["dtypes"][col] = str(df[col].dtype)

        main_path = self.base_dir / f"{self.table_name}.pkl"
        pickleio(main_path, data=df, mode="save")
        self.save_schema(schema)

    def validate_schema(self, df: pd.DataFrame) -> None:
        """
        驗證 df 是否符合目前載入的 schema。
        """
        if not self.schema:
            raise FileNotFoundError(f"No schema loaded for table '{self.table_name}'")

        pk = self.schema.get("primary_key")
        pk_list = self._normalize_primary_key(pk)

        if pk_list:
            missing = [c for c in pk_list if c not in df.columns]
            if missing:
                raise ValueError(f"Some primary key columns {missing} missing in DataFrame for table '{self.table_name}'")
            if df[pk_list].isna().any().any():
                raise ValueError(f"Primary key columns {pk_list} contain NaN in table '{self.table_name}'")
            if df.duplicated(subset=pk_list).any():
                raise ValueError(f"Primary key columns {pk_list} in table '{self.table_name}' do not form a unique constraint")

        for col, expected_type in (self.schema.get("dtypes", {}) or {}).items():
            if col not in df.columns:
                raise ValueError(f"Missing column '{col}' in table '{self.table_name}'")
            actual_type = str(df[col].dtype)
            if actual_type != expected_type:
                raise TypeError(
                    f"Column '{col}' in table '{self.table_name}' expected type '{expected_type}', "
                    f"got '{actual_type}'"
                )
