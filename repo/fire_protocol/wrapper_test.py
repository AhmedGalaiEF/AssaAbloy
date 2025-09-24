#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simple task execution test (no GPIO).
Creates the "refined wrapper" flow, then monitors robot position and
prints distance to key POIs until timeout or Ctrl+C.

Flow:
  1) P1 -> LIFT UP
  2) wrapper -> LIFT DOWN
  3) standby -> WAIT 240s
  4) wrapper -> LIFT UP
  5) P2 -> LIFT DOWN
  backPt: back
"""

import sys
import time
import math
import argparse
import numbers

# If your SDK is in a local path, add it here (adjust as needed)
# sys.path.append("/home/ag/Desktop/EF/dev/sdk/AX_PY_SDK")
# sys.path.append("/home/ag/Desktop/EF/dev/sdk")

# SDK imports
from AX_PY_SDK_3 import *  # Robot, create_task, etc.

# -----------------------------
# Minimal constants
# -----------------------------
RUN_TYPE_LIFT  = 29
TASK_TYPE_LIFT = 29     # use 29 (lift)
SOURCE_SDK     = 6
ROUTE_SEQ      = 1
RUNMODE_FLEX   = 1

ACTION = {
    "pause": 18,
    "lift_up": 47,
    "lift_down": 48,
}

# -----------------------------
# Helpers (no pandas)
# -----------------------------
def _act_lift_up(use_area_id=None):
    return {"type": ACTION["lift_up"], "data": ({"useAreaId": use_area_id} if use_area_id else {})}

def _act_lift_down(use_area_id=None):
    return {"type": ACTION["lift_down"], "data": ({"useAreaId": use_area_id} if use_area_id else {})}

def _act_pause(sec):
    return {"type": ACTION["pause"], "data": {"pauseTime": int(sec)}}

def _xy_from_any(p):
    """Extract (x, y) from dict-like `p` returned by the SDK."""
    if isinstance(p, dict):
        for kx, ky in (("x","y"), ("posX","posY"), ("X","Y")):
            if p.get(kx) is not None and p.get(ky) is not None:
                return float(p[kx]), float(p[ky])
        for k in ("coordinate","coord","position","pos"):
            v = p.get(k)
            if isinstance(v, (list, tuple)) and len(v) >= 2 and all(isinstance(v[i], numbers.Number) for i in (0,1)):
                return float(v[0]), float(v[1])
            if isinstance(v, dict):
                for kx, ky in (("x","y"),("posX","posY")):
                    if v.get(kx) is not None and v.get(ky) is not None:
                        return float(v[kx]), float(v[ky])
    raise RuntimeError(f"Cannot extract x/y from: {p!r}")

def _normalize_poi_record(rec: dict):
    """Ensure dict has x,y,yaw,areaId."""
    x, y = _xy_from_any(rec)
    yaw = float(rec.get("yaw", 0.0))
    areaId = rec.get("areaId") or rec.get("areaID") or rec.get("area_id") or rec.get("area")
    if areaId is None:
        raise RuntimeError(f"POI missing areaId-like field: {rec}")
    return {"x": x, "y": y, "yaw": yaw, "areaId": areaId}

def _pt_from_poi(poi: dict, *, acts=None, stop_radius=1.0):
    n = _normalize_poi_record(poi)
    out = {
        "x": n["x"], "y": n["y"], "yaw": n["yaw"],
        "areaId": n["areaId"], "stopRadius": float(stop_radius),
    }
    if acts:
        out["stepActs"] = acts
    return out

def _cur_pt_from_poi(poi: dict, *, stop_radius=1.0):
    n = _normalize_poi_record(poi)
    return {"x": n["x"], "y": n["y"], "yaw": n["yaw"], "areaId": n["areaId"], "stopRadius": float(stop_radius)}

def _find_poi(robot: "Robot", name: str) -> dict:
    """
    Robust POI fetch by name using get_poi_details with a few casings.
    Avoids pandas to dodge ABI/version issues.
    """
    for candidate in {name, name.lower(), name.upper(), name.capitalize()}:
        try:
            d = robot.get_poi_details(candidate)
            if isinstance(d, dict) and d:
                return _normalize_poi_record(d)
        except Exception:
            pass
    raise RuntimeError(f"POI '{name}' not found via get_poi_details(). Check spelling/case.")

def _dist_xy(a: dict, b: dict) -> float:
    ax, ay = _xy_from_any(a); bx, by = _xy_from_any(b)
    return math.hypot(ax - bx, ay - by)

# -----------------------------
# Main
# -----------------------------
def main():
    ap = argparse.ArgumentParser(description="Simple wrapper task tester (no GPIO).")
    ap.add_argument("--robot-id", required=True, help="Robot ID/SN to control")
    ap.add_argument("--p1", default="Abhol 1", help="POI name for P1 (lift up)")
    ap.add_argument("--p2", default="Abhol 2", help="POI name for P2 (final lift down)")
    ap.add_argument("--wrapper", default="Abhol 3", help="POI name for wrapper point")
    ap.add_argument("--standby", default="Wartepunkt", help="POI name to wait at (240s)")
    ap.add_argument("--back", default="Standby", help="POI name for backPt (dock/standby)")
    ap.add_argument("--speed", type=float, default=0.4, help="Task speed (m/s, -1 for robot default)")
    ap.add_argument("--detour", type=float, default=1.0, help="detourRadius")
    ap.add_argument("--tol", type=float, default=0.10, help="distance tolerance (m) for progress messages")
    ap.add_argument("--monitor-secs", type=int, default=900, help="how long to monitor after submit")
    ap.add_argument("--no-submit", action="store_true", help="Do not create task, only resolve POIs and monitor")
    args = ap.parse_args()

    # Bind robot
    robot = Robot(args.robot_id)
    print(f"[INFO] Using robot: {args.robot_id}")

    # Resolve POIs
    P1        = _find_poi(robot, args.p1)
    P2        = _find_poi(robot, args.p2)
    WRAPPER   = _find_poi(robot, args.wrapper)
    STANDBY   = _find_poi(robot, args.standby)
    BACK_PT   = _find_poi(robot, args.back)

    print("[INFO] POIs resolved:")
    for nm, p in (("P1",P1),("P2",P2),("WRAPPER",WRAPPER),("STANDBY",STANDBY),("BACK",BACK_PT)):
        print(f"  - {nm}: area={p['areaId']}  x={p['x']:.3f}  y={p['y']:.3f}  yaw={p['yaw']:.1f}")

    # Build task points
    pts = [
        _pt_from_poi(P1,      acts=[_act_lift_up(use_area_id=P1["areaId"])]),
        _pt_from_poi(WRAPPER, acts=[_act_lift_down(use_area_id=WRAPPER["areaId"])]),
        _pt_from_poi(STANDBY, acts=[_act_pause(240)]),
        _pt_from_poi(WRAPPER, acts=[_act_lift_up(use_area_id=WRAPPER["areaId"])]),
        _pt_from_poi(P2,      acts=[_act_lift_down(use_area_id=P2["areaId"])]),
    ]
    backPt = _cur_pt_from_poi(BACK_PT)

    # Create task (unless dry-run)
    task_name = f"refined_wrapper_test_{int(time.time())}"
    if args.no_submit:
        print("[DRY-RUN] Not submitting task (--no-submit).")
    else:
        print(f"[INFO] Creating task: {task_name}")
        try:
            resp = create_task(
                task_name=task_name,
                robot=robot.df,
                runType=RUN_TYPE_LIFT,
                sourceType=SOURCE_SDK,
                taskPts=pts,
                runNum=1,
                taskType=TASK_TYPE_LIFT,
                routeMode=ROUTE_SEQ,
                runMode=RUNMODE_FLEX,
                speed=args.speed,
                detourRadius=args.detour,
                ignorePublicSite=False,
                backPt=backPt,
            )
            print("[INFO] Task created. SDK response:")
            print(resp)
        except Exception as e:
            print(f"[ERROR] Failed to create task: {e}", file=sys.stderr)
            sys.exit(2)

    # Monitor loop
    print(f"[INFO] Monitoring current position for up to {args.monitor_secs}s. Ctrl+C to stop.")
    t0 = time.time()
    last_log = 0.0
    reached_flags = {"P1": False, "WRAPPER1": False, "STANDBY": False, "WRAPPER2": False, "P2": False}

    try:
        while True:
            if time.time() - t0 > args.monitor_secs:
                print("[INFO] Monitor timeout reached.")
                break

            try:
                curr = robot.get_curr_pos()  # dict with x,y,yaw,areaId
            except Exception as e:
                print(f"[WARN] get_curr_pos() failed: {e}")
                time.sleep(0.8)
                continue

            d_p1      = _dist_xy(curr, P1)
            d_wrap    = _dist_xy(curr, WRAPPER)
            d_standby = _dist_xy(curr, STANDBY)
            d_p2      = _dist_xy(curr, P2)

            # Throttled log (every ~2s)
            if time.time() - last_log > 2.0:
                print(f"[POSE] x={curr.get('x'):.3f} y={curr.get('y'):.3f} | "
                      f"d(P1)={d_p1:.2f}  d(WR)={d_wrap:.2f}  d(STB)={d_standby:.2f}  d(P2)={d_p2:.2f}")
                last_log = time.time()

            # Lightweight progress beeps
            if not reached_flags["P1"] and d_p1 <= args.tol:
                print("[PROGRESS] Reached P1 (≈ lift up).")
                reached_flags["P1"] = True
            if not reached_flags["WRAPPER1"] and reached_flags["P1"] and d_wrap <= args.tol:
                print("[PROGRESS] Reached wrapper (1) (≈ lift down).")
                reached_flags["WRAPPER1"] = True
            if not reached_flags["STANDBY"] and reached_flags["WRAPPER1"] and d_standby <= args.tol:
                print("[PROGRESS] Reached standby (wait).")
                reached_flags["STANDBY"] = True
            if not reached_flags["WRAPPER2"] and reached_flags["STANDBY"] and d_wrap <= args.tol:
                print("[PROGRESS] Reached wrapper (2) (≈ lift up).")
                reached_flags["WRAPPER2"] = True
            if not reached_flags["P2"] and reached_flags["WRAPPER2"] and d_p2 <= args.tol:
                print("[SUCCESS] Reached P2 (≈ final lift down).")
                reached_flags["P2"] = True
                # We can stop early once final point is reached:
                break

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user.")

    print("[INFO] Done.")

if __name__ == "__main__":
    main()

