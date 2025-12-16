# SQLMesh DAG Generator

Generate Apache Airflow DAGs from SQLMesh projects - **no cloud dependencies required**.

Transform your SQLMesh models into production-ready Airflow DAGs with **full data lineage**, automatically!

## ✨ Key Features

- 🔥 **Dynamic DAG Generation (Default)**: Fire-and-forget - place DAG once, auto-discovers models at runtime
- 📅 **Auto-Scheduling**: Automatically detects DAG schedule from SQLMesh model intervals - no manual configuration!
- 🔐 **Runtime Connection Parametrization**: Pass database credentials via Airflow Connections - no hardcoded secrets!
- ✅ **Full Lineage in Airflow**: Each SQLMesh model = One Airflow task with proper dependencies
- 🌍 **Multi-Environment Support**: Use Airflow Variables + SQLMesh gateways for dev/staging/prod
- ⚡ **Incremental Models**: Proper handling with `data_interval_start/end`
- 🎯 **Enhanced Error Handling**: SQLMesh-specific error messages in Airflow logs
- 🛠️ **Dual Mode**: Dynamic (auto-discovery, default) or Static (full control)
- 🚫 **No Vendor Lock-in**: Open source, no cloud dependencies

## ⚠️ Important: Gateway vs Environment

**SQLMesh uses "gateways" to switch between environments, NOT an "environment" parameter.**

```python
# ❌ WRONG - environment parameter is for SQLMesh virtual environments (testing)
generator = SQLMeshDAGGenerator(
    sqlmesh_project_path="/path/to/project",
    environment="prod",  # ERROR: Environment 'prod' was not found
)

# ✅ CORRECT - Use gateway to switch between dev/staging/prod
generator = SQLMeshDAGGenerator(
    sqlmesh_project_path="/path/to/project",
    gateway="prod",  # This is how you select your environment!
    # environment defaults to "" (empty string) - perfect for production
)
```

**📚 Read [Understanding SQLMesh Environments](docs/SQLMESH_ENVIRONMENTS.md) for the complete explanation of the difference between `gateway` and `environment`.**

## 🚀 Quick Start (3 Steps)

### 1. Install
```bash
pip install sqlmesh-dag-generator  # (when published)
# OR
git clone <repo> && cd SQLMeshDAGGenerator && pip install -e .
```

### 2. Generate DAG (Dynamic Mode - Default!)
```python
from sqlmesh_dag_generator import SQLMeshDAGGenerator

# Point to your SQLMesh project
generator = SQLMeshDAGGenerator(
    sqlmesh_project_path="/path/to/your/sqlmesh/project",
    dag_id="my_pipeline",
    schedule_interval="@daily"
)

# Generate dynamic DAG (default - fire and forget!)
dag_code = generator.generate_dynamic_dag()

# Save it
with open("my_pipeline.py", "w") as f:
    f.write(dag_code)
```

### 3. Deploy to Airflow
```bash
cp my_pipeline.py /opt/airflow/dags/
```

**That's it! 🎉** Your SQLMesh models are now orchestrated by Airflow. The DAG will auto-discover models at runtime - no regeneration needed when models change!

## 💡 What You Get

### Your SQLMesh Project:
```
my_project/
└── models/
    ├── raw_orders.sql
    ├── stg_orders.sql      # depends on raw_orders
    └── orders_summary.sql  # depends on stg_orders
```

### Generated Airflow DAG:
```
Airflow Graph View:
  [raw_orders] → [stg_orders] → [orders_summary]
  
✅ Each model = separate task
✅ SQLMesh dependencies = Airflow dependencies  
✅ Full lineage visible in Airflow UI
```

## 📚 Documentation

### Getting Started
- **[Quick Start Guide](docs/QUICKSTART.md)** - Step-by-step tutorial (start here!)
- **[Quick Reference](docs/QUICK_REFERENCE.md)** - One-page cheat sheet
- **[Examples](examples/)** - Code examples

### Configuration & Features
- **[Auto-Scheduling Guide](docs/AUTO_SCHEDULING.md)** - Automatic schedule detection 📅
- **[Runtime Configuration](docs/RUNTIME_CONFIGURATION.md)** - Pass credentials via Airflow Connections 🔐
- **[Multi-Environment Setup](docs/MULTI_ENVIRONMENT.md)** - Configure for dev/staging/prod ⚠️ IMPORTANT
- **[Dynamic DAGs](docs/DYNAMIC_DAGS.md)** - Fire-and-forget mode explained

