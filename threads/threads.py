import abc
import multiprocessing
import queue
import signal
import traceback
from typing import Set, Dict, TypeVar, Generic

from impulse.core import job_printer
from impulse.core import debug as dbg


class Messages(object):
  EMPTY_RESPONSE = 'Internal: Empty Response'
  TIMEOUT = 'Job Waiter Timed Out'


class Task():
  def __init__(self, func, *args, **kwargs):
    self.func = func
    self.args = args
    self.kwargs = kwargs

  def Run(self):
    return self.func(*self.args, **self.kwargs)

  def __repr__(self):
    return str(self)

  def __str__(self):
    return f'{self.func.__name__}({" ".join(str(x) for x in self.args)})'


class NullTask(Task):
  def __init__(self):
    pass

  def __eq__(self, other):
    return isinstance(other, NullTask)


class JobResponse(object):
  class LEVEL(object):
    FATAL = '__L_FATAL__'
    WARNING = '__L_WARNING__'
    YELLOW = '__L_YELLOW__'
    GREEN = '__L_GREEN__'

  def __init__(self, level:str, job_id:int, message:str='', result=None):
    self._level = level
    self._msg = message
    self._result = result or []
    self._id = job_id

  def level(self) -> str:
    return self._level

  def message(self) -> str:
    return self._msg

  def result(self) -> [Task]:
    return self._result

  def id(self) -> int:
    return self._id


class Worker(multiprocessing.Process):
  POISON = NullTask()
  def __init__(self,
               worker_id:int,
               job_input_queue:multiprocessing.JoinableQueue,
               job_response_queue:multiprocessing.Queue):
    super().__init__()
    self._id = worker_id
    self._job_input_queue = job_input_queue
    self._job_response_queue = job_response_queue
    self.name = f'Watchdog#{self._id}'

  def _Fail(self, exc:Exception):
    self._job_response_queue.put(JobResponse(
        JobResponse.LEVEL.FATAL, self._id,
        message=str(exc)))
    traceback.print_exc()

  def run(self):
    while True:
      job = Worker.POISON
      try:
        job = self._job_input_queue.get(timeout=5)
      except:
        self._job_response_queue.put(JobResponse(
          JobResponse.LEVEL.WARNING, self._id,
          message=Messages.TIMEOUT))
        continue

      if job == Worker.POISON:
        self._job_input_queue.task_done()
        self._job_input_queue.join()
        return

      self._job_response_queue.put(JobResponse(
        JobResponse.LEVEL.YELLOW, self._id, message=str(job)))

      try:
        job_result = job.Run()
      except Exception as e:
        self._job_input_queue.task_done()
        self._Fail(e)
        continue

      self._job_response_queue.put(JobResponse(
        JobResponse.LEVEL.GREEN, self._id,
        result=job_result))
      self._job_input_queue.task_done()


class ThreadPool(multiprocessing.Process):
  def __init__(self, poolcount:int, debug:bool = False):
    super().__init__()
    if debug:
      dbg.EnableDebug()
    self._job_response_queue:queue.Queue[JobResponse] = multiprocessing.Queue()
    self._job_input_queue:queue.Queue[Task] = multiprocessing.JoinableQueue()
    self._pool_count:int = poolcount
    self._printer = job_printer.JobPrinter(0, poolcount)
    self._input = None
    self._error_message = None
    self._workers = []
    self._active_tasks = 0


  def Start(self, data:Task, threaded=True):
    self._input = data
    self._create_workers()
    if threaded:
      self.start()
    else:
      self.run()

  def run(self):
    self._addTask(self._input)
    self._run_loop()

  def _addTask(self, task):
    self._active_tasks += 1
    self._printer.add_job_count(1)
    self._job_input_queue.put(task)

  def _isFinished(self):
    return not (self._active_tasks or self._job_input_queue.qsize())

  def _create_workers(self):
    for i in range(self._pool_count):
      worker = Worker(
        worker_id = i,
        job_input_queue = self._job_input_queue,
        job_response_queue = self._job_response_queue)
      worker.start()
      self._workers.append(worker)

  def _kill_workers(self):
    for _ in range(self._pool_count):
      self._job_input_queue.put(Worker.POISON)
    self._job_input_queue.join()
    for worker in self._workers:
      worker.kill()

  def _run_loop(self):
    while True:
      if self._isFinished():
        self._kill_workers()
        self._printer.finished()
        return

      if self._active_tasks:
        response = self._job_response_queue.get()
        if not response:
          self._kill_workers()
          self._printer.finished(err=Messages.EMPTY_RESPONSE)

        if response.level() == JobResponse.LEVEL.FATAL:
          self._active_tasks -= 1
          self._kill_workers()
          self._printer.finished(err=response.message())
          return

        if response.level() == JobResponse.LEVEL.WARNING:
          self._active_tasks -= 1
          pass

        if response.level() == JobResponse.LEVEL.YELLOW:
          self._printer.write_task_msg(response.id(), response.message())

        if response.level() == JobResponse.LEVEL.GREEN:
          self._active_tasks -= 1
          self._printer.remove_task_msg(response.id())
          for task in response.result():
            self._addTask(task)









