
# """
# ##########################################################################################
#   Imports
# ##########################################################################################
# """

# #### api abstraction
# # from rich import pretty
# from rich import print as rptint
# from rich import inspect as rinspect

# # from __future__ import annotations
# import time
# import hashlib

# import logging
# import requests

# try:
#     import pandas as pd
# except ImportError:
#     pd = None  # Only used if caller asks for DataFrame

# # ---- Rich logging setup (drop-in, safe to call multiple times) ----
# try:
#     from rich.logging import RichHandler
#     _root = logging.getLogger()
#     if not any(isinstance(h, RichHandler) for h in _root.handlers):
#         logging.basicConfig(
#             level=logging.INFO,
#             format="%(message)s",
#             datefmt="[%X]",
#             handlers=[RichHandler(rich_tracebacks=True, show_time=True, show_level=True, show_path=False)],
#         )
# except Exception:
#     # Fall back silently if rich isn't installed; user can pip install rich
#     logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

# log = logging.getLogger(__name__)
# # pretty.install()
# """
# ##########################################################################################
#   Inits
# ##########################################################################################
# """

# ##### api reöated

# ## Ruwen's tokens:
# from dotenv import load_dotenv
# import io, os

# # Clean the file in place
# with open('.env', 'rb') as f:
#     data = f.read().replace(b'\x00', b'')

# with open('.env', 'wb') as f:
#     f.write(data)

# load_dotenv()

# app_id = os.getenv("APPID")
# app_secret = os.getenv("APPSECRET")
# app_code = os.getenv("APPCODE")

# ####### Urls:
# URL_BASE = r"https://apiglobal.autoxing.com"
# URL_ROUTING_DICT = {
#     "x-token" : r"/auth/v1.1/token",
#     "business_list" : r"/business/v1.1/list",
#     "robot_list" : r"/robot/v1.1/list",
#     "building_list" : r"/building/v1.1/list",
#     "create_task" : r"/task/v3/create",
#     "task_list" : r"/task/v1.1/list",
#     "task_details": r"/task/v3/taskId",
#     "cancel_task" : r"/task/v3/taskId/cancel",
#     "area_list" : r"/map/v1.1/area/list",
#     "poi_list" : r"/map/v1.1/poi/list",
#     "map_image" : r"/map/v1.1/area/areaId/base-map",
#     "execute_task" : r"/task/v1.1/taskId/execute",
#     "task_status" : r"/task/v2.0/taskId/state",
#     "robot_status" : r"/robot/v2.0/robotId/state",
#     "poi_details": r"/map/v1.1/poi/poiId",
# }

# #### sdk related





# ### raspberrypi related

# """
# ##########################################################################################
#   util
# ##########################################################################################
# """

# def try_get_unique_row(df, col, value):
#     matches = df[df[col] == value]
#     if len(matches) > 1:
#         log.warning("Expected Unique Id, Received duplicate values:")
#         print(matches)
#     if len(matches) == 1:
#         return matches.iloc[0]
#     return None

# def _build_url(base_url, path):
#     return base_url.rstrip("/") + "/" + str(path).lstrip("/")

# # from googletrans import Translator

# # translator = Translator()


# """
# ##########################################################################################
#   API Functions
# ##########################################################################################
# """

# #### auth

# def get_token():
#     ####### x-auth token
#     timestamp = int(time.time())
#     md5_hash = hashlib.md5()
    
#     signature = app_id + str(timestamp) + app_secret
#     md5_hash.update(signature.encode('utf-8'))
#     hash_result = md5_hash.hexdigest()
    
#     url = _build_url(URL_BASE, URL_ROUTING_DICT['x-token'])
#     r = requests.post(
#         url,
#         headers = {
#             "Authorization" : app_code
#         },
#         json = {
#             "appId" : app_id,
#             "timestamp" : timestamp,
#             "sign" : hash_result
#         })
#     try:
#         return r.json()["data"]["token"]
#     except Exception as exp:
#         log.exception("api abstraction error")
#         # rinspect(r)
#         return r.text

# X_TOKEN = get_token() #### remember to reset !

# ########### Decorators
# # def api_post(route_key):
# #     """
# #     Decorator: turns a payload-factory function into an API call.
# #     The wrapped function should return a dict payload (or None).
# #     """
# #     def deco(func):
# #         def wrapped(
# #             *,
# #             base_url,
# #             routes,
# #             token_provider,
# #             timeout=10.0,
# #             max_retries=3,
# #             as_dataframe=False,
# #             **kwargs
# #         ):
# #             url = _build_url(base_url, routes[route_key])
# #             headers = {
# #                 "Accept": "application/json",
# #                 "Content-Type": "application/json",
# #                 "X-Token": token_provider(),
# #             }
# #             payload = func(**kwargs) or {}

