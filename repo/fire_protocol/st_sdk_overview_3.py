# # app.py
# import streamlit as st
# import pandas as pd

# import AX_PY_SDK_3 as sdk
# import task_library as tl

# import logging
# st.set_option("client.showErrorDetails", False)
# for name in ("streamlit", "streamlit.dataframe_util", "pyarrow"):
#     logging.getLogger(name).setLevel(logging.ERROR)



# st.set_page_config(page_title="Robots Dashboard", layout="wide")
# # Auto-refresh every 5 seconds (adjust as needed)
# # from streamlit_autorefresh import st_autorefresh  # if you use the external helper
# # st_autorefresh(interval=5000, key="status_refresh")
# # Or native:
# # st.experimental_rerun  # not needed here unless you wire a timer; autorefresh package is cleaner

# # --- Auth gate (blocks page until unlocked) ---
# import os, hashlib
# import streamlit as st
# import streamlit.components.v1 as components

# # def _sha256(s: str) -> str:
# #     return hashlib.sha256(s.encode("utf-8")).hexdigest()

# # def require_auth():
# #     # already unlocked in this server session?
# #     if st.session_state.get("auth_ok"):
# #         return

# #     # unlock if ?auth=1 present (persists across refreshes)
# #     try:
# #         qp = st.experimental_get_query_params()
# #         if qp.get("auth", ["0"])[0] == "1":
# #             st.session_state.auth_ok = True
# #             return
# #     except Exception:
# #         pass

# #     # password hash from env (prefer hash)
# #     pw_hash_env = os.getenv("DASH_PW_SHA256")
# #     if not pw_hash_env:
# #         pw_plain = os.getenv("DASH_PW", "ef-ax-sdk-ahmed")
# #         pw_hash_env = _sha256(pw_plain)

# #     # blocking UI (form prevents extra reruns)
# #     gate = st.empty()
# #     with gate.container():
# #         st.markdown("### Authentication required")
# #         with st.form("auth_form", clear_on_submit=True):
# #             pw = st.text_input("Password", type="password")
# #             submitted = st.form_submit_button("Unlock", use_container_width=True)

# #         if submitted:
# #             if _sha256(pw or "") == pw_hash_env:
# #                 # 1) mark unlocked for this session
# #                 st.session_state.auth_ok = True
# #                 # 2) persist across refresh: set query param server-side
# #                 try:
# #                     st.experimental_set_query_params(auth="1")
# #                 except Exception:
# #                     pass
# #                 # 3) optional: mirror to browser sessionStorage (no redirect!)
# #                 components.html(
# #                     "<script>try{sessionStorage.setItem('dash_auth_ok','1');}catch(e){}</script>",
# #                     height=0,
# #                 )
# #                 # 4) clean rerun — no extra clicks
# #                 st.rerun()
# #             else:
# #                 st.error("Wrong password.")

# #         # hard-stop to block rest of the app until unlocked
# #         st.stop()

# import os

# APP_PASSWORD = os.environ.get("APP_PASSWORD", "ef-ax-sdk-ahmed")

# def require_auth():
#     # already authed → show a tiny badge and return
#     if st.session_state.get("authed") is True:
#         st.sidebar.success("🔓 Unlocked")
#         return

#     # block the app with a lightweight form
#     st.title("Authentication required")
#     with st.form("auth_form", clear_on_submit=True):
#         pwd = st.text_input("Password", type="password")
#         ok  = st.form_submit_button("Unlock")
#     if ok:
#         if APP_PASSWORD and pwd == APP_PASSWORD:
#             st.session_state.authed = True
#             st.rerun()  # immediately restart in authed state
#         else:
#             st.error("Wrong password")
#     st.stop()  # nothing else in the app runs until authed


# # Call BEFORE rendering anything else
# require_auth()
# def _do_logout():
#     # clear auth + anything sensitive you want
#     for k in ("authed", "auth_form", "auth_pwd", "auth_ts"):
#         st.session_state.pop(k, None)
#     # optional: clear caches & selections
#     try:
#         st.cache_data.clear()
#     except Exception:
#         pass
#     st.session_state.pop("selected_robot_ids", None)
#     st.session_state.pop("confirm_payload", None)
#     st.session_state.pop("robots_source", None)
#     st.rerun()  # ← critical: jump back to the auth gate now

# st.sidebar.button("Log out", key="logout_btn", use_container_width=True, on_click=_do_logout)



# # --- tiny CSS tweaks ---
# st.markdown("""
# <style>
# .active-robot { font-size: 1.05rem; font-weight: 600; }
# .robot-pill { padding: 2px 8px; border-radius: 6px; background: #262730; margin-right: 6px; }
# .robot-pill b { color: #e6e6e6; }
# </style>
# """, unsafe_allow_html=True)

# # =========================================================
# # Helpers
# # =========================================================

# # --- Map scatter for selected robots + POIs of monitored robot ---
# import math
# # import matplotlib.pyplot as plt

# def _yaw_to_rad(yaw):
#     try:
#         y = float(yaw)
#     except Exception:
#         return 0.0
#     # Heuristic: if magnitude > ~2π, assume degrees
#     return math.radians(y) if abs(y) > 6.3 else y

# import math, textwrap
# import matplotlib.pyplot as plt

# def validate_same_area(selected_robot_ids):
#     """Return (all_same, common_area, areas_by_robot). `None` areaIds are treated as distinct."""
#     areas = {}
#     for rid in selected_robot_ids or []:
#         try:
#             areas[rid] = getattr(sdk.Robot(rid).df, "areaId", None)
#         except Exception:
#             areas[rid] = None
#     uniq = {a for a in areas.values()}
#     all_same = len(uniq) <= 1
#     common = next(iter(uniq)) if all_same else None
#     return all_same, common, areas


# def plot_selected_robots_and_pois(selected_robot_ids, monitored_robot, keep_equal_scale=True):
#     # 1) Collect robots' current positions + yaw
#     robots_pts = []
#     for rid in selected_robot_ids or []:
#         try:
#             r = sdk.Robot(rid)
#             x, y = r.get_curr_pos()  # (x, y)
#             # Prefer r.df.yaw if present; otherwise try from status
#             yaw = getattr(getattr(r, "df", None), "yaw", None)
#             if yaw is None:
#                 try:
#                     st_df = r.get_status()
#                     if isinstance(st_df, pd.DataFrame):
#                         # try common keys
#                         for cand in ["yaw", "theta", "heading"]:
#                             if cand in st_df.columns:
#                                 yaw = st_df[cand].iloc[-1]
#                                 break
#                             if "key" in st_df.columns:
#                                 # key/value style
#                                 sub = st_df[st_df["key"].astype(str).str.lower().eq(cand)]
#                                 if not sub.empty:
#                                     # pick last non-null in a likely value column
#                                     for vcol in ["value","val","data","status","message"]:
#                                         if vcol in sub.columns and sub[vcol].notna().any():
#                                             yaw = sub[vcol].dropna().iloc[-1]
#                                             break
#                                     if yaw is not None:
#                                         break
#                 except Exception:
#                     pass
#             yaw = _yaw_to_rad(yaw if yaw is not None else 0.0)
#             robots_pts.append({"rid": rid, "x": float(x), "y": float(y), "yaw": yaw})
#         except Exception:
#             continue

#     # 2) Collect POIs from the monitored robot
#     pois_pts = []
#     try:
#         pois_df = monitored_robot.get_pois()
#         if isinstance(pois_df, pd.DataFrame) and not pois_df.empty:
#             for _, row in pois_df.iterrows():
#                 try:
#                     coord = row.get("coordinate", None)
#                     if isinstance(coord, (list, tuple)) and len(coord) >= 2:
#                         px, py = float(coord[0]), float(coord[1])
#                         pois_pts.append({"name": str(row.get("name", "")), "x": px, "y": py})
#                 except Exception:
#                     continue
#     except Exception:
#         pass

#     # 3) Plot
#     fig, ax = plt.subplots(figsize=(9, 7), dpi=140)  # bigger canvas

#     # POIs (green with shorter labels)
#     if pois_pts:
#         ax.scatter([p["x"] for p in pois_pts], [p["y"] for p in pois_pts],
#                    c="green", s=20, marker="o", label="POIs")
#         for p in pois_pts:
#             name = p["name"]
#             # shorten long labels so they don't spill outside
#             name = textwrap.shorten(name, width=26, placeholder="…")
#             ax.annotate(name, (p["x"], p["y"]),
#                         xytext=(3, 3), textcoords="offset points",
#                         fontsize=8, color="green", clip_on=False)  # <-- no clip

#     # Robots (red triangles + heading arrow + id suffix)
#     arrow_len = 0.6
#     if robots_pts:
#         ax.scatter([r["x"] for r in robots_pts], [r["y"] for r in robots_pts],
#                    c="red", s=50, marker="^", label="Robots")
#         for r in robots_pts:
#             dx = arrow_len * math.cos(r["yaw"])
#             dy = arrow_len * math.sin(r["yaw"])
#             ax.quiver(r["x"], r["y"], dx, dy, angles="xy",
#                       scale_units="xy", scale=1, color="red", width=0.004)
#             ax.annotate(f"…{r['rid'][-4:]}", (r["x"], r["y"]),
#                         xytext=(4, -10), textcoords="offset points",
#                         fontsize=9, color="red", clip_on=False)  # <-- no clip

#     # Dynamic padding so labels fit
#     xs = [p["x"] for p in pois_pts] + [r["x"] for r in robots_pts]
#     ys = [p["y"] for p in pois_pts] + [r["y"] for r in robots_pts]
#     if xs and ys:
#         x0, x1 = min(xs), max(xs)
#         y0, y1 = min(ys), max(ys)
#         pad_x = max(1.0, 0.10 * (x1 - x0))  # 10% or at least 1 unit
#         pad_y = max(1.0, 0.15 * (y1 - y0))  # 15% or at least 1 unit
#         ax.set_xlim(x0 - pad_x, x1 + pad_x)
#         ax.set_ylim(y0 - pad_y, y1 + pad_y)

#     ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.5)
#     ax.set_title("Robots & POIs (map view)")
#     ax.legend(loc="best")

#     if keep_equal_scale:
#         ax.set_aspect("equal", adjustable="datalim")
#     else:
#         ax.set_aspect("auto")  # gives more room if your data is very tall/wide

#     plt.tight_layout(pad=0.6)   # <-- fit inside figure frame
#     st.pyplot(fig, clear_figure=True)


# import re

# def _kv_status_to_wide(df: pd.DataFrame) -> pd.DataFrame:
#     """
#     Convert key/value style status into a single-row wide frame.
#     Looks for a 'key' column and picks a plausible value column.
#     """
#     if "key" not in df.columns:
#         return df

#     # pick first reasonable value column
#     candidates = [c for c in ["value","val","data","status","message"] if c in df.columns]
#     if not candidates:
#         # fallback: any non-'key' column; if multiple, try the last (often the actual value)
#         other = [c for c in df.columns if c != "key"]
#         if not other:
#             return df
#         value_col = other[-1]
#     else:
#         value_col = candidates[0]

#     wide = df[["key", value_col]].copy()
#     wide.columns = ["key", "value"]
#     # unique keys only (last wins)
#     wide = wide.dropna(subset=["key"]).drop_duplicates(subset=["key"], keep="last")
#     wide = wide.set_index("key").T
#     # sanitize column names
#     wide.columns = [str(c) for c in wide.columns]
#     return wide

# def _append_status_history(robot_id: str, status_df: pd.DataFrame):
#     """
#     Normalize to wide single row, add timestamp, append to per-robot history in session_state.
#     """
#     # normalize
#     if "key" in status_df.columns:
#         row = _kv_status_to_wide(status_df)
#     else:
#         row = status_df.copy()
#         # If multiple rows, prefer last one
#         if len(row) > 1:
#             row = row.tail(1)
#     # single row guard
#     if len(row) != 1:
#         row = row.head(1)

