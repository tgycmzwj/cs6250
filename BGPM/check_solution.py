#!/usr/bin/env python3

import os
import sys
import traceback
import json
import pickle
from pathlib import Path
from termcolor import colored


# pickle files are a standard way of serializing data in Python
# https://docs.python.org/3/library/pickle.html
def load_p(data_set, task):
    try:
        with open(Path(data_set, f"solution/{task}.p"), "rb") as f:
            return pickle.load(f)
    except Exception as e:
        print(f"{err_prologue} (pickle): {repr(e)}\n")


# pickle files are a standard way of serializing data in Python
# https://docs.python.org/3/library/pickle.html
def write_p(data, fpath):
    try:
        with open(Path(fpath), "wb") as f:
            pickle.dump(data, f)
    except Exception as e:
        print(f"{err_prologue} (pickle): {repr(e)}\n")


# Python also allow serialization of data to JSON, but you're not guaranteed to be able to capture all Python type
# https://docs.python.org/3/library/pickle.html#comparison-with-json
#def write_j(data, fpath, task):
def write_j(data, fpath, sort_keys=False, indent=4):
    try:
        with open(Path(fpath), "w") as f:
            json.dump(data, f, sort_keys=sort_keys, indent=indent)
            f.write("\n")
    except Exception as e:
        print(f"{err_prologue} {task} (json): {repr(e)}\n")


if __name__ == "__main__":
    BASE_DIR = Path(os.path.abspath(__file__)).parent
    if BASE_DIR != Path(os.getcwd()):
        # print(f"{BASE_DIR} != {os.getcwd()} - changing")
        os.chdir(BASE_DIR)

    def get_cache_files(data_set, kind):
        return sorted([str(p) for p in Path(data_set, kind).glob("*.cache")])

    err_bullet = colored(">>>", "red")
    inf_bullet = colored(">>>", "green")

    try:
        # import all the functions and exit with error if any fail
        try:
            from bgpm import unique_prefixes_by_snapshot
            from bgpm import unique_ases_by_snapshot
            from bgpm import top_10_ases_by_prefix_growth
            from bgpm import shortest_path_by_origin_by_snapshot
            from bgpm import aw_event_durations
            from bgpm import rtbh_event_durations
            msg = colored("All functions imported", attrs=["bold"])
            print(f"{inf_bullet} {msg}")
        except (ImportError, Exception) as e:
            print(f"{err_bullet} {repr(e)}")

        tasks = [
            ("task_1a", unique_prefixes_by_snapshot, "rib_files"),
            ("task_1b", unique_ases_by_snapshot, "rib_files"),
            ("task_1c", top_10_ases_by_prefix_growth, "rib_files"),
            ("task_2", shortest_path_by_origin_by_snapshot, "rib_files"),
            ("task_3", aw_event_durations, "update_files"),
            ("task_4", rtbh_event_durations, "update_files_blackholing"),
        ]

        collectors = ["rrc04", "rrc06"]

        for collector in collectors:
            msg = colored(f"Processing {collector}", attrs=["bold"])
            print(f"\n{msg}")
            output_dir = Path(f"{collector}_output")
            for task, func, arg in tasks:
                # task_name = colored(task, attrs=["bold"])
                # msg = f"{task_name}: {func.__name__}()"
                # # msg = colored(f"{task}: {func.__name__}()", attrs=["bold"])
                # print(msg)
                task_id = f"{collector}[{task:<7}]"
                inf_prologue = f"{inf_bullet} {task_id}"
                err_prologue = f"{err_bullet} {task_id}"

                is_correct_value = False
                json_sort_keys = True if task in ["task_2", "task_3", "task_4"] else False
                try:
                    res = func(get_cache_files(collector, arg))
                    if not res:
                        # res is empty, so nothing need be cached to disk - student skipped this task
                        print(f"{err_prologue} nothing returned for this task")
                    else:
                        # something was returned - check signature of result
                        if task in ["task_1a", "task_1b", "task_1c"]:
                            is_correct_type = False if type(res) is not list else True
                            # if type(res) is not list:
                            #         print(f"{err_prologue} return type should be list (not {type(res)})")
                            # else:
                            #     print(f"{inf_prologue} return type is correct ({type(res)})")

                            if task in ["task_2", "task_3", "task_4"]:
                                is_correct_type = False if type(res) is not dict else True
                            # if type(res) is not dict:
                            #     print(f"{err_prologue} return type should be dict (not {type(res)})")
                            # else:
                            #     print(f"{inf_prologue} return type is correct ({type(res)})")

                        # something was returned - compare and report
                        solution = load_p(collector, task)
                        if solution != res:
                            output_base_name = f"{output_dir}/{task}"
                            # if you really want to create a pickle file (https://docs.python.org/3/library/pickle.html), you can uncomment this
                            # write_p(res, f"{output_base_name}.p")
                            write_j(res, f"{output_base_name}.json", sort_keys=json_sort_keys)
                            result_msg = f"{err_prologue} returned value is incorrect ({collector}_output/{task}.json)"
                        else:
                            result_msg = f"{inf_prologue} returned value is correct"
                        print(result_msg)

                    # print(f"{inf_bullet} {task}: completed", file=stderr_orig)
                except (ImportError, Exception) as e:
                    print(f"{err_prologue} {repr(e)}\n")
                    traceback.print_exc()
    except Exception as e:
        # something bad happened, so print it to real stderr
        print(repr(e))
    finally:
        # clean up stdout
        sys.stdout.flush()
