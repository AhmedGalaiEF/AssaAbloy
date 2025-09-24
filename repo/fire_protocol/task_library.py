
# from AX_PY_SDK_3 import *


# """
# ##########################################################################################
#   API DOC Task scenarios
# ##########################################################################################
# """

# # ---- human-readable → int maps ----
# TASK_TYPE = {
#     "disinfection": 0, "return_to_dock": 1, "restaurant": 2, "hotel": 3,
#     "delivery": 4, "factory": 5, "chassis_miniapp": 6, "charge_sched": 7,
#     "lift": 29, "default": 6  # pick your backend default
# }

# RUN_TYPE = {
#     "sched_disinfect": 0, "temp_disinfect": 1,
#     "quick_meal": 20, "multi_meal": 21, "direct": 22, "roam": 23,
#     "return": 24, "charging_station": 25, "summon": 26, "birthday": 27,
#     "guide": 28, "lift": 29, "lift_cruise": 30, "flex_carry": 31,
#     "roll": 32, "full_unplug": 33, "sequential": 21
# }

# ACTION = {
#     "open_door": 6, "close_door": 28, "pause": 18, "play_audio": 5,
#     "spray": 32, "set_speed": 41, "light_on": 37, "light_off": 38,
#     "wait_interaction": 40, "lift_up": 47, "lift_down": 48
# }

# RUN_MODE = {"flex_avoid": 1, "traj_limited": 2, "traj_no_avoid": 3, "traj_no_dock_repl": 4}
# ROUTE_MODE = {"sequential": 1, "shortest": 2}
# SOURCE_TYPE = {
#     "unknown": 0, "head_app": 1, "miniapp": 2, "pager": 3, "chassis": 4,
#     "dispatch": 5, "sdk": 6, "pad": 7
# }

# # ---- tiny helpers ----
# # BEFORE
# # def point(x, y, areaId, p_type, yaw=0, name=None, poiId=None, stopRadius=1, acts=None):

# # REPLACE the old point/cur_pt with this:

# def point(x, y, areaId, yaw=0, name=None, poiId=None, stopRadius=1, acts=None, p_type=None):
#     p = {
#         "x": x, "y": y, "yaw": yaw, "stopRadius": stopRadius,
#         "areaId": areaId,
#         "ext": {k: v for k, v in {"name": name, "id": poiId}.items() if v is not None},
#     }
#     if acts:
#         p["stepActs"] = acts
#     if p_type is not None:  # only include when you have one
#         p["type"] = p_type
#     return p

# def cur_pt(x, y, yaw, areaId, p_type=None, stopRadius=1):
#     p = {"x": x, "y": y, "yaw": yaw, "areaId": areaId, "stopRadius": stopRadius}
#     if p_type is not None:
#         p["type"] = p_type
#     return p


# def act_open_doors(door_ids, mode=1):  return {"type": ACTION["open_door"],  "data": {"mode": mode, "doorIds": door_ids}}
# def act_close_doors(door_ids, mode=1):  return {"type": ACTION["close_door"], "data": {"mode": mode, "doorIds": door_ids}}
# def act_pause(sec):                     return {"type": ACTION["pause"], "data": {"pauseTime": sec}}
# def act_wait():                         return {"type": ACTION["wait_interaction"], "data": {}}
# def act_lift_up(useAreaId=None):        return {"type": ACTION["lift_up"], "data": ({ "useAreaId": useAreaId } if useAreaId else {})}
# def act_lift_down(useAreaId=None):      return {"type": ACTION["lift_down"], "data": ({ "useAreaId": useAreaId } if useAreaId else {})}

# # -------------------------------------------------------------------
# # SCENARIOS (all call your create_task)
# # -------------------------------------------------------------------

# def task_go_C(task_name, robot, areaId, x, y, yaw=0,
#               runNum=1, taskType="default", runType="direct",
#               routeMode="sequential", runMode="flex_avoid",
#               speed=0.4, sourceType="sdk", *, p_type=None):
#     taskPts = [point(x, y, areaId, yaw, p_type=p_type)]
#     return create_task(
#         task_name, robot, RUN_TYPE[runType], SOURCE_TYPE[sourceType],
#         taskPts=taskPts, runNum=runNum, taskType=TASK_TYPE[taskType],
#         routeMode=ROUTE_MODE[routeMode], runMode=RUN_MODE[runMode],
#         ignorePublicSite=False, speed=speed
#     )

