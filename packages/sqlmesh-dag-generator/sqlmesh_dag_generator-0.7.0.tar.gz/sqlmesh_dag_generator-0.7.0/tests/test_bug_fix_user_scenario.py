"""
Test that simulates the exact user scenario from the bug report.

This ensures the fix resolves the actual error:
  SQLMeshError: Environment 'prod' was not found.
"""
import tempfile
from pathlib import Path
from sqlmesh_dag_generator import SQLMeshDAGGenerator


def test_user_scenario_no_environment_parameter():
    """
    Simulate the exact user scenario where they DON'T pass environment parameter.
    Before fix: Would default to "prod" and fail
    After fix: Defaults to "" and works
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        project_path = Path(tmp_dir) / "sqlmesh_project"
        project_path.mkdir()

        # Create minimal config (no "prod" environment)
        config_yaml = project_path / "config.yaml"
        config_yaml.write_text("""
model_defaults:
  dialect: duckdb

gateways:
  default:
    connection:
      type: duckdb
      database: ':memory:'
    state_connection:
      type: duckdb
      database: ':memory:'
""")

        # Create models directory
        models_dir = project_path / "models"
        models_dir.mkdir()

        # Create a simple model
        model_file = models_dir / "test_model.sql"
        model_file.write_text("""
MODEL (
  name test_db.test_model,
  kind FULL
);

SELECT 1 as id;
""")

        # This is what the user did - NO environment parameter
        # Before fix: This would fail with "Environment 'prod' was not found"
        # After fix: This should work (defaults to "")
        generator = SQLMeshDAGGenerator(
            sqlmesh_project_path=str(project_path),
            dag_id="test_dag",
            # NOTE: No environment parameter!
        )

        # Verify environment is empty string (not "prod")
        assert generator.config.sqlmesh.environment == "", \
            f"Expected empty string, got '{generator.config.sqlmesh.environment}'"

        # Load context - this would fail before the fix
        context = generator.load_sqlmesh_context()

        # Extract models - should work without errors
        generator.extract_models()

        print("✅ SUCCESS: User scenario works without environment parameter!")
        print(f"   Environment: '{generator.config.sqlmesh.environment}' (empty string = production mode)")
        print(f"   Models found: {len(generator.models)}")


def test_user_scenario_explicit_empty_string():
    """
    Simulate user explicitly passing environment="" (what they should do for production)
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        project_path = Path(tmp_dir) / "sqlmesh_project"
        project_path.mkdir()

        # Create minimal config
        config_yaml = project_path / "config.yaml"
        config_yaml.write_text("""
model_defaults:
  dialect: duckdb

gateways:
  default:
    connection:
      type: duckdb
      database: ':memory:'
    state_connection:
      type: duckdb
      database: ':memory:'
""")

        models_dir = project_path / "models"
        models_dir.mkdir()

        model_file = models_dir / "test_model.sql"
        model_file.write_text("""
MODEL (
  name test_db.test_model,
  kind FULL
);

SELECT 1 as id;
""")

        # User explicitly passes environment=""
        generator = SQLMeshDAGGenerator(
            sqlmesh_project_path=str(project_path),
            dag_id="test_dag",
            environment="",  # Explicit empty string for production
        )

        assert generator.config.sqlmesh.environment == ""

        context = generator.load_sqlmesh_context()
        generator.extract_models()

        print("✅ SUCCESS: Explicit environment='' works!")


if __name__ == "__main__":
    print("=" * 80)
    print("Testing User Scenario from Bug Report")
    print("=" * 80)
    print()

    print("Test 1: No environment parameter (most common case)")
    print("-" * 80)
    test_user_scenario_no_environment_parameter()
    print()

    print("Test 2: Explicit environment='' (recommended for production)")
    print("-" * 80)
    test_user_scenario_explicit_empty_string()
    print()

    print("=" * 80)
    print("✅ ALL TESTS PASSED - Bug is fixed!")
    print("=" * 80)

