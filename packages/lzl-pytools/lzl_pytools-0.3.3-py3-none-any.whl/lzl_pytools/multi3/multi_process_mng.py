import time
import uuid
import multiprocessing
import queue
import os
import logging
import logging.handlers
import traceback
import random
import asyncio
import aiohttp
import json

from .aio_task_runner import AioTaskRunner
from .parallel_config import ParallelConfig, AioParallelConfig, TaskMonitorInfo

def defautl_logger_setup(logger=None, log_filename='', log_level=logging.WARNING, 
                         file_show_log=True, stdout_show_log=False, log_dir='', make_subdir=False, file_delay=False):
    if logger is None:
        logger = logging.getLogger()
    logger.setLevel(log_level)
    formatter = logging.Formatter("%(asctime)s %(levelname)s - %(message)s")
    if file_show_log:
        if make_subdir:
            log_dir = os.path.join(log_dir, time.strftime("%Y-%m-%d_%H-%M-%S") + '_' + uuid.uuid4().hex[0:8])
        if log_dir != '':
            os.makedirs(log_dir, exist_ok=True)
        if log_filename == '':
            log_filename = 'run_%s_%s.log' % (time.strftime("%Y-%m-%d_%H-%M-%S"), uuid.uuid4().hex[0:8])
        file_handler = logging.handlers.RotatingFileHandler(os.path.join(log_dir, log_filename), maxBytes=18 * 1024 * 1024, backupCount=100, delay=file_delay)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    if stdout_show_log:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger

PROC_TYPE_PRODUCER = 1
PROC_TYPE_CONSUMER = 2

class ProcessProc:
    def __init__(self, user_data, *args, **kwargs) -> None:
        self.p_idx = kwargs['p_idx']
        self.p_type = kwargs['p_type']
        self.stop_event = kwargs['stop_event']
        self.queue:multiprocessing.Queue = kwargs['queue']
        self.msg_queue:multiprocessing.Queue = kwargs['msg_queue']
        self.user_data:dict = user_data
        self.counter_info = TaskMonitorInfo()
        self.counter_interval = 1 
        self.put_counter_time = time.time()
    def pre_start(self):
        pass
    def pre_stop(self):
        pass
    def step_run(self):   # str, is_exit. str is in [norun, success, fail, except]
        return 'norun', False
    def run(self):
        try:
            while not self.stop_event.is_set():
                start_time = time.time()
                self.counter_info.rec_start()
                rslt, is_exit = self.step_run()
                if rslt == 'norun':
                    self.counter_info.reverse_start()  # 回退1次
                else:
                    self.counter_info.rec_end(rslt, time.time() - start_time)
                self.put_counter()
                if is_exit:
                    break
        except KeyboardInterrupt:
            pass
        self.put_counter(force=True)
    def put_data(self, data): # is only called by producer
        self.queue.put(data)
        self.counter_info.rec_msg() 
        self.put_counter()
    def get_data(self):  # is only called by consumer
        self.put_counter()
        try:
            data = self.queue.get_nowait()
            self.counter_info.rec_msg()
            return data
        except queue.Empty:
            return None
    def _put_msg(self, msg_type, data):
        self.msg_queue.put({'type': msg_type, 'p_type': self.p_type, 'p_idx': self.p_idx, 'data': data})
    def put_msg(self, msg_type, data):
        self._put_msg(msg_type, data)
        self.put_counter()
    def put_counter(self, force=False):
        cur_time = time.time()
        if cur_time - self.put_counter_time >= self.counter_interval or force:
            self.put_counter_time = cur_time
            self._put_msg('_counter', self.counter_info.get_json_and_clear())
    def put_log(self, level, text):
        self.put_msg('_log', {'level': level, 'text': text})
    def info(self, text):
        self.put_log(logging.INFO, text)
    def warning(self, text):
        self.put_log(logging.WARNING, text)
    def error(self, text):
        self.put_log(logging.ERROR, text)
    def critical(self, text):
        self.put_log(logging.CRITICAL, text)

def _processProc(ProcessProcClass, user_data, p_idx, p_type, queue, stop_event, msg_queue):
    proc = ProcessProcClass(user_data, p_idx=p_idx, queue=queue, stop_event=stop_event, p_type=p_type, msg_queue=msg_queue)
    proc.pre_start()
    proc.run()
    proc.pre_stop()
    # print('================> stop', p_idx)