# def task_go_B_open_door(task_name, robot, areaId, x, y, yaw, poiId, poiName,
#                         runNum=1, taskType="default", runType="sequential",
#                         routeMode="sequential", runMode="flex_avoid",
#                         door_ids=(1,2,3,4), speed=0.4, sourceType="sdk",
#                         cur=None, *, p_type=None):
#     taskPts = [point(x, y, areaId, yaw, poiName, poiId,
#                      acts=[act_open_doors(list(door_ids))], p_type=p_type)]
#     return create_task(
#         task_name, robot, RUN_TYPE[runType], SOURCE_TYPE[sourceType],
#         taskPts=taskPts, runNum=runNum, taskType=TASK_TYPE[taskType],
#         routeMode=ROUTE_MODE[routeMode], runMode=RUN_MODE[runMode],
#         ignorePublicSite=False, speed=speed, detourRadius=1, backPt={}
#     )

# def task_close_door_wait(task_name, robot, areaId, x, y, yaw, poiId, poiName,
#                          wait_s=10, runNum=1, taskType="default", runType="sequential",
#                          routeMode="sequential", runMode="flex_avoid",
#                          door_ids=(1,2,3,4), speed=0.4, sourceType="sdk",
#                          cur=None, *, p_type=None):
#     acts = [act_close_doors(list(door_ids)), act_pause(wait_s)]
#     taskPts = [point(x, y, areaId, yaw, poiName, poiId, acts=acts, p_type=p_type)]
#     return create_task(
#         task_name, robot, RUN_TYPE[runType], SOURCE_TYPE[sourceType],
#         taskPts=taskPts, runNum=runNum, taskType=TASK_TYPE[taskType],
#         routeMode=ROUTE_MODE[routeMode], runMode=RUN_MODE[runMode],
#         ignorePublicSite=False, speed=speed
#     )

# def task_lift_raise_at_A(task_name, robot, areaId, x, y, yaw=0, useAreaId=None,
#                          runNum=1, taskType="lift", runType="lift",
#                          routeMode="sequential", runMode="flex_avoid",
#                          speed=0.4, sourceType="sdk", *, p_type=None):
#     taskPts = [point(x, y, areaId, yaw, acts=[act_lift_up(useAreaId or areaId)], p_type=p_type)]
#     return create_task(
#         task_name, robot, RUN_TYPE[runType], SOURCE_TYPE[sourceType],
#         taskPts=taskPts, runNum=runNum, taskType=TASK_TYPE[taskType],
#         routeMode=ROUTE_MODE[routeMode], runMode=RUN_MODE[runMode],
#         speed=speed
#     )

# def task_lift_lower_at_A(task_name, robot, areaId, x, y, yaw=0, useAreaId=None,
#                          runNum=1, taskType="lift", runType="lift",
#                          routeMode="sequential", runMode="flex_avoid",
#                          speed=0.4, sourceType="sdk", *, p_type=None):
#     taskPts = [point(x, y, areaId, yaw, acts=[act_lift_down(useAreaId or areaId)], p_type=p_type)]
#     return create_task(
#         task_name, robot, RUN_TYPE[runType], SOURCE_TYPE[sourceType],
#         taskPts=taskPts, runNum=runNum, taskType=TASK_TYPE[taskType],
#         routeMode=ROUTE_MODE[routeMode], runMode=RUN_MODE[runMode],
#         speed=speed
#     )

# def task_areaA_to_areaB_lift(task_name, robot, A, A_areaId, B, B_areaId,
#                               runNum=1, taskType="lift", runType="lift",
#                               routeMode="sequential", runMode="flex_avoid",
#                               speed=0.4, sourceType="sdk", *,
#                               A_type=None, B_type=None):
#     Ax, Ay, Ayaw = A; Bx, By, Byaw = B
#     pts = [
#         point(Ax, Ay, A_areaId, Ayaw, name="A", poiId=A_areaId,
#               acts=[act_lift_up(useAreaId=A_areaId)], p_type=A_type),
#         point(Bx, By, B_areaId, Byaw, name="B", poiId=B_areaId,
#               acts=[act_lift_down(useAreaId=B_areaId)], p_type=B_type),
#     ]
#     return create_task(
#         task_name, robot, RUN_TYPE[runType], SOURCE_TYPE[sourceType],
#         taskPts=pts, runNum=runNum, taskType=TASK_TYPE[taskType],
#         routeMode=ROUTE_MODE[routeMode], runMode=RUN_MODE[runMode],
#         speed=speed
#     )


