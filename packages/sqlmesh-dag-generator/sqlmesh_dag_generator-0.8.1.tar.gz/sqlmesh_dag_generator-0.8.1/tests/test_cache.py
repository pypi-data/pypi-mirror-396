"""
Test cache directory handling
"""
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from sqlmesh_dag_generator import SQLMeshDAGGenerator


def test_cache_dir_warning_when_set(tmp_path, caplog):
    """Test that warning is logged when SQLMESH_CACHE_DIR is set"""
    cache_dir = tmp_path / "custom_cache"
    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / "config.yaml").write_text("gateways: {}")
    (project_path / "models").mkdir()
    (project_path / "models" / "test.sql").write_text("SELECT 1")

    with patch.dict(os.environ, {'SQLMESH_CACHE_DIR': str(cache_dir)}):
        with patch('sqlmesh_dag_generator.generator.Context') as mock_context:
            mock_context.return_value._models = {}

            generator = SQLMeshDAGGenerator(
                sqlmesh_project_path=str(project_path),
            )

            generator.load_sqlmesh_context()

            # Check that warning was logged
            assert "SQLMESH_CACHE_DIR is set" in caplog.text
            assert "NOT needed if you're using EFS" in caplog.text


def test_no_warning_when_not_set(tmp_path, caplog):
    """Test that no warning when SQLMESH_CACHE_DIR is not set"""
    project_path = tmp_path / "project"
    project_path.mkdir()
    (project_path / "config.yaml").write_text("gateways: {}")
    (project_path / "models").mkdir()
    (project_path / "models" / "test.sql").write_text("SELECT 1")

    # Ensure SQLMESH_CACHE_DIR is not set
    with patch.dict(os.environ, {}, clear=False):
        if 'SQLMESH_CACHE_DIR' in os.environ:
            del os.environ['SQLMESH_CACHE_DIR']

        with patch('sqlmesh_dag_generator.generator.Context') as mock_context:
            mock_context.return_value._models = {}

            generator = SQLMeshDAGGenerator(
                sqlmesh_project_path=str(project_path),
            )

            generator.load_sqlmesh_context()

            # Should not have cache warning
            assert "SQLMESH_CACHE_DIR" not in caplog.text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

