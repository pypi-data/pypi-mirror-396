# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2024/11/4 下午2:10
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""
import functools
import multiprocessing
import threading
import warnings

from joblib import Parallel, delayed
import logair
from .exceptions import WarnException, FailTaskError
from .delay import delay

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from tqdm.auto import tqdm

logger = logair.get_logger("ygo")

def run_job(job, task_id, queue):
    """执行任务并更新队列"""
    try:
        result = job()
    except WarnException as e:
        logger.warning(FailTaskError(task_name=job.task_name, error=e))
        result = None
    except Exception as e:
        logger.error(FailTaskError(task_name=job.task_name, error=e), exc_info=e)
        result = None
    queue.put((task_id, 1))
    return result


def update_progress_bars(tqdm_objects: list[tqdm],
                         task_ids,
                         queue: multiprocessing.Queue,
                         num_tasks: int,
                         task_counts: dict):
    """根据队列中的消息更新 tqdm 进度条"""
    completed_tasks = 0
    completed_task_jobs = {id_: 0 for id_ in task_ids}
    while completed_tasks < num_tasks:
        task_id, progress_value = queue.get()  # 从队列获取进度更新
        completed_task_jobs[task_id] += 1
        if completed_task_jobs[task_id] >= task_counts[task_id]:
            completed_tasks += 1
        tqdm_objects[task_id].update(progress_value)
    [tqdm_object.close() for tqdm_object in tqdm_objects]


class pool:
    """
    每个fn运行一次算一个job，每个job需要指定job_name, 如果没有job_name, 则默认分配 TaskDefault
    相同 job_name 的fn归到同一个task, 同时该task命名为job_name
    即一个task中包含了多个需要运行的 job fn
    task1 <job_fn1, job_fn2, ...>
    task2 <job_fn3, job_fn4, ...>
    所有的job_fn都会通过joblib并行运行
    """

    def __init__(self, n_jobs=5, show_progress=True, backend='threading', ):
        """backend: loky/threading/multiprocessing"""
        self.show_progress = show_progress
        self._n_jobs = n_jobs
        self._parallel = Parallel(n_jobs=self._n_jobs, verbose=0, backend=backend) if self._n_jobs > 1 else None
        self._default_task_name = "GO-JOB"
        self._all_jobs = list()  # list[job]
        self._all_tasks = list()  # list[task_name]
        self._task_ids = dict()  # {task_name1: 0, task_name2: 1, ...}
        self._task_counts = dict()
        self._leave_mapping = dict()
        self._id_counts = dict()
        self._manager = None

    def submit(self, fn, job_name: str = "", postfix: str = "", leave: bool = True):
        """
        提交并行任务
        Parameters
        ----------
        fn: callable
            需要并行的callable对象
        job_name: str
            提交到的任务名, 不同的任务对应不同的进度条
        postfix: str
            后缀
        leave: bool
            进度条完成后是否保留在屏幕上，默认 True
        Returns
        -------

        Examples
        --------
        import time
        import ygo
        >>> def task_fn1(a, b):
                time.sleep(3)
                return a+b
        >>> def task_fn2():
                time.sleep(5)
                return 0
        >>> with ygo.pool() as go:
                go.submit(task_fn1, job_name="task1")(a=1, b=2)
                go.submit(task_fn2, job_name="task2")()

                go.do()
        """

        # 提交任务，对任务进行分类，提交到对应的task id中，并且封装新的功能：使其在运行完毕后将任务进度更新放入队列
        @functools.wraps(fn)
        def collect(**kwargs):
            """归集所有的job到对应的task"""
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                job = delay(fn)(**kwargs)
                task_name = self._default_task_name if not job_name else job_name
                task_name = f"{task_name}::{postfix}"
                if task_name not in self._task_ids:
                    self._task_ids[task_name] = len(self._all_tasks)
                    self._task_counts[task_name] = 0
                    self._all_tasks.append(task_name)
                    self._id_counts[self._task_ids[task_name]] = 0
                    self._leave_mapping[task_name] = leave
                self._task_counts[task_name] += 1
                self._id_counts[self._task_ids[task_name]] += 1
                job.task_id = self._task_ids[task_name]
                job.job_id = self._task_counts[task_name]
                job.task_name = task_name
                self._all_jobs.append(job)
                return job

        return collect

    def do(self):
        if self.show_progress:
            # 消息队列进行通信
            self._manager = multiprocessing.Manager()
            queue = self._manager.Queue()
            tqdm_bars = [tqdm(total=self._task_counts[task_name],
                              desc=f"{str(task_name.split('::')[0])}",
                              postfix=task_name.split("::")[1],
                              leave=self._leave_mapping.get(task_name, True)) for task_name in
                         self._all_tasks]
            # 初始化多个任务的进度条，每个任务一个
            task_ids = [task_id for task_id in range(len(self._all_tasks))]
            # 创建并启动用于更新进度条的线程
            progress_thread = threading.Thread(target=update_progress_bars, args=(
                tqdm_bars, task_ids, queue, len(self._all_tasks), self._id_counts))
            progress_thread.start()
            if self._parallel is not None:
                # 执行并行任务
                result = self._parallel(delayed(run_job)(job=job,
                                                         task_id=job.task_id,
                                                         queue=queue) for job in self._all_jobs)
            else:
                result = [run_job(job=job, task_id=job.task_id, queue=queue) for job in self._all_jobs]
            # 等待进度更新线程执行完毕
            progress_thread.join()
        else:
            if self._parallel is not None:
                result = self._parallel(delayed(job)() for job in self._all_jobs)
            else:
                result = [job() for job in self._all_jobs]
        self._all_jobs = list()  # list[job]
        self._all_tasks = list()  # list[task_name]
        self._task_ids = dict()  # {task_name1: 0, task_name2: 1, ...}
        self._task_counts = dict()
        self._id_counts = dict()
        self._leave_mapping = dict()
        self.close()
        return result

    def close(self):
        """释放所有资源"""
        if hasattr(self, '_parallel') and self._parallel is not None:
            try:
                self._parallel.__exit__(None, None, None)
            except Exception as e:
                logger.warning(f"Failed to close Parallel: {e}")

        if hasattr(self, '_manager') and self._manager is not None:
            try:
                self._manager.shutdown()
            except Exception as e:
                logger.warning(f"Failed to shutdown Manager: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 释放进程
        self.close()