# #             data = None
# #             for attempt in range(1, max_retries + 1):
# #                 try:
# #                     log.debug("POST %s attempt=%d payload=%s", url, attempt, payload)
# #                     r = requests.post(url, json=payload, headers=headers, timeout=timeout)
# #                 except requests.RequestException as e:
# #                     log.warning("Network error on attempt %d: %s", attempt, e)
# #                 else:
# #                     try:
# #                         data = r.json()
# #                     except ValueError:
# #                         log.error("Non-JSON response from %s: %s", url, r.text[:300])
# #                         time.sleep(1); continue
# #                     if r.status_code in (401, 403):
# #                         raise RuntimeError(f"Auth failed ({r.status_code})")
# #                     if r.ok:
# #                         break
# #                     log.warning("API error on attempt %d: %s", attempt, data)
# #                 time.sleep(1)
# #             else:
# #                 raise RuntimeError(f"Failed to POST to {url} after {max_retries} attempts")

# #             lists = (((data or {}).get("data") or {}).get("lists")) or []
# #             if not isinstance(lists, list):
# #                 raise RuntimeError("'data.lists' is not a list")

# #             if as_dataframe:
# #                 try:
# #                     import pandas as pd
# #                 except ImportError:
# #                     raise ImportError("pandas not installed")
# #                 return pd.DataFrame(lists)

# #             return lists
# #         return wrapped
# #     return deco

# # # --- Use it: your function only defines the payload (if any) ---
# # @api_post("task_list")
# # def get_tasks_payload(payload=None):
# #     # do any payload shaping/validation here; or just pass through
# #     return payload or {}

# #### buildings and business
# def get_buildings():
#     url = _build_url(URL_BASE, URL_ROUTING_DICT['building_list'])
#     r = requests.post(
#         url,
#         headers = {
#             "X-Token" : X_TOKEN
#         },
#         json = {
            
#     })
#     try:
#         return pd.DataFrame(r.json()["data"]["lists"])
#     except Exception as exp:
#         log.exception("api abstraction error")
#         # rinspect(r)
#         return r.text
    
# buildings_df = get_buildings()


# def get_business(name=None):
#     url = _build_url(URL_BASE, URL_ROUTING_DICT['business_list'])
#     r = requests.post(
#         url,
#         headers = {
#             "X-Token" : X_TOKEN
#         },
#         json = {
            
#     })
#     try:
#         df = pd.DataFrame(r.json()["data"]["lists"])

#         if name:
#             df = df[df.name.str.startswith(name)]
#         return df
#     except Exception as exp:
#         log.exception("api abstraction error")
#         # rinspect(r)
#         return r.text
    
# business_df = get_business()

# #### robots

# def get_robots(robot_id = None):
#     url = _build_url(URL_BASE, URL_ROUTING_DICT['robot_list'])
#     r = requests.post(
#         url,
#         headers = {
#             "X-Token" : X_TOKEN
#         },
#         json = {
            
#     })
#     try:
#         df = pd.DataFrame(r.json()["data"]["list"])
#         df = pd.merge(df, business_df[["id","name"]].rename(columns={"id":"businessId", "name":"business_name"}), on="businessId", how="left")
#         # df['model_en'] = df['model'].apply(
#         #     lambda x: translator.translate(x, src='zh-cn', dest='en').text
#         # )
#         if robot_id:
#             df = df[df.robotId.str.endswith(robot_id)]
#         return df
#     except Exception as exp:
#         log.exception("api abstraction error")
#         rinspect(r)
#         return r.text
    
# robots_df = get_robots()

# def get_online_robots():
#     return robots_df[robots_df.isOnLine]
    
# def get_ef_robots():
#     return get_business_robots('EF') # use regex

# def get_business_robots(business_name_start):
#     ef_business_ids = get_business(business_name_start).id.values
#     robots = robots_df[robots_df['businessId'].isin(ef_business_ids)]
#     return robots

# def get_robot_curr_pos(robot):
#     x, y = robot.x, robot.y
#     return (x, y)

