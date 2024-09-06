"""
SynthTIGER
Copyright (c) 2021-present NAVER Corp.
MIT license
"""

import argparse
import pprint
import sys
import time

import synthtiger


def _print_progress(current, total, start_time):
    elapsed_time = time.time() - start_time
    progress = current / total if total is not None else 0
    eta = (elapsed_time / current) * (total - current) if total is not None else float('inf')

    bar_length = 30
    filled_length = int(bar_length * progress)
    bar = '=' * filled_length + '-' * (bar_length - filled_length)

    if eta > 300:  # More than 5 minutes
        eta_str = f"{int(eta // 60)}m {int(eta % 60)}s"
    elif eta > 60:  # Between 1 and 5 minutes
        eta_str = f"{int(eta // 60)}m {int(eta % 60)}s"
    else:  # Less than 1 minute
        eta_str = f"{eta:.2f}s"

    sys.stdout.write(f'\r[{bar}] {current}/{total if total is not None else "inf"} - ETA: {eta_str}')
    sys.stdout.flush()

    if current == total:
        print()  # Move to the next line when finished


def run(args):
    if args.config is not None:
        config = synthtiger.read_config(args.config)

    pprint.pprint(config)

    synthtiger.set_global_random_seed(args.seed)
    template = synthtiger.read_template(args.script, args.name, config)
    generator = synthtiger.generator(
        args.script,
        args.name,
        config=config,
        count=args.count,
        worker=args.worker,
        seed=args.seed,
        retry=True,
        verbose=args.verbose,
    )

    if args.output is not None:
        template.init_save(args.output)

    start_time = time.time()
    for idx, (task_idx, data) in enumerate(generator):
        if args.output is not None:
            template.save(args.output, data, task_idx)

        if args.progress:
            _print_progress(idx + 1, args.count, start_time)
        else:
            print(f"Generated {idx + 1} data (task {task_idx})")

    if args.output is not None:
        template.end_save(args.output)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--output",
        metavar="DIR",
        type=str,
        help="Directory path to save data.",
    )
    parser.add_argument(
        "-c",
        "--count",
        metavar="NUM",
        type=int,
        default=100,
        help="Number of output data. [default: 100]",
    )
    parser.add_argument(
        "-w",
        "--worker",
        metavar="NUM",
        type=int,
        default=0,
        help="Number of workers. If 0, It generates data in the main process. [default: 0]",
    )
    parser.add_argument(
        "-s",
        "--seed",
        metavar="NUM",
        type=int,
        default=None,
        help="Random seed. [default: None]",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Print error messages while generating data.",
    )
    parser.add_argument(
        "script",
        metavar="SCRIPT",
        type=str,
        help="Script file path.",
    )
    parser.add_argument(
        "name",
        metavar="NAME",
        type=str,
        help="Template class name.",
    )
    parser.add_argument(
        "config",
        metavar="CONFIG",
        type=str,
        nargs="?",
        help="Config file path.",
    )
    parser.add_argument(
        "--progress",
        action="store_true",
        default=False,
        help="Print progress bar while generating data.",
    )
    args = parser.parse_args()

    pprint.pprint(vars(args))

    return args


def main():
    start_time = time.time()
    args = parse_args()
    run(args)
    end_time = time.time()
    print(f"{end_time - start_time:.2f} seconds elapsed")


if __name__ == "__main__":
    main()
