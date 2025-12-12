from pathlib import Path

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from artificer.workflows import Workflow
from artificer.workflows.store import workflow_store

mcp = FastMCP(name="Artificer Workflows Development MCP", version="0.1.0")


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


# Workflow definition
class AddFeature(Workflow):
    templates_dir = Path(__file__).parent / "templates" / "add_feature"


class CollectRequirementsStep(AddFeature.Step, start=True):
    class OutputModel(BaseModel):
        summary: str = Field(description="Brief summary of collected requirements")
        artifact: ArtifactMetadata = Field(
            description="Requirements document artifact (e.g., requirements.md)"
        )

    def start(self, previous_result=None) -> str:
        artifacts = get_artifacts_from_workflow(self.workflow_id)
        workflow = workflow_store.get_workflow(self.workflow_id)
        step_dir = (
            f".artificer/workflow-AddFeature-{workflow.start_time}-"
            f"{self.workflow_id}/step-CollectRequirementsStep-{self.start_time}-{self.step_id}"
        )
        template = AddFeature._jinja_env.get_template("collect_requirements.md")
        return template.render(
            result=previous_result, artifacts=artifacts, step_dir=step_dir
        )

    def complete(self, output: OutputModel) -> type["ArchitectureReviewStep"]:
        return ArchitectureReviewStep


class ArchitectureReviewStep(AddFeature.Step):
    class OutputModel(BaseModel):
        architecture_analysis: str = Field(
            description="Analysis of where the feature fits in current architecture"
        )
        simplifications_needed: list[str] = Field(
            description="List of things to simplify or remove before adding the feature"
        )
        refactoring_required: list[str] = Field(
            description="List of refactorings needed to support the feature"
        )
        architecture_changes: str = Field(
            description="Description of how the architecture will change"
        )
        artifact: ArtifactMetadata = Field(
            description="Updated ARCHITECTURE.md document"
        )

    def start(self, previous_result: CollectRequirementsStep.OutputModel = None) -> str:
        artifacts = get_artifacts_from_workflow(self.workflow_id)
        workflow = workflow_store.get_workflow(self.workflow_id)
        step_dir = (
            f".artificer/workflow-AddFeature-{workflow.start_time}-"
            f"{self.workflow_id}/step-ArchitectureReviewStep-{self.start_time}-{self.step_id}"
        )
        template = AddFeature._jinja_env.get_template("review_architecture.md")
        return template.render(
            result=previous_result, artifacts=artifacts, step_dir=step_dir
        )

    def complete(self, output: OutputModel) -> type["CreatePlanStep"]:
        return CreatePlanStep


class CreatePlanStep(AddFeature.Step):
    class OutputModel(BaseModel):
        summary: str = Field(description="Brief summary of the implementation plan")
        artifact: ArtifactMetadata = Field(
            description="Implementation plan artifact (e.g., plan.md)"
        )

    def start(self, previous_result: ArchitectureReviewStep.OutputModel = None) -> str:
        artifacts = get_artifacts_from_workflow(self.workflow_id)
        workflow = workflow_store.get_workflow(self.workflow_id)
        step_dir = (
            f".artificer/workflow-AddFeature-{workflow.start_time}-"
            f"{self.workflow_id}/step-CreatePlanStep-{self.start_time}-{self.step_id}"
        )
        template = AddFeature._jinja_env.get_template("create_plan.md")
        return template.render(
            result=previous_result, artifacts=artifacts, step_dir=step_dir
        )

    def complete(self, output: OutputModel) -> type["ImplementFeatureStep"]:
        return ImplementFeatureStep