# # def task_go_B_open_door(task_name, robot, areaId, x, y, yaw, poiId, poiName,
# #                         runNum=1, taskType="default", runType="sequential",
# #                         routeMode="sequential", runMode="flex_avoid",
# #                         door_ids=(1,2,3,4), speed=0.4, sourceType="sdk",
# #                         cur=None):
# #     taskPts = [point(x, y, areaId, yaw, poiName, poiId, acts=[act_open_doors(list(door_ids))])]
# #     return create_task(
# #         task_name, robot,
# #         RUN_TYPE[runType], SOURCE_TYPE[sourceType],
# #         taskPts=taskPts, runNum=runNum, taskType=TASK_TYPE[taskType],
# #         routeMode=ROUTE_MODE[routeMode], runMode=RUN_MODE[runMode],
# #         ignorePublicSite=False, speed=speed,
# #         detourRadius=1, backPt={}
# #     )

# # def task_close_door_wait(task_name, robot, areaId, x, y, yaw, poiId, poiName,
# #                          wait_s=10, runNum=1, taskType="default", runType="sequential",
# #                          routeMode="sequential", runMode="flex_avoid",
# #                          door_ids=(1,2,3,4), speed=0.4, sourceType="sdk",
# #                          cur=None):
# #     acts = [act_close_doors(list(door_ids)), act_pause(wait_s)]
# #     taskPts = [point(x, y, areaId, yaw, poiName, poiId, acts=acts)]
# #     return create_task(
# #         task_name, robot, RUN_TYPE[runType], SOURCE_TYPE[sourceType],
# #         taskPts=taskPts, runNum=runNum, taskType=TASK_TYPE[taskType],
# #         routeMode=ROUTE_MODE[routeMode], runMode=RUN_MODE[runMode],
# #         ignorePublicSite=False, speed=speed
# #     )
# # def task_go_C(task_name, robot, areaId, x, y, yaw=0,
# #               runNum=1, taskType="default", runType="direct",
# #               routeMode="sequential", runMode="flex_avoid",
# #               speed=0.4, sourceType="sdk", *, p_type=None):
# #     taskPts = [point(x, y, areaId, yaw, p_type=p_type)]
# #     return create_task(...)

# # def task_go_B_open_door(task_name, robot, areaId, x, y, yaw, poiId, poiName,
# #                         runNum=1, taskType="default", runType="sequential",
# #                         routeMode="sequential", runMode="flex_avoid",
# #                         door_ids=(1,2,3,4), speed=0.4, sourceType="sdk",
# #                         cur=None, *, p_type=None):
# #     taskPts = [point(x, y, areaId, yaw, poiName, poiId,
# #                      acts=[act_open_doors(list(door_ids))],
# #                      p_type=p_type)]
# #     return create_task(...)

# # def task_close_door_wait(task_name, robot, areaId, x, y, yaw, poiId, poiName,
# #                          wait_s=10, runNum=1, taskType="default", runType="sequential",
# #                          routeMode="sequential", runMode="flex_avoid",
# #                          door_ids=(1,2,3,4), speed=0.4, sourceType="sdk",
# #                          cur=None, *, p_type=None):
# #     acts = [act_close_doors(list(door_ids)), act_pause(wait_s)]
# #     taskPts = [point(x, y, areaId, yaw, poiName, poiId, acts=acts, p_type=p_type)]
# #     return create_task(...)

# # def task_lift_raise_at_A(task_name, robot, areaId, x, y, yaw=0, useAreaId=None,
# #                          runNum=1, taskType="lift", runType="lift",
# #                          routeMode="sequential", runMode="flex_avoid",
# #                          speed=0.4, sourceType="sdk", *, p_type=None):
# #     taskPts = [point(x, y, areaId, yaw, acts=[act_lift_up(useAreaId or areaId)], p_type=p_type)]
# #     return create_task(...)

# # def task_lift_lower_at_A(task_name, robot, areaId, x, y, yaw=0, useAreaId=None,
# #                          runNum=1, taskType="lift", runType="lift",
# #                          routeMode="sequential", runMode="flex_avoid",
# #                          speed=0.4, sourceType="sdk", *, p_type=None):
# #     taskPts = [point(x, y, areaId, yaw, acts=[act_lift_down(useAreaId or areaId)], p_type=p_type)]
# #     return create_task(...)

