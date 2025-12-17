from abc import abstractmethod

import ray
import time
import traceback
import os
import sys
from typing import Any, Tuple, Dict, List, Callable
from ray.exceptions import GetTimeoutError

from adtools import PyProgram
from adtools.evaluator import PyEvaluator


class PyEvaluatorRay(PyEvaluator):
    def __init__(
        self,
        exec_code: bool = True,
        debug_mode: bool = False,
        num_cpus: int = 1,
        num_gpus: int = 0,
        *,
        join_timeout_seconds: int = 10,
    ):
        """Evaluator using Ray for secure, isolated execution.
        It supports efficient zero-copy return of large objects (e.g., Tensors).

        Args:
            exec_code: Whether to execute the code using 'exec()'.
            debug_mode: Enable debug print statements.
            num_cpus: Number of CPU cores to allocate for the sandbox process.
            num_gpus: Number of GPUs to allocate for the sandbox process.
            join_timeout_seconds: (Not primarily used in Ray logic, but kept for compatibility).
        """
        # We set find_and_kill_children_evaluation_process to False because Ray
        # manages the process tree, and we use ray.kill() to clean up
        super().__init__(
            exec_code,
            find_and_kill_children_evaluation_process=False,
            debug_mode=debug_mode,
            join_timeout_seconds=join_timeout_seconds,
        )
        self.num_cpus = num_cpus
        self.num_gpus = num_gpus

        # Initialize Ray if not already running
        if not ray.is_initialized():
            ray.init(ignore_reinit_error=True)

    def secure_evaluate(
        self,
        program: str | PyProgram,
        timeout_seconds: int | float = None,
        redirect_to_devnull: bool = False,
        get_evaluate_time: bool = False,
        **kwargs,
    ) -> Any | Tuple[Any, float]:
        """Evaluates the program in a separate Ray Actor (process).
        Mechanism:
            1. Spawns a new Ray Actor (Worker).
            2. Sends 'self' (the evaluator) and the code to the Worker.
            3. Waits for the result with a timeout.
            4. Kills the Worker immediately to ensure a clean slate and resource release.
        """
        # Convert PyProgram to string if necessary
        program_str = str(program)

        # Create a new Ray Actor (Sandbox)
        # Create a fresh actor for every evaluation to ensure total isolation
        worker = _RayWorker.options(
            num_cpus=self.num_cpus, num_gpus=self.num_gpus
        ).remote()
        start_time = time.time()

        try:
            # Execute asynchronously
            # Pass 'self' to the remote worker. Ray pickles this instance
            # The actual execution logic (evaluate_program) runs inside the worker process
            future = worker.run_evaluation.remote(
                self, program_str, redirect_to_devnull, **kwargs
            )
            # Wait for result with timeout
            if timeout_seconds is not None:
                result = ray.get(future, timeout=timeout_seconds)
            else:
                result = ray.get(future)
        except GetTimeoutError:
            # Handle Timeout
            if self.debug_mode:
                print(f"DEBUG: Ray evaluation timed out after {timeout_seconds}s.")
            result = None
        except Exception as e:
            # Handle other runtime exceptions (syntax errors, runtime errors in code)
            if self.debug_mode:
                print(f"DEBUG: Ray evaluation exception:\n{traceback.format_exc()}")
            result = None
        finally:
            # Cleanup: Force kill the actor
            # 'no_restart=True' ensures Ray does not try to respawn this worker
            # This releases the resources (CPUs/GPUs) immediately
            ray.kill(worker, no_restart=True)
            eval_time = time.time() - start_time

        return (result, eval_time) if get_evaluate_time else result

    @abstractmethod
    def evaluate_program(
        self,
        program_str: str,
        callable_functions_dict: Dict[str, Callable] | None,
        callable_functions_list: List[Callable] | None,
        callable_classes_dict: Dict[str, Callable] | None,
        callable_classes_list: List[Callable] | None,
        **kwargs,
    ) -> Any:
        """Evaluate a given program.

        Args:
            program_str: The raw program text.
            callable_functions_dict: A dict maps function name to callable function.
            callable_functions_list: A list of callable functions.
            callable_classes_dict: A dict maps class name to callable class.
            callable_classes_list: A list of callable classes.
        Returns:
            Returns the evaluation result.
        """
        raise NotImplementedError(
            "Must provide an evaluator for a python program. "
            "Override this method in a subclass."
        )


@ray.remote(max_concurrency=1)
class _RayWorker:
    """A standalone Ray Actor used to execute the evaluation logic in a separate process."""

    def run_evaluation(
        self,
        evaluator_instance: "PyEvaluator",
        program_str: str,
        redirect_to_devnull: bool,
        **kwargs,
    ) -> Any:
        """Executes the evaluation inside the remote Ray process.

        Args:
            evaluator_instance: The evaluator object (pickled and sent to this worker).
            program_str: The code to evaluate.
            redirect_to_devnull: Whether to silence stdout/stderr.
            **kwargs: Arguments passed to evaluate_program.
        """
        # Handle Output Redirection
        if redirect_to_devnull:
            # Open devnull
            with open(os.devnull, "w") as devnull:
                # Save original file descriptors
                original_stdout_fd = sys.stdout.fileno()
                original_stderr_fd = sys.stderr.fileno()

                # Redirect stdout/stderr to devnull at the OS level
                os.dup2(devnull.fileno(), original_stdout_fd)
                os.dup2(devnull.fileno(), original_stderr_fd)

                try:
                    # Invoke the parent class's evaluate method
                    return evaluator_instance.evaluate(program_str, **kwargs)
                except Exception:
                    raise  # Re-raise to let Ray handle the exception
                finally:
                    pass
        else:
            # Run without redirection
            return evaluator_instance.evaluate(program_str, **kwargs)


if __name__ == "__main__":
    import numpy as np

    # Define your concrete evaluator
    class MyTensorEvaluator(PyEvaluatorRay):
        def evaluate_program(
            self,
            program_str,
            callable_functions_dict,
            callable_functions_list,
            callable_classes_dict,
            callable_classes_list,
            **kwargs,
        ) -> Any:
            # This code runs INSIDE the Ray process
            print(f"Executing: {program_str}")

            # Simulate generating a large Tensor (Zero-Copy return)
            # Ray Object Store will handle this efficiently
            return np.ones((1000, 1000))

    # Instantiate with resource constraints
    evaluator = MyTensorEvaluator(debug_mode=True, num_cpus=1.0)

    # Run secure evaluation
    result, duration = evaluator.secure_evaluate(
        program="print('Hello World')", timeout_seconds=5.0, get_evaluate_time=True
    )

    if result is not None:
        print(f"Success! Result shape: {result.shape}")
        print(f"Time taken: {duration:.4f}s")
    else:
        print("Evaluation failed or timed out.")