# def get_robot_status(robot):
#     url = _build_url(URL_BASE, URL_ROUTING_DICT["robot_status"].replace("robotId", robot.robotId))
#     r = requests.get(
#         url,
#         headers = {
#             "X-Token" : X_TOKEN
#         })
#     try:
#         return pd.DataFrame(r.json())
#     except Exception as exp:
#         # rinspect(r)
#         return r.text
#     # return r

# def connect_to_robot(robot):
#     return Robot(robot.robotId)

# ################# map
# from PIL import Image
# # import matplotlib.pyplot as plt

# from PIL import Image, UnidentifiedImageError  # <-- add this import

# def get_map_image(area_id):
#     url = _build_url(URL_BASE, URL_ROUTING_DICT["map_image"].replace("areaId", area_id))
#     r = requests.get(url, headers={"X-Token": X_TOKEN})
#     try:
#         img_data = r.content
#         image = Image.open(io.BytesIO(img_data))
#         return image
#     except UnidentifiedImageError:
#         log.info("UnidentifiedImageError")
#         return r.text
#     except Exception:
#         log.exception("api abstraction error")
#         return r.text

# # def plt_map_img(plt, img):
# #     plt.imshow(img)
# #     plt.axis('off')  # Hide axes
# #     plt.show()

# def get_pois(robot):
#     url = _build_url(URL_BASE, URL_ROUTING_DICT['poi_list'])
#     r = requests.post(
#         url,
#         headers = {
#             "X-Token" : X_TOKEN
#         },
#         json = {
#             "businessId" : robot.businessId,
#             "robotId" : robot.robotId,
#             "areaId" : robot.areaId
#     })
#     try:
#         return pd.DataFrame(r.json()['data']["list"])
#     except Exception as exp:
#         log.exception("api abstraction error")
#         # rinspect(r)
#         return r.text

# def get_poi_coordinates(robot, poi_name):
#     poi_df = get_pois(robot)
#     poi = try_get_unique_row(poi_df, "name", poi_name)
#     x, y = poi.coordinate[0], poi.coordinate[1]
#     return (x,y)

# def get_poi_details(robot, poi_name):
#     poi_df = get_pois(robot)
#     poi_id = try_get_unique_row(poi_df, "name", poi_name).id
#     url = _build_url(URL_BASE, URL_ROUTING_DICT["poi_details"].replace("poiId", poi_id))
#     r = requests.get(
#         url,
#         headers = {
#             "X-Token" : X_TOKEN
#         })
#     try:
#         return r.json()['data']
#     except Exception as exp:
#         log.exception("api abstraction error")
#         # rinspect(r)
#         return r.text

# def get_areas(robot):
#     url = _build_url(URL_BASE, URL_ROUTING_DICT['area_list'])
#     r = requests.post(
#         url,
#         headers = {
#             "X-Token" : X_TOKEN
#         },
#         json = {
#             "businessId" : robot.businessId,
#             "robotId" : robot.robotId
#     })
#     try:
#         return pd.DataFrame(r.json()['data']["list"])
#     except Exception as exp:
#         log.exception("api abstraction error")
#         # rinspect(r)
#         return r.text

# ########### tasks

# def get_tasks():
#     url = _build_url(URL_BASE, URL_ROUTING_DICT['task_list'])
#     r = requests.post(
#         url,
#         headers = {
#             "X-Token" : X_TOKEN
#         },
#         json = {
#             "pageSize": 100,
#             "pageNum" : 1,
#             # "startTime": sdk.time.time(),
#             # "endTime" : sdk.time.time() + 100,

#     })
#     try:
#         return pd.DataFrame(r.json()["data"]["list"])
#     except Exception as exp:
#         log.exception("api abstraction error")
#         # rinspect(r)
#         return r.text

# def execute_task(task_id):
#     url = _build_url(URL_BASE, URL_ROUTING_DICT["execute_task"].replace("taskId", task_id))
#     r = requests.post(
#         url,
#         headers = {
#             "X-Token" : X_TOKEN
#         },
#         json = {
#     })
#     try:
#       # return pd.DataFrame(r.json()['data']["list"])
#       return r.text
#     except Exception as exp:
#         log.exception("api abstraction error")
#     #   rinspect(r)
#     # raise NotImplementedError
#     # rinspect(r)
#         return r.text
#     # return r

# def cancel_task(task_id):
#     url = _build_url(URL_BASE, URL_ROUTING_DICT["cancel_task"].replace("taskId", task_id))
#     r = requests.post(
#         url,
#         headers = {
#             "X-Token" : X_TOKEN
#         },
#         json = {
#     })
#     try:
#       # return pd.DataFrame(r.json()['data']["list"])
#       return r.text
#     except Exception as exp:
#         log.exception("api abstraction error")
#       # rinspect(r)
#     # raise NotImplementedError
#     # rinspect(r)
#         return r.text
#     # return r