# # def task_areaA_to_areaB_lift(task_name, robot, A, A_areaId, B, B_areaId,
# #                               runNum=1, taskType="lift", runType="lift",
# #                               routeMode="sequential", runMode="flex_avoid",
# #                               speed=0.4, sourceType="sdk", *,
# #                               A_type=None, B_type=None):
# #     Ax, Ay, Ayaw = A; Bx, By, Byaw = B
# #     pts = [
# #         point(Ax, Ay, A_areaId, Ayaw, name="A", poiId=A_areaId,
# #               acts=[act_lift_up(useAreaId=A_areaId)], p_type=A_type),
# #         point(Bx, By, B_areaId, Byaw, name="B", poiId=B_areaId,
# #               acts=[act_lift_down(useAreaId=B_areaId)], p_type=B_type),
# #     ]
# #     return create_task(...)




# """
# ##########################################################################################
#   Custom Tasks
# ##########################################################################################
# """

# # action helpers
# def _lift_up(use_area_id=None):
#     return {"type": 47, "data": ({"useAreaId": use_area_id} if use_area_id else {})}

# def _lift_down(use_area_id=None):
#     return {"type": 48, "data": ({"useAreaId": use_area_id} if use_area_id else {})}

# def _pause(sec):
#     return {"type": 18, "data": {"pauseTime": sec}}

# def _pt(x, y, areaId, p_type, yaw=0, ext_id=None, name=None, acts=None, stopRadius=1.0):
#     p = {
#         "x": x, "y": y, "yaw": yaw, "areaId": areaId,
#         "type": p_type, "stopRadius": stopRadius,
#         "ext": {k: v for k, v in {"id": ext_id, "name": name}.items() if v is not None}
#     }
#     if acts: p["stepActs"] = acts
#     return p

# # type maps (only what we need here)
# RUN_TYPE_LIFT = 29
# TASK_TYPE_LIFT = 29
# SOURCE_PAGER = 3
# ROUTE_SEQ = 1
# RUNMODE_FLEX = 1

# def create_wrapper_task(
#     task_name,
#     robot,
#     *,
#     areaId_pickup,
#     pickup,     # dict: {"x":..., "y":..., "yaw":..., "shelf_area_id": "..."}
#     wrapper,    # dict: {"x":..., "y":..., "yaw":...}            # no area binding
#     waiting,    # dict: {"x":..., "y":..., "yaw":..., "pause_s": 240}  # no area binding
#     dropdown,   # dict: {"x":..., "y":..., "yaw":..., "shelf_area_id": "..."}
#     speed=0.4,
#     detourRadius=1.0
# ):
#     # Points (use the pickup areaId for all; wrapper/waiting have no useAreaId)
#     pts = [
#         _pt(
#             pickup["x"], pickup["y"], areaId_pickup, pickup.get("yaw", 0),
#             ext_id=pickup.get("shelf_area_id"),
#             acts=[_lift_up(pickup.get("shelf_area_id"))]
#         ),
#         _pt(
#             wrapper["x"], wrapper["y"], areaId_pickup, wrapper.get("yaw", 0),
#             acts=[_lift_down()]  # wrapper point has no area → no useAreaId
#         ),
#         _pt(
#             waiting["x"], waiting["y"], areaId_pickup, waiting.get("yaw", 0),
#             acts=[_pause(waiting.get("pause_s", 240))]
#         ),
#         _pt(
#             wrapper["x"], wrapper["y"], areaId_pickup, wrapper.get("yaw", 0),
#             acts=[_lift_up()]     # raise again, still no useAreaId
#         ),
#         _pt(
#             dropdown["x"], dropdown["y"], areaId_pickup, dropdown.get("yaw", 0),
#             ext_id=dropdown.get("shelf_area_id"),
#             acts=[_lift_down(dropdown.get("shelf_area_id"))]
#         ),
#     ]

#     return create_task(
#         task_name=task_name,
#         robot=robot,
#         runType=RUN_TYPE_LIFT,
#         sourceType=SOURCE_PAGER,
#         taskPts=pts,
#         runNum=1,
#         taskType=TASK_TYPE_LIFT,
#         routeMode=ROUTE_SEQ,
#         runMode=RUNMODE_FLEX,
#         ignorePublicSite=False,
#         speed=speed,
#         detourRadius=detourRadius,
#         backPt={}
#     )


# ### call example : 

