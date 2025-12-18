# -*- coding: utf-8 -*-
"""
Driver Tree 工具（Funding_Amt 變動拆解版）
======================================

目標：找出「最有效的切法」來解釋 base_period → comp_period 的 Funding_Amt 變動
（注意：這是描述性 explain，不是因果性 cause。）

改版重點（針對「不是巧合」的科學依據）：
1) 每個節點在挑 split_dim 前，先對「所有候選欄位」計分並排名（dim_scores）。
2) split_policy：
   - 'best_overall'：所有候選欄位一起比（預設、較可辯護）
   - 'role_first'  ：依 ROLE_ORDER 先挑到的 role 就不看後面（簡報敘事用）
3) 分數使用「移動量集中度」（gross-move concentration）：
   - gross_move = Σ |delta_i|
   - gross_share_i = |delta_i| / gross_move
   - HHI = Σ gross_share_i^2   （1/n ~ 1，越大越集中、越像“主因集中”）
   - 同時報 top1 / top3 移動量占比
4) pivot 會補齊判讀欄位：
   abs_delta, gross_share_in_node, net_share_in_node,
   base_share, comp_share, share_change_pp, rank_abs_delta
5) summary 會先講：候選欄位數與排名、為何選中，再講該欄位底下哪個類別影響最大（用比例）。

"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple

import numpy as np
import pandas as pd

from StevenTricks.analysis.scenario_compare import two_period_change_pivot


# ------------------------------------------------------------
# 一、欄位角色設定
# ------------------------------------------------------------

DIM_ROLE: Dict[str, str] = {
    "Funding_Date_yymm": "time",

    "Product_Flag_new": "product",

    "Property_Location_Flag": "region",

    "Tenor_Flag": "structure",
    "Grace_Length_Flag": "structure",
    "OLTV_Flag": "structure",

    "Cust_Flag": "customer",

    "Investor_Flag": "investor",
    "cb_Investor_flag": "investor",
    "Public_Flag2024": "investor",

    "Acct_Type_Code": "account",
    "Int_Category_Code": "account",

    "Batch_Flag": "project",
    "special_flag": "project",
}

ROLE_ORDER: List[str] = [
    "product",
    "region",
    "structure",
    "customer",
    "investor",
    "account",
    "project",
]


# ------------------------------------------------------------
# 二、樹節點資料結構
# ------------------------------------------------------------

@dataclass
class DriverTreeNode:
    node_id: int
    depth: int
    path: Dict[str, Any]

    amt_base: float
    amt_comp: float
    delta_amt: float
    delta_share: float  # relative to global net delta

    split_dim: Optional[str] = None
    split_role: Optional[str] = None
    split_policy: Optional[str] = None
    split_reason: Optional[str] = None

    # chosen dim score (for quick view)
    split_score_hhi: Optional[float] = None
    split_top1_gross_share: Optional[float] = None
    split_top3_gross_share: Optional[float] = None

    pivot: Optional[pd.DataFrame] = None
    summary_zh: Optional[str] = None

    children: List["DriverTreeNode"] = field(default_factory=list)


# ------------------------------------------------------------
# 三、Driver Tree 主體
# ------------------------------------------------------------

class DriverTree:
    def __init__(
        self,
        max_depth: int = 3,
        min_node_share: float = 0.05,
        top_k: int = 5,
        split_policy: str = "best_overall",  # ✅ 預設 best_overall
    ) -> None:
        self.max_depth = max_depth
        self.min_node_share = min_node_share
        self.top_k = top_k

        if split_policy not in ("best_overall", "role_first"):
            raise ValueError("split_policy must be one of: 'best_overall', 'role_first'")
        self.split_policy = split_policy

        self.root: Optional[DriverTreeNode] = None
        self._nodes: List[DriverTreeNode] = []
        self._next_node_id: int = 1

        self.target_col: str = "Funding_Amt"
        self.time_col: str = "Funding_Date_yymm"
        self.base_period: Any = None
        self.comp_period: Any = None
        self.global_delta_amt: float = 0.0

        # node_id -> candidates score table
        self._dim_scores: Dict[int, pd.DataFrame] = {}

        # meta
        self._meta: Dict[str, Any] = {}

    def fit(
        self,
        df: pd.DataFrame,
        base_period: Any,
        comp_period: Any,
        dims: Optional[List[str]] = None,
        target_col: str = "Funding_Amt",
        time_col: str = "Funding_Date_yymm",
    ) -> "DriverTree":
        self.target_col = target_col
        self.time_col = time_col
        self.base_period = base_period
        self.comp_period = comp_period

        if dims is None:
            dims = [col for col, role in DIM_ROLE.items() if role != "time"]
        dims = [d for d in dims if d in df.columns]

        df_base = df[df[time_col] == base_period]
        df_comp = df[df[time_col] == comp_period]
        amt_base = float(df_base[target_col].sum())
        amt_comp = float(df_comp[target_col].sum())
        delta_amt = amt_comp - amt_base

        self.global_delta_amt = delta_amt if delta_amt != 0 else 1e-9

        root = DriverTreeNode(
            node_id=self._alloc_node_id(),
            depth=0,
            path={},
            amt_base=amt_base,
            amt_comp=amt_comp,
            delta_amt=delta_amt,
            delta_share=1.0,
        )
        self.root = root
        self._nodes = [root]

        # 建樹
        self._build_node(df=df, parent_node=root, available_dims=dims)

        # ✅ meta 必須先算好，summary 才能引用節點數
        self._meta = {
            "n_nodes": len(self._nodes),
            "n_leaves": sum(1 for n in self._nodes if n.split_dim is None),
            "max_depth_reached": max(n.depth for n in self._nodes) if self._nodes else 0,
            "max_depth_setting": self.max_depth,
            "min_node_share": self.min_node_share,
            "top_k": self.top_k,
            "split_policy": self.split_policy,
        }

        # 再產生 summary
        self._populate_summaries()
        return self

    def to_result(self) -> Dict[str, Any]:
        if self.root is None:
            raise RuntimeError("請先呼叫 fit() 再取結果。")

        nodes_records = []
        pivots: Dict[int, pd.DataFrame] = {}

        for node in self._nodes:
            rec = {
                "node_id": node.node_id,
                "depth": node.depth,
                "path": node.path,
                "amt_base": node.amt_base,
                "amt_comp": node.amt_comp,
                "delta_amt": node.delta_amt,
                "delta_share": node.delta_share,
                "split_dim": node.split_dim,
                "split_role": node.split_role,
                "split_policy": node.split_policy,
                "split_reason": node.split_reason,
                "split_score_hhi": node.split_score_hhi,
                "split_top1_gross_share": node.split_top1_gross_share,
                "split_top3_gross_share": node.split_top3_gross_share,
                "summary_zh": node.summary_zh,
            }
            nodes_records.append(rec)

            if node.pivot is not None:
                pivots[node.node_id] = node.pivot.copy()

        nodes_df = pd.DataFrame(nodes_records)
        return {
            "root": self.root,
            "nodes_df": nodes_df,
            "pivots": pivots,
            "dim_scores": {k: v.copy() for k, v in self._dim_scores.items()},
            "meta": dict(self._meta),
        }

    # --------------------------
    # 內部：建樹邏輯
    # --------------------------

    def _alloc_node_id(self) -> int:
        nid = self._next_node_id
        self._next_node_id += 1
        return nid

    def _build_node(
        self,
        df: pd.DataFrame,
        parent_node: DriverTreeNode,
        available_dims: List[str],
    ) -> None:
        if parent_node.depth >= self.max_depth:
            return
        if abs(parent_node.delta_share) < self.min_node_share:
            return

        df_sub = self._filter_by_path(df, parent_node.path)
        if df_sub.empty:
            return

        best_dim, best_pivot, pick_info = self._find_best_split_dim(
            node_id=parent_node.node_id,
            df_sub=df_sub,
            candidate_dims=available_dims,
        )
        if best_dim is None or best_pivot is None:
            return

        parent_node.split_dim = best_dim
        parent_node.pivot = best_pivot

        parent_node.split_role = pick_info.get("role")
        parent_node.split_policy = pick_info.get("policy")
        parent_node.split_reason = pick_info.get("reason")
        parent_node.split_score_hhi = pick_info.get("score_hhi")
        parent_node.split_top1_gross_share = pick_info.get("top1_gross_share")
        parent_node.split_top3_gross_share = pick_info.get("top3_gross_share")

        pivot = best_pivot.copy().sort_values("abs_delta", ascending=False)

        # ✅ 子節點用 abs_delta 排序，避免正負抵銷造成誤判
        top = pivot.head(self.top_k).copy()
        others = pivot.iloc[self.top_k:].copy()

        for cat, row in top.iterrows():
            amt_b = float(row["amt_base"])
            amt_c = float(row["amt_comp"])
            delta = float(row["delta_amt"])
            share = float(delta / self.global_delta_amt)

            child_node = DriverTreeNode(
                node_id=self._alloc_node_id(),
                depth=parent_node.depth + 1,
                path={**parent_node.path, best_dim: cat},
                amt_base=amt_b,
                amt_comp=amt_c,
                delta_amt=delta,
                delta_share=share,
            )
            parent_node.children.append(child_node)
            self._nodes.append(child_node)

            next_dims = [d for d in available_dims if d != best_dim]
            self._build_node(df=df, parent_node=child_node, available_dims=next_dims)

        if not others.empty:
            amt_b = float(others["amt_base"].sum())
            amt_c = float(others["amt_comp"].sum())
            delta = float(others["delta_amt"].sum())
            share = float(delta / self.global_delta_amt)

            child_node = DriverTreeNode(
                node_id=self._alloc_node_id(),
                depth=parent_node.depth + 1,
                path={**parent_node.path, best_dim: "其他"},
                amt_base=amt_b,
                amt_comp=amt_c,
                delta_amt=delta,
                delta_share=share,
            )
            parent_node.children.append(child_node)
            self._nodes.append(child_node)

            next_dims = [d for d in available_dims if d != best_dim]
            self._build_node(df=df, parent_node=child_node, available_dims=next_dims)

    def _filter_by_path(self, df: pd.DataFrame, path: Dict[str, Any]) -> pd.DataFrame:
        if not path:
            return df
        mask = pd.Series(True, index=df.index)
        for col, val in path.items():
            if val == "其他":
                continue
            mask &= (df[col] == val)
        return df[mask]

    # --------------------------
    # 核心：候選欄位評分 & 選欄位
    # --------------------------

    def _find_best_split_dim(
        self,
        node_id: int,
        df_sub: pd.DataFrame,
        candidate_dims: List[str],
    ) -> Tuple[Optional[str], Optional[pd.DataFrame], Dict[str, Any]]:
        scored_rows = []

        # 先把所有候選 dim 都算分數（科學依據靠這張表）
        for dim in candidate_dims:
            role = DIM_ROLE.get(dim)
            if role is None or role == "time":
                continue
            if dim not in df_sub.columns:
                continue

            pivot = self._pivot_change_by_dim(df_sub, dim)
            if pivot is None or pivot.empty:
                continue

            node_delta = float(pivot["delta_amt"].sum())
            gross_move = float(pivot["abs_delta"].sum())

            if gross_move <= 0:
                continue

            gross_share = pivot["gross_share_in_node"]
            score_hhi = float((gross_share ** 2).sum())  # 1/n ~ 1

            top1 = float(gross_share.max())
            top3 = float(pivot.sort_values("abs_delta", ascending=False).head(3)["abs_delta"].sum() / gross_move)

            n_cats = int(len(pivot))
            move_to_net_ratio = float(gross_move / (abs(node_delta) if node_delta != 0 else 1e-9))

            scored_rows.append({
                "dim": dim,
                "role": role,
                "n_cats": n_cats,
                "node_delta": node_delta,
                "gross_move": gross_move,
                "move_to_net_ratio": move_to_net_ratio,
                "top1_gross_share": top1,
                "top3_gross_share": top3,
                "score_hhi": score_hhi,     # ✅ 主分數（集中度）
            })

        if not scored_rows:
            self._dim_scores[node_id] = pd.DataFrame()
            return None, None, {}

        scores_df = pd.DataFrame(scored_rows)
        scores_df = scores_df.sort_values(
            ["score_hhi", "top1_gross_share", "top3_gross_share"],
            ascending=False
        ).reset_index(drop=True)

        self._dim_scores[node_id] = scores_df

        if self.split_policy == "best_overall":
            pick = scores_df.iloc[0]
            reason = (
                "policy=best_overall：所有候選欄位一起排名，"
                "以 HHI(移動量集中度) 最大者為主；tie-break 用 top1/top3。"
            )
        else:
            pick = None
            for role in ROLE_ORDER:
                sub = scores_df[scores_df["role"] == role]
                if not sub.empty:
                    pick = sub.iloc[0]
                    reason = (
                        f"policy=role_first：依 ROLE_ORDER 先遇到 role='{role}' 就停止往後比較；"
                        "於該 role 內挑 HHI 最大者。"
                    )
                    break
            if pick is None:
                pick = scores_df.iloc[0]
                reason = "policy=role_first：未能依 role 命中，退回 best_overall 第一名。"

        best_dim = str(pick["dim"])
        best_role = str(pick["role"])

        best_pivot = self._pivot_change_by_dim(df_sub, best_dim)

        info = {
            "policy": self.split_policy,
            "role": best_role,
            "reason": reason,
            "score_hhi": float(pick["score_hhi"]),
            "top1_gross_share": float(pick["top1_gross_share"]),
            "top3_gross_share": float(pick["top3_gross_share"]),
        }
        return best_dim, best_pivot, info

    def _pivot_change_by_dim(self, df_sub: pd.DataFrame, dim: str) -> Optional[pd.DataFrame]:
        if df_sub.empty:
            return None

        pivot = two_period_change_pivot(
            df=df_sub,
            dim=dim,
            value_col=self.target_col,
            time_col=self.time_col,
            base_period=self.base_period,
            comp_period=self.comp_period,
        )
        if pivot is None or pivot.empty:
            return None

        node_amt_base = float(pivot["amt_base"].sum())
        node_amt_comp = float(pivot["amt_comp"].sum())
        node_delta = float(pivot["delta_amt"].sum())

        pivot = pivot.copy()
        pivot["abs_delta"] = pivot["delta_amt"].abs()

        gross_move = float(pivot["abs_delta"].sum())
        if gross_move == 0:
            gross_move = 1e-9

        pivot["gross_share_in_node"] = pivot["abs_delta"] / gross_move
        pivot["net_share_in_node"] = pivot["delta_amt"] / (node_delta if node_delta != 0 else 1e-9)

        pivot["base_share"] = pivot["amt_base"] / (node_amt_base if node_amt_base != 0 else 1e-9)
        pivot["comp_share"] = pivot["amt_comp"] / (node_amt_comp if node_amt_comp != 0 else 1e-9)
        pivot["share_change_pp"] = (pivot["comp_share"] - pivot["base_share"]) * 100

        pivot["rank_abs_delta"] = pivot["abs_delta"].rank(method="dense", ascending=False).astype(int)
        return pivot

    # --------------------------
    # 中文摘要
    # --------------------------

    def _populate_summaries(self) -> None:
        for node in self._nodes:
            node.summary_zh = self._build_node_summary(node)
    def _build_node_summary(self, node: DriverTreeNode) -> str:
        """
        產生較易閱讀的多行中文摘要。

        結構說明：
        1. 先描述：在什麼條件下、Funding_Amt 從多少變到多少、增加/減少多少。
           - root 節點：描述「整體」並附上本次 Driver Tree 的參數設定。
           - 其他節點：描述該 path 條件下的變動與占整體的比例。
        2. 若有 split_dim：
           - 列出候選欄位的評分與前五名排名（根據 HHI、top1、top3）。
           - 說明本層選用的欄位與選擇原因。
           - 列出最有影響力的幾個類別（依 |delta| 排序），含移動量與淨貢獻。
        """
        path_str = self._format_path(node.path)
        amt_b = node.amt_base
        amt_c = node.amt_comp
        delta = node.delta_amt
        direction = "增加" if delta >= 0 else "減少"
        delta_abs = abs(delta)

        lines: List[str] = []

        # -------------------------
        # 1. 先寫「基礎敘述」
        # -------------------------
        if node.depth == 0:
            # root：整體變動概況
            lines.append(
                f"整體 Funding_Amt 從基準月（{self.base_period}）到比較月（{self.comp_period}），"
            )
            lines.append(
                f"由 {amt_b:,.0f} 變為 {amt_c:,.0f}，{direction} {delta_abs:,.0f}。"
            )
            lines.append("")  # 空行

            meta = self._meta or {}
            n_nodes = meta.get("n_nodes", len(self._nodes))
            max_depth_setting = meta.get("max_depth_setting", self.max_depth)
            min_node_share = meta.get("min_node_share", self.min_node_share)
            top_k = meta.get("top_k", self.top_k)
            split_policy = meta.get("split_policy", self.split_policy)

            lines.append("本次 Driver Tree 設定：")
            lines.append(f"- 節點數：{n_nodes} 個")
            lines.append(f"- max_depth：{max_depth_setting}")
            lines.append(f"- min_node_share：{min_node_share}")
            lines.append(f"- top_k：{top_k}")
            lines.append(f"- split_policy：{split_policy}")
            lines.append("")  # 空行

        else:
            # 非 root：該路徑下的局部變動概況
            share_global = node.delta_share * 100
            lines.append(
                f"在條件 {path_str} 下，從基準月（{self.base_period}）到比較月（{self.comp_period}），"
            )
            lines.append(
                f"Funding_Amt 由 {amt_b:,.0f} 變為 {amt_c:,.0f}，"
                f"{direction} {delta_abs:,.0f}，約占整體變動的 {share_global:.1f}%。"
            )
            lines.append("")  # 空行

        # 若沒有 split_dim / pivot（葉節點），到此為止
        if node.split_dim is None or node.pivot is None:
            return "\n".join(lines)

        # -------------------------
        # 2. 候選欄位分數與排名
        # -------------------------
        scores_df = self._dim_scores.get(node.node_id)
        if scores_df is not None and not scores_df.empty:
            lines.append("候選欄位分數與排名：")
            lines.append(f"- 總數：{len(scores_df)} 個")
            lines.append("- 評分方式：HHI（以 |delta| 移動量占比平方和，越大代表集中度越高）")

            top_dims = scores_df.head(5)
            if not top_dims.empty:
                lines.append("前五名欄位（依 HHI 排序）：")
                for i, r in top_dims.iterrows():
                    dim = r["dim"]
                    role = r["role"]
                    hhi = r["score_hhi"]
                    top1 = r["top1_gross_share"] * 100
                    top3 = r["top3_gross_share"] * 100
                    lines.append(
                        f"  {i+1}) {dim}（role={role}） - "
                        f"HHI={hhi:.3f}，top1={top1:.1f}% ，top3={top3:.1f}%"
                    )
            else:
                lines.append("（無有效候選欄位。）")

            lines.append("")  # 空行
        else:
            lines.append("候選欄位評分：無可用評分資料（可能為上游資料或 pivot 函式異常）。")
            lines.append("")  # 空行

        # -------------------------
        # 3. 本層選用欄位與理由
        # -------------------------
        if node.split_score_hhi is not None:
            hhi_str = f"{node.split_score_hhi:.3f}"
        else:
            hhi_str = "N/A"

        if node.split_top1_gross_share is not None:
            top1_str = f"{node.split_top1_gross_share*100:.1f}%"
        else:
            top1_str = "N/A"

        if node.split_top3_gross_share is not None:
            top3_str = f"{node.split_top3_gross_share*100:.1f}%"
        else:
            top3_str = "N/A"

        lines.append("本層選用欄位：")
        lines.append(f"- 使用欄位：{node.split_dim}（role={node.split_role}）")
        lines.append(f"- HHI：{hhi_str}")
        lines.append(f"- 最大類別移動量占比：{top1_str}")
        lines.append(f"- 前三大類別移動量占比：{top3_str}")
        if node.split_reason:
            lines.append(f"- 選擇原因：{node.split_reason}")
        lines.append("")  # 空行

        # -------------------------
        # 4. 影響最大細項（依 |delta| 排序）
        # -------------------------
        pv = node.pivot.copy().sort_values("abs_delta", ascending=False)
        top = pv.head(3)

        lines.append("影響最大細項（依移動量 |delta| 排序）：")
        node_delta = node.delta_amt if node.delta_amt != 0 else 1e-9

        detail_exist = False
        for idx, row in top.iterrows():
            d = float(row["delta_amt"])
            if d == 0:
                continue
            detail_exist = True

            dir2 = "增加" if d >= 0 else "減少"
            d_abs = abs(d)
            gross_share = float(row["gross_share_in_node"] * 100)
            net_share = float((d / node_delta) * 100)  # 可能 >100%，代表有抵銷

            lines.append(
                f"- {node.split_dim} = {idx}：{dir2} {d_abs:,.0f} "
                f"（移動量 {gross_share:.1f}%｜淨貢獻 {net_share:.1f}%）"
            )

        if not detail_exist:
            lines.append("- （此欄位底下各類別的 delta 幾乎為 0。）")

        lines.append("")  # 空行
        lines.append("註：『淨貢獻』可以超過 100%，代表其他類別有反向抵銷。")

        return "\n".join(lines)

    def _format_path(self, path: Dict[str, Any]) -> str:
        if not path:
            return "【全體】"
        return "、".join([f"{k} = {v}" for k, v in path.items()])


# ------------------------------------------------------------
# 四、外部方便呼叫的包裝函式
# ------------------------------------------------------------

def run_driver_tree_change(
    df: pd.DataFrame,
    base_period: Any,
    comp_period: Any,
    dims: Optional[List[str]] = None,
    target_col: str = "Funding_Amt",
    time_col: str = "Funding_Date_yymm",
    max_depth: int = 3,
    min_node_share: float = 0.05,
    top_k: int = 5,
    split_policy: str = "best_overall",
) -> Dict[str, Any]:
    tree = DriverTree(
        max_depth=max_depth,
        min_node_share=min_node_share,
        top_k=top_k,
        split_policy=split_policy,
    )
    tree.fit(
        df=df,
        base_period=base_period,
        comp_period=comp_period,
        dims=dims,
        target_col=target_col,
        time_col=time_col,
    )
    return tree.to_result()