# def get_task_details(task_id):
#     url = _build_url(URL_BASE, URL_ROUTING_DICT["task_details"].replace("taskId", task_id))
#     r = requests.get(
#         url,
#         headers = {
#             "X-Token" : X_TOKEN
#         })
#     try:
#         return pd.DataFrame(r.json()['data'])
#     except Exception as exp:
#         log.exception("api abstraction error")
#         # rinspect(r)
#         return r.text

# def get_task_status(task_id):
#     url = _build_url(URL_BASE, URL_ROUTING_DICT["task_status"].replace("taskId", task_id))
#     r = requests.get(
#         url,
#         headers = {
#             "X-Token" : X_TOKEN
#         })
#     try:
#         return pd.DataFrame(r.json()['data'])
#     except Exception as exp:
#         log.exception("api abstraction error")
#         # rinspect(r)
#         return r.text

# # def create_task(task_name, robot, runType, sourceType, taskPts=[], runNum=1, taskType=5, routeMode=1, runMode=1, ignorePublicSite=False, speed=0.4, detourRadius=1, backPt={}):
# #     task_dict = {
# #       "name": task_name,
# #       "robotId": robot.robotId,
# #       "runNum": runNum,
# #       "taskType": taskType,
# #       "runType": runType, # 29 for lifting
# #       "routeMode": routeMode, # 1 for sequential routing , 2 for shortest distance routing
# #       "runMode": runMode, # 1 flexible obst avoi
# #       "taskPts": taskPts,
# #       "businessId": robot.df.businessId,
# #       "sourceType": sourceType, # 3, # for pager
# #       "ignorePublicSite": ignorePublicSite,
# #       "speed": speed, # 0.4 to 1
# #       "detourRadius": detourRadius, # safety dist in meters
# #       "backPt": backPt
# #     }

# #     url = _build_url(URL_BASE, URL_ROUTING_DICT['create_task'])
# #     r = requests.post(
# #         url,
# #         headers = {
# #             "X-Token" : X_TOKEN
# #         },
# #         json = task_dict
# #     )
# #     try:
# #       return pd.DataFrame(r.json()["data"])
# #     except Exception as exp:
# #         # log.exception("api abstraction error")
# #     # raise NotImplementedError
# #     #   rinspect(r)
# #         return r.text


# def create_task(
#     task_name,
#     robot,
#     runType,
#     sourceType,
#     taskPts=None,
#     runNum=1,
#     taskType=5,
#     routeMode=1,
#     runMode=1,
#     ignorePublicSite=False,
#     speed=0.4,
#     detourRadius=1,
#     backPt=None
# ):
#     if taskPts is None:
#         taskPts = []
#     if backPt is None:
#         backPt = {}

#     task_dict = {
#         "name": task_name,
#         "robotId": robot.robotId,
#         "businessId": robot.businessId,
#         "runNum": runNum,
#         "taskType": taskType,
#         "runType": runType,
#         "routeMode": routeMode,
#         "runMode": runMode,
#         "taskPts": taskPts,
#         "sourceType": sourceType,
#         "ignorePublicSite": ignorePublicSite,
#         "speed": speed,
#         "detourRadius": detourRadius,
#         "backPt": backPt,
#     }

#     url = _build_url(URL_BASE, URL_ROUTING_DICT['create_task'])
#     r = requests.post(url, headers={"X-Token": X_TOKEN}, json=task_dict)

#     if r.status_code != 200:
#         raise RuntimeError(f"Task creation failed {r.status_code}: {r.text}")

#     try:
#         data = r.json()
#     except Exception:
#         raise RuntimeError(f"Invalid JSON response: {r.text}")

#     if data.get("status") != 200:
#         raise RuntimeError(f"API error: {data}")

#     # Return the useful stuff, not a DataFrame
#     return data["data"]   # e.g. contains taskId, etc.



# """
# ##########################################################################################
#   Classes
# ##########################################################################################
# """

# # class Client():
# #     def __init__(self):
# #         ...
# #     def _get():
# #     def _post_json():

# #     def get_buildings():
# #     def get_business():
# #     def get_robots(): # as classes

# class Robot():
#     def __init__(self, serial_number):
#         self.SN = serial_number
#         self.refresh()
#         self.business = try_get_unique_row(business_df,'id',self.df.businessId).name
#         # self.building = try_get_unique_row(get_buildings(),'id',self.df.buildingId).name

