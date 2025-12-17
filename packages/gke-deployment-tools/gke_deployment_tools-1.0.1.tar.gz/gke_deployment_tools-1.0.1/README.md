"""
# GKE Deployment Tools

Comprehensive deployment management tools for GKE with connection pooling and token caching.

## Installation

```bash
pip install gke-deployment-tools
```

## Quick Start

```python
from gke_deployment_tools import (
    get_deployment_usage_sync,
    get_deployment_images_sync,
    update_deployment_image_tag_sync
)

# Get deployment resource usage
usage = get_deployment_usage_sync(
    namespace="prod-app",
    cluster="main-cluster",
    project="my-project"
)

# Update deployment image tag
result = update_deployment_image_tag_sync(
    namespace="prod-app",
    deployment_name="ecommerce",
    new_tag="v1.2.3",
    cluster="main-cluster",
    project="my-project"
)
```

## Features

- Deployment resource monitoring (CPU/memory usage)
- Image management and updates with Artifact Registry validation
- Pod operations (logs, directory listing, file search)
- Log search with time range and keyword filtering
- Deployment rollback capabilities
- Connection pooling for performance
- Automatic token refresh
- Thread-safe operations

## Usage Examples

### Resource Monitoring

```python
from gke_deployment_tools import get_deployment_usage_sync

usage = get_deployment_usage_sync("prod-app", "cluster-1", "project-1")
print(f"Deployments: {usage['deployments']}")
```

### Log Operations

```python
from gke_deployment_tools import search_logs_by_timerange_and_keyword_sync

logs = search_logs_by_timerange_and_keyword_sync(
    namespace="prod-app",
    deployment_name="ecommerce",
    file_path="/var/log/server.log",
    from_time="10:00:00",
    to_time="11:00:00",
    keyword="ERROR",
    cluster="cluster-1",
    project="project-1"
)
```

### Deployment Updates

```python
from gke_deployment_tools import update_deployment_image_tag_sync

result = update_deployment_image_tag_sync(
    namespace="prod-app",
    deployment_name="api",
    new_tag="v2.0.0",
    cluster="main",
    project="my-project"
)
```

## Requirements

- gke-cache-builder>=1.0.0
- kubernetes>=28.1.0
- google-cloud-container>=2.30.0

## License

MIT License
"""