# # task_id_or_resp = create_wrapper_task(
# #     "Wrapper Protocol",
# #     robot,
# #     areaId_pickup=area_id,
# #     pickup={"x": x_pickup_pt, "y": y_pickup_pt, "yaw": yaw_pickup_pt, "shelf_area_id": pickup_pt_details["areaId"]},
# #     wrapper={"x": x_wrapper_pt, "y": y_wrapper_pt, "yaw": yaw_wrapper_pt},
# #     waiting={"x": x_waiting_pt, "y": y_waiting_pt, "yaw": yaw_waiting_pt, "pause_s": 240},
# #     dropdown={"x": x_dropdown_pt, "y": y_dropdown_pt, "yaw": yaw_dropdown_pt, "shelf_area_id": dropdown_pt_details["areaId"]},
# # )


# import math

# def _collect_evac_pts(robot):
#     pts = []
#     for _, row in robot.get_pois().iterrows():
#         name = row["name"]
#         if name.startswith("evacuation"):
#             d = robot.get_poi_details(name)
#             pts.append({
#                 "name": name,
#                 "areaId": d["areaId"],
#                 "x": d["coordinate"][0],
#                 "y": d["coordinate"][1],
#                 "yaw": d.get("yaw", 0),
#                 "id": d["id"],
#             })
#     return pts

# def _nearest_unassigned(rx, ry, pts, used_ids):
#     # return the closest pt whose id is not in used_ids (or None)
#     candidates = sorted(pts, key=lambda p: math.dist((rx, ry), (p["x"], p["y"])))
#     for p in candidates:
#         if p["id"] not in used_ids:
#             return p
#     return None

# def assign_evacuation_tasks(robots, *, allow_sharing=False):
#     if not isFireAlarm():
#         return []

#     if not robots:
#         return []

#     # Assume same map across robots; use first to fetch POIs
#     evac_pts = _collect_evac_pts(robots[0])
#     if not evac_pts:
#         raise RuntimeError("No evacuation points found")

#     used_ids = set()
#     tasks = []

#     for robot in robots:
#         rx, ry = robot.get_curr_pos()
#         pt = _nearest_unassigned(rx, ry, evac_pts, used_ids)

#         if pt is None:
#             if not allow_sharing:
#                 # no unique point left for this robot
#                 continue
#             # pick absolute nearest (even if already used)
#             pt = min(evac_pts, key=lambda p: math.dist((rx, ry), (p["x"], p["y"])))

#         else:
#             used_ids.add(pt["id"])

#         # BEFORE inside taskPts = [{
#         #   ...
#         #   "type": pt,
#         #   ...
#         # }]

#         # AFTER
#         taskPts = [{
#             "x": pt["x"], "y": pt["y"], "yaw": pt["yaw"], "stopRadius": 1,
#             "areaId": pt["areaId"],
#             "ext": {"id": pt["id"], "name": pt["name"]},
#         }]


#         # Evac: shortest route, obstacle avoidance, ignore public sites, max speed
#         task = create_task(
#             task_name=f"Evacuate → {pt['name']}",
#             robot=robot,
#             runType=21,           # sequential
#             sourceType=6,         # SDK
#             taskPts=taskPts,
#             runNum=1,
#             taskType=6,           # generic/default
#             routeMode=2,          # shortest
#             runMode=1,            # flexible avoidance
#             ignorePublicSite=True,
#             speed=1.0,
#             detourRadius=1.0,
#             backPt={}
#         )
#         tasks.append(task)

#     return tasks


#     #### call example


#     # while True:
#     #     assign_evacuation_tasks(...)
# task_library.py

from AX_PY_SDK_3 import *  # expects create_task(...) etc.

"""
##########################################################################################
  API DOC Task scenarios
##########################################################################################
"""

# ---- human-readable → int maps ----
TASK_TYPE = {
    "disinfection": 0, "return_to_dock": 1, "restaurant": 2, "hotel": 3,
    "delivery": 4, "factory": 5, "chassis_miniapp": 6, "charge_sched": 7,
    "lift": 29,
}

RUN_TYPE = {
    "sched_disinfect": 0, "temp_disinfect": 1,
    "quick_meal": 20, "multi_meal": 21, "direct": 22, "roam": 23,
    "return": 24, "charging_station": 25, "summon": 26, "birthday": 27,
    "guide": 28, "lift": 29, "lift_cruise": 30, "flex_carry": 31,
    "roll": 32, "full_unplug": 33,
}

ACTION = {
    "open_door": 6, "close_door": 28, "pause": 18, "play_audio": 5,
    "spray": 32, "set_speed": 41, "light_on": 37, "light_off": 38,
    "wait_interaction": 40, "lift_up": 47, "lift_down": 48
}

