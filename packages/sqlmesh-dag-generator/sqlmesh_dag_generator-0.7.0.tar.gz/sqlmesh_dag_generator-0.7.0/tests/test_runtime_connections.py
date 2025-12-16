"""
Test that runtime connections are properly passed to task execution.

This tests the fix for the issue where runtime connections (passed via connection parameter)
were not being used when creating SQLMesh Context in the execute_model function.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestRuntimeConnections:
    """Test runtime connection handling in task execution"""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary SQLMesh project"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            # Create models directory
            models_dir = project_path / "models"
            models_dir.mkdir()

            # Create a simple test model
            model_file = models_dir / "test_model.sql"
            model_file.write_text("""
MODEL (
    name test_schema.test_model,
    kind INCREMENTAL_BY_TIME_RANGE (
        time_column ds
    ),
    cron '@daily'
);

SELECT 1 as id, CURRENT_DATE as ds;
""")

            # Create config.yaml
            config_file = project_path / "config.yaml"
            config_file.write_text("""
gateways:
  test_gateway:
    connection:
      type: duckdb
      database: ':memory:'
    state_connection:
      type: duckdb
      database: ':memory:'

default_gateway: test_gateway
model_defaults:
  dialect: duckdb
""")

            yield project_path

    def test_merged_config_stored(self, temp_project):
        """Test that merged config is stored when runtime connections are provided"""
        from sqlmesh_dag_generator import SQLMeshDAGGenerator

        # Create generator with runtime connection
        generator = SQLMeshDAGGenerator(
            sqlmesh_project_path=str(temp_project),
            connection={
                "type": "duckdb",
                "database": ":memory:",
            },
            gateway="test_gateway"
        )

        # Load context - this should create and store merged config
        generator.load_sqlmesh_context()

        # Verify merged config was stored
        assert generator.merged_config is not None, "Merged config should be stored for runtime use"

    def test_merged_config_not_stored_without_runtime_connection(self, temp_project):
        """Test that merged config is not stored when no runtime connections are provided"""
        from sqlmesh_dag_generator import SQLMeshDAGGenerator

        # Create generator without runtime connection
        generator = SQLMeshDAGGenerator(
            sqlmesh_project_path=str(temp_project),
            gateway="test_gateway"
        )

        # Load context
        generator.load_sqlmesh_context()

        # Verify merged config was not stored (None)
        assert generator.merged_config is None, "Merged config should not be stored when no runtime connections provided"

    def test_execute_model_uses_merged_config(self, temp_project):
        """Test that execute_model function uses the merged config"""
        from sqlmesh_dag_generator import SQLMeshDAGGenerator
        from airflow import DAG
        from datetime import datetime
        from unittest.mock import patch, MagicMock

        # Create generator with runtime connection
        generator = SQLMeshDAGGenerator(
            sqlmesh_project_path=str(temp_project),
            connection={
                "type": "duckdb",
                "database": ":memory:",
            },
            state_connection={
                "type": "duckdb",
                "database": ":memory:",
            },
            gateway="test_gateway",
        )

        # Load models
        generator.extract_models()

        # Verify merged config is stored
        assert generator.merged_config is not None
        assert generator.runtime_gateway == "test_gateway"

        # Create a DAG
        dag = DAG(
            dag_id="test_dag",
            start_date=datetime(2023, 1, 1),
            schedule=None,
        )

        # Create tasks
        with dag:
            tasks = generator.create_tasks_in_dag(dag)

        # Verify tasks were created
        assert len(tasks) > 0

        # Get the first task
        task = list(tasks.values())[0]

        # Mock the Context to verify it's called with config
        with patch('sqlmesh.Context') as mock_context:
            mock_ctx_instance = MagicMock()
            mock_context.return_value = mock_ctx_instance

            # Mock the run method to avoid actual execution
            mock_ctx_instance.run = MagicMock(return_value=None)

            # Execute the task's callable
            task.python_callable(
                data_interval_start=datetime(2023, 1, 1),
                data_interval_end=datetime(2023, 1, 2),
            )

            # Verify Context was called with config and gateway
            mock_context.assert_called_once()
            call_kwargs = mock_context.call_args[1]

            # Verify the merged config and gateway were passed
            assert "config" in call_kwargs, "Context should be called with 'config' parameter"
            assert "gateway" in call_kwargs, "Context should be called with 'gateway' parameter"
            assert call_kwargs["config"] == generator.merged_config, "Context should use stored merged config"
            assert call_kwargs["gateway"] == "test_gateway", "Context should use runtime gateway"

    def test_connection_error_without_runtime_config(self, temp_project):
        """Test that helpful error occurs if no connection is configured"""
        from sqlmesh_dag_generator import SQLMeshDAGGenerator
        from sqlmesh.utils.errors import ConfigError

        # Create minimal config without connections
        config_file = temp_project / "config.yaml"
        config_file.write_text("""
model_defaults:
  dialect: duckdb
""")

        # Create generator WITHOUT runtime connection and WITHOUT gateway
        generator = SQLMeshDAGGenerator(
            sqlmesh_project_path=str(temp_project),
            gateway=None,  # No gateway specified
        )

        # This should fail when trying to load context
        with pytest.raises(ConfigError, match="No connection configured"):
            generator.load_sqlmesh_context()

    def test_runtime_connection_overrides_config_file(self, temp_project):
        """Test that runtime connection overrides config.yaml connections"""
        from sqlmesh_dag_generator import SQLMeshDAGGenerator

        # Create generator with runtime connection
        runtime_conn = {
            "type": "duckdb",
            "database": ":memory:",
        }

        generator = SQLMeshDAGGenerator(
            sqlmesh_project_path=str(temp_project),
            connection=runtime_conn,
            gateway="test_gateway"
        )

        # Load context
        generator.load_sqlmesh_context()

        # Verify merged config was created
        assert generator.merged_config is not None

        # Check that the gateway has the runtime connection
        assert "test_gateway" in generator.merged_config.gateways
        gateway_config = generator.merged_config.gateways["test_gateway"]

        # The runtime connection should be in the gateway config
        assert gateway_config.connection is not None
        # SQLMesh converts the dict to a ConnectionConfig object, so check the type
        connection = gateway_config.connection
        # Check it's a DuckDB connection
        assert "DuckDB" in str(type(connection).__name__)
        assert connection.database == ":memory:"

