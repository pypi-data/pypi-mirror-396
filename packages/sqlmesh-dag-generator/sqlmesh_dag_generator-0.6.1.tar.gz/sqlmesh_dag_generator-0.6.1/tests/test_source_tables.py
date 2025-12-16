"""
Test source table extraction and dummy task creation
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from sqlmesh_dag_generator import SQLMeshDAGGenerator


def test_source_tables_extraction(tmp_path):
    """Test that source tables are extracted from SQLMesh models"""
    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / "config.yaml").write_text("gateways: {}")
    (project_path / "models").mkdir()

    # Create a simple model file
    (project_path / "models" / "test_model.sql").write_text("""
    MODEL (name test_model);
    SELECT * FROM raw.source_table_1;
    """)

    with patch('sqlmesh_dag_generator.generator.Context') as mock_context:
        # Create mock model with source tables
        mock_model = MagicMock()
        mock_model.name = "test_model"
        mock_model.depends_on = {"raw.source_table_1", "raw.source_table_2"}
        mock_model.source_tables = {"raw.source_table_1", "raw.source_table_2"}
        mock_model.cron = None
        mock_model.interval_unit = None
        mock_model.kind = "FULL"
        mock_model.owner = None
        mock_model.tags = []
        mock_model.description = None

        mock_context.return_value._models = {"test_model": mock_model}

        generator = SQLMeshDAGGenerator(
            sqlmesh_project_path=str(project_path),
            include_source_tables=True,
        )

        generator.load_sqlmesh_context()
        generator.extract_models()

        # Get source tables
        source_tables = generator.get_source_tables("test_model")

        # Should extract source tables
        assert len(source_tables) == 2
        assert "raw.source_table_1" in source_tables
        assert "raw.source_table_2" in source_tables


def test_source_tables_dummy_tasks_created(tmp_path):
    """Test that dummy tasks are created for source tables"""
    from airflow import DAG
    from datetime import datetime

    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / "config.yaml").write_text("gateways: {}")
    (project_path / "models").mkdir()

    with patch('sqlmesh_dag_generator.generator.Context') as mock_context:
        # Create mock model
        mock_model = MagicMock()
        mock_model.name = "test_model"
        mock_model.depends_on = set()
        mock_model.source_tables = {"raw.event_hub", "raw.connector"}
        mock_model.cron = None
        mock_model.interval_unit = None
        mock_model.kind = "FULL"
        mock_model.owner = None
        mock_model.tags = []
        mock_model.description = None

        mock_context.return_value._models = {"test_model": mock_model}
        mock_context.return_value.run = MagicMock()

        generator = SQLMeshDAGGenerator(
            sqlmesh_project_path=str(project_path),
            include_source_tables=True,
        )

        # Create DAG
        with DAG(
            dag_id="test_dag",
            start_date=datetime(2023, 1, 1),
            schedule="@daily",
        ) as dag:
            tasks = generator.create_tasks_in_dag(dag)

        # Should have model task + source table tasks
        assert len(tasks) > 1

        # Check source table tasks exist
        assert "raw.event_hub" in tasks
        assert "raw.connector" in tasks

        # Check task IDs are valid
        source_task_ids = [task.task_id for task in tasks.values()]
        assert "source__raw_event_hub" in source_task_ids
        assert "source__raw_connector" in source_task_ids


def test_source_tables_disabled(tmp_path):
    """Test that source table tasks are not created when disabled"""
    from airflow import DAG
    from datetime import datetime

    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / "config.yaml").write_text("gateways: {}")
    (project_path / "models").mkdir()

    with patch('sqlmesh_dag_generator.generator.Context') as mock_context:
        mock_model = MagicMock()
        mock_model.name = "test_model"
        mock_model.depends_on = set()
        mock_model.source_tables = {"raw.source_table"}
        mock_model.cron = None
        mock_model.interval_unit = None
        mock_model.kind = "FULL"
        mock_model.owner = None
        mock_model.tags = []
        mock_model.description = None

        mock_context.return_value._models = {"test_model": mock_model}
        mock_context.return_value.run = MagicMock()

        generator = SQLMeshDAGGenerator(
            sqlmesh_project_path=str(project_path),
            include_source_tables=False,  # Disabled
        )

        with DAG(
            dag_id="test_dag",
            start_date=datetime(2023, 1, 1),
            schedule="@daily",
        ) as dag:
            tasks = generator.create_tasks_in_dag(dag)

        # Should only have model task, no source tasks
        assert len(tasks) == 1
        assert "test_model" in tasks
        assert "raw.source_table" not in tasks


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