RUN_MODE    = {"flex_avoid": 1, "traj_limited": 2, "traj_no_avoid": 3, "traj_no_dock_repl": 4}
ROUTE_MODE  = {"sequential": 1, "shortest": 2}
SOURCE_TYPE = {"unknown": 0, "head_app": 1, "miniapp": 2, "pager": 3, "chassis": 4,
               "dispatch": 5, "sdk": 6, "pad": 7}

# ---- tiny helpers --------------------------------------------------------------

def _maybe(kwargs_key: str, value):
    """Return {kwargs_key: value} only if value is a non-empty dict."""
    return {kwargs_key: value} if isinstance(value, dict) and bool(value) else {}

def point(x, y, areaId, yaw=0, name=None, poiId=None, stopRadius=1, acts=None, p_type=None):
    """
    Build a task point. 'type' is included only when p_type is an int.
    """
    p = {
        "x": x, "y": y, "yaw": yaw, "stopRadius": stopRadius,
        "areaId": areaId,
        "ext": {k: v for k, v in {"name": name, "id": poiId}.items() if v is not None},
    }
    if acts:
        p["stepActs"] = acts
    if isinstance(p_type, int):
        p["type"] = p_type
    return p

def cur_pt(x, y, yaw, areaId, stopRadius=1, p_type=None):
    """
    Current-location-style point. 'type' is optional and omitted unless int.
    """
    p = {"x": x, "y": y, "yaw": yaw, "areaId": areaId, "stopRadius": stopRadius}
    if isinstance(p_type, int):
        p["type"] = p_type
    return p

def act_open_doors(door_ids, mode=1):  return {"type": ACTION["open_door"],  "data": {"mode": int(mode), "doorIds": list(door_ids)}}
def act_close_doors(door_ids, mode=1): return {"type": ACTION["close_door"], "data": {"mode": int(mode), "doorIds": list(door_ids)}}
def act_pause(sec):                    return {"type": ACTION["pause"], "data": {"pauseTime": int(sec)}}
def act_wait():                        return {"type": ACTION["wait_interaction"], "data": {}}
def act_lift_up(useAreaId=None):       return {"type": ACTION["lift_up"],   "data": ({"useAreaId": useAreaId} if useAreaId else {})}
def act_lift_down(useAreaId=None):     return {"type": ACTION["lift_down"], "data": ({"useAreaId": useAreaId} if useAreaId else {})}

# ---- Scenarios ----------------------------------------------------------------

def task_go_C(task_name, robot, areaId, x, y, yaw=0,
              runNum=1, taskType="delivery", runType="direct",
              routeMode="sequential", runMode="flex_avoid",
              speed=0.4, sourceType="sdk", *, p_type=None, backPt=None):
    taskPts = [point(x, y, areaId, yaw, p_type=p_type)]
    extra = _maybe("backPt", backPt)
    return create_task(
        task_name, robot, RUN_TYPE[runType], SOURCE_TYPE[sourceType],
        taskPts=taskPts, runNum=int(runNum), taskType=TASK_TYPE[taskType],
        routeMode=ROUTE_MODE[routeMode], runMode=RUN_MODE[runMode],
        ignorePublicSite=False, speed=float(speed), **extra
    )

def task_go_B_open_door(task_name, robot, areaId, x, y, yaw, poiId, poiName,
                        runNum=1, taskType="delivery", runType="direct",
                        routeMode="sequential", runMode="flex_avoid",
                        door_ids=(1,2,3,4), speed=0.4, sourceType="sdk",
                        *, p_type=None):
    taskPts = [point(x, y, areaId, yaw, name=poiName, poiId=poiId,
                     acts=[act_open_doors(list(door_ids))], p_type=p_type)]
    return create_task(
        task_name, robot, RUN_TYPE[runType], SOURCE_TYPE[sourceType],
        taskPts=taskPts, runNum=int(runNum), taskType=TASK_TYPE[taskType],
        routeMode=ROUTE_MODE[routeMode], runMode=RUN_MODE[runMode],
        ignorePublicSite=False, speed=float(speed), detourRadius=1
    )

def task_close_door_wait(task_name, robot, areaId, x, y, yaw, poiId, poiName,
                         wait_s=10, runNum=1, taskType="delivery", runType="direct",
                         routeMode="sequential", runMode="flex_avoid",
                         door_ids=(1,2,3,4), speed=0.4, sourceType="sdk",
                         *, p_type=None):
    acts = [act_close_doors(list(door_ids)), act_pause(wait_s)]
    taskPts = [point(x, y, areaId, yaw, name=poiName, poiId=poiId, acts=acts, p_type=p_type)]
    return create_task(
        task_name, robot, RUN_TYPE[runType], SOURCE_TYPE[sourceType],
        taskPts=taskPts, runNum=int(runNum), taskType=TASK_TYPE[taskType],
        routeMode=ROUTE_MODE[routeMode], runMode=RUN_MODE[runMode],
        ignorePublicSite=False, speed=float(speed)
    )