#     def refresh(self):
#         self.df = try_get_unique_row(get_robots(), 'robotId', self.SN)

#     def __str__(self):
#         # Human-friendly description
#         rinspect(self, methods=True)
#         return ""
#         # return None

#     def __repr__(self):
#         # Debug/developer-friendly with all key attributes
#         return f"{self.__class__.__name__}(id={self.SN!r}, business={self.business}, model={self.df.model}, isOnLine={self.df.isOnLine})"

#     def get_map_image(self):
#         return get_map_image(self.df.areaId)

#     def get_pois(self):
#         return get_pois(self.df)

#     def get_poi_coordinates(self, poi_name):
#         return get_poi_coordinates(self.df, poi_name)
    
#     def get_poi_details(self, poi_name):
#         return get_poi_details(self.df, poi_name)

#     def get_areas(self):
#         return get_areas(self.df)

# ##### require refresh

#     def get_curr_pos(self):
#         self.refresh()
#         return get_robot_curr_pos(self.df)
#     def get_status(self):
#         self.refresh()
#         if self.df.isOnLine:
#             return get_robot_status(self.df)
#         log.info("robot is offline")
#         return pd.DataFrame(columns=["status","message","data"])


#     # def execute_task(self, task_id):
#     #     raise NotImplementedError

#     # def get_task_details(self, task_id):
#     #     raise NotImplementedError

#     # def get_task_status(self, task_id):
#     #     raise NotImplementedError

#     # def create_task(self, task_dict):
#     #     raise NotImplementedError

#     # def get_tasks(self, task_dict):
#     #     raise NotImplementedError

#     # def get_business(self, task_dict):
#     #     raise NotImplementedError

#     # def get_buildings(self, task_dict):
#     #     raise NotImplementedError

#     # def get_robots(self, task_dict):
#     #     raise NotImplementedError

#     # def cancel_task(self):
#     #     raise NotImplementedError

# """
# ##########################################################################################
#   Raspberrypi abstractions
# ##########################################################################################
# """

# ##### web requests

# # import requests

# # # Replace with the machine's API endpoint
# # url = "http://192.168.1.100/start"  
# # payload = {"command": "start"}  # Depends on machine API
# # headers = {"Content-Type": "application/json"}

# # response = requests.post(url, json=payload, headers=headers)

# # if response.status_code == 200:
# #     print("Wrapping machine started successfully.")
# # else:
# #     print(f"Failed to start machine: {response.status_code} {response.text}")

# ######### GPIO output

# # import RPi.GPIO as GPIO
# # import time

# # GPIO.setmode(GPIO.BCM)
# # relay_pin = 18  # GPIO pin connected to relay
# # GPIO.setup(relay_pin, GPIO.OUT)

# # print("Turning on wrapping machine...")
# # GPIO.output(relay_pin, GPIO.HIGH)  # Close relay (simulate button press)
# # time.sleep(1)                      # Hold for 1 second
# # GPIO.output(relay_pin, GPIO.LOW)   # Release relay

# # GPIO.cleanup()
# # print("Done.")


# ##### serial client


# # from pymodbus.client import ModbusSerialClient

# # # For RS-485 / Modbus RTU
# # client = ModbusSerialClient(port='/dev/ttyUSB0', baudrate=9600, parity='N', stopbits=1, bytesize=8, timeout=2)

# # if client.connect():
# #     # Example: Write to coil 1 (turn machine ON)
# #     result = client.write_coil(1, True, unit=1)
# #     if result.isError():
# #         print("Failed to send command.")
# #     else:
# #         print("Machine start command sent.")
# #     client.close()
# # else:
# #     print("Failed to connect to machine.")


# ##### SPI Input

# # import spidev

# # # SPI setup for MCP3008 ADC
# # spi = spidev.SpiDev()
# # spi.open(0, 0)  # Bus 0, Device (CS) 0
# # spi.max_speed_hz = 1350000

# # # Read MCP3008 channel function
# # def read_adc(channel):
# #     if channel < 0 or channel > 7:
# #         raise ValueError("ADC channel must be 0-7")
# #     adc = spi.xfer2([1, (8 + channel) << 4, 0])
# #     data = ((adc[1] & 3) << 8) + adc[2]
# #     return data  # 0-1023 range (10-bit ADC)


# ##### GPIO Input

# # import RPi.GPIO as GPIO
# # import time

