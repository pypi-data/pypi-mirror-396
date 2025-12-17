"""
Tests for enterprise features:
- Callback support (on_failure, on_success, sla_miss)
- Tag-based filtering
- Pool configuration
- Pattern-based model selection
- Trigger downstream DAG
"""
import pytest
from sqlmesh_dag_generator import SQLMeshDAGGenerator, DAGGeneratorConfig
from sqlmesh_dag_generator.config import SQLMeshConfig, AirflowConfig, GenerationConfig
from sqlmesh_dag_generator.models import SQLMeshModelInfo


class TestCallbackSupport:
    """Test callback configuration"""

    def test_on_failure_callback_in_config(self):
        """Test that on_failure_callback can be set"""
        config = AirflowConfig(
            dag_id="test_dag",
            on_failure_callback="my_module.slack_alert",
        )
        assert config.on_failure_callback == "my_module.slack_alert"

    def test_on_success_callback_in_config(self):
        """Test that on_success_callback can be set"""
        config = AirflowConfig(
            dag_id="test_dag",
            on_success_callback="my_module.log_success",
        )
        assert config.on_success_callback == "my_module.log_success"

    def test_sla_miss_callback_in_config(self):
        """Test that sla_miss_callback can be set"""
        config = AirflowConfig(
            dag_id="test_dag",
            sla_miss_callback="my_module.sla_alert",
        )
        assert config.sla_miss_callback == "my_module.sla_alert"

    def test_sla_seconds_in_config(self):
        """Test that SLA can be set in seconds"""
        config = AirflowConfig(
            dag_id="test_dag",
            sla=3600,  # 1 hour
        )
        assert config.sla == 3600

    def test_generator_with_callbacks(self, tmp_path):
        """Test generator accepts callback parameters"""
        project_path = tmp_path / "project"
        project_path.mkdir()
        (project_path / "config.yaml").write_text("gateways:\n  default:\n    connection:\n      type: duckdb")

        generator = SQLMeshDAGGenerator(
            sqlmesh_project_path=str(project_path),
            dag_id="test_callback_dag",
            on_failure_callback="alerts.slack_notify",
            on_success_callback="alerts.log_success",
            sla=7200,
        )

        assert generator.config.airflow.on_failure_callback == "alerts.slack_notify"
        assert generator.config.airflow.on_success_callback == "alerts.log_success"
        assert generator.config.airflow.sla == 7200


class TestTagBasedFiltering:
    """Test tag-based model filtering"""

    def test_include_tags_in_config(self):
        """Test that include_tags can be set"""
        config = GenerationConfig(
            include_tags=["finance", "core"],
        )
        assert config.include_tags == ["finance", "core"]

    def test_exclude_tags_in_config(self):
        """Test that exclude_tags can be set"""
        config = GenerationConfig(
            exclude_tags=["deprecated", "test"],
        )
        assert config.exclude_tags == ["deprecated", "test"]

    def test_generator_with_tags(self, tmp_path):
        """Test generator accepts tag filter parameters"""
        project_path = tmp_path / "project"
        project_path.mkdir()
        (project_path / "config.yaml").write_text("gateways:\n  default:\n    connection:\n      type: duckdb")

        generator = SQLMeshDAGGenerator(
            sqlmesh_project_path=str(project_path),
            dag_id="test_tag_dag",
            include_tags=["production", "tier1"],
            exclude_tags=["experimental"],
        )

        assert generator.config.generation.include_tags == ["production", "tier1"]
        assert generator.config.generation.exclude_tags == ["experimental"]


class TestPoolConfiguration:
    """Test Airflow pool configuration"""

    def test_pool_in_config(self):
        """Test that pool can be set"""
        config = GenerationConfig(
            pool="sqlmesh_pool",
            pool_slots=2,
        )
        assert config.pool == "sqlmesh_pool"
        assert config.pool_slots == 2

    def test_pool_slots_default(self):
        """Test that pool_slots defaults to 1"""
        config = GenerationConfig()
        assert config.pool_slots == 1

    def test_generator_with_pool(self, tmp_path):
        """Test generator accepts pool parameters"""
        project_path = tmp_path / "project"
        project_path.mkdir()
        (project_path / "config.yaml").write_text("gateways:\n  default:\n    connection:\n      type: duckdb")

        generator = SQLMeshDAGGenerator(
            sqlmesh_project_path=str(project_path),
            dag_id="test_pool_dag",
            pool="db_pool",
            pool_slots=3,
        )

        assert generator.config.generation.pool == "db_pool"
        assert generator.config.generation.pool_slots == 3


