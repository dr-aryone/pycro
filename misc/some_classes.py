#!/usr/bin/python3

import sys

sys.exit(0)

def __compiler_worker(
        initial_job,
        jobs_queue,

        cache_folder_path,
        compiler_env,

        error_event,
        ):

    # --- get cache file path ---
    cache_file_path = \
            __get_cache_file_path(
                    cache_folder_path, 
                    file_real_path)

    # --- compile & and save cache ---
    try:
        code_object = \
                __compile_if_needed(
                        file_real_path, 
                        cache_file_path, 
                        compiler_env)

    except OSError:
        # stop all other threads

        pass

    # --- append code object to job list ---

class __CompilerWorker(threading.Thread):
    def __init__(
            self, 
            jobs_queue,

            cache_folder_path,
            compiler_env,

            exit_event,
            ):
        
        self.jobs_queue = jobs_queue

        self.cache_folder_path
        self.compiler_env

    def run(self):
        job = jobs_queue.get()

        if exit_event.is_set():
            return

