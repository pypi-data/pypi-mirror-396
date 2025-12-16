# encoding:utf-8

from __future__ import unicode_literals

import datetime
import gzip
import json
import os
import queue
import re
import threading
import time
from enum import Enum
from urllib.parse import urlparse

import requests
from requests import ConnectionError

__NAME_REGULAR_EXPRESSION = "^\\${0,1}([a-z][a-z\\d_]{0,49})|([a-z][a-z\\d_]{0,50})|(__[a-z][a-z\\d_]{0,50})$"
__NAME_PATTERN = re.compile(__NAME_REGULAR_EXPRESSION, re.I)
__version__ = '1.0.6'

LIB_NAME = "python"
LIB_VERSION = __version__

GE_ROTATE_MODE = Enum('GE_ROTATE_MODE', ('DAILY', 'HOURLY'))


def get_now_time() -> int:
    return int(time.time() * 1000)


def is_str(s):
    return isinstance(s, str)


def is_int(n):
    return isinstance(n, int)


def is_number(s):
    if is_int(s):
        return True
    if isinstance(s, float):
        return True
    return False


def assert_properties(action_type, properties):
    if properties is not None:
        for key, value in properties.items():
            if not is_str(key):
                raise GEIllegalDataException("Property key must be a str. [key=%s]" % str(key))

            if value is None:
                continue

            if not __NAME_PATTERN.match(key):
                raise GEIllegalDataException(
                    "type[%s] property key must be a valid variable name. [key=%s]" % (action_type, str(key)))

            if 'user_increment' == action_type.lower() and not is_number(value) and not key.startswith('#'):
                raise GEIllegalDataException('user_increment properties must be number type')


def ge_log(msg=None):
    if msg is not None and is_print:
        print('[GEData][%s] %s' % (datetime.datetime.now(), msg))


class GEException(Exception):
    pass


class GEIllegalDataException(GEException):
    pass


class GENetworkException(GEException):
    pass


class GEDynamicSuperPropertiesTracker(object):
    def __init__(self):
        pass

    def get_dynamic_super_properties(self):
        raise NotImplementedError


