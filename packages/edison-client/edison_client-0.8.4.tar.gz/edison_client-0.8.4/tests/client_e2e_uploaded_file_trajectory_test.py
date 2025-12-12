import os
import tempfile
from pathlib import Path
from uuid import UUID

import pytest
import pytest_asyncio

from edison_client.clients.rest_client import RestClient
from edison_client.models.app import JobNames, RuntimeConfig, Stage, TaskRequest
from edison_client.models.data_storage_methods import RawFetchResponse

ADMIN_API_KEY = os.environ.get("PLAYWRIGHT_ADMIN_API_KEY", "")


@pytest_asyncio.fixture(name="admin_client")
async def fixture_admin_client():
    """Create a RestClient for testing; using a admin user key with privileged access."""
    client = RestClient(
        stage=Stage.DEV,
        api_key=ADMIN_API_KEY,
    )
    try:
        yield client
    finally:
        await client.aclose()
        client.close()


@pytest.mark.timeout(300)
def test_upload_and_run_analysis_task(admin_client: RestClient):
    """Test uploading a file with prompt, running analysis task, and downloading outputs."""
    prompt_content = "draw a blue square"

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", encoding="utf-8"
    ) as temp_file:
        temp_file.write(prompt_content)
        temp_file.flush()
        temp_file_path = Path(temp_file.name)

        data_entry_uri = admin_client.upload_file(
            file_path=temp_file_path,
            name="blue_square_prompt",
            description="A prompt to draw a blue square",
        )

        # Verify the upload by extracting the ID and fetching
        data_storage_id = data_entry_uri.split(":", 1)[1]
        fetch_response = admin_client.fetch_data_from_storage(UUID(data_storage_id))
        assert isinstance(fetch_response, RawFetchResponse)
        assert fetch_response.content == prompt_content

        task_request = TaskRequest(
            name=JobNames.ANALYSIS,  # Use the data analysis crow
            query="Open the attached file and follow the instructions in it. Create an image as specified.",
            runtime_config=RuntimeConfig(
                timeout=200,
            ),
        )

        results = admin_client.run_tasks_until_done(
            task_data=task_request,
            files=[data_entry_uri],  # Simple file attachment!
            verbose=True,
            progress_bar=True,
            timeout=600,  # 10 minute timeout
        )

        assert len(results) == 1
        task_result = results[0]
        output_files = admin_client.list_files(str(task_result.task_id))

        assert len(output_files["data"]) > 0, (
            "Task should have created at least one output file"
        )

        with tempfile.TemporaryDirectory() as output_dir:
            for file_entry in output_files["data"]:
                data_storage = file_entry["data_storage"]
                file_id = data_storage["id"]

                result = admin_client.fetch_data_from_storage(UUID(file_id))

                # Save the file content
                if isinstance(result, RawFetchResponse):
                    downloaded_path = Path(output_dir) / (
                        result.filename.name if result.filename else result.entry_name
                    )
                    downloaded_path.write_text(result.content)
                elif isinstance(result, Path):
                    downloaded_path = result
                else:
                    raise TypeError(f"Unexpected result type: {type(result)}")

                assert downloaded_path.exists()
                assert downloaded_path.stat().st_size > 0

        # Clean up the uploaded input file
        admin_client.delete_data_storage_entry(UUID(data_storage_id))