# # # Use BCM pin numbering
# # GPIO.setmode(GPIO.BCM)

# # # List of input pins you want to check
# # input_pins = [17, 27, 22]  # Change these to your desired GPIO pins

# # # Set up pins as inputs with pull-down resistors
# # for pin in input_pins:
# #     GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# # print("Reading GPIO inputs (press Ctrl+C to exit)...")

# # try:
# #     while True:
# #         for pin in input_pins:
# #             state = GPIO.input(pin)
# #             print(f"GPIO {pin}: {'HIGH' if state else 'LOW'}")
# #         time.sleep(0.5)  # Delay between readings
# # except KeyboardInterrupt:
# #     print("\nExiting...")
# # finally:
# #     GPIO.cleanup()


"""
##########################################################################################
  Imports
##########################################################################################
"""
from rich import print as rprint
from rich import inspect as rinspect

import time
import hashlib
import logging
import requests
import io, os

try:
    import pandas as pd
except ImportError:
    pd = None

# ---- Rich logging (safe to call multiple times) ----
try:
    from rich.logging import RichHandler
    _root = logging.getLogger()
    if not any(isinstance(h, RichHandler) for h in _root.handlers):
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler(rich_tracebacks=True, show_time=True, show_level=True, show_path=False)],
        )
except Exception:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

log = logging.getLogger(__name__)

"""
##########################################################################################
  Inits
##########################################################################################
"""
from dotenv import load_dotenv

# Clean .env of stray nulls (windows copy/paste issue sometimes)
if os.path.exists(".env"):
    with open(".env", "rb") as f:
        data = f.read().replace(b"\x00", b"")
    with open(".env", "wb") as f:
        f.write(data)

load_dotenv()

app_id     = os.getenv("APPID")
app_secret = os.getenv("APPSECRET")
app_code   = os.getenv("APPCODE")

URL_BASE = r"https://apiglobal.autoxing.com"
URL_ROUTING_DICT = {
    "x-token"      : r"/auth/v1.1/token",
    "business_list": r"/business/v1.1/list",
    "robot_list"   : r"/robot/v1.1/list",
    "building_list": r"/building/v1.1/list",
    "create_task"  : r"/task/v3/create",
    "task_list"    : r"/task/v1.1/list",
    "task_details" : r"/task/v3/taskId",
    "cancel_task"  : r"/task/v3/taskId/cancel",
    "area_list"    : r"/map/v1.1/area/list",
    "poi_list"     : r"/map/v1.1/poi/list",
    "map_image"    : r"/map/v1.1/area/areaId/base-map",
    "execute_task" : r"/task/v1.1/taskId/execute",
    "task_status"  : r"/task/v2.0/taskId/state",
    "robot_status" : r"/robot/v2.0/robotId/state",
    "poi_details"  : r"/map/v1.1/poi/poiId",
}

def try_get_unique_row(df, col, value):
    matches = df[df[col] == value]
    if len(matches) > 1:
        log.warning("Expected unique value for %s=%r, got duplicates.", col, value)
        print(matches)
    if len(matches) == 1:
        return matches.iloc[0]
    return None

def _build_url(base_url, path):
    return base_url.rstrip("/") + "/" + str(path).lstrip("/")

def get_token():
    timestamp = int(time.time())
    signature = app_id + str(timestamp) + app_secret
    md5_hash = hashlib.md5()
    md5_hash.update(signature.encode("utf-8"))
    url = _build_url(URL_BASE, URL_ROUTING_DICT['x-token'])
    r = requests.post(url, headers={"Authorization": app_code},
                      json={"appId": app_id, "timestamp": timestamp, "sign": md5_hash.hexdigest()})
    try:
        return r.json()["data"]["token"]
    except Exception:
        log.exception("get_token failed: %s", r.text)
        return r.text

X_TOKEN = get_token()

########################
# Lists / lookups
########################
def get_buildings():
    url = _build_url(URL_BASE, URL_ROUTING_DICT['building_list'])
    r = requests.post(url, headers={"X-Token": X_TOKEN}, json={})
    try:
        return pd.DataFrame(r.json()["data"]["lists"])
    except Exception:
        log.exception("get_buildings error")
        return pd.DataFrame()

def get_business(name=None):
    url = _build_url(URL_BASE, URL_ROUTING_DICT['business_list'])
    r = requests.post(url, headers={"X-Token": X_TOKEN}, json={})
    try:
        df = pd.DataFrame(r.json()["data"]["lists"])
        if name:
            df = df[df.name.astype(str).str.startswith(name)]
        return df
    except Exception:
        log.exception("get_business error")
        return pd.DataFrame()