#     row = row.copy()
#     row["ts"] = pd.Timestamp.utcnow()

#     store = st.session_state.setdefault("status_history", {})
#     hist = store.get(robot_id)
#     if hist is None or not isinstance(hist, pd.DataFrame):
#         hist = row
#     else:
#         hist = pd.concat([hist, row], ignore_index=True)

#     # keep only last N points
#     max_points = st.session_state.get("status_history_max_points", 600)
#     if len(hist) > max_points:
#         hist = hist.tail(max_points)

#     store[robot_id] = hist

# def _pick_col(df: pd.DataFrame, candidates) -> str | None:
#     """Return the first existing column from candidates (case-insensitive)."""
#     if df is None or df.empty:
#         return None
#     cols_l = {c.lower(): c for c in df.columns}
#     for pat in candidates:
#         # allow exact or substring (e.g., 'battery' in 'batteryPercent')
#         for lc, real in cols_l.items():
#             if lc == pat.lower() or pat.lower() in lc:
#                 return real
#     return None

# def _to_float_series(s):
#     try:
#         return pd.to_numeric(s, errors="coerce")
#     except Exception:
#         return pd.Series([pd.NA]*len(s), index=s.index)


# # --- Custom task helpers ---
# def _build_action_from_cfg(kind: str, cfg: dict):
#     # uses task_library helpers
#     if kind == "open_door":
#         return tl.act_open_doors(cfg.get("door_ids", [1,2,3,4]), cfg.get("mode", 1))
#     if kind == "close_door":
#         return tl.act_close_doors(cfg.get("door_ids", [1,2,3,4]), cfg.get("mode", 1))
#     if kind == "pause":
#         return tl.act_pause(int(cfg.get("pause_s", 5)))
#     if kind == "wait_interaction":
#         return tl.act_wait()
#     if kind == "lift_up":
#         return tl.act_lift_up(cfg.get("useAreaId") or None)
#     if kind == "lift_down":
#         return tl.act_lift_down(cfg.get("useAreaId") or None)
#     return None  # ignore unknown

# def _resolve_step_for_robot(robot_id: str, step: dict):
#     ...
#     if step.get("source") == "POI":
#         poi_name = step.get("poiName")
#         meta = _poi_details_for(robot_id, poi_name) if poi_name else None
#         if not meta:
#             raise RuntimeError(f"POI '{poi_name}' not found for robot {robot_id}")
#         x, y, yaw, areaId = meta["x"], meta["y"], meta.get("yaw", 0.0), meta["areaId"]
#         name  = meta.get("poiName", poi_name)
#         poiId = meta.get("poiId", poiId)
#         ptype = meta.get("type")
#     else:
#         ...
#         ptype = None

#     ...
#     return {
#         "x": x, "y": y, "yaw": yaw, "areaId": areaId,
#         "name": name, "poiId": poiId, "stopRadius": stopRadius,
#         "acts": acts, "type": ptype               # <-- new
#     }



# from functools import lru_cache
# try:
#     from googletrans import Translator
# except Exception:
#     Translator = None

# @st.cache_resource(show_spinner=False)
# def _translator():
#     return Translator() if Translator else None

# @lru_cache(maxsize=2048)
# def _translate_model_zh_to_en(text: str) -> str:
#     if not text:
#         return ""
#     # if it already has ASCII, don't translate
#     if any(ch.isascii() for ch in str(text)):
#         return str(text)
#     tr = _translator()
#     if not tr:
#         return str(text)
#     try:
#         return tr.translate(str(text), src="zh-cn", dest="en").text
#     except Exception:
#         # network issues / quota / parser changes → fall back to original
#         return str(text)


# # ---- POI type mapping (int -> label) ----
# POI_TYPE_MAP = {
#     9:  "Charging Pile",
#     10: "Standby Point",
#     11: "Table Number",
#     12: "Private Room",
#     16: "Lobby",
#     19: "Reception Desk",
#     21: "Room Number",
#     22: "Workstation Number",
#     25: "Waypoint",
#     26: "Disinfection Point",
#     27: "Exchange Point",
#     28: "Elevator Waiting Point",
#     29: "Scheduling Point",
#     30: "Distribution Station",
#     34: "Shelf Point",
# }

# def format_poi_types(df: pd.DataFrame) -> pd.DataFrame:
#     if not isinstance(df, pd.DataFrame) or df.empty:
#         return df
#     out = df.copy()
#     if "type" in out.columns:
#         out["type_raw"] = pd.to_numeric(out["type"], errors="coerce").astype("Int64")
#         out["type_label"] = out["type_raw"].map(POI_TYPE_MAP).fillna(out["type_raw"].astype(str))
#         # Optional: hide or drop 'type' to avoid mixed dtype issues
#         # out.drop(columns=["type"], inplace=True)

#     # Sanitize other object columns (lists/dicts) → strings
#     for c in out.columns:
#         if out[c].dtype == "object":
#             out[c] = out[c].apply(
#                 lambda v: v if isinstance(v, (str, type(None)))
#                 else (", ".join(map(str, v)) if isinstance(v, (list, tuple, set)) else str(v))
#             )
#     return out


# @st.cache_data(show_spinner=False)
# def list_robot_poi_names(robot_id: str):
#     try:
#         df = sdk.Robot(robot_id).get_pois()
#         if isinstance(df, pd.DataFrame) and not df.empty and "name" in df.columns:
#             return sorted([str(n) for n in df["name"].dropna().unique().tolist()])
#     except Exception:
#         pass
#     return []

# @st.cache_data(show_spinner=False)
# def common_poi_names(robot_ids: list[str]):
#     """Intersection of POI names across robots. Empty list if none/unknown."""
#     if not robot_ids:
#         return []
#     base = None
#     for rid in robot_ids:
#         names = set(list_robot_poi_names(rid))
#         if base is None:
#             base = names
#         else:
#             base &= names
#         if not base:
#             break
#     return sorted(base or [])

# def _poi_details_for(robot_id: str, poi_name: str):
#     try:
#         d = sdk.Robot(robot_id).get_poi_details(poi_name)
#         if not isinstance(d, dict):
#             return None
#         coord = d.get("coordinate") or [None, None]
#         return {
#             "areaId": d.get("areaId"),
#             "x": coord[0],
#             "y": coord[1],
#             "yaw": d.get("yaw", 0),
#             "poiId": d.get("id"),
#             "poiName": d.get("name", poi_name),
#             "type": d.get("type"),   # <-- add this
#         }
#     except Exception:
#         return None


# # =========================================================
# # Cache
# # =========================================================
# @st.cache_data(show_spinner=False)
# def load_businesses():
#     df = sdk.get_business()
#     if not isinstance(df, pd.DataFrame) or df.empty:
#         return pd.DataFrame(columns=["id", "name"])
#     return df[["id", "name"]].dropna().drop_duplicates()

# @st.cache_data(show_spinner=False)
# def load_robots():
#     df = sdk.get_robots()
#     if not isinstance(df, pd.DataFrame) or df.empty:
#         return pd.DataFrame(columns=["robotId","businessId","areaId","x","y","model","isOnLine","business_name"])
#     # translate unique models only (via the lru_cache)
#     df["model"] = df["model"].astype(str)
#     df["model_en"] = df["model"].map(_translate_model_zh_to_en)
#     return df


# @st.cache_data(show_spinner=False)
# def load_online_robots():
#     try:
#         df = sdk.get_online_robots()
#         return df if isinstance(df, pd.DataFrame) else pd.DataFrame()
#     except Exception:
#         return pd.DataFrame()

# @st.cache_data(show_spinner=False)
# def load_ef_robots():
#     try:
#         df = sdk.get_ef_robots()
#         return df if isinstance(df, pd.DataFrame) else pd.DataFrame()
#     except Exception:
#         return pd.DataFrame()

# # =========================================================
# # Table helper
# # =========================================================
# def with_online_icons(df: pd.DataFrame) -> pd.DataFrame:
#     if "isOnLine" in df.columns:
#         df = df.copy()
#         df["isOnLine"] = df["isOnLine"].map(lambda v: "✅" if bool(v) else "❌")
#     return df

# def df_toggles_and_table(
#     name: str,
#     df: pd.DataFrame,
#     pref_cols,
#     default_checked: dict,
#     key_prefix: str,
#     selectable: bool = False
# ):
#     if df is None or df.empty:
#         st.info(f"No rows in **{name}**.")
#         return []

#     cols = [c for c in pref_cols if c in df.columns] or list(df.columns)

#     st.write(f"**{name}** – columns")
#     checks, row = {}, st.columns(min(len(cols), 8))
#     for i, c in enumerate(cols):
#         if i % 8 == 0 and i > 0:
#             row = st.columns(min(len(cols) - i, 8))
#         col = row[i % 8]
#         def_val = bool(default_checked.get(c, True))
#         checks[c] = col.checkbox(c, value=def_val, key=f"{key_prefix}_col_{c}")

#     shown = [c for c in cols if checks.get(c)]
#     if not shown:
#         st.warning("All columns hidden.")
#         return []

#     table_df = with_online_icons(df[shown])
#     st.dataframe(table_df, hide_index=True, use_container_width=True)
#     return []

# # =========================================================
# # Session
# # =========================================================
# if "saved_tasks" not in st.session_state:
#     st.session_state.saved_tasks = {}
# if "confirm_payload" not in st.session_state:
#     st.session_state.confirm_payload = None
# # Default to EF robots (fallback to all if EF list is empty)
# if "robots_source" not in st.session_state:
#     ef = load_ef_robots()
#     st.session_state.robots_source = "ef" if (isinstance(ef, pd.DataFrame) and not ef.empty) else "all"
# if "selected_robot_ids" not in st.session_state:
#     st.session_state.selected_robot_ids = []

# # =========================================================
# # Data
# # =========================================================
# business_df = load_businesses()
# robots_all   = load_robots()
# robots_online = load_online_robots()
# robots_ef     = load_ef_robots()

# # =========================================================
# # Sidebar
# # =========================================================
# st.sidebar.header("Pickers")

# # source toggles
# if st.sidebar.button("Use Online Robots as main list", use_container_width=True):
#     st.session_state.robots_source = "online"
# if st.sidebar.button("Use EF Robots as main list", use_container_width=True):
#     st.session_state.robots_source = "ef"
# if st.sidebar.button("Reset to All Robots", use_container_width=True):
#     st.session_state.robots_source = "all"

# if st.sidebar.button("Refresh caches", use_container_width=True):
#     load_businesses.clear(); load_robots.clear(); load_online_robots.clear(); load_ef_robots.clear()
#     st.rerun()

# # choose main robots df
# if st.session_state.robots_source == "online":
#     robots_df = robots_online if not robots_online.empty else robots_all
# elif st.session_state.robots_source == "ef":
#     robots_df = robots_ef if not robots_ef.empty else robots_all
# else:
#     robots_df = robots_all

# st.title("Robot Control & Telemetry")

# # Business dropdown (searchable)
# biz_options = ["— All businesses —"] + business_df["name"].sort_values().unique().tolist()
# selected_business = st.sidebar.selectbox("Business", biz_options, index=0, key="business_picker")

# # Filter robots by business
# if selected_business != "— All businesses —":
#     allowed_ids = set(business_df.loc[business_df["name"] == selected_business, "id"])
#     robots_scoped = robots_df[robots_df["businessId"].isin(allowed_ids)]
# else:
#     robots_scoped = robots_df


# # Build options as strings
# robot_id_options = (
#     robots_scoped["robotId"]
#     .dropna()
#     .astype(str)
#     .sort_values()
#     .unique()
#     .tolist()
# )

# # Sanitize session defaults to the current options
# prev_sel = [str(x) for x in st.session_state.get("selected_robot_ids", [])]
# valid_defaults = [x for x in prev_sel if x in robot_id_options]

# # If nothing survives, pick a safe fallback (or [])
# if not valid_defaults and robot_id_options:
#     # choose first N as a sensible default
#     valid_defaults = robot_id_options[:1]   # or :3 if you like

