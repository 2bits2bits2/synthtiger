"""
SynthTIGER
Copyright (c) 2021-present NAVER Corp.
MIT license
"""

import itertools
import os
import random
import sys
import time
import traceback
from multiprocessing import Process, Queue

import imgaug
import numpy as np
import yaml


def read_template(path, name, config=None):
    path = os.path.abspath(path)
    root = os.path.dirname(path)
    module = os.path.splitext(os.path.basename(path))[0]
    sys.path.append(root)
    template = getattr(__import__(module), name)(config)
    sys.path.remove(root)
    del sys.modules[module]
    return template


def read_config(path):
    with open(path, "r", encoding="utf-8") as fp:
        config = yaml.load(fp, Loader=yaml.SafeLoader)
    return config


def generator(
    path, name, config=None, count=None, worker=0, seed=None, retry=True, verbose=False, progress=True
):
    counter = range(count) if count is not None else itertools.count()
    tasks = _task_generator(seed)

    if progress:
        start_time = time.time()

    if worker > 0:
        task_queue = Queue(maxsize=worker)
        data_queue = Queue(maxsize=worker)
        pre_count = min(worker, count) if count is not None else worker
        post_count = count - pre_count if count is not None else None

        for _ in range(worker):
            _run(_worker, (path, name, config, task_queue, data_queue, retry, verbose))
        for _ in range(pre_count):
            task_queue.put(next(tasks))

        for idx in counter:
            task_idx, data = data_queue.get()
            if post_count is None or idx < post_count:
                task_queue.put(next(tasks))
            if progress:
                _print_progress(idx + 1, count, start_time)
            yield task_idx, data
    else:
        template = read_template(path, name, config)

        for idx in counter:
            task_idx, task_seed = next(tasks)
            data = _generate(template, task_seed, retry, verbose)
            if progress:
                _print_progress(idx + 1, count, start_time)
            yield task_idx, data


def get_global_random_states():
    states = {
        "random": random.getstate(),
        "numpy": np.random.get_state(),
        "imgaug": imgaug.random.get_global_rng().state,
    }
    return states


def set_global_random_states(states):
    random.setstate(states["random"])
    np.random.set_state(states["numpy"])
    imgaug.random.get_global_rng().state = states["imgaug"]


def set_global_random_seed(seed=None):
    random.seed(seed)
    np.random.set_state(np.random.RandomState(np.random.MT19937(seed)).get_state())
    imgaug.random.seed(seed)


def _run(func, args):
    proc = Process(target=func, args=args)
    proc.daemon = True
    proc.start()
    return proc


def _task_generator(seed):
    random_generator = random.Random(seed)
    task_idx = -1

    while True:
        task_idx += 1
        task_seed = random_generator.getrandbits(128)
        yield task_idx, task_seed


def _worker(path, name, config, task_queue, data_queue, retry, verbose):
    template = read_template(path, name, config)

    while True:
        task_idx, task_seed = task_queue.get()
        data = _generate(template, task_seed, retry, verbose)
        data_queue.put((task_idx, data))


def _generate(template, seed, retry, verbose):
    states = get_global_random_states()
    set_global_random_seed(seed)
    data = None

    while True:
        try:
            data = template.generate()
        except:
            if verbose:
                print(f"{traceback.format_exc()}")
            if retry:
                continue
        break

    set_global_random_states(states)
    return data


def _print_progress(current, total, start_time):
    elapsed_time = time.time() - start_time
    progress = current / total if total is not None else 0
    eta = (elapsed_time / current) * (total - current) if total is not None else float('inf')

    bar_length = 30
    filled_length = int(bar_length * progress)
    bar = '=' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write(f'\r[{bar}] {current}/{total if total is not None else "inf"} - ETA: {eta:.2f}s')
    sys.stdout.flush()

    if current == total:
        print()  # Move to the next line when finished
