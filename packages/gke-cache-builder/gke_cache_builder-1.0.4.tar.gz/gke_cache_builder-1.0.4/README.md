"""
# GKE Cache Builder

Multi-cluster GKE cache builder with fuzzy search capabilities for hosts, namespaces, and clients.

## Installation

```bash
pip install gke-cache-builder
```

## Quick Start

```python
from gke_cache_builder import build_cache, get_cache, fuzzy_search_hosts

# Build cache from GCP organization
cache = build_cache(org_id="123456789")

# Get cached data
cache_data = get_cache()

# Fuzzy search for hosts
results = fuzzy_search_hosts("example.com", max_results=5)
```

## Features

- Multi-cluster GKE discovery
- Host-to-namespace mapping
- Fuzzy search for hosts, namespaces, and clients
- CSV-based client name mapping
- NFS storage mapping support
- Thread-safe operations

## Configuration

Set environment variables:

```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
export GCP_ORG_ID=123456789
export CLIENT_MAPPINGS_CSV=client_mappings.csv
```

## Usage Examples

### Building Cache

```python
from gke_cache_builder import build_cache

# Build from organization
cache = build_cache(org_id="123456789")

# Build from folder
cache = build_cache(folder_id="987654321")
```

### Searching

```python
from gke_cache_builder import fuzzy_search_hosts, fuzzy_search_namespaces

# Search hosts
host_results = fuzzy_search_hosts("acme", max_results=5, min_score=0.4)

# Search namespaces
ns_results = fuzzy_search_namespaces("prod", max_results=5)
```

### Client CSV Mapping

```python
from gke_cache_builder import get_csv_handler, create_sample_csv

# Create sample CSV
create_sample_csv("client_mappings.csv")

# Use CSV handler
handler = get_csv_handler()
client_data = handler.get_client_data("www.example.com")
```

## License

MIT License
"""