class TestTriggerDownstreamDAG:
    """Test trigger downstream DAG configuration"""

    def test_trigger_dag_id_in_config(self):
        """Test that trigger_dag_id can be set"""
        config = GenerationConfig(
            trigger_dag_id="ml_training_dag",
        )
        assert config.trigger_dag_id == "ml_training_dag"

    def test_trigger_dag_conf_in_config(self):
        """Test that trigger_dag_conf can be set"""
        config = GenerationConfig(
            trigger_dag_id="ml_training_dag",
            trigger_dag_conf={"model_version": "v2", "retrain": True},
        )
        assert config.trigger_dag_conf == {"model_version": "v2", "retrain": True}

    def test_generator_with_trigger_dag(self, tmp_path):
        """Test generator accepts trigger DAG parameters"""
        project_path = tmp_path / "project"
        project_path.mkdir()
        (project_path / "config.yaml").write_text("gateways:\n  default:\n    connection:\n      type: duckdb")

        generator = SQLMeshDAGGenerator(
            sqlmesh_project_path=str(project_path),
            dag_id="test_trigger_dag",
            trigger_dag_id="downstream_dag",
            trigger_dag_conf={"key": "value"},
        )

        assert generator.config.generation.trigger_dag_id == "downstream_dag"
        assert generator.config.generation.trigger_dag_conf == {"key": "value"}


class TestModelPatternFiltering:
    """Test model pattern (regex) filtering"""

    def test_model_pattern_in_config(self):
        """Test that model_pattern can be set"""
        config = GenerationConfig(
            model_pattern=r"^analytics\..*",
        )
        assert config.model_pattern == r"^analytics\..*"

    def test_generator_with_pattern(self, tmp_path):
        """Test generator accepts model_pattern parameter"""
        project_path = tmp_path / "project"
        project_path.mkdir()
        (project_path / "config.yaml").write_text("gateways:\n  default:\n    connection:\n      type: duckdb")

        generator = SQLMeshDAGGenerator(
            sqlmesh_project_path=str(project_path),
            dag_id="test_pattern_dag",
            model_pattern=r".*_fact$",
        )

        assert generator.config.generation.model_pattern == r".*_fact$"


class TestCombinedEnterpriseFeatures:
    """Test multiple enterprise features together"""

    def test_full_enterprise_config(self, tmp_path):
        """Test full enterprise configuration with all new features"""
        project_path = tmp_path / "project"
        project_path.mkdir()
        (project_path / "config.yaml").write_text("gateways:\n  default:\n    connection:\n      type: duckdb")

        generator = SQLMeshDAGGenerator(
            sqlmesh_project_path=str(project_path),
            dag_id="enterprise_dag",
            # Callbacks
            on_failure_callback="alerts.pagerduty_alert",
            on_success_callback="metrics.record_success",
            sla_miss_callback="alerts.sla_breach",
            sla=1800,  # 30 minutes
            # Tag filtering
            include_tags=["production"],
            exclude_tags=["deprecated"],
            # Resource management
            pool="prod_pool",
            pool_slots=2,
            # Pattern filtering
            model_pattern=r"^prod\..*",
            # Trigger downstream
            trigger_dag_id="feature_store_update",
            trigger_dag_conf={"source": "sqlmesh"},
        )

        # Verify all config values
        assert generator.config.airflow.on_failure_callback == "alerts.pagerduty_alert"
        assert generator.config.airflow.on_success_callback == "metrics.record_success"
        assert generator.config.airflow.sla_miss_callback == "alerts.sla_breach"
        assert generator.config.airflow.sla == 1800
        assert generator.config.generation.include_tags == ["production"]
        assert generator.config.generation.exclude_tags == ["deprecated"]
        assert generator.config.generation.pool == "prod_pool"
        assert generator.config.generation.pool_slots == 2
        assert generator.config.generation.model_pattern == r"^prod\..*"
        assert generator.config.generation.trigger_dag_id == "feature_store_update"
        assert generator.config.generation.trigger_dag_conf == {"source": "sqlmesh"}