# # Now render the widget safely
# selected_robot_ids = st.sidebar.multiselect(
#     "Robots (multi-select)",
#     options=robot_id_options,
#     default=valid_defaults,
#     key="selected_robot_ids",
# )



# # =========================================================
# # Main robots table (display only)
# # =========================================================
# ROBOT_DEFAULTS = {
#     "robotId": True, "business_name": True, "model": True, "isOnLine": True,
#     "areaId": False, "x": False, "y": False,
# }
# robot_pref_cols = ["robotId","business_name","model","isOnLine","areaId","x","y"]

# df_toggles_and_table(
#     "Business Robots (filtered)",
#     robots_scoped.reset_index(drop=True),
#     pref_cols=robot_pref_cols,
#     default_checked=ROBOT_DEFAULTS,
#     key_prefix="mainrobots",
#     selectable=False
# )

# # =========================================================
# # Tabs: Monitoring / Tasking
# # =========================================================
# tab_mon, tab_task = st.tabs(["Monitoring", "Tasking"])

# with tab_mon:
#     if not selected_robot_ids:
#         st.info("Pick at least one robot in the sidebar.")
#     else:
#         # selected_robot_ids = list from sidebar

#         monitor_choice = st.radio(
#             "Monitor robot:",
#             options=selected_robot_ids,
#             index=0,
#             horizontal=True,
#             key="monitor_robot_choice"
#         )

#         # Build the Robot instance to monitor
#         try:
#             robot = sdk.Robot(monitor_choice)
#         except Exception as e:
#             st.error(f"Failed to initialize Robot('{monitor_choice}'): {e}")
#             robot = None

#         if robot:
#             # header: active robot + quick facts
#             biz = getattr(robot.df, "business_name", "") or ""
#             model_raw = getattr(robot.df, "model", "") or ""
#             model_en  = _translate_model_zh_to_en(model_raw)
#             online_badge = "✅ Online" if bool(getattr(robot.df, "isOnLine", False)) else "❌ Offline"

#             st.markdown(
#                 f'<div class="active-robot">Active robot: <code>{robot.SN}</code></div>'
#                 f'<div style="margin-top:6px;">'
#                 f'  <span class="robot-pill"><b>Business:</b> {biz}</span>'
#                 f'  <span class="robot-pill"><b>Model:</b> {model_en or model_raw}</span>'
#                 f'  <span class="robot-pill"><b>Status:</b> {online_badge}</span>'
#                 f'</div>',
#                 unsafe_allow_html=True
#             )
#             # robot = monitored sdk.Robot chosen in Monitoring tab

#             all_same, common_area, areas_map = validate_same_area(selected_robot_ids)

#             if not all_same:
#                 # Option A: only plot robots that match the monitored robot’s map
#                 mon_area = getattr(getattr(robot, "df", None), "areaId", None)
#                 same_area_ids = [rid for rid, a in areas_map.items() if a == mon_area]

#                 if not same_area_ids:
#                     st.error(
#                         "Selected robots span multiple maps (areaId mismatch) "
#                         f"and none match monitored robot’s area {mon_area!r}. Skipping map plot."
#                     )
#                 else:
#                     st.warning(
#                         "Robots are on different maps. Plotting only those in area "
#                         f"{mon_area!r}: {', '.join('…'+rid[-4:] for rid in same_area_ids)}"
#                     )
#                     plot_selected_robots_and_pois(same_area_ids, robot)

#             else:
#                 # All good — everyone shares the same area
#                 plot_selected_robots_and_pois(selected_robot_ids, robot)


#             # # Status
#             # try:
#             #     status_df = robot.get_status()
#             #     status_df["key"] = status_df.index
#             #     if isinstance(status_df, pd.DataFrame) and not status_df.empty:
#             #         df_toggles_and_table(
#             #             "Live Status",
#             #             status_df,
#             #             pref_cols=list(status_df.columns),
#             #             default_checked={c: True for c in status_df.columns},
#             #             key_prefix="status",
#             #             selectable=False
#             #         )
#             #     else:
#             #         st.warning("Robot is offline or no status available.")
#             # except Exception as e:
#             #     st.error(f"Error fetching status: {e}")

#             # Status + logging + charts
#             try:
#                 status_df = robot.get_status()
#                 if isinstance(status_df, pd.DataFrame) and not status_df.empty:
#                     # If you’re creating key column elsewhere, OK; otherwise this is safe:
#                     if "key" not in status_df.columns:
#                         status_df["key"] = status_df.index

#                     # --- toggle logging
#                     rec_col1, rec_col2 = st.columns([1,3])
#                     with rec_col1:
#                         record = st.checkbox("Record status", value=True, key=f"log_status_{robot.SN}")
#                     with rec_col2:
#                         st.caption("When enabled, each rerun appends one sample to the history buffer.")

#                     if record:
#                         _append_status_history(robot.SN, status_df)

#                     # show current status table (as you already do)
#                     df_toggles_and_table(
#                         "Live Status",
#                         status_df,
#                         pref_cols=list(status_df.columns),
#                         default_checked={c: True for c in status_df.columns},
#                         key_prefix="status",
#                         selectable=False
#                     )

#                     # ----- charts from history -----
#                     hist = st.session_state.get("status_history", {}).get(robot.SN)
#                     if isinstance(hist, pd.DataFrame) and not hist.empty and "ts" in hist.columns:
#                         st.subheader("Trends")

#                         # set ts index for charts
#                         h = hist.copy()
#                         h = h.sort_values("ts").set_index("ts")

#                         # Try to find common signals
#                         col_batt = _pick_col(h, ["batteryPercent","battery","electricQuantity","power","batteryLevel"])
#                         col_charge = _pick_col(h, ["isCharging","charging","chargeState"])
#                         col_speed = _pick_col(h, ["speed","velocity","linearSpeed","linear_speed"])
#                         col_x = _pick_col(h, ["x","pos_x","pose_x"])
#                         col_y = _pick_col(h, ["y","pos_y","pose_y"])
#                         col_yaw = _pick_col(h, ["yaw","theta","heading"])

#                         charts = []

#                         if col_batt and col_batt in h.columns:
#                             s = _to_float_series(h[col_batt])
#                             st.line_chart(s, height=160, use_container_width=True)
#                             st.caption(f"Battery over time ({col_batt})")

#                         if col_charge and col_charge in h.columns:
#                             # coerce to 0/1 for plotting
#                             ch = h[col_charge].astype(str).str.lower().str.replace(r"[^a-z0-9\-\.]", "", regex=True)
#                             ch = ch.map({"true":1, "1":1, "charging":1}).fillna(0)
#                             st.line_chart(ch, height=140, use_container_width=True)
#                             st.caption(f"Charging state over time (1=charging) [{col_charge}]")

#                         if col_speed and col_speed in h.columns:
#                             s = _to_float_series(h[col_speed])
#                             st.line_chart(s, height=160, use_container_width=True)
#                             st.caption(f"Speed over time ({col_speed})")

#                         if col_x and col_y and col_x in h.columns and col_y in h.columns:
#                             xy = pd.DataFrame({"x": _to_float_series(h[col_x]), "y": _to_float_series(h[col_y])}, index=h.index)
#                             st.line_chart(xy, height=200, use_container_width=True)
#                             st.caption(f"Position (x/y) over time ({col_x}, {col_y})")

#                         if col_yaw and col_yaw in h.columns:
#                             s = _to_float_series(h[col_yaw])
#                             st.line_chart(s, height=160, use_container_width=True)
#                             st.caption(f"Yaw/Heading over time ({col_yaw})")

#                         if not any([col_batt, col_charge, col_speed, (col_x and col_y), col_yaw]):
#                             st.info("No typical numeric fields detected (battery/speed/pose). Check your status schema.")
#                     else:
#                         st.info("No history yet. Enable “Record status” and let the page rerun a few times.")
#                 else:
#                     st.warning("Robot is offline or no status available.")
#             except Exception as e:
#                 st.error(f"Error fetching status: {e}")


#             # Map
#             st.caption("Map Image")
#             try:
#                 img = robot.get_map_image()
#                 if hasattr(img, "size"):
#                     st.image(img, use_column_width=True)
#                 else:
#                     st.write(img if img else "No image returned.")
#             except Exception as e:
#                 st.error(f"Error fetching map image: {e}")

#             # POIs (mapped types)
#             try:
#                 pois_df = robot.get_pois()
#                 if isinstance(pois_df, pd.DataFrame) and not pois_df.empty:
#                     POI_DEFAULTS = {"name": True, "id": False, "coordinate": True, "type_label": True, "floor": True}
#                     pref_cols = ["name","id","coordinate","yaw","type_label","floor"]

#                     df_toggles_and_table(
#                         "POIs",
#                         format_poi_types(pois_df),
#                         pref_cols=pref_cols,
#                         default_checked=POI_DEFAULTS,
#                         key_prefix="pois",
#                         selectable=False
#                     )
#                 else:
#                     st.info("No POIs found for this robot.")
#             except Exception as e:
#                 st.error(f"Error fetching POIs: {e}")

# with tab_task:
#     st.header("Task Scenarios")

#     if not selected_robot_ids:
#         st.info("Pick robots in the sidebar to enable tasking.")
#     else:
#         # Target robots via checkboxes (labels show last 4 chars)
#         st.subheader("Targets")
#         cols = st.columns(min(6, max(1, len(selected_robot_ids))))
#         selected_for_task = []
#         for i, rid in enumerate(selected_robot_ids):
#             label = f"…{rid[-4:]}" if len(rid) >= 4 else rid
#             with cols[i % len(cols)]:
#                 if st.checkbox(label, value=True, key=f"task_target_{rid}", help=rid):
#                     selected_for_task.append(rid)

#         if not selected_for_task:
#             st.warning("No robots selected for tasking. Tick at least one above.")

#         # POI options shared across the selected robots
#         poi_options = common_poi_names(selected_for_task)
#         if not poi_options and selected_for_task:
#             # Fallback: use first robot's POIs
#             poi_options = list_robot_poi_names(selected_for_task[0])
#             if poi_options:
#                 st.info(f"No common POI names across robots; using POIs from {selected_for_task[0]}.")

#         left, right = st.columns([3, 2])
#         with left:
#             scenario = st.selectbox(
#                 "Scenario",
#                 [
#                     "task_go_C",
#                     "task_return_to_dock",
#                     "task_go_B_open_door",
#                     "task_close_door_wait",
#                     "task_lift_raise_at_A",
#                     "task_lift_lower_at_A",
#                     "task_areaA_to_areaB_lift",
#                     "create_wrapper_task",
#                 ],
#                 index=0
#             )
#         with right:
#             saved_names = ["— none —"] + sorted(st.session_state.saved_tasks.keys())
#             load_name = st.selectbox("Load saved preset", saved_names, index=0)

#         # Defaults for name only
#         defaults_robot_id = (selected_for_task[0] if selected_for_task else (selected_robot_ids[0] if selected_robot_ids else ""))

#         loaded = None
#         if load_name != "— none —":
#             loaded = st.session_state.saved_tasks.get(load_name, None)
#             if loaded and loaded.get("scenario") != scenario:
#                 st.warning(f"Preset “{load_name}” was saved for scenario '{loaded['scenario']}'. Switching to it.")
#                 scenario = loaded["scenario"]

#         st.write("### Parameters")
#         params = {}
#         with st.form(key="task_params_form", clear_on_submit=False):
#             task_name_default = (loaded or {}).get("params", {}).get(
#                 "task_name",
#                 f"{scenario} for {defaults_robot_id}"
#             )
#             task_name = st.text_input("Task name", value=task_name_default)

#             # --- POI-driven inputs: choose POI names only ---
#             if scenario == "task_go_C":
#                 params["poi_name"] = st.selectbox("Point (POI name)", options=poi_options, key="poi_goC")

#             elif scenario == "task_return_to_dock":
#                 pass

