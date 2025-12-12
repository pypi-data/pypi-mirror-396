from typing import Union

import time


class Timer:
    """
    Class to measure how long certain methods take
    to execute and complete. Just call the
    `.start()` method before the code is executed
    and the `.stop()` when it finishes.

    It can be used as a context manager with this:
    ```
    with Timer():
        # do some code
    ```
    And it can include the flag to not print the time
    elapsed:
    ```
    with Timer(is_silent_as_context = True):
        # do some code
    ```
    """

    @property
    def time_elapsed(
        self
    ) -> float:
        """
        The time elapsed in which the timer has been running
        (and the `.stop()` or `.reset()` method has not been
        called). This value can be requested at any time and
        the current time elapsed will be returned.

        Check the `self._t_elapsed` value to get the static
        value fixed on the last `.pause()` or `.stop()` call.
        """
        return (
            self._t_elapsed + time.perf_counter() - self._t_start
            if self._is_running else
            self._t_elapsed
        )

    @property
    def time_elapsed_str(
        self
    ) -> str:
        """
        The time elapsed between the 'start' and the
        'stop' method call, but as a printable string.
        """
        return str(round(self.time_elapsed, 2))

    def __init__(
        self,
        is_silent_as_context: bool = False
    ):
        self._is_silent_as_context: bool = is_silent_as_context
        """
        Flag to indicate if it must print the info
        or not when used as a context and finished.
        """

        self.reset()

    def start(
        self
    ) -> 'Timer':
        """
        Start the timer.
        """
        self._t_elapsed = 0.0
        self._t_start = time.perf_counter()
        self._is_running = True

        return self
    
    def resume(
        self
    ) -> 'Timer':
        """
        The timer starts running again if it was stopped.
        """
        if not self._is_running:
            self._t_start = time.perf_counter()
            self._is_running = True

        return self

    def pause(
        self
    ) -> 'Timer':
        """
        Pause the timer, that will not reset the values.
        """
        # TODO: Maybe limit it a bit more
        if self._is_running:
            self._t_elapsed += time.perf_counter() - self._t_start
            self._is_running = False
            self._t_start = None

        return self

    def stop(
        self
    ) -> 'Timer':
        """
        Stop completely the timer and set the `._t_elapsed`.
        """
        if self._is_running:
            self._t_elapsed += time.perf_counter() - self._t_start
            self._is_running = False
            self._t_start = None

        return self
    
    def reset(
        self
    ) -> 'Timer':
        """
        Reset the timer to the initial condition, as if it was
        recently instantiated, and will be stopped.
        """
        self._t_start: Union[float, None] = None
        """
        The time moment in which the timer executed the last
        `.start()` call.
        """
        self._t_elapsed: float = 0.0
        """
        The time that has elapsed since the last `.start()` call.
        """
        self._is_running: bool = False
        """
        Internal flag to indicate if the timer is counting or if
        it is not (paused or not initialized).
        """

    def print(
        self,
        message: str = 'Time elapsed:'
    ) -> None:
        """
        Print the time elapsed in the console after the `message`
        text provided.
        """
        print(f'{message} {self.time_elapsed_str}')

    # Allowing 'with Timer():' context below
    def __enter__(
        self
    ) -> 'Timer':
        self.start()

        return self

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb
    ):
        self.stop()
        
        if not self._is_silent_as_context:
            self.print()