class MultiProcessMng:
    def __init__(self, queue_size=100, queue_num=1, msg_queue_size=65535, log_counter=True, logger=None) -> None:
        self.queue_size = queue_size
        self.queues = [multiprocessing.Queue(maxsize=queue_size) for i in range(queue_num)]
        self.stop_event = multiprocessing.Event()
        self.producers = []
        self.consumers = []
        self.msg_queue = multiprocessing.Queue(maxsize=msg_queue_size)

        self.producer_counter = TaskMonitorInfo()
        self.consumer_counter = TaskMonitorInfo()
        self.is_log_counter = log_counter
        self.logger = logger
        if self.logger is None:
            self.logger = logging.getLogger()
    def _startProcess(self, p_type, ProcessProcClass, num_process=5, user_data=None):
        ps = []
        for p_idx in range(num_process):
            p = multiprocessing.Process(target=_processProc, args=(ProcessProcClass, user_data, p_idx, p_type,
                    self.queues[p_idx % len(self.queues)], self.stop_event, self.msg_queue))
            p.start()
            ps.append(p)
        return ps
    def start_producer(self, ProcessProcClass, num_producers=5, user_data=None):
        self.producers = self._startProcess(PROC_TYPE_PRODUCER, ProcessProcClass, num_producers, user_data)
    def start_consumer(self, ProcessProcClass, num_consumers=2, user_data=None):
        self.consumers = self._startProcess(PROC_TYPE_CONSUMER, ProcessProcClass, num_consumers, user_data)
    def stop(self, timeout=1):
        t = time.time()
        self.stop_event.set()
        # for q in self.queues:  # the queue may be block when queue is full.. should use terminate
        #     for _ in range(self.queue_size):
        #         import queue
        #         try:
        #             q.get_nowait()
        #         except queue.Empty:
        #             break
        ps = self.consumers + self.producers
        for p in ps:
            try:
                diff = time.time() - t
                if diff < timeout:
                    p.join(timeout=max(min(timeout - diff, timeout), 0.001))
                if p.is_alive():
                    p.terminate()
                p.join()
                # print('===> join end xx')
            except KeyboardInterrupt:
                p.terminate()
                p.join()
    def run(self, max_task_num=-1, run_time_len=-1, callback=None, callback_interval=1, msg_callback=None):
        start_time = time.time()
        prev_time = start_time
        while True:
            cur_time = time.time()
            if run_time_len > 0 and cur_time - start_time >= run_time_len:
                self.stop_event.set()
                break
            if max_task_num > 0 and self.consumer_counter.end >= max_task_num:
                self.stop_event.set()
                break
            
            if cur_time - prev_time >= callback_interval:
                self.log_counter()
                prev_time = cur_time
                if callback and callback(self):
                    break

            is_continue, is_exit = self.msg_proc(msg_callback)
            if is_continue:
                continue
            if is_exit:
                break
            time.sleep(0.05)
        self.log_counter()
        if callback:
            callback(self)

    def log_counter(self):
        if self.is_log_counter:
            self.logger.warning(f'producer:{self.producer_counter}  consumer:{self.consumer_counter}')
    def msg_proc(self, callback):
        try:
            msg = self.msg_queue.get_nowait()
            msg_type = msg.get('type', '')
            # self.logger.warning(f'====> {msg}')
            if msg_type == '_counter':
                if msg['p_type'] == PROC_TYPE_PRODUCER:
                    self.producer_counter.add_one_json(msg['data'])
                elif msg['p_type'] == PROC_TYPE_CONSUMER:
                    self.consumer_counter.add_one_json(msg['data'])
            elif msg_type == '_log':
                self.logger.log(msg['data']['level'], msg['data']['text'])
            elif callback:
                return callback(msg, self)
            return True, False
        except queue.Empty:
            return False, False

# producer示例
class ProducerProc(ProcessProc):
    def producer_proc(self):
        return 'success', False  # 'fail', False

    def step_run(self):
        try:
            return self.producer_proc()
        except:
            self.error(f'excet: {traceback.format_exc()}')
            time.sleep(0.1)
            return 'except', False

# 从task_queue中不断取数据，然后生产msg，推送
class TaskProducerProc(ProcessProc):
    @staticmethod
    def init_task_queue(tasks):
        task_queue = multiprocessing.Queue()
        for idx, task in enumerate(tasks):
            task_queue.put([idx, task])
        return task_queue

    def pre_start(self):
        self.task_queue = self.user_data.get('data').get('task_queue')

    def task_proc(self, task_idx, task):
        return 'success', False  # 'fail', False

    def step_run(self):
        while True:
            try:
                task_idx, task = self.task_queue.get_nowait()
                break
            except queue.Empty:
                time.sleep(3)
                return 'norun', False
        self.info(f"start task_idx={task_idx}, {task}")
        try:
            return self.task_proc(task_idx, task)
        except:
            self.error(f'excet: {task_idx}, {task}, {traceback.format_exc()}')
            time.sleep(0.1)
            return 'except', False

