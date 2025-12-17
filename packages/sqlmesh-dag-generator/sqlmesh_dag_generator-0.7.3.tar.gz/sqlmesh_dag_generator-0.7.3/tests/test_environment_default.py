"""
Test to verify the environment default fix works correctly.
"""
import pytest
from sqlmesh_dag_generator import SQLMeshDAGGenerator
from sqlmesh_dag_generator.config import SQLMeshConfig


def test_environment_default_is_empty_string():
    """Test that the default environment is now empty string, not 'prod'"""
    config = SQLMeshConfig(project_path="/tmp/test")
    assert config.environment == "", f"Expected empty string, got: '{config.environment}'"


def test_generator_without_environment_uses_empty_string(tmp_path):
    """Test that generator without explicit environment parameter uses empty string"""
    # Create minimal SQLMesh project
    project_path = tmp_path / "sqlmesh_project"
    project_path.mkdir()
    (project_path / "config.yaml").write_text("""
gateways:
  default:
    connection:
      type: duckdb
      database: ':memory:'
""")
    models_dir = project_path / "models"
    models_dir.mkdir()

    # Create generator without environment parameter
    generator = SQLMeshDAGGenerator(
        sqlmesh_project_path=str(project_path),
        dag_id="test_dag"
    )

    # Verify environment is empty string
    assert generator.config.sqlmesh.environment == "", \
        f"Expected empty string, got: '{generator.config.sqlmesh.environment}'"


def test_generator_with_explicit_empty_string(tmp_path):
    """Test that explicitly passing environment='' works"""
    # Create minimal SQLMesh project
    project_path = tmp_path / "sqlmesh_project"
    project_path.mkdir()
    (project_path / "config.yaml").write_text("""
gateways:
  default:
    connection:
      type: duckdb
      database: ':memory:'
""")
    models_dir = project_path / "models"
    models_dir.mkdir()

    # Create generator with explicit empty string
    generator = SQLMeshDAGGenerator(
        sqlmesh_project_path=str(project_path),
        dag_id="test_dag",
        environment=""  # Explicit empty string
    )

    # Verify environment is empty string
    assert generator.config.sqlmesh.environment == "", \
        f"Expected empty string, got: '{generator.config.sqlmesh.environment}'"


def test_generator_with_explicit_environment(tmp_path):
    """Test that explicitly passing environment='some_env' triggers a warning"""
    # Create minimal SQLMesh project
    project_path = tmp_path / "sqlmesh_project"
    project_path.mkdir()
    (project_path / "config.yaml").write_text("""
gateways:
  default:
    connection:
      type: duckdb
      database: ':memory:'
""")
    models_dir = project_path / "models"
    models_dir.mkdir()

    # Create generator with explicit environment - should warn
    with pytest.warns(UserWarning, match="environment='dev' detected"):
        generator = SQLMeshDAGGenerator(
            sqlmesh_project_path=str(project_path),
            dag_id="test_dag",
            environment="dev"  # Explicit non-empty environment
        )

    # Verify environment is set correctly
    assert generator.config.sqlmesh.environment == "dev", \
        f"Expected 'dev', got: '{generator.config.sqlmesh.environment}'"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