### Deployment & Production
- **[Deployment Checklist](docs/DEPLOYMENT_CHECKLIST.md)** - Step-by-step deployment guide ✅ NEW!
- **[Container Deployment](docs/CONTAINER_DEPLOYMENT.md)** - Docker, Kubernetes, ECS, Cloud Composer 🐳 NEW!
- **[Common Issues](docs/COMMON_ISSUES.md)** - Real-world problems and solutions 🔧 NEW!
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Debug guide
- **[Deployment Warnings](docs/DEPLOYMENT_WARNINGS.md)** - Critical production considerations

### Reference
- **[Usage Guide](docs/USAGE.md)** - Complete reference
- **[Migration Guide](docs/MIGRATION_GUIDE.md)** - Fix common configuration issues
- **[Architecture](docs/ARCHITECTURE.md)** - Technical details

## 🔥 Why Dynamic Mode (Default)?

**Dynamic mode** auto-discovers SQLMesh models at runtime:

```python
dag_code = generator.generate_dynamic_dag()  # Default behavior!
```

**Benefits:**
- ✅ **No regeneration needed** when SQLMesh models change
- ✅ **Always in sync** - DAG updates automatically
- ✅ **Multi-environment** - Uses Airflow Variables
- ✅ **Production-ready** - Enhanced error handling

Want static mode instead? Just use `generator.generate_dag()` - see [Usage Guide](docs/USAGE.md).

## 🎯 Simple Example

The simplest possible usage - just 3 lines of code:

```python
from sqlmesh_dag_generator import SQLMeshDAGGenerator

generator = SQLMeshDAGGenerator(
    sqlmesh_project_path="/path/to/your/sqlmesh/project",
    dag_id="my_pipeline"
)

dag_code = generator.generate_dynamic_dag()
```

See [examples/simple_generate.py](examples/simple_generate.py) for a complete runnable example.

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

[Your License Here]

---

**Built with ❤️ for the data engineering community**

### Configuration File

Create a `dag_generator_config.yaml`:

```yaml
sqlmesh:
  project_path: "/path/to/sqlmesh/project"
  gateway: "prod"
  environment: ""  # Empty for production
  default_catalog: "my_catalog" # Optional: For 3-part naming support

airflow:
  dag_id: "sqlmesh_pipeline"
  schedule_interval: "0 0 * * *"
  default_args:
    owner: "data-team"
    retries: 3
    retry_delay_minutes: 5
  tags:
    - sqlmesh
    - analytics

generation:
  output_dir: "/path/to/airflow/dags"
  operator_type: "python"  # or "bash"
  include_tests: true
  parallel_tasks: true
  auto_replan_on_change: true  # Automatically run 'sqlmesh plan' if models change
  return_value: true           # Enable/disable XCom return values
```

## How It Works

1. **Load SQLMesh Project**: Reads your SQLMesh project configuration and models
2. **Extract Dependencies**: Analyzes SQL queries to build dependency graph
3. **Generate Tasks**: Creates Airflow tasks for each SQLMesh model
4. **Set Dependencies**: Connects tasks based on model dependencies
5. **Apply Schedules**: Preserves cron schedules and execution logic
6. **Output DAG**: Generates Python file ready for Airflow

## Architecture

```
SQLMesh Project
    ↓
SQLMeshDAGGenerator
    ├── Context Loader (loads SQLMesh context)
    ├── Model Parser (extracts model metadata)
    ├── Dependency Resolver (builds dependency graph)
    └── DAG Builder (generates Airflow DAG)
    ↓
Airflow DAG File
```

## Advanced Features

### Custom Operators

```python
from sqlmesh_dag_generator import SQLMeshDAGGenerator
from airflow.operators.python import PythonOperator

generator = SQLMeshDAGGenerator(
    sqlmesh_project_path="/path/to/project",
    custom_operator_class=PythonOperator,
    operator_kwargs={"provide_context": True}
)
```

### Model Filtering

```python
# Generate DAG for specific models only
generator = SQLMeshDAGGenerator(
    sqlmesh_project_path="/path/to/project",
    include_models=["model1", "model2"],
    exclude_models=["test_*"]
)
```

### Dynamic Task Generation

```python
# Generate tasks with dynamic parallelism
generator = SQLMeshDAGGenerator(
    sqlmesh_project_path="/path/to/project",
    enable_dynamic_tasks=True,
    max_parallel_tasks=10
)
```

## ⚠️ Important: Deployment Warnings

### 🔴 Distributed Airflow Requires Shared Volume

If you're using **KubernetesExecutor**, **CeleryExecutor**, or any distributed Airflow setup:

**Your SQLMesh project MUST be accessible to all workers!**