# 从消息队列取数据消费
class ConsumerProc(ProcessProc):
    def consumer_proc(self, data):
        return 'success', False  # 'fail', False

    def step_run(self):
        try:
            data = self.get_data()
            if data is None:
                time.sleep(0.1)
                return 'norun', False
            return self.consumer_proc(data)
        except:
            self.error(f'excet: {data}, {traceback.format_exc()}')
            time.sleep(0.1)
            return 'except', False

class AioHttpRunProc(ProcessProc):
    def pre_start(self):
        self.parallel_cfg:AioParallelConfig = self.user_data['_sys_cfg']['parallel_cfg']
        # self.runner = AioTaskRunner(self.parallel_cfg.one_parallel_task_num, lambda para: self.put_counter(force=True))
        self.runner = AioTaskRunner(self.parallel_cfg.one_parallel_task_num)
    def run(self):
        try:
            if self.parallel_cfg.no_wait:
                asyncio.run(self.runner.run_times_per_second(self.parallel_cfg.aio_parallel_num, self._task_proc))
            else:
                asyncio.run(self.runner.parallel_run(self.parallel_cfg.aio_parallel_num, self._task_proc))
        except KeyboardInterrupt:
            self.runner.stop()
        except asyncio.CancelledError:
            pass
    async def _task_proc(self, session: aiohttp.ClientSession, parallet_id, task_idx, user_data):
        if self.stop_event.is_set():
            self.runner.stop_flag = True
            return
        req_data = self.get_data()
        if req_data is None:
            await asyncio.sleep(0.01)
            return
        req_start_time = time.time()
        self.counter_info.rec_start()
        rslt = await self._req(session, req_data)
        self.counter_info.rec_end(rslt, time.time() - req_start_time)
    async def _req(self, session: aiohttp.ClientSession, req_data):
        try:
            rsp = await session.post(url=req_data[0], headers=req_data[1], data=req_data[2], timeout=self.parallel_cfg.timeout, ssl=False)
            text = await rsp.text()
            if rsp.status != 200:
                self.error(f"rsp err: {rsp.status}, {text}")
            print(json.loads(text))
        except Exception as e:
            self.error(f'send excet: {traceback.format_exc()}')
            await asyncio.sleep(0.01)
            return 'except'
        return 'success'

def start_multi_task(config:ParallelConfig, ProducerProcClass=ProcessProc, ConsumerProcClass=ProcessProc, data={}, 
                     callback=None, callback_interval=1, msg_callback=None):
    _sys_cfg = {'parallel_cfg': config}
    mng = MultiProcessMng(queue_size=config.queue_size, queue_num=config.queue_num)
    try:
        mng.start_producer(ProducerProcClass, config.producer_num, {'_sys_cfg': _sys_cfg, 'data': data})
        mng.start_consumer(ConsumerProcClass, config.consumer_num, {'_sys_cfg': _sys_cfg, 'data': data})
        mng.run(max_task_num=config.max_task_num, run_time_len=config.run_time_len, 
                callback=callback, callback_interval=callback_interval, msg_callback=msg_callback)
    except KeyboardInterrupt:
        pass
    finally:
        mng.stop()

def normal_end_by_task_num(task_num):
    def func(mng:MultiProcessMng):
        nonlocal task_num
        if mng.producer_counter.end == task_num and mng.producer_counter.msg == mng.consumer_counter.end:
            return True
    return func

def run_aio_parallel_task(parallel_cfg:AioParallelConfig, ProducerProcClass=ProcessProc, ConsumerProcClass=AioHttpRunProc,
    data={}, callback=None, callback_interval=1, msg_callback=None, log_counter=True):
    _sys_cfg = {'parallel_cfg': parallel_cfg}
    mng = MultiProcessMng(parallel_cfg.queue_size, parallel_cfg.queue_num, log_counter=log_counter)
    try:
        mng.start_producer(ProducerProcClass, parallel_cfg.producer_num, {'_sys_cfg': _sys_cfg, 'data': data})
        time.sleep(3)
        mng.start_consumer(ConsumerProcClass, parallel_cfg.consumer_num, {'_sys_cfg': _sys_cfg, 'data': data})
        time.sleep(2)
        mng.run(max_task_num=parallel_cfg.max_task_num, run_time_len=parallel_cfg.run_time_len, 
            callback=callback, callback_interval=callback_interval, msg_callback=msg_callback)
    except KeyboardInterrupt:
        pass
    finally:
        mng.stop()
    return mng
