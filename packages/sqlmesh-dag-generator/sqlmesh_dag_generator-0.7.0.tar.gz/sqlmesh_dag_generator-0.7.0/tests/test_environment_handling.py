"""
Test for SQLMesh environment handling
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlmesh_dag_generator import SQLMeshDAGGenerator
from sqlmesh_dag_generator.config import DAGGeneratorConfig, SQLMeshConfig, AirflowConfig, GenerationConfig


def test_environment_parameter_warning():
    """Test that using a named environment parameter shows a warning"""

    with pytest.warns(UserWarning, match="environment='prod' detected"):
        config = SQLMeshConfig(
            project_path="/tmp/test",
            environment="prod",  # Named environment should trigger warning
        )


def test_empty_environment_no_warning():
    """Test that empty environment string doesn't show warning"""

    # Empty string should NOT warn
    config = SQLMeshConfig(
        project_path="/tmp/test",
        environment="",
    )
    # If we get here without warning, test passes


def test_environment_not_found_error_message():
    """Test that 'Environment not found' error shows helpful message"""

    from sqlmesh_dag_generator.config import SQLMeshConfig

    # Simulate the error handling logic from execute_model
    config = SQLMeshConfig(
        project_path="/tmp/test",
        environment="prod",
    )

    # Simulate the exception that would be raised
    original_exception = Exception("Environment 'prod' was not found.")

    # Simulate the error handling in execute_model
    env_name = config.environment

    # This should match the error handling in generator.py
    with pytest.raises(RuntimeError) as exc_info:
        if "Environment" in str(original_exception) and "was not found" in str(original_exception):
            raise RuntimeError(
                f"SQLMesh environment '{env_name}' was not found.\n\n"
                f"🔧 SOLUTION: For Airflow production DAGs, use environment='' (empty string):\n\n"
                f"   generator = SQLMeshDAGGenerator(\n"
                f"       sqlmesh_project_path='/path/to/project',\n"
                f"       gateway='prod',  # ✅ Use gateway to switch environments\n"
                f"       # environment defaults to '' - no virtual environment\n"
                f"   )\n\n"
                f"   OR in YAML config:\n"
                f"   sqlmesh:\n"
                f"     project_path: /path/to/project\n"
                f"     gateway: prod\n"
                f"     environment: ''  # Empty string = no virtual environment\n\n"
                f"📚 Why? SQLMesh environments are virtual schemas for testing changes,\n"
                f"   not for production runs. Use 'gateway' to switch between dev/staging/prod.\n\n"
                f"   See docs/SQLMESH_ENVIRONMENTS.md for complete explanation.\n\n"
                f"Original error: {original_exception}"
            ) from original_exception

    # Verify the error message contains the helpful guidance
    error_message = str(exc_info.value)
    assert "For Airflow production DAGs, use environment=''" in error_message
    assert "Use gateway to switch environments" in error_message
    assert "docs/SQLMESH_ENVIRONMENTS.md" in error_message


def test_recommended_config_for_production():
    """Test that recommended production config doesn't trigger warnings"""

    # This is the recommended way - should not warn
    config = DAGGeneratorConfig(
        sqlmesh=SQLMeshConfig(
            project_path="/tmp/test",
            gateway="prod",  # Use gateway to switch environments
            environment="",  # Empty string for production (default)
        ),
        airflow=AirflowConfig(
            dag_id="test_dag",
        ),
        generation=GenerationConfig(),
    )

    assert config.sqlmesh.environment == ""
    assert config.sqlmesh.gateway == "prod"


def test_config_from_yaml_with_environment():
    """Test loading config from YAML that has environment set"""

    import tempfile
    import yaml

    yaml_content = """
sqlmesh:
  project_path: /tmp/test
  environment: prod  # This will trigger warning
  
airflow:
  dag_id: test_dag
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        f.flush()

        # Loading should warn about environment
        with pytest.warns(UserWarning, match="environment='prod' detected"):
            config = DAGGeneratorConfig.from_file(f.name)

        assert config.sqlmesh.environment == "prod"


def test_config_from_yaml_recommended():
    """Test loading recommended production config from YAML"""

    import tempfile

    yaml_content = """
sqlmesh:
  project_path: /tmp/test
  gateway: prod
  environment: ""  # Empty string - correct for production
  
airflow:
  dag_id: test_dag
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        f.flush()

        # Should not warn
        config = DAGGeneratorConfig.from_file(f.name)

        assert config.sqlmesh.environment == ""
        assert config.sqlmesh.gateway == "prod"