def task_lift_raise_at_A(task_name, robot, areaId, x, y, yaw=0, useAreaId=None,
                         runNum=1, taskType="lift", runType="lift",
                         routeMode="sequential", runMode="flex_avoid",
                         speed=0.4, sourceType="sdk", *, p_type=None):
    taskPts = [point(x, y, areaId, yaw, acts=[act_lift_up(useAreaId or areaId)], p_type=p_type)]
    return create_task(
        task_name, robot, RUN_TYPE[runType], SOURCE_TYPE[sourceType],
        taskPts=taskPts, runNum=int(runNum), taskType=TASK_TYPE[taskType],
        routeMode=ROUTE_MODE[routeMode], runMode=RUN_MODE[runMode],
        speed=float(speed)
    )

def task_lift_lower_at_A(task_name, robot, areaId, x, y, yaw=0, useAreaId=None,
                         runNum=1, taskType="lift", runType="lift",
                         routeMode="sequential", runMode="flex_avoid",
                         speed=0.4, sourceType="sdk", *, p_type=None):
    taskPts = [point(x, y, areaId, yaw, acts=[act_lift_down(useAreaId or areaId)], p_type=p_type)]
    return create_task(
        task_name, robot, RUN_TYPE[runType], SOURCE_TYPE[sourceType],
        taskPts=taskPts, runNum=int(runNum), taskType=TASK_TYPE[taskType],
        routeMode=ROUTE_MODE[routeMode], runMode=RUN_MODE[runMode],
        speed=float(speed)
    )

def task_areaA_to_areaB_lift(task_name, robot,
                              A, A_areaId, B, B_areaId,  # A/B = (x,y,yaw[,type])
                              runNum=1, taskType="lift", runType="lift",
                              routeMode="sequential", runMode="flex_avoid",
                              speed=0.4, sourceType="sdk"):
    Ax, Ay, Ayaw, *At = A
    Bx, By, Byaw, *Bt = B
    Atype = At[0] if At else None
    Btype = Bt[0] if Bt else None
    pts = [
        point(Ax, Ay, A_areaId, Ayaw, name="A", poiId=A_areaId,
              acts=[act_lift_up(useAreaId=A_areaId)],
              p_type=(Atype if isinstance(Atype, int) else None)),
        point(Bx, By, B_areaId, Byaw, name="B", poiId=B_areaId,
              acts=[act_lift_down(useAreaId=B_areaId)],
              p_type=(Btype if isinstance(Btype, int) else None)),
    ]
    return create_task(
        task_name, robot, RUN_TYPE[runType], SOURCE_TYPE[sourceType],
        taskPts=pts, runNum=int(runNum), taskType=TASK_TYPE[taskType],
        routeMode=ROUTE_MODE[routeMode], runMode=RUN_MODE[runMode],
        speed=float(speed)
    )

def task_multi_wait_interaction(task_name, robot, pts,  # pts: [(x,y,yaw,areaId,name,id[,type]), ...]
                                runNum=1, taskType="delivery", runType="direct",
                                routeMode="sequential", runMode="flex_avoid",
                                backPt=None, ignorePublicSite=True,
                                speed=0.4, sourceType="head_app", detourRadius=1):
    taskPts = []
    for tup in pts:
        x, y, yaw, areaId, name, pid, *maybe_t = tup
        p_type = maybe_t[0] if (maybe_t and isinstance(maybe_t[0], int)) else None
        taskPts.append(point(x, y, areaId, yaw, name, pid, acts=[act_wait()], p_type=p_type))
    extra = _maybe("backPt", backPt)
    return create_task(
        task_name, robot, RUN_TYPE[runType], SOURCE_TYPE[sourceType],
        taskPts=taskPts, runNum=int(runNum), taskType=TASK_TYPE[taskType],
        routeMode=ROUTE_MODE[routeMode], runMode=RUN_MODE[runMode],
        ignorePublicSite=bool(ignorePublicSite), speed=float(speed),
        detourRadius=float(detourRadius), **extra
    )