**Solutions:**
- **Option 1 (Recommended):** Mount project on shared volume (EFS/NFS/Filestore)
- **Option 2:** Bake project into Docker image (loses fire-and-forget benefit)

**See full guide:** [docs/DEPLOYMENT_WARNINGS.md](docs/DEPLOYMENT_WARNINGS.md)

### 🟡 Operator Type Limitations

- **Dynamic Mode:** Python operator only (current limitation)
- **Static Mode:** Supports Python, Bash, and Kubernetes operators

For Bash/Kubernetes in dynamic mode, use static generation for now.

### 🟢 Kubernetes Operator Support

To use `operator_type: kubernetes`:
```yaml
generation:
  operator_type: kubernetes
  docker_image: "your-registry/sqlmesh:v1.0"  # REQUIRED
  namespace: "data-pipelines"
```

**📖 Full Documentation:** [docs/DEPLOYMENT_WARNINGS.md](docs/DEPLOYMENT_WARNINGS.md)

## Requirements

- Python >= 3.8
- Apache Airflow >= 2.0
- SQLMesh >= 0.20.0

## Development

```bash
# Clone the repository
git clone https://github.com/yourusername/sqlmesh-dag-generator.git
cd sqlmesh-dag-generator

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
black .
ruff check .
```

## 🔧 Troubleshooting

### Common Issues

#### 1. `TypeError: Object of type CompletionStatus is not JSON serializable`
**Cause:** Airflow cannot serialize the SQLMesh `CompletionStatus` enum returned by tasks.
**Fix:** Upgrade to v0.7.2+. This version automatically converts the status to a string.
Alternatively, use `return_value=False` in your generator config:
```python
generator = SQLMeshDAGGenerator(
    ...,
    return_value=False  # Disable XCom return values
)
```

#### 2. `ConfigError: A query is required and must be a SELECT statement` (External Models)
**Cause:** Defining external models in `.sql` files is not supported by the generator.
**Fix:** Define external models in `external_models.yaml` instead.
```yaml
# external_models.yaml
models:
  - name: raw.users
    kind: EXTERNAL
    columns:
      id: INT
      name: TEXT
```

#### 3. "Environment 'prod' was not found"
**Cause:** You are using `environment="prod"` instead of `gateway="prod"`.
**Fix:** Set `gateway="prod"` and leave `environment` as empty string (default).
```python
generator = SQLMeshDAGGenerator(
    ...,
    gateway="prod",
    environment=""  # Correct for production
)
```

#### 4. Changes to models are not picked up
**Cause:** SQLMesh requires a plan/apply step to register changes.
**Fix:** Enable `auto_replan_on_change` in your generator config:
```python
generator = SQLMeshDAGGenerator(
    ...,
    auto_replan_on_change=True  # Automatically runs 'sqlmesh plan --auto-apply'
)
```
Or run `sqlmesh plan --auto-apply` manually.

#### 5. 3-Part Table Naming Issues (Cross-Database)
**Cause:** SQLMesh generates queries with 3-part names (catalog.schema.table) which might fail if the catalog name doesn't match.
**Fix:** Set `default_catalog` in your config to tell SQLMesh which catalog to omit or use.
```python
generator = SQLMeshDAGGenerator(
    ...,
    default_catalog="my_catalog"
)
```

### Advanced Features

#### Health Check Task
Add a pre-flight check to verify database connectivity before running models:
```python
generator = SQLMeshDAGGenerator(
    ...,
    enable_health_check=True
)
```

#### Skip Audits
For faster development iterations, you can skip audit checks:
```python
generator = SQLMeshDAGGenerator(
    ...,
    skip_audits=True
)
```

#### Partial DAG Runs
You can generate tasks for a subset of models (useful for testing):
```python
# In your DAG file
generator.create_tasks_in_dag(dag, models=["model_a", "model_b"])
```

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Comparison with Tobiko Cloud

| Feature | Tobiko Cloud | SQLMesh DAG Generator |
|---------|-------------|----------------------|
| Cost | Paid | **Free & Open Source** |
| Deployment | Cloud-based | **Self-hosted** |
| Customization | Limited | **Fully Customizable** |
| Privacy | External | **On-premise** |
| Dependencies | Cloud connection | **None** |

## Support

- 📖 [Documentation](https://github.com/yourusername/sqlmesh-dag-generator/docs)
- 🐛 [Issue Tracker](https://github.com/yourusername/sqlmesh-dag-generator/issues)
- 💬 [Discussions](https://github.com/yourusername/sqlmesh-dag-generator/discussions)