#             elif scenario == "task_go_B_open_door":
#                 params["poi_name"] = st.selectbox("Destination (POI name)", options=poi_options, key="poi_open_door")
#                 door_ids_str = st.text_input("door_ids (comma-separated)", value=(loaded or {}).get("params", {}).get("door_ids", "1,2,3,4"))
#                 try:
#                     params["door_ids"] = tuple(int(s.strip()) for s in door_ids_str.split(",") if s.strip())
#                 except Exception:
#                     params["door_ids"] = (1,2,3,4)

#             elif scenario == "task_close_door_wait":
#                 params["poi_name"] = st.selectbox("Destination (POI name)", options=poi_options, key="poi_close_wait")
#                 params["wait_s"] = st.number_input("wait_s", value=int((loaded or {}).get("params", {}).get("wait_s", 10)), step=1)
#                 door_ids_str = st.text_input("door_ids (comma-separated)", value=(loaded or {}).get("params", {}).get("door_ids", "1,2,3,4"))
#                 try:
#                     params["door_ids"] = tuple(int(s.strip()) for s in door_ids_str.split(",") if s.strip())
#                 except Exception:
#                     params["door_ids"] = (1,2,3,4)

#             elif scenario in ("task_lift_raise_at_A", "task_lift_lower_at_A"):
#                 params["poi_name"] = st.selectbox("Lift point (POI name)", options=poi_options, key=f"poi_{scenario}")

#             elif scenario == "task_areaA_to_areaB_lift":
#                 cA, cB = st.columns(2)
#                 with cA:
#                     params["poi_A"] = st.selectbox("Point A (POI name)", options=poi_options, key="poi_A")
#                 with cB:
#                     params["poi_B"] = st.selectbox("Point B (POI name)", options=poi_options, key="poi_B")

#             elif scenario == "create_wrapper_task":
#                 st.markdown("**Pickup**")
#                 params["poi_pickup"] = st.selectbox("pickup (POI name)", options=poi_options, key="poi_pickup")

#                 st.markdown("**Wrapper**")
#                 params["poi_wrapper"] = st.selectbox("wrapper (POI name)", options=poi_options, key="poi_wrapper")

#                 st.markdown("**Waiting**")
#                 params["poi_waiting"] = st.selectbox("waiting (POI name)", options=poi_options, key="poi_waiting")
#                 params["waiting_pause_s"] = st.number_input("waiting.pause_s", value=int((loaded or {}).get("params", {}).get("waiting_pause_s", 240)), step=10)

#                 st.markdown("**Dropdown**")
#                 params["poi_dropdown"] = st.selectbox("dropdown (POI name)", options=poi_options, key="poi_dropdown")

#             c1, c2, c3 = st.columns([2, 1, 1])
#             with c1:
#                 preset_name = st.text_input("Save as (name)", value=(load_name if load_name != "— none —" else ""))
#             with c2:
#                 save_clicked = st.form_submit_button("Save preset")
#             with c3:
#                 unsave_clicked = st.form_submit_button("Unsave preset")

#             submit_clicked = st.form_submit_button("Create task…", use_container_width=True)

#         # Presets store scenario + params; robot list is chosen live
#         if save_clicked and preset_name.strip():
#             st.session_state.saved_tasks[preset_name.strip()] = {
#                 "scenario": scenario,
#                 "params": {"task_name": task_name, **params},
#             }
#             st.success(f"Saved preset “{preset_name.strip()}”.")
#         if unsave_clicked and preset_name.strip() and preset_name.strip() in st.session_state.saved_tasks:
#             del st.session_state.saved_tasks[preset_name.strip()]
#             st.warning(f"Removed preset “{preset_name.strip()}”.")

#         with st.expander("➕ Custom task (advanced)", expanded=False):
#             if not selected_robot_ids:
#                 st.info("Pick robots in the sidebar first.")
#             else:
#                 # top-level config
#                 c1, c2, c3, c4 = st.columns(4)
#                 runType_key     = c1.selectbox("Run Type", list(tl.RUN_TYPE.keys()), index=list(tl.RUN_TYPE.keys()).index("direct"))
#                 taskType_key    = c2.selectbox("Task Type", list(tl.TASK_TYPE.keys()), index=list(tl.TASK_TYPE.keys()).index("default"))
#                 routeMode_key   = c3.selectbox("Route Mode", list(tl.ROUTE_MODE.keys()), index=list(tl.ROUTE_MODE.keys()).index("sequential"))
#                 runMode_key     = c4.selectbox("Run Mode", list(tl.RUN_MODE.keys()), index=list(tl.RUN_MODE.keys()).index("flex_avoid"))

#                 c5, c6, c7, c8 = st.columns(4)
#                 sourceType_key  = c5.selectbox("Source", list(tl.SOURCE_TYPE.keys()), index=list(tl.SOURCE_TYPE.keys()).index("sdk"))
#                 runNum          = c6.number_input("runNum", min_value=1, value=1, step=1)
#                 speed           = c7.number_input("speed (-1=robot default)", value=-1.0, step=0.1)
#                 detourRadius    = c8.number_input("detourRadius", value=1.0, step=0.1)
#                 ignorePublicSite= st.checkbox("ignorePublicSite", value=False)

#                 st.markdown("#### Steps")
#                 # keep a per-session steps list
#                 if "custom_steps" not in st.session_state:
#                     st.session_state.custom_steps = [{
#                         "source": "POI",  # or "Manual"
#                         "poiName": None,
#                         "areaId": "",
#                         "x": 0.0, "y": 0.0, "yaw": 0.0,
#                         "name": "", "poiId": "",
#                         "stopRadius": 1.0,
#                         "actions": []  # list of {"kind": "...", "cfg": {...}}
#                     }]

#                 # Add/remove controls
#                 b1, b2, b3 = st.columns(3)
#                 if b1.button("➕ Add step"):
#                     st.session_state.custom_steps.append({
#                         "source": "POI", "poiName": None, "areaId": "", "x": 0.0, "y": 0.0, "yaw": 0.0,
#                         "name": "", "poiId": "", "stopRadius": 1.0, "actions": []
#                     })
#                 if b2.button("➖ Remove last") and st.session_state.custom_steps:
#                     st.session_state.custom_steps.pop()
#                 if b3.button("⟳ Reset"):
#                     st.session_state.custom_steps = st.session_state.custom_steps[:1]

#                 # Use the first selected robot to list POIs (same POI names assumed across the checked robots)
#                 base_robot_for_pois = selected_robot_ids[0]
#                 poi_names = ["— none —"] + list_robot_poi_names(base_robot_for_pois)

#                 # Render each step editor
#                 for i, step in enumerate(st.session_state.custom_steps):
#                     with st.container(border=True):
#                         st.write(f"**Step {i+1}**")
#                         s1, s2 = st.columns([1, 2])
#                         step["source"] = s1.radio("Point source", ["POI", "Manual"], index=(0 if step.get("source","POI")=="POI" else 1), key=f"custom_src_{i}")
#                         if step["source"] == "POI":
#                             sel = s2.selectbox("POI name", poi_names, index=0 if not step.get("poiName") else (poi_names.index(step["poiName"]) if step["poiName"] in poi_names else 0), key=f"custom_poi_{i}")
#                             step["poiName"] = (None if sel == "— none —" else sel)
#                         else:
#                             colA = st.columns(4)
#                             step["areaId"] = colA[0].text_input("areaId", value=step.get("areaId",""), key=f"custom_area_{i}")
#                             step["x"]      = colA[1].number_input("x", value=float(step.get("x",0.0)), step=0.1, key=f"custom_x_{i}")
#                             step["y"]      = colA[2].number_input("y", value=float(step.get("y",0.0)), step=0.1, key=f"custom_y_{i}")
#                             step["yaw"]    = colA[3].number_input("yaw", value=float(step.get("yaw",0.0)), step=1.0, key=f"custom_yaw_{i}")

#                         colB = st.columns(3)
#                         step["name"]       = colB[0].text_input("ext.name (optional)", value=step.get("name",""), key=f"custom_name_{i}")
#                         step["poiId"]      = colB[1].text_input("ext.id / poiId (optional)", value=step.get("poiId",""), key=f"custom_poiid_{i}")
#                         step["stopRadius"] = colB[2].number_input("stopRadius", value=float(step.get("stopRadius",1.0)), step=0.1, key=f"custom_stop_{i}")

#                         # Actions picker
#                         st.write("Actions")
#                         available = ["open_door","close_door","pause","wait_interaction","lift_up","lift_down"]
#                         chosen = st.multiselect("Add actions", available, default=[a["kind"] for a in step.get("actions",[])], key=f"custom_actpick_{i}")
#                         # ensure step["actions"] matches 'chosen'
#                         current = {a["kind"]: a for a in step.get("actions", [])}
#                         step["actions"] = [current.get(k, {"kind": k, "cfg": {}}) for k in chosen]

#                         # Per-action params
#                         for a_idx, act in enumerate(step["actions"]):
#                             kind = act["kind"]
#                             with st.container():
#                                 st.caption(f"Action: `{kind}`")
#                                 if kind in ("open_door","close_door"):
#                                     c = act.setdefault("cfg", {})
#                                     c["door_ids"] = st.text_input("door_ids (comma-separated)", value=c.get("door_ids", "1,2,3,4") if isinstance(c.get("door_ids"), str) else "1,2,3,4", key=f"custom_{i}_{kind}_doors")
#                                     # normalize to list[int] on submit
#                                     c["mode"] = st.number_input("mode", value=int(c.get("mode", 1)), step=1, key=f"custom_{i}_{kind}_mode")
#                                 elif kind == "pause":
#                                     c = act.setdefault("cfg", {})
#                                     c["pause_s"] = st.number_input("pause_s", value=int(c.get("pause_s", 5)), step=1, key=f"custom_{i}_pause_s")
#                                 elif kind in ("lift_up","lift_down"):
#                                     c = act.setdefault("cfg", {})
#                                     c["useAreaId"] = st.text_input("useAreaId (optional)", value=c.get("useAreaId",""), key=f"custom_{i}_{kind}_usearea")
#                                 elif kind == "wait_interaction":
#                                     act.setdefault("cfg", {})  # no params

#                 # Build & stage payload for confirm modal
#                 task_name_adv = st.text_input("Task name", value=f"custom for {selected_robot_ids[0]}")
#                 if st.button("Create custom task…", type="primary", use_container_width=True):
#                     # sanitize actions (door_ids string -> list[int])
#                     steps_clean = []
#                     for s in st.session_state.custom_steps:
#                         s2 = {**s}
#                         acts2 = []
#                         for a in s2.get("actions", []):
#                             a2 = {"kind": a["kind"], "cfg": dict(a.get("cfg", {}))}
#                             if a2["kind"] in ("open_door","close_door"):
#                                 raw = a2["cfg"].get("door_ids", "1,2,3,4")
#                                 if isinstance(raw, str):
#                                     a2["cfg"]["door_ids"] = [int(x.strip()) for x in raw.split(",") if x.strip().isdigit()]
#                             acts2.append(a2)
#                         s2["actions"] = acts2
#                         steps_clean.append(s2)

#                     st.session_state.confirm_payload = {
#                         "scenario": "custom_task",
#                         "robotIds": selected_for_task[:] if 'selected_for_task' in locals() and selected_for_task else selected_robot_ids[:],
#                         "params": {
#                             "task_name": task_name_adv,
#                             "runType_key": runType_key,
#                             "taskType_key": taskType_key,
#                             "routeMode_key": routeMode_key,
#                             "runMode_key": runMode_key,
#                             "sourceType_key": sourceType_key,
#                             "runNum": int(runNum),
#                             "speed": float(speed),
#                             "detourRadius": float(detourRadius),
#                             "ignorePublicSite": bool(ignorePublicSite),
#                             "steps": steps_clean
#                         },
#                     }
#                     st.rerun()


#         if submit_clicked:
#             st.session_state.confirm_payload = {
#                 "scenario": scenario,
#                 "robotIds": selected_for_task[:],   # fan-out list
#                 "params": {"task_name": task_name, **params},
#             }

