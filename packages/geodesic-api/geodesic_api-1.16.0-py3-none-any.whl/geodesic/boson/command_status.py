from geodesic.bases import _APIObject
from geodesic.descriptors import (
    _BoolDescr,
    _StringDescr,
    _TypeConstrainedDescr,
    _IntDescr,
    _DictDescr,
    _ListDescr,
    _DatetimeDescr,
    _TimeDeltaDescr,
)

COMMAND_INITIALIZE = "initialize"
PENDING = "pending"
RUNNING = "running"
SUCCESS = "success"
FAILED = "failed"
UNKNOWN = "unknown"

states = [PENDING, RUNNING, SUCCESS, FAILED, UNKNOWN]


class _Timed(_APIObject):
    started_at = _DatetimeDescr(doc="Timestamp when the operation started", optional=True)
    updated_at = _DatetimeDescr(doc="Timestamp when the operation was last updated", optional=True)
    finished_at = _DatetimeDescr(doc="Timestamp when the operation ended", optional=True)


class Stage(_Timed):
    name = _StringDescr(doc="Name of the stage")
    state = _StringDescr(doc="State of the stage", soft_one_of=states)
    task_label = _StringDescr(doc="Label for tasks in this stage", default="tasks")
    task_count = _IntDescr(doc="Number of tasks in the stage", default=0)
    tasks_completed = _IntDescr(doc="Number of completed tasks in the stage", default=0)
    error = _StringDescr(doc="Error message, if any")

    def update_progress_bar(self, bar):
        """Update a tqdm progress bar based on the current state of the stage.

        Args:
            bar: A tqdm progress bar instance.
            index: The index of the stage (for display purposes).
        """
        bar.desc = f"└─ {self.name}: {self.state.upper()}"
        bar.unit = self.task_label
        if self.state == RUNNING:
            bar.total = self.task_count
            bar.update(self.tasks_completed - bar.n)
            bar.refresh()
        elif self.state in [SUCCESS, FAILED]:
            bar.n = self.task_count
            bar.refresh()
            bar.close()
            return


class CommandStatus(_Timed):
    command = _StringDescr(doc="The name of the command that was run", default="")
    args = _DictDescr(doc="The arguments that were passed to the command", default={})
    result = _DictDescr(doc="The result of the command, if any", default={})
    stages = _ListDescr(
        (Stage, dict), coerce_items=True, doc="List of stages for the command", default=[]
    )
    current_stage = _IntDescr(doc="Index of the current stage", default=0)
    detail = _StringDescr(doc="Detailed message about the command status", default="")
    state = _StringDescr(
        doc="Current state of the command",
        soft_one_of=states,
        default=UNKNOWN,
    )
    error = _StringDescr(doc="Error message, if any", optional=True)
    timeout = _TimeDeltaDescr(doc="Timeout for the command in seconds", optional=True)
    elapsed = _TimeDeltaDescr(doc="Elapsed time for the command in seconds", optional=True)


class CommandStatusResponse(_APIObject):
    success = _BoolDescr(doc="Whether the command completed successfully")
    detail = _StringDescr(doc="Detailed message about the command status")
    result = _TypeConstrainedDescr(
        (CommandStatus, dict),
        coerce=True,
        doc="Result object returned by the indexing command, if any",
    )

    def __init__(self, label: str = "Status", **kwargs):
        super().__init__(**kwargs)
        self._label = label

    def __repr__(self):
        if self.result.command == COMMAND_INITIALIZE:
            if self.result.state == SUCCESS:
                return f"{self._label}: ready"
        return f"{self._label}: {self.result.state}"

    def progress_bars(self, progress_bar_class=None):
        """Create and return a tqdm progress bar for the indexing command.

        Args:
            progress_bar_class: The tqdm class to use for creating progress bars. If None, uses
                `tqdm.auto.tqdm`.

        Returns:
            A tuple containing the overall progress bar and a dictionary of stage progress bars.
        """
        from tqdm.auto import tqdm

        if progress_bar_class is None:
            progress_bar_class = tqdm

        result: CommandStatus = self.result
        overall_bar = progress_bar_class(
            total=len(result.stages),
            position=0,
            initial=min(result.current_stage, max(len(result.stages), 0)),
            desc="Processing",
            unit="stages",
            leave=True,
        )
        stage_bars = {}
        self.update_progress_bars(overall_bar, stage_bars, progress_bar_class=progress_bar_class)
        return overall_bar, stage_bars

    def update_progress_bars(self, overall_bar, stage_bars, progress_bar_class=None):
        """Update progress bars based on the current state of the indexing command.

        Args:
            overall_bar: A tqdm progress bar instance for the overall command.
            stage_bars: A dictionary of tqdm progress bars for each stage.
            progress_bar_class: The tqdm class to use for creating new progress bars.
                If None, uses `tqdm.auto.tqdm`.
        """
        from tqdm.auto import tqdm

        if progress_bar_class is None:
            progress_bar_class = tqdm

        result: CommandStatus = self.result

        total_stages = len(result.stages)
        if total_stages == 0:
            total_stages = 1  # Avoid division by zero
        overall_bar.total = total_stages
        overall_bar.n = min(result.current_stage + 1, max(total_stages, 0))
        for i, stage in enumerate(result.stages):
            stage_name = stage.name
            if stage_name not in stage_bars and stage.state != UNKNOWN:
                stage_bars[stage_name] = progress_bar_class(
                    total=stage.task_count,
                    position=i + 1,
                    initial=stage.tasks_completed,
                    desc=f"└─ {stage_name}: {stage.state.upper()}",
                    unit="tasks",
                    leave=True,
                )
            elif stage_name in stage_bars:
                stage.update_progress_bar(stage_bars[stage_name])

        if result.state == SUCCESS:
            overall_bar.set_description("Completed")
        elif self.failed():
            overall_bar.set_description("Failed")
        overall_bar.refresh()

    def completed(self) -> bool:
        """Check if the command has completed.

        Returns:
            True if the command is in a terminal state (SUCCESS or FAILED), or has timed out/stalled
        """
        result: CommandStatus = self.result
        if result.state in [PENDING, RUNNING]:
            if result.timeout and result.elapsed and result.elapsed > result.timeout:
                return True
            if result.updated_at and result.started_at:
                stalled_time = result.updated_at - result.started_at
                if stalled_time.total_seconds() > 600:  # 10 minutes of no updates
                    return True
            return False

        return result.state in [SUCCESS, FAILED]

    def failed(self) -> bool:
        """Check if the command has failed.

        Returns:
            True if the command state is FAILED, False otherwise.
        """
        result: CommandStatus = self.result
        return result.state == FAILED

    def state_message(self):
        """Get a message describing the current state of the command.

        Returns:
            A string describing the current state of the command.
        """
        result: CommandStatus = self.result
        if result.state in [PENDING, RUNNING]:
            if result.timeout and result.elapsed and result.elapsed > result.timeout:
                return "command has timed out"
            if result.updated_at and result.started_at:
                stalled_time = result.updated_at - result.started_at
                if stalled_time.total_seconds() > 600:  # 10 minutes of no updates
                    return "command has stalled (>10 minutes with no updates)"
            return "command is still in progress"

        if result.state == SUCCESS:
            return "command completed successfully"
        elif result.state == FAILED:
            return result.error

        return "command is in an unknown state"