business_df = get_business()

def get_robots(robot_id=None):
    url = _build_url(URL_BASE, URL_ROUTING_DICT['robot_list'])
    r = requests.post(url, headers={"X-Token": X_TOKEN}, json={})
    try:
        df = pd.DataFrame(r.json()["data"]["list"])
        df = pd.merge(df, business_df[["id","name"]].rename(columns={"id":"businessId","name":"business_name"}),
                      on="businessId", how="left")
        if robot_id:
            df = df[df.robotId.astype(str).str.endswith(str(robot_id))]
        return df
    except Exception:
        log.exception("get_robots error")
        return pd.DataFrame()

robots_df = get_robots()

def get_online_robots():
    try:
        return robots_df[robots_df.isOnLine]
    except Exception:
        return pd.DataFrame()

def get_business_robots(prefix):
    try:
        ids = get_business(prefix).id.values
        return robots_df[robots_df['businessId'].isin(ids)]
    except Exception:
        return pd.DataFrame()

def get_ef_robots():
    return get_business_robots('EF')

########################
# Robot helpers
########################
from PIL import Image, UnidentifiedImageError

def get_map_image(area_id):
    url = _build_url(URL_BASE, URL_ROUTING_DICT["map_image"].replace("areaId", str(area_id)))
    r = requests.get(url, headers={"X-Token": X_TOKEN})
    try:
        image = Image.open(io.BytesIO(r.content))
        return image
    except UnidentifiedImageError:
        log.info("UnidentifiedImageError when decoding map image")
        return r.text
    except Exception:
        log.exception("get_map_image error")
        return r.text

def get_pois(robot_row):
    url = _build_url(URL_BASE, URL_ROUTING_DICT['poi_list'])
    r = requests.post(url, headers={"X-Token": X_TOKEN},
                      json={"businessId": robot_row.businessId, "robotId": robot_row.robotId, "areaId": robot_row.areaId})
    try:
        return pd.DataFrame(r.json()['data']["list"])
    except Exception:
        log.exception("get_pois error")
        return pd.DataFrame()

def get_poi_coordinates(robot_row, poi_name):
    poi_df = get_pois(robot_row)
    poi = try_get_unique_row(poi_df, "name", poi_name)
    return (poi.coordinate[0], poi.coordinate[1]) if poi is not None else (None, None)

def get_poi_details(robot_row, poi_name):
    poi_df = get_pois(robot_row)
    row = try_get_unique_row(poi_df, "name", poi_name)
    if row is None:
        return {}
    poi_id = row.id
    url = _build_url(URL_BASE, URL_ROUTING_DICT["poi_details"].replace("poiId", str(poi_id)))
    r = requests.get(url, headers={"X-Token": X_TOKEN})
    try:
        return r.json()['data']
    except Exception:
        log.exception("get_poi_details error")
        return {}

def get_areas(robot_row):
    url = _build_url(URL_BASE, URL_ROUTING_DICT['area_list'])
    r = requests.post(url, headers={"X-Token": X_TOKEN},
                      json={"businessId": robot_row.businessId, "robotId": robot_row.robotId})
    try:
        return pd.DataFrame(r.json()['data']["list"])
    except Exception:
        log.exception("get_areas error")
        return pd.DataFrame()

def get_robot_curr_pos(robot_row):
    return (robot_row.x, robot_row.y)

def get_robot_status(robot_row):
    url = _build_url(URL_BASE, URL_ROUTING_DICT["robot_status"].replace("robotId", str(robot_row.robotId)))
    r = requests.get(url, headers={"X-Token": X_TOKEN})
    try:
        return pd.DataFrame(r.json())
    except Exception:
        return pd.DataFrame()

########################
# Tasks
########################
def get_tasks():
    url = _build_url(URL_BASE, URL_ROUTING_DICT['task_list'])
    r = requests.post(url, headers={"X-Token": X_TOKEN}, json={"pageSize": 100, "pageNum": 1})
    try:
        return pd.DataFrame(r.json()["data"]["list"])
    except Exception:
        log.exception("get_tasks error")
        return pd.DataFrame()

import requests
import pandas as pd
import logging as log