#         if st.session_state.confirm_payload:
#             with st.container(border=True):
#                 st.warning("Confirm task submission")
#                 cp = st.session_state.confirm_payload
#                 st.write(f"**Scenario:** `{cp['scenario']}`")
#                 st.write("**Robots:**")
#                 st.code("\n".join(cp["robotIds"]), language="text")
#                 st.json(cp["params"])
#                 cc1, cc2 = st.columns([1,1])
#                 with cc1:
#                     if st.button("Confirm & Submit", type="primary", use_container_width=True):
#                         results, errors = [], []
#                         try:
#                             for rid in cp["robotIds"]:
#                                 try:
#                                     rob = sdk.Robot(rid)
#                                     pname = cp["params"].get("task_name", f"{cp['scenario']} for {rid}")
#                                     p = dict(cp["params"]); p.pop("task_name", None)
#                                     s = cp["scenario"]

#                                     # ----- Resolve POIs to coords per robot -----
#                                     # ... after meta = _poi_details_for(rid, p["poi_name"])
#                                     if s in ("task_go_C", "task_go_B_open_door", "task_close_door_wait",
#                                             "task_lift_raise_at_A", "task_lift_lower_at_A"):
#                                         meta = _poi_details_for(rid, p["poi_name"])
#                                         if not meta:
#                                             raise RuntimeError(f"POI '{p['poi_name']}' not found on {rid}")
#                                         p["areaId"], p["x"], p["y"], p["yaw"] = meta["areaId"], meta["x"], meta["y"], meta["yaw"]
#                                         p["p_type"] = meta.get("type")            # <-- pass type when available
#                                         if s in ("task_go_B_open_door", "task_close_door_wait"):
#                                             p["poiId"], p["poiName"] = meta.get("poiId"), meta.get("poiName")

#                                     elif s == "task_areaA_to_areaB_lift":
#                                         mA = _poi_details_for(rid, p["poi_A"])
#                                         mB = _poi_details_for(rid, p["poi_B"])
#                                         if not mA or not mB:
#                                             raise RuntimeError("POI A or POI B not found")
#                                         p["A_areaId"], p["Ax"], p["Ay"], p["Ayaw"] = mA["areaId"], mA["x"], mA["y"], mA["yaw"]
#                                         p["B_areaId"], p["Bx"], p["By"], p["Byaw"] = mB["areaId"], mB["x"], mB["y"], mB["yaw"]
#                                         p["A_type"] = mA.get("type")              # <-- types per point
#                                         p["B_type"] = mB.get("type")


#                                     elif s == "create_wrapper_task":
#                                         mp = _poi_details_for(rid, p["poi_pickup"])
#                                         mw = _poi_details_for(rid, p["poi_wrapper"])
#                                         mwait = _poi_details_for(rid, p["poi_waiting"])
#                                         md = _poi_details_for(rid, p["poi_dropdown"])
#                                         if not all([mp, mw, mwait, md]):
#                                             raise RuntimeError("One or more wrapper POIs not found")
#                                         p["areaId_pickup"] = mp["areaId"]
#                                         p["pickup_x"], p["pickup_y"], p["pickup_yaw"] = mp["x"], mp["y"], mp["yaw"]
#                                         p["pickup_shelf_area_id"] = mp["areaId"]

#                                         p["wrapper_x"], p["wrapper_y"], p["wrapper_yaw"] = mw["x"], mw["y"], mw["yaw"]

#                                         p["waiting_x"], p["waiting_y"], p["waiting_yaw"] = mwait["x"], mwait["y"], mwait["yaw"]

#                                         p["dropdown_x"], p["dropdown_y"], p["dropdown_yaw"] = md["x"], md["y"], md["yaw"]
#                                         p["dropdown_shelf_area_id"] = md["areaId"]
#                                     # --------------------------------------------

#                                     # ----- Dispatch -----
#                                     if s == "task_go_C":
#                                         resp = tl.task_go_C(pname, rob.df, areaId=p["areaId"], x=p["x"], y=p["y"], yaw=p["yaw"],
#                                                             p_type=p.get("p_type"))
#                                     elif s == "task_go_B_open_door":
#                                         resp = tl.task_go_B_open_door(
#                                             pname, rob.df,
#                                             areaId=p["areaId"], x=p["x"], y=p["y"], yaw=p["yaw"],
#                                             poiId=p.get("poiId"), poiName=p.get("poiName"),
#                                             door_ids=p.get("door_ids",(1,2,3,4)),
#                                             p_type=p.get("p_type")
#                                         )
#                                     elif s == "task_close_door_wait":
#                                         resp = tl.task_close_door_wait(
#                                             pname, rob.df,
#                                             areaId=p["areaId"], x=p["x"], y=p["y"], yaw=p["yaw"],
#                                             poiId=p.get("poiId"), poiName=p.get("poiName"),
#                                             wait_s=p["wait_s"], door_ids=p.get("door_ids",(1,2,3,4)),
#                                             p_type=p.get("p_type")
#                                         )
#                                     elif s == "task_lift_raise_at_A":
#                                         resp = tl.task_lift_raise_at_A(
#                                             pname, rob.df, areaId=p["areaId"], x=p["x"], y=p["y"], yaw=p["yaw"],
#                                             useAreaId=(p.get("useAreaId") or None),
#                                             p_type=p.get("p_type")
#                                         )
#                                     elif s == "task_lift_lower_at_A":
#                                         resp = tl.task_lift_lower_at_A(
#                                             pname, rob.df, areaId=p["areaId"], x=p["x"], y=p["y"], yaw=p["yaw"],
#                                             useAreaId=(p.get("useAreaId") or None),
#                                             p_type=p.get("p_type")
#                                         )
#                                     elif s == "task_areaA_to_areaB_lift":
#                                         A = (p["Ax"], p["Ay"], p["Ayaw"]); B = (p["Bx"], p["By"], p["Byaw"])
#                                         resp = tl.task_areaA_to_areaB_lift(
#                                             pname, rob.df, A=A, A_areaId=p["A_areaId"], B=B, B_areaId=p["B_areaId"],
#                                             A_type=p.get("A_type"), B_type=p.get("B_type")
#                                         )

#                                     elif s == "custom_task":
#                                         # unpack header params
#                                         runType     = tl.RUN_TYPE[p["runType_key"]]
#                                         taskType    = tl.TASK_TYPE[p["taskType_key"]]
#                                         routeMode   = tl.ROUTE_MODE[p["routeMode_key"]]
#                                         runMode     = tl.RUN_MODE[p["runMode_key"]]
#                                         sourceType  = tl.SOURCE_TYPE[p["sourceType_key"]]
#                                         runNum      = int(p.get("runNum", 1))
#                                         speed       = float(p.get("speed", -1.0))
#                                         detourRadius= float(p.get("detourRadius", 1.0))
#                                         ignorePublic= bool(p.get("ignorePublicSite", False))

#                                         # build taskPts for THIS rob.dfot
#                                         taskPts = []
#                                         for step in p["steps"]:
#                                             # BEFORE (typo)
#                                         # resolved = _resolve_step_for_rob.dfot(rid, step)

#                                         # AFTER
#                                             resolved = _resolve_step_for_robot(rid, step)

#                                             # and when building each point:
#                                             taskPts.append(
#                                                 tl.point(
#                                                     resolved["x"], resolved["y"], resolved["areaId"], resolved["yaw"],
#                                                     name=resolved.get("name") or None,
#                                                     poiId=resolved.get("poiId") or None,
#                                                     stopRadius=resolved.get("stopRadius", 1.0),
#                                                     acts=resolved.get("acts") or None,
#                                                     p_type=resolved.get("type")          # <-- include if present
#                                                 )
#                                             )

#                                             resp = tl.create_task(
#                                                 pname, rob.df,
#                                                 runType=runType, sourceType=sourceType,
#                                                 taskPts=taskPts, runNum=runNum, taskType=taskType,
#                                                 routeMode=routeMode, runMode=runMode,
#                                                 ignorePublicSite=ignorePublic, speed=speed,
#                                                 detourRadius=detourRadius, backPt={}
#                                             )

#                                     else:
#                                         raise RuntimeError(f"Unsupported scenario '{s}'")
#                                     # --------------------------------------------

#                                     results.append({"robotId": rid, "response": resp})
#                                 except Exception as e:
#                                     errors.append({"robotId": rid, "error": str(e)})

#                             if results:
#                                 st.success(f"Tasks created for {len(results)} robot(s).")
#                                 st.json(results)
#                             if errors:
#                                 st.error(f"Errors for {len(errors)} robot(s).")
#                                 st.json(errors)
#                         finally:
#                             st.session_state.confirm_payload = None
#                             st.rerun()
#                 with cc2:
#                     if st.button("Cancel", use_container_width=True):
#                         st.session_state.confirm_payload = None
#                         st.info("Submission cancelled.")
#                         st.rerun()

# st.markdown("---")
# st.caption("Pick POI names for task points; coordinates are resolved per robot at submit-time. All selected robots use the same POI names.")
import logging, os, math, textwrap
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

import AX_PY_SDK_3 as sdk
import task_library as tl

# Quiet the arrow noise a bit
st.set_option("client.showErrorDetails", False)
for name in ("streamlit", "streamlit.dataframe_util", "pyarrow"):
    logging.getLogger(name).setLevel(logging.ERROR)

st.set_page_config(page_title="Robots Dashboard", layout="wide")

# --- Auth (unchanged from your working version) ---
APP_PASSWORD = os.environ.get("APP_PASSWORD", "ef-ax-sdk-ahmed")
def require_auth():
    if st.session_state.get("authed") is True:
        st.sidebar.success("🔓 Unlocked")
        return
    st.title("Authentication required")
    with st.form("auth_form", clear_on_submit=True):
        pwd = st.text_input("Password", type="password")
        ok  = st.form_submit_button("Unlock")
    if ok:
        if APP_PASSWORD and pwd == APP_PASSWORD:
            st.session_state.authed = True
            st.rerun()
        else:
            st.error("Wrong password")
    st.stop()
require_auth()

def _do_logout():
    for k in ("authed", "auth_form", "auth_pwd", "auth_ts"):
        st.session_state.pop(k, None)
    try:
        st.cache_data.clear()
    except Exception:
        pass
    st.session_state.pop("selected_robot_ids", None)
    st.session_state.pop("confirm_payload", None)
    st.session_state.pop("robots_source", None)
    st.rerun()
st.sidebar.button("Log out", key="logout_btn", use_container_width=True, on_click=_do_logout)

# --- CSS ---
st.markdown("""
<style>
.active-robot { font-size: 1.05rem; font-weight: 600; }
.robot-pill { padding: 2px 8px; border-radius: 6px; background: #262730; margin-right: 6px; }
.robot-pill b { color: #e6e6e6; }
</style>
""", unsafe_allow_html=True)

# =========================
# POI helpers (robust)
# =========================

# --- Actions & step resolver (from your older code) ---
def _build_action_from_cfg(kind: str, cfg: dict):
    # maps UI to task_library actions
    if kind == "open_door":
        return tl.act_open_doors(cfg.get("door_ids", [1,2,3,4]), cfg.get("mode", 1))
    if kind == "close_door":
        return tl.act_close_doors(cfg.get("door_ids", [1,2,3,4]), cfg.get("mode", 1))
    if kind == "pause":
        return tl.act_pause(int(cfg.get("pause_s", 5)))
    if kind == "wait_interaction":
        return tl.act_wait()
    if kind == "lift_up":
        return tl.act_lift_up(cfg.get("useAreaId") or None)
    if kind == "lift_down":
        return tl.act_lift_down(cfg.get("useAreaId") or None)
    return None

