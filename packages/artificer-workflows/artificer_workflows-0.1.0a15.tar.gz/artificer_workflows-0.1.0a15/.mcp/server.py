from pathlib import Path

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from artificer.workflows import Workflow
from artificer.workflows.store import workflow_store

mcp = FastMCP(name="Workflows MCP", version="0.1.0")


# Shared model used by multiple steps
class ArtifactMetadata(BaseModel):
    """Metadata for artifacts created during workflow execution."""

    name: str = Field(description="Artifact filename (e.g., 'requirements.md')")
    path: str = Field(description="Path to the artifact")
    description: str | None = Field(
        default=None, description="Optional description of the artifact"
    )
    type: str | None = Field(
        default=None, description="Optional type hint (e.g., 'markdown', 'json')"
    )


class ReviewIssue(BaseModel):
    """An issue found during code review."""

    severity: str = Field(
        description="Issue severity: 'critical', 'major', 'minor', or 'nitpick'"
    )
    description: str = Field(description="Description of the issue")
    location: str | None = Field(
        default=None, description="File/line location of the issue (if applicable)"
    )


class AddFeature(Workflow):
    templates_dir = Path(__file__).parent / "templates"


def get_artifacts_from_workflow(workflow_id: str) -> list[dict]:
    """Extract all artifacts from completed steps in a workflow."""
    workflow = workflow_store.get_workflow(workflow_id)
    if workflow is None:
        return []

    artifacts = []
    for step in workflow.steps.values():
        result = step.current_result
        if result is None:
            continue
        # Handle single artifact
        if "artifact" in result and result["artifact"]:
            artifacts.append(result["artifact"])
        # Handle multiple artifacts
        if "artifacts" in result:
            artifacts.extend(result["artifacts"])
    return artifacts


class StepMixin:
    """Mixin that adds step_dir and artifacts to template rendering."""

    def _init_step_context(self):
        self._workflow = workflow_store.get_workflow(self.workflow_id)
        self._step_dir = (
            f".artificer/workflow-AddFeature-{self._workflow.start_time}-"
            f"{self.workflow_id}/step-{self.__class__.__name__}-{self.start_time}-{self.step_id}"
        )
        self._artifacts = get_artifacts_from_workflow(self.workflow_id)

    def render_template(self, template_name: str, *args, **kwargs) -> str:
        if not hasattr(self, '_step_dir'):
            self._init_step_context()
        return super().render_template(
            template_name,
            *args,
            artifacts=self._artifacts,
            step_dir=self._step_dir,
            **kwargs
        )


class CollectRequirementsStep(StepMixin, AddFeature.Step, start=True):
    class OutputModel(BaseModel):
        summary: str = Field(description="Brief summary of collected requirements")
        artifacts: list[ArtifactMetadata] = Field(
            description="Requirements document artifacts (e.g., requirements.md)"
        )

    def start(self, previous_result=None) -> str:
        return self.render_template("collect_requirements.md")

    def complete(self, output: OutputModel) -> type["CreatePlanStep"]:
        return CreatePlanStep


class CreatePlanStep(StepMixin, AddFeature.Step):
    class OutputModel(BaseModel):
        summary: str = Field(description="Brief summary of the implementation plan")
        artifact: ArtifactMetadata = Field(
            description="Implementation plan artifact (e.g., plan.md)"
        )

    def start(self, previous_result: CollectRequirementsStep.OutputModel = None) -> str:
        return self.render_template("create_plan.md")

    def complete(self, output: OutputModel) -> type["ImplementFeatureStep"]:
        return ImplementFeatureStep


class ImplementFeatureStep(StepMixin, AddFeature.Step):
    class OutputModel(BaseModel):
        summary: str = Field(description="Brief summary of what was implemented")
        artifacts: list[ArtifactMetadata] = Field(
            min_length=1,
            description="List of files/artifacts created during implementation",
        )
        

    def start(self, previous_result: CreatePlanStep.OutputModel = None) -> str:
        return self.render_template("implement_feature.md")

    def complete(self, output: OutputModel) -> type["ReviewFeatureStep"]:
        return ReviewFeatureStep


class ReviewFeatureStep(StepMixin, AddFeature.Step):
    class OutputModel(BaseModel):
        needs_revision: bool = Field(
            description="Whether the feature needs revision based on review (set based on user's decision)"
        )
        summary: str = Field(description="Brief summary of review findings")
        issues: list[ReviewIssue] = Field(
            description="List of issues found during review"
        )
        artifact: ArtifactMetadata = Field(
            description="Code review artifact (e.g., review.md)"
        )

    def start(self, previous_result: ImplementFeatureStep.OutputModel = None) -> str:
        return self.render_template("review_feature.md")

    def complete(
        self, output: OutputModel
    ) -> type["CreatePlanStep"] | type["SummaryStep"]:
        if output.needs_revision:
            return CreatePlanStep
        return SummaryStep


class SummaryStep(StepMixin, AddFeature.Step):
    class OutputModel(BaseModel):
        summary: str = Field(description="Brief summary of completed feature work")
        artifact: ArtifactMetadata = Field(
            description="Summary document artifact (e.g., summary.md)"
        )

    def start(self, previous_result: ReviewFeatureStep.OutputModel = None) -> str:
        return self.render_template("summary.md")

    def complete(self, output: OutputModel) -> None:  # noqa: ARG002
        return None


AddFeature.register(mcp)


if __name__ == "__main__":
    mcp.run()