def get_most_recent_task(robot_id: str):
    url = _build_url(URL_BASE, URL_ROUTING_DICT['task_list'])
    page_num = 1
    all_tasks = []

    while True:
        r = requests.post(
            url,
            headers={"X-Token": X_TOKEN},
            json={"pageSize": 100, "pageNum": page_num}
        )

        try:
            data = r.json()["data"]["list"]
        except Exception:
            log.exception("get_tasks error")
            break

        if not data:
            break  # no more pages

        all_tasks.extend(data)
        page_num += 1

    if not all_tasks:
        return None

    df = pd.DataFrame(all_tasks)

    # filter for the robotId
    df = df[df["robotId"] == robot_id]

    if df.empty:
        return None

    # pick the row with the largest createTime
    most_recent = df.loc[df["createTime"].idxmax()]

    return most_recent


def execute_task(task_id):
    url = _build_url(URL_BASE, URL_ROUTING_DICT["execute_task"].replace("taskId", str(task_id)))
    r = requests.post(url, headers={"X-Token": X_TOKEN}, json={})
    return r.text

def cancel_task(task_id):
    url = _build_url(URL_BASE, URL_ROUTING_DICT["cancel_task"].replace("taskId", str(task_id)))
    r = requests.post(url, headers={"X-Token": X_TOKEN}, json={})
    return r.text

def get_task_details(task_id):
    url = _build_url(URL_BASE, URL_ROUTING_DICT["task_details"].replace("taskId", str(task_id)))
    r = requests.get(url, headers={"X-Token": X_TOKEN})
    try:
        return pd.DataFrame(r.json()['data'])
    except Exception:
        log.exception("get_task_details error")
        return pd.DataFrame()

def get_task_status(task_id):
    url = _build_url(URL_BASE, URL_ROUTING_DICT["task_status"].replace("taskId", str(task_id)))
    r = requests.get(url, headers={"X-Token": X_TOKEN})
    try:
        return pd.DataFrame(r.json()['data'])
    except Exception:
        log.exception("get_task_status error")
        return pd.DataFrame()
def create_task(
    task_name,
    robot,
    runType,
    sourceType,
    taskPts=None,
    runNum=1,
    taskType=5,
    routeMode=1,
    runMode=1,
    ignorePublicSite=False,
    speed=0.4,
    detourRadius=1,
    backPt=None,   # keep default None
):
    if taskPts is None:
        taskPts = []

    task_dict = {
        "name": task_name,
        "robotId": robot.robotId,
        "businessId": robot.businessId,
        "runNum": runNum,
        "taskType": taskType,
        "runType": runType,
        "routeMode": routeMode,
        "runMode": runMode,
        "taskPts": taskPts,
        "sourceType": sourceType,
        "ignorePublicSite": ignorePublicSite,
        "speed": speed,
        "detourRadius": detourRadius,
    }
    # ✅ only include when truthy ({} is falsy)
    if isinstance(backPt, dict) and backPt:
        task_dict["backPt"] = backPt
    rprint(task_dict)
    url = _build_url(URL_BASE, URL_ROUTING_DICT['create_task'])
    r = requests.post(url, headers={"X-Token": X_TOKEN}, json=task_dict)
    rinspect(r)
    if r.status_code != 200:
        raise RuntimeError(f"Task creation failed {r.status_code}: {r.text}")

    try:
        data = r.json()
    except Exception:
        raise RuntimeError(f"Invalid JSON response: {r.text}")

    if data.get("status") != 200:
        raise RuntimeError(f"API error: {data}")

    return data["data"]



########################
# Robot class
########################
class Robot():
    def __init__(self, serial_number):
        self.SN = serial_number
        self.refresh()
        try:
            self.business = try_get_unique_row(business_df, 'id', self.df.businessId).name
        except Exception:
            self.business = ""

    def refresh(self):
        self.df = try_get_unique_row(get_robots(), 'robotId', self.SN)

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.SN!r}, business={self.business}, model={getattr(self.df,'model',None)}, isOnLine={getattr(self.df,'isOnLine',None)})"

    def get_map_image(self):
        return get_map_image(self.df.areaId)

    def get_pois(self):
        return get_pois(self.df)

    # def get_poi_coordinates(self, poi_name):
    #     return get_poi_coordinates(self.df, poi_name)

    def get_poi_details(self, poi_name):
        return get_poi_details(self.df, poi_name)

    def get_areas(self):
        return get_areas(self.df)

    def get_curr_pos(self):
        self.refresh()
        return get_robot_curr_pos(self.df)

    def get_status(self):
        self.refresh()
        if getattr(self.df, "isOnLine", False):
            return get_robot_status(self.df)
        log.info("robot is offline")
        return pd.DataFrame(columns=["status","message","data"])