def _resolve_step_for_robot(robot_id: str, step: dict):
    """
    Resolve a UI step (POI or Manual) into coords + acts.
    Returns dict x,y,yaw,areaId,name,poiId,stopRadius,acts,type
    """
    source = step.get("source", "POI")
    stopRadius = float(step.get("stopRadius", 1.0))
    acts_cfg = step.get("actions", []) or []
    acts = []
    for a in acts_cfg:
        act = _build_action_from_cfg(a.get("kind"), a.get("cfg", {}))
        if act:
            # normalize door_ids if user typed string
            if act["type"] in (tl.ACTION["open_door"], tl.ACTION["close_door"]):
                raw = a.get("cfg", {}).get("door_ids")
                if isinstance(raw, str):
                    act["data"]["doorIds"] = [int(s.strip()) for s in raw.split(",") if s.strip().isdigit()]
            acts.append(act)

    if source == "POI":
        poi_name = step.get("poiName")
        meta = _poi_details_for(robot_id, poi_name) if poi_name else None
        if not meta:
            raise RuntimeError(f"POI '{poi_name}' not found for robot {robot_id}")
        return {
            "x": meta["x"], "y": meta["y"], "yaw": meta.get("yaw", 0.0),
            "areaId": meta["areaId"],
            "name": meta.get("poiName", poi_name),
            "poiId": meta.get("poiId"),
            "stopRadius": stopRadius,
            "acts": acts,
            "type": meta.get("type"),
        }

    # Manual step
    return {
        "x": float(step.get("x", 0.0)),
        "y": float(step.get("y", 0.0)),
        "yaw": float(step.get("yaw", 0.0)),
        "areaId": str(step.get("areaId") or ""),
        "name": step.get("name") or "",
        "poiId": step.get("poiId") or "",
        "stopRadius": stopRadius,
        "acts": acts,
        "type": None
    }

def _area_from_poi_list(robot_id: str, poi_name: str):
    try:
        df = sdk.Robot(robot_id).get_pois()
        if isinstance(df, pd.DataFrame) and not df.empty:
            row = df.loc[df["name"] == poi_name]
            if not row.empty:
                for cand in ("areaId","areaID","area_id"):
                    if cand in row.columns:
                        val = row.iloc[0][cand]
                        return (str(val).strip() or None) if pd.notna(val) else None
    except Exception:
        pass
    return None

def _poi_details_for(robot_id: str, poi_name: str):
    """Return dict: areaId,x,y,yaw,poiId,poiName,type; error if areaId missing."""
    d = sdk.Robot(robot_id).get_poi_details(poi_name)
    print(d)
    if not isinstance(d, dict) or not d:
        raise RuntimeError(f"POI '{poi_name}' not found for robot {robot_id}")
    coord = d.get("coordinate") or [None, None]
    area  = d.get("areaId") or _area_from_poi_list(robot_id, poi_name)
    if not area:
        raise RuntimeError(f"POI '{poi_name}' has no areaId for robot {robot_id}")
    return {
        "areaId": str(area),
        "x": coord[0],
        "y": coord[1],
        "yaw": d.get("yaw", 0),
        "poiId": d.get("id"),
        "poiName": d.get("name", poi_name),
        "type": d.get("type"),
    }

# =========================
# Cache/data loaders
# =========================
@st.cache_data(show_spinner=False)
def load_businesses():
    df = sdk.get_business()
    if not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame(columns=["id","name"])
    return df[["id","name"]].dropna().drop_duplicates()

@st.cache_data(show_spinner=False)
def load_robots():
    df = sdk.get_robots()
    return df if isinstance(df, pd.DataFrame) else pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_online_robots():
    try:
        df = sdk.get_online_robots()
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

@st.cache_data(show_spinner=False)
def load_ef_robots():
    try:
        df = sdk.get_ef_robots()
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

# =========================
# Table helper
# =========================
def with_online_icons(df: pd.DataFrame) -> pd.DataFrame:
    if "isOnLine" in df.columns:
        df = df.copy()
        df["isOnLine"] = df["isOnLine"].map(lambda v: "✅" if bool(v) else "❌")
    return df

def df_toggles_and_table(name: str, df: pd.DataFrame, pref_cols, default_checked: dict, key_prefix: str):
    if df is None or df.empty:
        st.info(f"No rows in **{name}**.")
        return
    cols = [c for c in pref_cols if c in df.columns] or list(df.columns)
    st.write(f"**{name}** – columns")
    checks, row = {}, st.columns(min(len(cols), 8))
    for i, c in enumerate(cols):
        if i % 8 == 0 and i > 0:
            row = st.columns(min(len(cols) - i, 8))
        col = row[i % 8]
        checks[c] = col.checkbox(c, value=bool(default_checked.get(c, True)), key=f"{key_prefix}_col_{c}")
    shown = [c for c in cols if checks.get(c)]
    if not shown:
        st.warning("All columns hidden.")
        return
    table_df = with_online_icons(df[shown])
    st.dataframe(table_df, hide_index=True, use_container_width=True)

# =========================
# Session
# =========================
if "saved_tasks" not in st.session_state:
    st.session_state.saved_tasks = {}
if "confirm_payload" not in st.session_state:
    st.session_state.confirm_payload = None
if "robots_source" not in st.session_state:
    ef = load_ef_robots()
    st.session_state.robots_source = "ef" if (isinstance(ef,pd.DataFrame) and not ef.empty) else "all"
if "selected_robot_ids" not in st.session_state:
    st.session_state.selected_robot_ids = []

# =========================
# Data
# =========================
business_df  = load_businesses()
robots_all   = load_robots()
robots_online= load_online_robots()
robots_ef    = load_ef_robots()

# =========================
# Sidebar
# =========================
st.sidebar.header("Pickers")
if st.sidebar.button("Use Online Robots as main list", use_container_width=True):
    st.session_state.robots_source = "online"
if st.sidebar.button("Use EF Robots as main list", use_container_width=True):
    st.session_state.robots_source = "ef"
if st.sidebar.button("Reset to All Robots", use_container_width=True):
    st.session_state.robots_source = "all"
if st.sidebar.button("Refresh caches", use_container_width=True):
    load_businesses.clear(); load_robots.clear(); load_online_robots.clear(); load_ef_robots.clear()
    st.rerun()

robots_df = robots_all
if st.session_state.robots_source == "online" and not robots_online.empty:
    robots_df = robots_online
elif st.session_state.robots_source == "ef" and not robots_ef.empty:
    robots_df = robots_ef

st.title("Robot Control & Telemetry")

biz_options = ["— All businesses —"] + business_df["name"].sort_values().unique().tolist()
selected_business = st.sidebar.selectbox("Business", biz_options, index=0, key="business_picker")
robots_scoped = robots_df if selected_business == "— All businesses —" else robots_df[robots_df["businessId"].isin(set(business_df.loc[business_df["name"]==selected_business,"id"]))]

robot_id_options = (
    robots_scoped["robotId"].dropna().astype(str).sort_values().unique().tolist()
)
prev_sel = [str(x) for x in st.session_state.get("selected_robot_ids", [])]
valid_defaults = [x for x in prev_sel if x in robot_id_options] or (robot_id_options[:1] if robot_id_options else [])
selected_robot_ids = st.sidebar.multiselect("Robots (multi-select)", options=robot_id_options, default=valid_defaults, key="selected_robot_ids")

# =========================
# Main table
# =========================
ROBOT_DEFAULTS = {"robotId": True, "business_name": True, "model": True, "isOnLine": True, "areaId": False, "x": False, "y": False}
robot_pref_cols = ["robotId","business_name","model","isOnLine","areaId","x","y"]
df_toggles_and_table("Business Robots (filtered)", robots_scoped.reset_index(drop=True), robot_pref_cols, ROBOT_DEFAULTS, "mainrobots")

# =========================
# Tabs
# =========================
tab_mon, tab_task = st.tabs(["Monitoring", "Tasking"])

with tab_mon:
    if not selected_robot_ids:
        st.info("Pick at least one robot in the sidebar.")
    else:
        monitor_choice = st.radio("Monitor robot:", options=selected_robot_ids, index=0, horizontal=True, key="monitor_robot_choice")
        try:
            robot = sdk.Robot(monitor_choice)
        except Exception as e:
            st.error(f"Failed to initialize Robot('{monitor_choice}'): {e}")
            robot = None

        if robot:
            biz = getattr(robot.df, "business_name", "") or ""
            model_raw = getattr(robot.df, "model", "") or ""
            online_badge = "✅ Online" if bool(getattr(robot.df,"isOnLine",False)) else "❌ Offline"
            st.markdown(
                f'<div class="active-robot">Active robot: <code>{robot.SN}</code></div>'
                f'<div style="margin-top:6px;">'
                f'  <span class="robot-pill"><b>Business:</b> {biz}</span>'
                f'  <span class="robot-pill"><b>Model:</b> {model_raw}</span>'
                f'  <span class="robot-pill"><b>Status:</b> {online_badge}</span>'
                f'</div>', unsafe_allow_html=True
            )

            # (Charts + map image sections left as in your working app)
            try:
                img = robot.get_map_image()
                if hasattr(img, "size"):
                    st.image(img, use_container_width=True)
                else:
                    st.write(img if img else "No image returned.")
            except Exception as e:
                st.error(f"Error fetching map image: {e}")

            try:
                pois_df = robot.get_pois()
                if isinstance(pois_df, pd.DataFrame) and not pois_df.empty:
                    show = pois_df.copy()
                    st.dataframe(show, use_container_width=True, hide_index=True)
                else:
                    st.info("No POIs found for this robot.")
            except Exception as e:
                st.error(f"Error fetching POIs: {e}")

