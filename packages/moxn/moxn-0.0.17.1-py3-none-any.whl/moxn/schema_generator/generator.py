from pathlib import Path
from uuid import UUID

from moxn.client import MoxnClient


class SchemaGenerator:
    """
    Schema generator for writing API-generated typed models into user codebases.

    Example:
        ```python
        from moxn.schema_generator import SchemaGenerator

        generator = SchemaGenerator()
        await generator.generate_schema(
            task_id="your-task-id",
            branch_name="main",
            output_dir="./my_types"
        )
        ```
    """

    async def generate_schema(
        self,
        task_id: str | UUID,
        branch_name: str = "main",
        output_dir: str | Path = Path("./moxn/types"),
    ) -> list[Path]:
        """
        Generate schema models for a specific task using the new task-based generation.

        Args:
            task_id: The task ID to generate models from
            branch_name: Branch to fetch task from (defaults to "main")
            output_dir: Directory where schema files will be written

        Returns:
            List of paths to generated schema files

        Raises:
            RuntimeError: If the generation request fails
            IOError: If file operations fail
        """
        # Convert output_dir to Path
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Use the new task-based generation method
        async with MoxnClient() as client:
            try:
                codegen_response = await client.generate_task_models(
                    task_id=task_id,
                    branch_name=branch_name,
                    output_dir=None,  # We'll handle file writing ourselves
                )
            except Exception as e:
                raise RuntimeError(f"Failed to generate task models: {e}") from e

        written_files: list[Path] = []

        # Write the generated code to the output directory
        file_path = output_dir / codegen_response.filename
        file_path.write_text(codegen_response.generated_code)
        written_files.append(file_path)

        # Create __init__.py to make the directory a package
        init_file = output_dir / "__init__.py"
        init_file.touch()
        written_files.append(init_file)

        return written_files
