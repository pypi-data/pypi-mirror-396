import json
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from .settings import ARTIFICER_PROJECT_HOME

if TYPE_CHECKING:
    from .workflow import Workflow

logger = logging.getLogger(__name__)
ARTIFICER_PROJECT_HOME
logger.debug(f"Using workflows directory: {ARTIFICER_PROJECT_HOME}")
ARTIFICER_PROJECT_HOME_PATH = Path(ARTIFICER_PROJECT_HOME)
ARTIFICER_PROJECT_HOME_PATH.mkdir(parents=True, exist_ok=True)
workflows_store_path = ARTIFICER_PROJECT_HOME_PATH / "workflow_executions.json"


class WorkflowsStore:
    def __init__(self, store_path: Path = workflows_store_path):
        self.store_path = store_path
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.store_path.exists():
            self._write_store({})

    def _read_store(self) -> dict:
        if not self.store_path.exists():
            self._write_store({})
        with open(self.store_path, "r") as f:
            return json.load(f)

    def _write_store(self, data: dict) -> None:
        with open(self.store_path, "w") as f:
            json.dump(data, f, indent=2)

    def get_workflow(self, workflow_id: str) -> Optional["Workflow"]:
        from .workflow import Workflow

        store = self._read_store()
        data = store.get(workflow_id)
        if data is None:
            return None

        # Look up workflow class and use its serializer
        workflow_class_name = data.get("workflow_class")
        if workflow_class_name is None:
            raise ValueError("Missing workflow_class in data")

        workflow_cls = Workflow._workflow_registry.get(workflow_class_name)
        if workflow_cls is None:
            raise ValueError(f"Unknown workflow class: {workflow_class_name}")

        return workflow_cls.serializer_class().from_dict(data, workflow_cls)

    def save_workflow(self, workflow: "Workflow") -> None:
        store = self._read_store()
        serializer = type(workflow).serializer_class()
        store[workflow.workflow_id] = serializer.to_dict(workflow)
        self._write_store(store)

    @contextmanager
    def edit_workflow(self, workflow_id: str):
        """Context manager for editing and auto-saving workflows."""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Unknown workflow_id: {workflow_id}")

        try:
            yield workflow
        finally:
            # Always save, even if exception occurred
            self.save_workflow(workflow)


workflow_store = WorkflowsStore()