def task_return_to_dock(task_name, robot, runNum=1, sourceType="sdk",
                        routeMode="sequential", runMode="flex_avoid",
                        speed=0.4):
    return create_task(
        task_name, robot, RUN_TYPE["charging_station"], SOURCE_TYPE[sourceType],
        taskPts=[], runNum=int(runNum), taskType=TASK_TYPE["return_to_dock"],
        routeMode=ROUTE_MODE[routeMode], runMode=RUN_MODE[runMode], speed=float(speed)
    )

"""
##########################################################################################
  Custom Tasks
##########################################################################################
"""

# action helpers for wrapper pattern
def _lift_up(use_area_id=None):   return {"type": ACTION["lift_up"],   "data": ({"useAreaId": use_area_id} if use_area_id else {})}
def _lift_down(use_area_id=None): return {"type": ACTION["lift_down"], "data": ({"useAreaId": use_area_id} if use_area_id else {})}
def _pause(sec):                  return {"type": ACTION["pause"],     "data": {"pauseTime": int(sec)}}

def _pt(x, y, areaId, yaw=0, ext_id=None, name=None, acts=None, stopRadius=1.0, p_type=None):
    p = {
        "x": x, "y": y, "yaw": yaw, "areaId": areaId, "stopRadius": stopRadius,
        "ext": {k: v for k, v in {"id": ext_id, "name": name}.items() if v is not None},
    }
    if acts:
        p["stepActs"] = acts
    if isinstance(p_type, int):
        p["type"] = p_type
    return p

# type maps used here
RUN_TYPE_LIFT  = RUN_TYPE["lift"]
TASK_TYPE_LIFT = TASK_TYPE["lift"]
SOURCE_PAGER   = SOURCE_TYPE["pager"]
ROUTE_SEQ      = ROUTE_MODE["sequential"]
RUNMODE_FLEX   = RUN_MODE["flex_avoid"]

def create_wrapper_task(
    task_name,
    robot,
    *,
    areaId_pickup,
    pickup,     # {"x","y","yaw","shelf_area_id", "type"?}
    wrapper,    # {"x","y","yaw", "type"?}
    waiting,    # {"x","y","yaw","pause_s", "type"?}
    dropdown,   # {"x","y","yaw","shelf_area_id", "type"?}
    speed=0.4,
    detourRadius=1.0,
):
    """
    Wrapper flow:
      1) pickup  -> lift_up(useAreaId=pickup.shelf_area_id)
      2) wrapper -> lift_down()
      3) waiting -> pause(waiting.pause_s)
      4) wrapper -> lift_up()
      5) dropdown-> lift_down(useAreaId=dropdown.shelf_area_id)
    All points use areaId_pickup to keep the map binding consistent.
    """
    pts = [
        _pt(pickup["x"], pickup["y"], areaId_pickup, pickup.get("yaw", 0),
            ext_id=pickup.get("shelf_area_id"),
            acts=[_lift_up(pickup.get("shelf_area_id"))],
            p_type=(pickup.get("type") if isinstance(pickup.get("type"), int) else None)),
        _pt(wrapper["x"], wrapper["y"], areaId_pickup, wrapper.get("yaw", 0),
            acts=[_lift_down()],
            p_type=(wrapper.get("type") if isinstance(wrapper.get("type"), int) else None)),
        _pt(waiting["x"], waiting["y"], areaId_pickup, waiting.get("yaw", 0),
            acts=[_pause(waiting.get("pause_s", 240))],
            p_type=(waiting.get("type") if isinstance(waiting.get("type"), int) else None)),
        _pt(wrapper["x"], wrapper["y"], areaId_pickup, wrapper.get("yaw", 0),
            acts=[_lift_up()],
            p_type=(wrapper.get("type") if isinstance(wrapper.get("type"), int) else None)),
        _pt(dropdown["x"], dropdown["y"], areaId_pickup, dropdown.get("yaw", 0),
            ext_id=dropdown.get("shelf_area_id"),
            acts=[_lift_down(dropdown.get("shelf_area_id"))],
            p_type=(dropdown.get("type") if isinstance(dropdown.get("type"), int) else None)),
    ]

    return create_task(
        task_name=task_name, robot=robot,
        runType=RUN_TYPE_LIFT, sourceType=SOURCE_PAGER,
        taskPts=pts, runNum=1, taskType=TASK_TYPE_LIFT,
        routeMode=ROUTE_SEQ, runMode=RUNMODE_FLEX,
        ignorePublicSite=False, speed=float(speed), detourRadius=float(detourRadius)
        # NOTE: deliberately no backPt here
    )
