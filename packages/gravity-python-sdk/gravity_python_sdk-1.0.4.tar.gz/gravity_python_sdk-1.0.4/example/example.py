# encoding:utf-8
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from gesdk.sdk import *

GEAnalytics.enableLog(isPrint=True)
GE_ACCESS_TOKEN = 'xxx'
GE_SERVER_MAIN_URL = f'https://backend.gravity-engine.com/event_center/api/v1/event/collect/?access_token={GE_ACCESS_TOKEN}'

exited_client_id = '_test_client_id_0'
test_client_id = exited_client_id
test_user_prop_set_once = 'setonce1'
test_user_prop_unset = 'userunset0'
test_user_prop_init_type = 'setnum1'
test_user_prop_list_type = 'userlist0'
test_client_id_delete = 'py-sdk_test2025_11_06_18_02_03'
user_prop_common = "$name"
compress = True
compress = False
consumer = GEDebugConsumer(server_uri=GE_SERVER_MAIN_URL, device_id='')
# consumer = GEBatchConsumer(server_uri=GE_SERVER_MAIN_URL, compress=compress, )
# consumer = GEAsyncBatchConsumer(server_uri=GE_SERVER_MAIN_URL)
# consumer = GELogConsumer("./log", rotate_mode=GE_ROTATE_MODE.HOURLY, buffer_size=1)


ge = GEAnalytics(consumer, strict=True)

try:
    user_properties = {user_prop_common: f'user_$name{datetime.datetime.now()}', 'count': 1, 'arr': ['111', '222']}
    ge.user_set(client_id=test_client_id, properties=user_properties)
except Exception as e:
    raise GEIllegalDataException(e)

try:
    user_properties = {test_user_prop_init_type: 100}
    ge.user_increment(client_id=test_client_id, properties=user_properties)
except Exception as e:
    raise GEIllegalDataException(e)

try:
    user_set_once_properties = {test_user_prop_set_once: "111"}
    ge.user_set_once(test_client_id, user_set_once_properties)
except Exception as e:
    raise GEIllegalDataException(e)

try:
    user_set_once_properties = {test_user_prop_set_once: "222"}
    ge.user_set_once(test_client_id, user_set_once_properties)
except Exception as e:
    raise GEIllegalDataException(e)

try:
    user_properties = {test_user_prop_init_type: 100}
    ge.user_increment(client_id=test_client_id, properties=user_properties)
except Exception as e:
    raise GEIllegalDataException(e)

try:
    user_properties = {test_user_prop_init_type: 20000}
    ge.user_max(client_id=test_client_id, properties=user_properties)
except Exception as e:
    raise GEIllegalDataException(e)

try:
    user_properties = {test_user_prop_init_type: 10}
    ge.user_min(client_id=test_client_id, properties=user_properties)
except Exception as e:
    raise GEIllegalDataException(e)

try:
    user_properties = {test_user_prop_list_type: ["a", "a"]}
    ge.user_append(client_id=test_client_id, properties=user_properties)
except Exception as e:
    raise GEIllegalDataException(e)

try:
    user_properties = {test_user_prop_list_type: ["a", "b", "c", "c"]}
    ge.user_uniq_append(client_id=test_client_id, properties=user_properties)
except Exception as e:
    raise GEIllegalDataException(e)

try:
    user_properties = {test_user_prop_unset: "xxx"}
    ge.user_set(client_id=test_client_id, properties=user_properties)
except Exception as e:
    raise GEIllegalDataException(e)

try:
    user_properties = {test_user_prop_unset: ""}
    ge.user_unset(client_id=test_client_id, properties=user_properties)
except Exception as e:
    raise GEIllegalDataException(e)

try:
    user_properties = {user_prop_common: "py-name"}
    ge.user_set(client_id=test_client_id_delete, properties=user_properties)
except Exception as e:
    raise GEIllegalDataException(e)

try:
    user_properties = {user_prop_common: ""}
    ge.user_unset(client_id=test_client_id_delete, properties=user_properties)
except Exception as e:
    raise GEIllegalDataException(e)

try:
    ge.user_del(client_id=test_client_id_delete)
except Exception as e:
    raise GEIllegalDataException(e)

_time = datetime.datetime.now()
event_properties = {
    "$city": f'py-event_$city{datetime.datetime.now()}',
    "age": 18,
    "name": "hello",
    "array": ["a", "🙂", "😀"]
}

try:
    ge.track(client_id=test_client_id, event_name="$AppStart", properties=event_properties)
except Exception as e:
    raise GEIllegalDataException(e)

eventProperties_1 = {
    "age": 18,
    "name": "hello",
}

try:
    ge.track(client_id=test_client_id,
             event_name="$AppStart",
             properties=eventProperties_1)
except Exception as e:
    raise GEIllegalDataException(e)

ge.flush()
ge.close()