with tab_task:
    st.header("Task Scenarios")

    if not selected_robot_ids:
        st.info("Pick robots in the sidebar to enable tasking.")
    else:
        st.subheader("Targets")
        cols = st.columns(min(6, max(1, len(selected_robot_ids))))
        selected_for_task = []
        for i, rid in enumerate(selected_robot_ids):
            label = f"…{rid[-4:]}" if len(rid) >= 4 else rid
            with cols[i % len(cols)]:
                if st.checkbox(label, value=True, key=f"task_target_{rid}", help=rid):
                    selected_for_task.append(rid)

        def list_robot_poi_names(robot_id: str):
            try:
                df = sdk.Robot(robot_id).get_pois()
                if isinstance(df, pd.DataFrame) and not df.empty and "name" in df.columns:
                    return sorted([str(n) for n in df["name"].dropna().unique().tolist()])
            except Exception:
                pass
            return []

        def common_poi_names(robot_ids):
            base = None
            for rid in robot_ids or []:
                names = set(list_robot_poi_names(rid))
                if base is None:
                    base = names
                else:
                    base &= names
                if not base:
                    break
            return sorted(base or [])

        poi_options = common_poi_names(selected_for_task) or (list_robot_poi_names(selected_for_task[0]) if selected_for_task else [])

        left, right = st.columns([3, 2])
        with left:
            scenario = st.selectbox(
                "Scenario",
                ["task_go_C","task_return_to_dock","task_go_B_open_door","task_close_door_wait","task_lift_raise_at_A","task_lift_lower_at_A","task_areaA_to_areaB_lift","create_wrapper_task"],
                index=0
            )
        with right:
            saved_names = ["— none —"] + sorted(st.session_state.saved_tasks.keys())
            load_name = st.selectbox("Load saved preset", saved_names, index=0)

        defaults_robot_id = (selected_for_task[0] if selected_for_task else (selected_robot_ids[0] if selected_robot_ids else ""))

        loaded = None
        if load_name != "— none —":
            loaded = st.session_state.saved_tasks.get(load_name, None)
            if loaded and loaded.get("scenario") != scenario:
                st.warning(f"Preset “{load_name}” was saved for scenario '{loaded['scenario']}'. Switching to it.")
                scenario = loaded["scenario"]

        st.write("### Parameters")
        params = {}
        with st.form(key="task_params_form", clear_on_submit=False):
            task_name_default = (loaded or {}).get("params", {}).get("task_name", f"{scenario} for {defaults_robot_id}")
            task_name = st.text_input("Task name", value=task_name_default)

            if scenario == "task_go_C":
                params["poi_name"] = st.selectbox("Point (POI name)", options=poi_options, key="poi_goC")

            elif scenario == "task_return_to_dock":
                pass

            elif scenario == "task_go_B_open_door":
                params["poi_name"] = st.selectbox("Destination (POI name)", options=poi_options, key="poi_open_door")
                door_ids_str = st.text_input("door_ids (comma-separated)", value=(loaded or {}).get("params", {}).get("door_ids", "1,2,3,4"))
                try:
                    params["door_ids"] = tuple(int(s.strip()) for s in door_ids_str.split(",") if s.strip())
                except Exception:
                    params["door_ids"] = (1,2,3,4)

            elif scenario == "task_close_door_wait":
                params["poi_name"] = st.selectbox("Destination (POI name)", options=poi_options, key="poi_close_wait")
                params["wait_s"] = st.number_input("wait_s", value=int((loaded or {}).get("params", {}).get("wait_s", 10)), step=1)
                door_ids_str = st.text_input("door_ids (comma-separated)", value=(loaded or {}).get("params", {}).get("door_ids", "1,2,3,4"))
                try:
                    params["door_ids"] = tuple(int(s.strip()) for s in door_ids_str.split(",") if s.strip())
                except Exception:
                    params["door_ids"] = (1,2,3,4)

            elif scenario in ("task_lift_raise_at_A","task_lift_lower_at_A"):
                params["poi_name"] = st.selectbox("Lift point (POI name)", options=poi_options, key=f"poi_{scenario}")

            elif scenario == "task_areaA_to_areaB_lift":
                cA, cB = st.columns(2)
                with cA:
                    params["poi_A"] = st.selectbox("Point A (POI name)", options=poi_options, key="poi_A")
                with cB:
                    params["poi_B"] = st.selectbox("Point B (POI name)", options=poi_options, key="poi_B")

            elif scenario == "create_wrapper_task":
                st.markdown("**Pickup**")
                params["poi_pickup"] = st.selectbox("pickup (POI name)", options=poi_options, key="poi_pickup")

                st.markdown("**Wrapper**")
                params["poi_wrapper"] = st.selectbox("wrapper (POI name)", options=poi_options, key="poi_wrapper")

                st.markdown("**Waiting**")
                params["poi_waiting"] = st.selectbox("waiting (POI name)", options=poi_options, key="poi_waiting")
                params["waiting_pause_s"] = st.number_input("waiting.pause_s", value=int((loaded or {}).get("params", {}).get("waiting_pause_s", 240)), step=10)

                st.markdown("**Dropdown**")
                params["poi_dropdown"] = st.selectbox("dropdown (POI name)", options=poi_options, key="poi_dropdown")

            c1, c2, c3 = st.columns([2,1,1])
            with c1:
                preset_name = st.text_input("Save as (name)", value=(load_name if load_name != "— none —" else ""))
            with c2:
                save_clicked = st.form_submit_button("Save preset")
            with c3:
                unsave_clicked = st.form_submit_button("Unsave preset")

            submit_clicked = st.form_submit_button("Create task…", use_container_width=True)

        if save_clicked and preset_name.strip():
            st.session_state.saved_tasks[preset_name.strip()] = {"scenario": scenario, "params": {"task_name": task_name, **params}}
            st.success(f"Saved preset “{preset_name.strip()}”.")
        if unsave_clicked and preset_name.strip() and preset_name.strip() in st.session_state.saved_tasks:
            del st.session_state.saved_tasks[preset_name.strip()]
            st.warning(f"Removed preset “{preset_name.strip()}”.")
        if submit_clicked:
            st.session_state.confirm_payload = {"scenario": scenario, "robotIds": selected_for_task[:], "params": {"task_name": task_name, **params}}

        # -------------------------
        # Custom task (advanced)
        # -------------------------
        with st.expander("➕ Custom task (advanced)", expanded=False):
            if not selected_robot_ids:
                st.info("Pick robots in the sidebar first.")
            else:
                # Header parameters (ALL possible knobs)
                c1, c2, c3, c4 = st.columns(4)
                runType_key     = c1.selectbox("Run Type", list(tl.RUN_TYPE.keys()),
                                               index=list(tl.RUN_TYPE.keys()).index("direct"))
                taskType_key    = c2.selectbox("Task Type", list(tl.TASK_TYPE.keys()),
                                               index=list(tl.TASK_TYPE.keys()).index("delivery"))
                routeMode_key   = c3.selectbox("Route Mode", list(tl.ROUTE_MODE.keys()),
                                               index=list(tl.ROUTE_MODE.keys()).index("sequential"))
                runMode_key     = c4.selectbox("Run Mode", list(tl.RUN_MODE.keys()),
                                               index=list(tl.RUN_MODE.keys()).index("flex_avoid"))

                c5, c6, c7, c8 = st.columns(4)
                sourceType_key  = c5.selectbox("Source", list(tl.SOURCE_TYPE.keys()),
                                               index=list(tl.SOURCE_TYPE.keys()).index("sdk"))
                runNum          = c6.number_input("runNum", min_value=1, value=1, step=1)
                speed           = c7.number_input("speed (-1=robot default)", value=-1.0, step=0.1)
                detourRadius    = c8.number_input("detourRadius", value=1.0, step=0.1)
                ignorePublicSite= st.checkbox("ignorePublicSite", value=False)

                # Optional backPt
                st.markdown("#### Back point (optional)")
                use_back = st.checkbox("Include backPt", value=False)
                back_pt_mode = None
                backPt = None
                if use_back:
                    back_pt_mode = st.radio("Back point source", ["POI", "Manual"], horizontal=True)
                    if back_pt_mode == "POI":
                        poi_names_all = ["— none —"] + (common_poi_names(selected_robot_ids) or list_robot_poi_names(selected_robot_ids[0]))
                        back_poi = st.selectbox("backPt POI", poi_names_all, index=0)
                        if back_poi != "— none —":
                            # Resolve later per robot
                            backPt = {"__use_poi__": back_poi}
                    else:
                        colB = st.columns(4)
                        b_area = colB[0].text_input("areaId", "")
                        b_x    = colB[1].number_input("x", value=0.0, step=0.1)
                        b_y    = colB[2].number_input("y", value=0.0, step=0.1)
                        b_yaw  = colB[3].number_input("yaw", value=0.0, step=1.0)
                        backPt = {"areaId": b_area, "x": b_x, "y": b_y, "yaw": b_yaw}

                st.markdown("#### Steps")
                # Keep a per-session steps list
                if "custom_steps" not in st.session_state:
                    st.session_state.custom_steps = [{
                        "source": "POI",
                        "poiName": None,
                        "areaId": "",
                        "x": 0.0, "y": 0.0, "yaw": 0.0,
                        "name": "", "poiId": "",
                        "stopRadius": 1.0,
                        "actions": []  # list of {"kind": "...", "cfg": {...}}
                    }]

                b1, b2, b3 = st.columns(3)
                if b1.button("➕ Add step"):
                    st.session_state.custom_steps.append({
                        "source": "POI", "poiName": None, "areaId": "", "x": 0.0, "y": 0.0, "yaw": 0.0,
                        "name": "", "poiId": "", "stopRadius": 1.0, "actions": []
                    })
                if b2.button("➖ Remove last") and st.session_state.custom_steps:
                    st.session_state.custom_steps.pop()
                if b3.button("⟳ Reset"):
                    st.session_state.custom_steps = st.session_state.custom_steps[:1]

                base_robot_for_pois = selected_robot_ids[0]
                poi_names = ["— none —"] + list_robot_poi_names(base_robot_for_pois)

                # Render each step editor
                for i, step in enumerate(st.session_state.custom_steps):
                    with st.container(border=True):
                        st.write(f"**Step {i+1}**")
                        s1, s2 = st.columns([1,2])
                        step["source"] = s1.radio("Point source", ["POI","Manual"],
                                                  index=(0 if step.get("source","POI")=="POI" else 1),
                                                  key=f"custom_src_{i}")
                        if step["source"] == "POI":
                            sel = s2.selectbox("POI name", poi_names,
                                               index=0 if not step.get("poiName") else (poi_names.index(step["poiName"]) if step["poiName"] in poi_names else 0),
                                               key=f"custom_poi_{i}")
                            step["poiName"] = (None if sel == "— none —" else sel)
                        else:
                            colA = st.columns(4)
                            step["areaId"] = colA[0].text_input("areaId", value=step.get("areaId",""), key=f"custom_area_{i}")
                            step["x"]      = colA[1].number_input("x", value=float(step.get("x",0.0)), step=0.1, key=f"custom_x_{i}")
                            step["y"]      = colA[2].number_input("y", value=float(step.get("y",0.0)), step=0.1, key=f"custom_y_{i}")
                            step["yaw"]    = colA[3].number_input("yaw", value=float(step.get("yaw",0.0)), step=1.0, key=f"custom_yaw_{i}")

                        colB = st.columns(3)
                        step["name"]       = colB[0].text_input("ext.name (optional)", value=step.get("name",""), key=f"custom_name_{i}")
                        step["poiId"]      = colB[1].text_input("ext.id / poiId (optional)", value=step.get("poiId",""), key=f"custom_poiid_{i}")
                        step["stopRadius"] = colB[2].number_input("stopRadius", value=float(step.get("stopRadius",1.0)), step=0.1, key=f"custom_stop_{i}")

                        # Actions picker
                        st.write("Actions")
                        available = ["open_door","close_door","pause","wait_interaction","lift_up","lift_down"]
                        chosen = st.multiselect("Add actions", available, default=[a["kind"] for a in step.get("actions",[])], key=f"custom_actpick_{i}")
                        current = {a["kind"]: a for a in step.get("actions", [])}
                        step["actions"] = [current.get(k, {"kind": k, "cfg": {}}) for k in chosen]

                        # Per-action params
                        for a_idx, act in enumerate(step["actions"]):
                            kind = act["kind"]
                            with st.container():
                                st.caption(f"Action: `{kind}`")
                                if kind in ("open_door","close_door"):
                                    c = act.setdefault("cfg", {})
                                    c["door_ids"] = st.text_input("door_ids (comma-separated)",
                                                                  value=c.get("door_ids", "1,2,3,4") if isinstance(c.get("door_ids"), str) else "1,2,3,4",
                                                                  key=f"custom_{i}_{kind}_doors")
                                    c["mode"] = st.number_input("mode", value=int(c.get("mode", 1)), step=1,
                                                                key=f"custom_{i}_{kind}_mode")
                                elif kind == "pause":
                                    c = act.setdefault("cfg", {})
                                    c["pause_s"] = st.number_input("pause_s", value=int(c.get("pause_s", 5)), step=1,
                                                                   key=f"custom_{i}_pause_s")
                                elif kind in ("lift_up","lift_down"):
                                    c = act.setdefault("cfg", {})
                                    c["useAreaId"] = st.text_input("useAreaId (optional)", value=c.get("useAreaId",""),
                                                                   key=f"custom_{i}_{kind}_usearea")
                                elif kind == "wait_interaction":
                                    act.setdefault("cfg", {})  # no params

                task_name_adv = st.text_input("Task name", value=f"custom for {selected_robot_ids[0]}")
                if st.button("Create custom task…", type="primary", use_container_width=True):
                    # sanitize actions (door_ids string -> list[int])
                    steps_clean = []
                    for s in st.session_state.custom_steps:
                        s2 = {**s}
                        acts2 = []
                        for a in s2.get("actions", []):
                            a2 = {"kind": a["kind"], "cfg": dict(a.get("cfg", {}))}
                            if a2["kind"] in ("open_door","close_door"):
                                raw = a2["cfg"].get("door_ids", "1,2,3,4")
                                if isinstance(raw, str):
                                    a2["cfg"]["door_ids"] = [int(x.strip()) for x in raw.split(",") if x.strip().isdigit()]
                            acts2.append(a2)
                        s2["actions"] = acts2
                        steps_clean.append(s2)

                    st.session_state.confirm_payload = {
                        "scenario": "custom_task",
                        "robotIds": selected_for_task[:] if selected_for_task else selected_robot_ids[:],
                        "params": {
                            "task_name": task_name_adv,
                            "runType_key": runType_key,
                            "taskType_key": taskType_key,
                            "routeMode_key": routeMode_key,
                            "runMode_key": runMode_key,
                            "sourceType_key": sourceType_key,
                            "runNum": int(runNum),
                            "speed": float(speed),
                            "detourRadius": float(detourRadius),
                            "ignorePublicSite": bool(ignorePublicSite),
                            "steps": steps_clean,
                            "backPt": backPt,  # may be None; resolved later per robot
                        },
                    }
                    st.rerun()

        # -------------------------
        # Confirm & submit panel
        # -------------------------
        if st.session_state.confirm_payload:
            with st.container(border=True):
                st.warning("Confirm task submission")
                cp = st.session_state.confirm_payload
                st.write(f"**Scenario:** `{cp['scenario']}`")
                st.write("**Robots:**")
                st.code("\n".join(cp["robotIds"]), language="text")
                st.json(cp["params"])
                cc1, cc2 = st.columns([1,1])
                with cc1:
                    if st.button("Confirm & Submit", type="primary", use_container_width=True):
                        results, errors = [], []
                        try:
                            for rid in cp["robotIds"]:
                                try:
                                    rob = sdk.Robot(rid)
                                    pname = cp["params"].get("task_name", f"{cp['scenario']} for {rid}")
                                    p = dict(cp["params"]); p.pop("task_name", None)
                                    s = cp["scenario"]

                                    # ----- Resolve POIs per robot (with type) -----
                                    if s in ("task_go_C","task_go_B_open_door","task_close_door_wait","task_lift_raise_at_A","task_lift_lower_at_A"):
                                        meta = _poi_details_for(rid, p["poi_name"])
                                        if not meta.get("areaId"):  # guard
                                            raise RuntimeError(f"Resolved POI '{p['poi_name']}' has empty areaId for {rid}")
                                        p["areaId"], p["x"], p["y"], p["yaw"] = meta["areaId"], meta["x"], meta["y"], meta["yaw"]
                                        p["p_type"] = (int(meta["type"]) if isinstance(meta.get("type"), int) else None)
                                        if s in ("task_go_B_open_door","task_close_door_wait"):
                                            p["poiId"], p["poiName"] = meta.get("poiId"), meta.get("poiName")

                                    elif s == "task_areaA_to_areaB_lift":
                                        mA = _poi_details_for(rid, p["poi_A"])
                                        mB = _poi_details_for(rid, p["poi_B"])
                                        if not mA.get("areaId") or not mB.get("areaId"):
                                            raise RuntimeError("POI A or POI B resolved without areaId")
                                        p["A_areaId"], p["Ax"], p["Ay"], p["Ayaw"] = mA["areaId"], mA["x"], mA["y"], mA["yaw"]
                                        p["B_areaId"], p["Bx"], p["By"], p["Byaw"] = mB["areaId"], mB["x"], mB["y"], mB["yaw"]
                                        p["Atype"] = (int(mA["type"]) if isinstance(mA.get("type"), int) else None)
                                        p["Btype"] = (int(mB["type"]) if isinstance(mB.get("type"), int) else None)

                                    elif s == "create_wrapper_task":
                                        mp = _poi_details_for(rid, p["poi_pickup"])
                                        mw = _poi_details_for(rid, p["poi_wrapper"])
                                        mwait = _poi_details_for(rid, p["poi_waiting"])
                                        md = _poi_details_for(rid, p["poi_dropdown"])
                                        if not all([mp, mw, mwait, md]):
                                            raise RuntimeError("One or more wrapper POIs not found")
                                        if not mp.get("areaId"):
                                            raise RuntimeError("Pickup POI has no areaId; cannot create wrapper task.")
                                        p["areaId_pickup"] = mp["areaId"]
                                        p["pickup_x"], p["pickup_y"], p["pickup_yaw"] = mp["x"], mp["y"], mp["yaw"]
                                        p["pickup_shelf_area_id"] = mp["areaId"]
                                        p["pickup_type"] = (int(mp["type"]) if isinstance(mp.get("type"), int) else None)

                                        p["wrapper_x"], p["wrapper_y"], p["wrapper_yaw"] = mw["x"], mw["y"], mw["yaw"]
                                        p["wrapper_type"] = (int(mw["type"]) if isinstance(mw.get("type"), int) else None)

                                        p["waiting_x"], p["waiting_y"], p["waiting_yaw"] = mwait["x"], mwait["y"], mwait["yaw"]
                                        p["waiting_type"] = (int(mwait["type"]) if isinstance(mwait.get("type"), int) else None)

                                        p["dropdown_x"], p["dropdown_y"], p["dropdown_yaw"] = md["x"], md["y"], md["yaw"]
                                        p["dropdown_shelf_area_id"] = md["areaId"]
                                        p["dropdown_type"] = (int(md["type"]) if isinstance(md.get("type"), int) else None)
                                    # --------------------------------------------

                                    # Final guards
                                    if s != "task_return_to_dock":
                                        if not p.get("areaId") and s not in ("task_areaA_to_areaB_lift","create_wrapper_task"):
                                            raise RuntimeError("Refusing to submit a task with empty areaId.")

                                    # ----- Dispatch -----
                                    if s == "task_go_C":
                                        resp = tl.task_go_C(
                                            pname, rob.df,
                                            areaId=p["areaId"], x=p["x"], y=p["y"], yaw=p["yaw"],
                                            p_type=p.get("p_type"),  # include only if present
                                            backPt=None
                                        )
                                    elif s == "task_return_to_dock":
                                        resp = tl.task_return_to_dock(pname, rob.df)
                                    elif s == "task_go_B_open_door":
                                        resp = tl.task_go_B_open_door(
                                            pname, rob.df,
                                            areaId=p["areaId"], x=p["x"], y=p["y"], yaw=p["yaw"],
                                            poiId=p.get("poiId"), poiName=p.get("poiName"),
                                            door_ids=p.get("door_ids",(1,2,3,4)), p_type=p.get("p_type")
                                        )
                                    elif s == "task_close_door_wait":
                                        resp = tl.task_close_door_wait(
                                            pname, rob.df,
                                            areaId=p["areaId"], x=p["x"], y=p["y"], yaw=p["yaw"],
                                            poiId=p.get("poiId"), poiName=p.get("poiName"),
                                            wait_s=p["wait_s"], door_ids=p.get("door_ids",(1,2,3,4)),
                                            p_type=p.get("p_type")
                                        )
                                    elif s == "task_lift_raise_at_A":
                                        resp = tl.task_lift_raise_at_A(
                                            pname, rob.df,
                                            areaId=p["areaId"], x=p["x"], y=p["y"], yaw=p["yaw"],
                                            useAreaId=(p.get("useAreaId") or None), p_type=p.get("p_type")
                                        )
                                    elif s == "task_lift_lower_at_A":
                                        resp = tl.task_lift_lower_at_A(
                                            pname, rob.df,
                                            areaId=p["areaId"], x=p["x"], y=p["y"], yaw=p["yaw"],
                                            useAreaId=(p.get("useAreaId") or None), p_type=p.get("p_type")
                                        )
                                    elif s == "task_areaA_to_areaB_lift":
                                        A = (p["Ax"], p["Ay"], p["Ayaw"], p.get("Atype"))
                                        B = (p["Bx"], p["By"], p["Byaw"], p.get("Btype"))
                                        resp = tl.task_areaA_to_areaB_lift(
                                            pname, rob.df,
                                            A=A, A_areaId=p["A_areaId"],
                                            B=B, B_areaId=p["B_areaId"]
                                        )
                                    elif s == "create_wrapper_task":
                                        resp = tl.create_wrapper_task(
                                            pname, rob.df,
                                            areaId_pickup=p["areaId_pickup"],
                                            pickup={"x": p["pickup_x"], "y": p["pickup_y"], "yaw": p["pickup_yaw"],
                                                    "shelf_area_id": p["pickup_shelf_area_id"], "type": p.get("pickup_type")},
                                            wrapper={"x": p["wrapper_x"], "y": p["wrapper_y"], "yaw": p["wrapper_yaw"], "type": p.get("wrapper_type")},
                                            waiting={"x": p["waiting_x"], "y": p["waiting_y"], "yaw": p["waiting_yaw"],
                                                     "pause_s": p["waiting_pause_s"], "type": p.get("waiting_type")},
                                            dropdown={"x": p["dropdown_x"], "y": p["dropdown_y"], "yaw": p["dropdown_yaw"],
                                                      "shelf_area_id": p["dropdown_shelf_area_id"], "type": p.get("dropdown_type")},
                                        )
                                    elif s == "custom_task":
                                        # unpack header params
                                        runType     = tl.RUN_TYPE[p["runType_key"]]
                                        taskType    = tl.TASK_TYPE[p["taskType_key"]]
                                        routeMode   = tl.ROUTE_MODE[p["routeMode_key"]]
                                        runMode     = tl.RUN_MODE[p["runMode_key"]]
                                        sourceType  = tl.SOURCE_TYPE[p["sourceType_key"]]
                                        runNum      = int(p.get("runNum", 1))
                                        speed       = float(p.get("speed", -1.0))
                                        detourRadius= float(p.get("detourRadius", 1.0))
                                        ignorePublic= bool(p.get("ignorePublicSite", False))

                                        # build taskPts for THIS robot
                                        taskPts = []
                                        for step in p["steps"]:
                                            resolved = _resolve_step_for_robot(rid, step)
                                            taskPts.append(
                                                tl.point(
                                                    resolved["x"], resolved["y"], resolved["areaId"], resolved["yaw"],
                                                    name=resolved.get("name") or None,
                                                    poiId=resolved.get("poiId") or None,
                                                    stopRadius=resolved.get("stopRadius", 1.0),
                                                    acts=resolved.get("acts") or None,
                                                    p_type=resolved.get("type")
                                                )
                                            )

                                        # Optional backPt (resolve POI per robot if chosen)
                                        backPt_final = None
                                        bp_in = p.get("backPt")
                                        if isinstance(bp_in, dict):
                                            if "__use_poi__" in bp_in:
                                                meta = _poi_details_for(rid, bp_in["__use_poi__"])
                                                if meta:
                                                    backPt_final = tl.cur_pt(meta["x"], meta["y"], meta.get("yaw", 0.0), meta["areaId"])
                                            elif all(k in bp_in for k in ("areaId","x","y","yaw")):
                                                backPt_final = tl.cur_pt(bp_in["x"], bp_in["y"], bp_in["yaw"], bp_in["areaId"])

                                        resp = tl.create_task(
                                            pname, rob.df,
                                            runType=runType, sourceType=sourceType,
                                            taskPts=taskPts, runNum=runNum, taskType=taskType,
                                            routeMode=routeMode, runMode=runMode,
                                            ignorePublicSite=ignorePublic, speed=speed,
                                            detourRadius=detourRadius,
                                            backPt=backPt_final  # ✅ None → omitted in SDK; dict → kept
                                        )

                                    else:
                                        raise RuntimeError(f"Unsupported scenario '{s}'")

                                    results.append({"robotId": rid, "response": resp})
                                except Exception as e:
                                    errors.append({"robotId": rid, "error": str(e)})

                            if results:
                                st.success(f"Tasks created for {len(results)} robot(s).")
                                st.json(results)
                            if errors:
                                st.error(f"Errors for {len(errors)} robot(s).")
                                st.json(errors)
                        finally:
                            st.session_state.confirm_payload = None
                            st.rerun()
                with cc2:
                    if st.button("Cancel", use_container_width=True):
                        st.session_state.confirm_payload = None
                        st.info("Submission cancelled.")
                        st.rerun()

st.markdown("---")
st.caption("POI types are included only when available; coordinates & areaId are resolved per robot at submit-time.")