class GEDateTimeSerializer(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
            fmt = "%Y-%m-%d %H:%M:%S.%f"
            return obj.strftime(fmt)[:-3]
        return json.JSONEncoder.default(self, obj)


class GEAnalytics(object):
    __strict = False
    profile_send_types = {
        'user_set': 'profile_set',
        'user_set_once': 'profile_set_once',
        'user_increment': 'profile_increment',
        'user_max': 'profile_number_max',
        'user_min': 'profile_number_min',
        'user_append': 'profile_append',
        'user_uniq_append': 'profile_uniq_append',
        'user_unset': 'profile_unset',
        'user_del': 'profile_delete',
    }

    def __init__(self, consumer, enable_uuid=False, strict=None):
        """
        - GELogConsumer: Write local files in batches
        - GEBatchConsumer: Transfer data to the GE server in batches(synchronous blocking)
        - GEAsyncBatchConsumer:Transfer data to the GE server in batches(asynchronous blocking)
        - GEDebugConsumer: Send data one by one, and strictly verify the data format

        Parameters:
        - consumer -- required
        - enable_uuid -- true,false
        """

        self.__consumer = consumer
        if isinstance(consumer, GEDebugConsumer):
            self.__strict = True
        if strict is not None:
            self.__strict = strict

        self.__enableUuid = enable_uuid
        self.__super_properties = {}
        self.clear_super_properties()
        ge_log("init SDK success")

    def user_set(self, client_id=None, properties=None):
        """
        Set user property

        Parameters:
        - client_id: str
        - properties: dict

        Raises:
        - GEIllegalDataException
        """
        self.__add(client_id=client_id, send_type='user_set', properties_add=properties)

    def user_unset(self, client_id=None, properties=None):
        """
        clear user property

        Parameters:
        - client_id: str
        - properties: list, e.g. ['name', 'age']

        Raises:
            GEIllegalDataException
        """
        if isinstance(properties, list):
            properties = dict((key, 0) for key in properties)
        self.__add(client_id=client_id, send_type='user_unset', properties_add=properties)

    def user_set_once(self, client_id=None, properties=None):
        """
        If the user property you want to upload only needs to be set once,you can call user_set_once to set it.
        When the property has value before, this item will be ignored.

        Parameters:
        - client_id: string
        - properties: dict

        Raises:
            GEIllegalDataException
        """
        self.__add(client_id=client_id, send_type='user_set_once', properties_add=properties)

    def user_increment(self, client_id=None, properties=None):
        """
        Parameters:
        - client_id: string
        - properties: dict. value must be number. e.g. {'count': 1}

        Raises:
            GEIllegalDataException
        """
        self.__add(client_id=client_id, send_type='user_increment', properties_add=properties)

    def user_max(self, client_id=None, properties=None):
        """
        Parameters:
        - client_id: string
        - properties: dict. value must be number. e.g. {'count': 1}

        Raises:
            GEIllegalDataException
        """
        self.__add(client_id=client_id, send_type='user_max', properties_add=properties)

    def user_min(self, client_id=None, properties=None):
        """
        Parameters:
        - client_id: string
        - properties: dict. value must be number. e.g. {'count': 1}

        Raises:
            GEIllegalDataException
        """
        self.__add(client_id=client_id, send_type='user_min', properties_add=properties)

    def user_append(self, client_id=None, properties=None):
        """
        Parameters:
        - client_id: string
        - properties: dict

        Raises:
            GEIllegalDataException
        """
        self.__add(client_id=client_id, send_type='user_append', properties_add=properties)

    def user_uniq_append(self, client_id=None, properties=None):
        """
        Parameters:
        - client_id: string
        - properties: dict

        Raises:
            GEIllegalDataException
        """
        self.__add(client_id=client_id, send_type='user_uniq_append',
                   properties_add=properties)

    def user_del(self, client_id=None):
        """
        Delete user form GE.

        Parameters:
        - client_id: string

        Raises:
            GEIllegalDataException
        """
        self.__add(client_id=client_id, send_type='user_del')

    def track(self, client_id=None, event_name=None, properties=None):
        """
        Parameters:
        - client_id: string
        - event_name: string
        - properties: dict

        Raises:
            GEIllegalDataException
        """
        all_properties = self._public_track_add(event_name, properties)
        self.__add(client_id=client_id, send_type='track', event_name=event_name,
                   properties_add=all_properties)

    def flush(self):
        """
        Upload data immediately
        """
        ge_log("flush data immediately")
        self.__consumer.flush()

    def close(self):
        """
        Please call this api before exiting to avoid data loss in the cache
        """
        ge_log("close SDK")
        self.__consumer.close()

    def _public_track_add(self, event_name, properties):
        if not is_str(event_name):
            raise GEIllegalDataException('a string type event_name is required for track')

        all_properties = {
            '$lib': 'ge_python_sdk',
            '$lib_version': __version__,
        }
        all_properties.update(self.__super_properties)
        if properties:
            all_properties.update(properties)
        return all_properties
        pass

    def __add(self, client_id, send_type, event_name=None, properties_add=None):
        if self.__strict:
            is_empty_client_id = client_id is None or (isinstance(client_id, str) and len(str(client_id)) <= 0)
            if is_empty_client_id:
                raise GEException("client_id must be set  ")

        is_track = send_type == 'track'

        if not is_track and send_type not in self.profile_send_types.keys():
            raise GEException("send_type error")
        data = {}
        if send_type == '':

            data = {'client_id': client_id,
                    }
            if properties_add:
                data.update(properties_add)
        else:
            pass
            if is_track:
                if self.__strict and (
                        event_name is None or (isinstance(event_name, str) and len(str(event_name)) <= 0)):
                    raise GEException("event name must not be null")

            one_event = {}
            if properties_add:
                properties = properties_add.copy()
            else:
                properties = {}
            self.__move_preset_properties(["#ip", "#first_check_id", "#app_id", "#time", '#uuid'], data, properties)
            if self.__strict:
                assert_properties(send_type, properties)

            self.__buildData(data, 'client_id', client_id)

            _type = 'track' if is_track else 'profile'
            event = self.profile_send_types.get(send_type, event_name)
            self.__buildData(one_event, 'type', _type)
            self.__buildData(one_event, 'event', event)

            self.__buildData(one_event, 'time', get_now_time())
            self.__buildData(one_event, 'time_free', False)
            if is_track:
                properties['$lib'] = LIB_NAME
                properties['$lib_version'] = LIB_VERSION
            one_event['properties'] = properties

            data['event_list'] = [one_event]
        content = json.dumps(data, separators=(str(','), str(':')), cls=GEDateTimeSerializer)
        content_dict = json.loads(content)
        self.__consumer.add(content_dict)

    def __buildData(self, data, key, value):
        if value is not None:
            data[key] = value

    def __move_preset_properties(self, keys, data, properties):
        for key in keys:
            if key in properties.keys():
                data[key] = properties.get(key)
                del (properties[key])

    def clear_super_properties(self):
        self.__super_properties = {
            '$lib': LIB_NAME,
            '$lib_version': LIB_VERSION,
        }

    def set_super_properties(self, super_properties):
        """
        Parameters:
        - super_properties: dict
        """
        self.__super_properties.update(super_properties)

    @staticmethod
    def enableLog(isPrint=False):
        """
        Is enable SDK ge_log
        """
        global is_print
        is_print = isPrint


if os.name == 'nt':
    import msvcrt


    def _lock(file_):
        try:
            save_pos = file_.tell()
            file_.seek(0)
            try:
                msvcrt.locking(file_.fileno(), msvcrt.LK_LOCK, 1)
            except IOError as e:
                raise GEException(e)
            finally:
                if save_pos:
                    file_.seek(save_pos)
        except IOError as e:
            raise GEException(e)


    def _unlock(file_):
        try:
            save_pos = file_.tell()
            if save_pos:
                file_.seek(0)
            try:
                msvcrt.locking(file_.fileno(), msvcrt.LK_UNLCK, 1)
            except IOError as e:
                raise GEException(e)
            finally:
                if save_pos:
                    file_.seek(save_pos)
        except IOError as e:
            raise GEException(e)
elif os.name == 'posix':
    import fcntl


    def _lock(file_):
        try:
            fcntl.flock(file_.fileno(), fcntl.LOCK_EX)
        except IOError as e:
            raise GEException(e)


    def _unlock(file_):
        fcntl.flock(file_.fileno(), fcntl.LOCK_UN)
else:
    raise GEException("Python SDK is defined for NT and POSIX system.")


class _GEFileLock(object):
    def __init__(self, file_handler):
        self._file_handler = file_handler

    def __enter__(self):
        _lock(self._file_handler)
        return self

    def __exit__(self, t, v, tb):
        _unlock(self._file_handler)


class GELogConsumer(object):
    """
    Write data to local files in batches
    """
    _mutex = queue.Queue()
    _mutex.put(1)

    class _FileWriter(object):
        _writers = {}
        _writeMutex = queue.Queue()
        _writeMutex.put(1)

        @classmethod
        def instance(cls, filename):
            cls._writeMutex.get(block=True, timeout=None)
            try:
                if filename in cls._writers.keys():
                    result = cls._writers[filename]
                    result._count = result._count + 1
                else:
                    result = cls(filename)
                    cls._writers[filename] = result
                return result
            finally:
                cls._writeMutex.put(1)

        def __init__(self, filename):
            self._filename = filename
            self._file = open(self._filename, 'a')
            self._count = 1

        def close(self):
            GELogConsumer._FileWriter._writeMutex.get(block=True, timeout=None)
            try:
                self._count = self._count - 1
                if self._count == 0:
                    self._file.close()
                    del GELogConsumer._FileWriter._writers[self._filename]
            finally:
                GELogConsumer._FileWriter._writeMutex.put(1)

        def is_valid(self, filename):
            return self._filename == filename

        def write(self, messages):
            with _GEFileLock(self._file):
                for message in messages:
                    if isinstance(message, dict):
                        message = json.dumps(message, separators=(str(','), str(':')), cls=GEDateTimeSerializer)
                    self._file.write(message)
                    self._file.write('\n')
                self._file.flush()
                ge_log("Write data to file, count: {msgCount}".format(msgCount=len(messages)))

    @classmethod
    def construct_filename(cls, directory, date_suffix, file_size, file_prefix):
        filename = file_prefix + ".log." + date_suffix \
            if file_prefix is not None else "log." + date_suffix

        if file_size > 0:
            count = 0
            file_path = directory + filename + "_" + str(count)
            while os.path.exists(file_path) and cls.file_size_out(file_path, file_size):
                count = count + 1
                file_path = directory + filename + "_" + str(count)
            return file_path
        else:
            return directory + filename

    @classmethod
    def file_size_out(cls, file_path, file_size):
        f_size = os.path.getsize(file_path)
        f_size = f_size / float(1024 * 1024)
        if f_size >= file_size:
            return True
        return False

    @classmethod
    def unlock_logging_consumer(cls):
        cls._mutex.put(1)

    @classmethod
    def lock_logging_consumer(cls):
        cls._mutex.get(block=True, timeout=None)

    def __init__(self, log_directory, log_size=0, buffer_size=5, rotate_mode=GE_ROTATE_MODE.DAILY, file_prefix=None):
        """
        Write data to file

        Parameters:
        - log_directory: str. The directory where the ge_log files are saved
        - log_size: The size of a single ge_log file, in MB, log_size <= 0 means no limit on the size of a single file
        - buffer_size: The amount of data written to the file each time, the default is to write 5 pieces at a time
        - rotate_mode: Log splitting mode, by default splitting by day
        - file_prefix: ge_log file prefix
        """
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
        self.log_directory = log_directory
        self.sdf = '%Y-%m-%d-%H' if rotate_mode == GE_ROTATE_MODE.HOURLY else '%Y-%m-%d'
        self.suffix = datetime.datetime.now().strftime(self.sdf)
        self._fileSize = log_size
        if not self.log_directory.endswith("/"):
            self.log_directory = self.log_directory + "/"

        self._buffer = []
        self._buffer_size = buffer_size
        self._file_prefix = file_prefix
        self.lock_logging_consumer()
        filename = GELogConsumer.construct_filename(self.log_directory, self.suffix, self._fileSize, self._file_prefix)
        self._writer = GELogConsumer._FileWriter.instance(filename)
        self.unlock_logging_consumer()
        ge_log("init GELogConsumer")

    def add(self, msg):
        log = "Enqueue data = {msg}"
        ge_log(log.format(msg=msg))

        messages = None
        self.lock_logging_consumer()
        self._buffer.append(msg)
        if len(self._buffer) > self._buffer_size:
            messages = self._buffer
            self.refresh_writer()
            self._buffer = []

        if messages:
            self._writer.write(messages)
        self.unlock_logging_consumer()

    def flush_with_close(self, is_close):
        messages = None
        self.lock_logging_consumer()
        if len(self._buffer) > 0:
            messages = self._buffer
            self.refresh_writer()
            self._buffer = []
        if messages:
            self._writer.write(messages)
        if is_close:
            self._writer.close()
        self.unlock_logging_consumer()

    def refresh_writer(self):
        date_suffix = datetime.datetime.now().strftime(self.sdf)
        if self.suffix != date_suffix:
            self.suffix = date_suffix
        filename = GELogConsumer.construct_filename(self.log_directory, self.suffix, self._fileSize,
                                                    self._file_prefix)
        if not self._writer.is_valid(filename):
            self._writer.close()
            self._writer = GELogConsumer._FileWriter.instance(filename)

    def flush(self):
        self.flush_with_close(False)

    def close(self):
        self.flush_with_close(True)


class GEBatchConsumer(object):
    _batch_lock = threading.RLock()
    _cachelock = threading.RLock()

    def __init__(self, server_uri, batch=20, timeout=30000, interval=3, compress=True, max_cache_size=50):
        """
        Report data by http (synchronized)

        Parameters:
        - server_uri: str
        - batch: Specify the number of data to trigger uploading, the default is 20, and the maximum is 200 .
        - timeout: Request timeout, in milliseconds, default is 30000 ms .
        - interval: The maximum time interval for uploading data, in seconds, the default is 3 seconds .
        - compress: is compress data when request .
        - max_cache_size: cache size
        """
        self.__interval = interval
        self.__batch = min(batch, 200)
        self.__message_channel = []
        self.__max_cache_size = max_cache_size
        self.__cache_buffer = []
        self.__last_flush = time.time()
        self.__http_service = _HttpServices(server_uri, timeout)
        self.__http_service.compress = compress
        ge_log("init GEBatchConsumer")

    def add(self, msg):
        self._batch_lock.acquire()
        try:
            self.__message_channel.append(msg)
        finally:
            self._batch_lock.release()
        if len(self.__message_channel) >= self.__batch \
                or len(self.__cache_buffer) > 0:
            self.flush_once()

    def flush(self, throw_exception=True):
        while len(self.__cache_buffer) > 0 or len(self.__message_channel) > 0:
            try:
                self.flush_once(throw_exception)
            except GEIllegalDataException:
                continue

    def flush_once(self, throw_exception=True):
        if len(self.__message_channel) == 0 and len(self.__cache_buffer) == 0:
            return

        self._cachelock.acquire()
        self._batch_lock.acquire()
        try:
            try:
                if len(self.__message_channel) == 0 and len(self.__cache_buffer) == 0:
                    return
                if len(self.__cache_buffer) == 0 or len(self.__message_channel) >= self.__batch:
                    self.__cache_buffer.append(self.__message_channel)
                    self.__message_channel = []
            finally:
                self._batch_lock.release()
            msg = self.__cache_buffer[0]
            _msg = [json.dumps(i) for i in msg]
            self.__http_service.send('[' + ','.join(_msg) + ']', str(len(_msg)))
            self.__last_flush = time.time()
            self.__cache_buffer = self.__cache_buffer[1:]
        except GENetworkException as e:
            if throw_exception:
                raise e
        except GEIllegalDataException as e:
            self.__cache_buffer = self.__cache_buffer[1:]
            if throw_exception:
                raise e
        finally:
            if len(self.__cache_buffer) > self.__max_cache_size:
                self.__cache_buffer = self.__cache_buffer[1:]
            self._cachelock.release()

    def close(self):
        self.flush()

    pass


class GEAsyncBatchConsumer(object):

    def __init__(self, server_uri, interval=3, flush_size=20, queue_size=100000):
        """
        Report data by http (asynchronous)

        Parameters:
        - server_uri: str
        - interval: The maximum time interval for uploading data, in seconds, the default is 3 seconds
        - flush_size: The threshold of the queue cache, if this value is exceeded, it will be sent immediately
        - queue_size: The size of the storage queue
        """
        self.__http_service = _HttpServices(server_uri, 30000)
        self.__batch = flush_size
        self.__queue = queue.Queue(queue_size)

        self.__flushing_thread = self._AsyncFlushThread(self, interval)
        self.__flushing_thread.daemon = True
        self.__flushing_thread.start()
        ge_log("init AsyncBatchConsumer")

    def add(self, msg):
        try:
            self.__queue.put_nowait(msg)
        except queue.Full as e:
            raise GENetworkException(e)

        if self.__queue.qsize() > self.__batch:
            self.flush()

    def flush(self):
        self.__flushing_thread.flush()

    def close(self):
        self.flush()
        self.__flushing_thread.stop()
        while not self.__queue.empty():
            self._perform_request()

    def _perform_request(self):

        flush_buffer = []
        while len(flush_buffer) < self.__batch:
            try:
                flush_buffer.append(self.__queue.get_nowait())
            except queue.Empty:
                break

        if len(flush_buffer) > 0:
            for i in range(3):  # Retry 3 times in case of network exception
                try:
                    flush_buffer2 = [json.dumps(i) for i in flush_buffer]
                    _flush_buffer = '[' + ','.join(flush_buffer2) + ']'
                    self.__http_service.send(_flush_buffer, str(len(_flush_buffer)))
                    return True
                except GENetworkException:
                    pass
                except GEIllegalDataException:
                    break

    class _AsyncFlushThread(threading.Thread):
        def __init__(self, consumer, interval):
            threading.Thread.__init__(self)
            self._consumer = consumer
            self._interval = interval

            self._stop_event = threading.Event()
            self._finished_event = threading.Event()
            self._flush_event = threading.Event()

        def flush(self):
            self._flush_event.set()

        def stop(self):
            """
            Use of this method needs to be adjusted when exiting to ensure that the safe line program ends safely.
            """
            self._stop_event.set()
            self._finished_event.wait()

        def run(self):
            while True:
                self._flush_event.wait(self._interval)
                self._consumer._perform_request()
                self._flush_event.clear()
                if self._stop_event.is_set():
                    break
            self._finished_event.set()


def _gzip_string(data):
    try:
        return gzip.compress(data)
    except AttributeError:
        import StringIO
        buf = StringIO.StringIO()
        fd = gzip.GzipFile(fileobj=buf, mode="w")
        fd.write(data)
        fd.close()
        return buf.getvalue()


class _HttpServices(object):
    def __init__(self, server_uri, timeout=30000):
        self.url = server_uri
        self.timeout = timeout
        self.compress = True

    def send(self, data, length):
        """
        Parameters:
            data: str
            length: int. string length
        Raises:
            GEIllegalDataException: 
            GENetworkException: network error
        """
        headers = {'GE-Integration-Type': 'python-sdk', 'GE-Integration-Version': __version__,
                   'GE-Integration-Count': length,
                   'Content-Type': 'application/json',
                   }
        try:
            compress_type = 'gzip'
            json_data = json.loads(data)
            event_list = []
            for i in json_data:
                event_list.extend(i['event_list'])
            json_data_list = json_data[0]
            json_data_list['event_list'] = event_list
            if self.compress:
                json_data_list_str = json.dumps(json_data_list)
                data = _gzip_string(json_data_list_str.encode("utf-8"))
                headers['Gravity-Content-Compress'] = compress_type
            else:
                # compress_type = 'none'
                # data = data.encode("utf-8")
                data = json_data_list
            _json_data = data
            ge_log('request_data={}'.format(_json_data))
            if self.compress:
                response = requests.post(self.url, data=_json_data, headers=headers, timeout=self.timeout)
            else:
                response = requests.post(self.url, json=_json_data, headers=headers, timeout=self.timeout)
            response_data = json.loads(response.text)

            if response.status_code == 200:
                ge_log('response={}'.format(response_data))
                if response_data["code"] == 0:
                    return True
                else:
                    raise GEIllegalDataException("Unexpected result code: " + str(response_data["code"]))
            else:
                ge_log('response={}'.format(response.status_code))
                raise GENetworkException("Unexpected Http status code " + str(response.status_code))
        except ConnectionError as e:
            time.sleep(0.5)
            raise GENetworkException("Data transmission failed due to " + repr(e))


class GEDebugConsumer(object):
    """
    The server will strictly verify the data. When a certain attribute does not meet the specification,
    the entire data will not be stored. When the data format is wrong, an exception message containing detailed reasons
    will be thrown. It is recommended to use this Consumer first to debug buried point data.
    """

    def __init__(self, server_uri, timeout=30000, write_data=True, device_id=""):
        """
        Init debug consumer

        Parameters:
        - server_uri: str
        - timeout: Request timeout, in milliseconds, default is 30000 ms
        - write_data: write data to GE or not
        - device_id: debug device in GE
        """
        server_url = urlparse(server_uri)
        debug_url = server_url
        self.__server_uri = debug_url.geturl()
        self.__timeout = timeout
        self.__writer_data = write_data
        self.__device_id = device_id
        GEAnalytics.enableLog(True)
        ge_log("init DebugConsumer")

    def add(self, msg):
        try:
            dry_run = 0
            if not self.__writer_data:
                dry_run = 1
            params = msg
            headers = {
                'Content-Type': 'application/json',
                'Turbo-Debug-Mode': '1',
            }

            ge_log('request={}'.format(params))

            response = requests.post(self.__server_uri,
                                     json=params,
                                     timeout=self.__timeout,
                                     headers=headers,
                                     )
            response_data = json.loads(response.text)

            if response.status_code == 200:
                ge_log('response={}'.format(response_data))
                if response_data["code"] == 0:
                    return True
                else:
                    print("Unexpected result : \n %s" % response_data)
            else:
                raise GENetworkException("Unexpected http status code: " + str(response.status_code))
        except ConnectionError as e:
            time.sleep(0.5)
            raise GENetworkException("Data transmission failed due to " + repr(e))

    def flush(self, throw_exception=True):
        pass

    def close(self):
        pass