class ImplementFeatureStep(AddFeature.Step):
    class OutputModel(BaseModel):
        summary: str = Field(description="Brief summary of what was implemented")
        artifacts: list[ArtifactMetadata] = Field(
            min_length=1,
            description="List of files/artifacts created during implementation",
        )

    def start(self, previous_result: ArchitectureReviewStep.OutputModel = None) -> str:
        artifacts = get_artifacts_from_workflow(self.workflow_id)
        workflow = workflow_store.get_workflow(self.workflow_id)
        step_dir = (
            f".artificer/workflow-AddFeature-{workflow.start_time}-"
            f"{self.workflow_id}/step-ImplementFeatureStep-{self.start_time}-{self.step_id}"
        )
        template = AddFeature._jinja_env.get_template("implement_feature.md")
        return template.render(
            result=previous_result, artifacts=artifacts, step_dir=step_dir
        )

    def complete(self, output: OutputModel) -> type["TestFeatureStep"]:
        return TestFeatureStep


class TestFeatureStep(AddFeature.Step):
    class OutputModel(BaseModel):
        passed: bool = Field(description="Whether all tests passed")
        summary: str = Field(description="Brief summary of test results")
        artifact: ArtifactMetadata | None = Field(
            default=None,
            description="Optional test results artifact (e.g., test_output.txt)",
        )

    def start(self, previous_result: ImplementFeatureStep.OutputModel = None) -> str:
        artifacts = get_artifacts_from_workflow(self.workflow_id)
        workflow = workflow_store.get_workflow(self.workflow_id)
        step_dir = (
            f".artificer/workflow-AddFeature-{workflow.start_time}-"
            f"{self.workflow_id}/step-TestFeatureStep-{self.start_time}-{self.step_id}"
        )
        template = AddFeature._jinja_env.get_template("test_feature.md")
        return template.render(
            result=previous_result, artifacts=artifacts, step_dir=step_dir
        )

    def complete(self, output: OutputModel) -> type["ReviewFeatureStep"]:
        return ReviewFeatureStep


class ReviewFeatureStep(AddFeature.Step):
    class OutputModel(BaseModel):
        needs_revision: bool = Field(
            description="Whether the feature needs revision based on review"
        )
        summary: str = Field(description="Brief summary of review findings")
        artifact: ArtifactMetadata = Field(
            description="Code review artifact (e.g., review.md)"
        )

    def start(self, previous_result: TestFeatureStep.OutputModel = None) -> str:
        artifacts = get_artifacts_from_workflow(self.workflow_id)
        workflow = workflow_store.get_workflow(self.workflow_id)
        step_dir = (
            f".artificer/workflow-AddFeature-{workflow.start_time}-"
            f"{self.workflow_id}/step-ReviewFeatureStep-{self.start_time}-{self.step_id}"
        )
        template = AddFeature._jinja_env.get_template("review_feature.md")
        return template.render(
            result=previous_result, artifacts=artifacts, step_dir=step_dir
        )

    def complete(
        self, output: OutputModel
    ) -> type["CreatePlanStep"] | type["SummaryStep"]:
        if output.needs_revision:
            return CreatePlanStep
        return SummaryStep


class SummaryStep(AddFeature.Step):
    class OutputModel(BaseModel):
        summary: str = Field(description="Brief summary of completed feature work")
        artifact: ArtifactMetadata = Field(
            description="Summary document artifact (e.g., summary.md)"
        )

    def start(self, previous_result: ReviewFeatureStep.OutputModel = None) -> str:
        artifacts = get_artifacts_from_workflow(self.workflow_id)
        workflow = workflow_store.get_workflow(self.workflow_id)
        step_dir = (
            f".artificer/workflow-AddFeature-{workflow.start_time}-"
            f"{self.workflow_id}/step-SummaryStep-{self.start_time}-{self.step_id}"
        )
        template = AddFeature._jinja_env.get_template("summary.md")
        return template.render(
            result=previous_result, artifacts=artifacts, step_dir=step_dir
        )

    def complete(self, output: OutputModel) -> None:  # noqa: ARG002
        return None


AddFeature.register(mcp)


if __name__ == "__main__":
    mcp.run()
