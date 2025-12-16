<div align="center">
  <img src="Whisper_Logo.png" alt="Whisper Logo" width="400"/>

  # Whisper API SDK - Python

[![CI](https://github.com/whisper-sec/sdk-python/actions/workflows/python.yml/badge.svg)](https://github.com/whisper-sec/sdk-python/actions/workflows/python.yml)
[![PyPI version](https://badge.fury.io/py/whisper_api_sdk.svg)](https://badge.fury.io/py/whisper_api_sdk)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

> **Official Python SDK for Whisper API** - Comprehensive threat intelligence and security operations for domains, IPs, and web infrastructure.

**[Website](https://whisper.security)** | **[Dashboard](https://dash.whisper.security)** | **[Documentation](https://docs.whisper.security)** | **[API Reference](https://developer.whisper.security)** | **[API Playground](https://dash.whisper.security/playground)** | **[Contact Us](https://whisper.security/contactus)**

</div>

---

## Quick Start

### Installation

```bash
pip install whisper_api_sdk
```

### Get Your API Key

Sign up at [dash.whisper.security](https://dash.whisper.security) to get your API key.

### First Request

```python
import whisper_api_sdk

configuration = whisper_api_sdk.Configuration(
    host="https://api.whisper.security",
    access_token="YOUR_API_KEY"
)

with whisper_api_sdk.ApiClient(configuration) as api_client:
    api = whisper_api_sdk.EnrichmentApi(api_client)

    # Enrich an IP address
    response = api.get_indicator("ip", "8.8.8.8")
    print(response)
```

---

## Key Features

- **Async Support** - Built-in support for async/await patterns
- **Fully Typed** - Complete type hints for IDE autocomplete
- **Comprehensive** - IP, Domain, DNS, WHOIS, Routing, Geolocation, Screenshots, AI/ML
- **Fast** - Sub-500ms typical response times with strategic caching
- **Python 3.8+** - Modern Python with full type annotations

---

## API Overview

### Enrichment API
Enrich IPs and domains with comprehensive threat intelligence.

```python
api = whisper_api_sdk.EnrichmentApi(api_client)

# Basic enrichment
ip_data = api.get_indicator("ip", "8.8.8.8")

# With additional data modules
domain_data = api.get_indicator("domain", "example.com", include="whois,dns_details,routing,rpki")

# Get relationship graph
graph = api.get_indicator_graph("ip", "8.8.8.8")

# Historical data
history = api.get_indicator_history("domain", "example.com", limit=10)

# Predictive risk score (AI-powered)
risk = api.get_predictive_risk("ip", "8.8.8.8")

# Subdomain discovery
subdomains = api.get_subdomains("example.com", limit=100)

# Bulk enrichment (async job)
job = api.bulk_enrichment(bulk_request)

# Search by WHOIS fields
search_job = api.search_indicators(search_request)

# Similar/typosquat domain generation
similar_job = api.similar_domains(similar_request)
```

### Location API
Geolocation lookups and network analysis.

```python
api = whisper_api_sdk.LocationApi(api_client)

# Single IP geolocation
location = api.get_ip_location("8.8.8.8")

# Bulk geolocation (up to 1000 IPs)
bulk_result = api.get_bulk_ip_location(bulk_request)

# Network/CIDR lookup
network = api.get_network_location("8.8.8.0/24")

# Search by attributes
results = api.search_location(field="city", value="San Francisco", limit=100)

# Location statistics
stats = api.get_location_stats()
```

### Screenshots API
Capture and schedule website screenshots.

```python
api = whisper_api_sdk.ScreenshotsApi(api_client)

# Screenshot capture (returns job ID)
job = api.create_screenshot(screenshot_request)

# Schedule recurring screenshots
schedule = api.schedule_screenshot(schedule_request)

# Get screenshot history
history = api.get_screenshot_history(url="https://example.com")

# List scheduled screenshots
schedules = api.list_screenshot_schedules()
```

### AI Intelligence API
AI-powered threat investigation and analysis.

```python
api = whisper_api_sdk.AiIntelligenceApi(api_client)

# Industry security benchmark (synchronous)
benchmark = api.get_industry_benchmark("financial_services", size="enterprise")

# AI-powered investigation (async job)
investigation = api.ai_investigate(investigate_request)

# Find similar threat cases
cases = api.find_similar_cases(similar_cases_request)

# Infrastructure pivoting
pivot = api.ai_pivot(pivot_request)

# Threat actor attribution
attribution = api.ai_attribute(attribute_request)

# Global indicator correlation
correlation = api.ai_correlate(correlate_request)
```

### Infrastructure Scanning API
Discover and analyze infrastructure.

```python
api = whisper_api_sdk.InfrastructureScanningApi(api_client)

# Infrastructure scan (SSL, technologies, subdomains, ports)
scan_job = api.create_infrastructure_scan(scan_request)

# Infrastructure relationship mapping
map_job = api.create_infrastructure_map(map_request)
```

### Monitoring API
Uptime and availability monitoring.

```python
api = whisper_api_sdk.MonitoringApi(api_client)

# Create monitoring check
check = api.create_monitor_check(monitor_request)

# List monitoring checks
checks = api.list_monitor_checks()

# Get dashboard summary
dashboard = api.get_monitor_dashboard()

# Configure alerts
api.create_monitoring_alert(check_id, alert_request)
```

### Change Tracking API
Monitor indicators for changes.

```python
api = whisper_api_sdk.ChangeTrackingApi(api_client)

# Start tracking an indicator
api.start_change_tracking("domain", "example.com", tracking_request)

# Get detected changes
changes = api.get_changes("domain", "example.com")

# List tracked indicators
tracked = api.list_tracked_indicators()

# Trigger immediate check
api.trigger_check("domain", "example.com")
```

### Graph Database API
Direct access to the threat intelligence graph.

```python
api = whisper_api_sdk.GraphDatabaseApi(api_client)

# Execute Cypher query
result = api.execute_cypher_query(cypher_request)

# Execute GraphQL query
result = api.execute_graph_ql(graphql_request)

# Get graph schema
schema = api.get_schema()
```

### Jobs API
Manage async operations.

```python
api = whisper_api_sdk.JobsApi(api_client)

# Get job status and results
job = api.get_job(job_id)

# List your jobs
jobs = api.list_jobs()
```

---

## Authentication

All endpoints require Bearer token authentication:

```python
import os

configuration = whisper_api_sdk.Configuration(
    host="https://api.whisper.security",
    access_token=os.getenv("WHISPER_API_KEY")
)
```

---

## Rate Limits

| Category | Limit |
|----------|-------|
| Indicators (`/v1/indicators/*`) | 100 req/sec |
| Location (`/v1/location/*`) | 100 req/sec |
| Jobs (`/v1/ops/jobs/*`) | 100 req/sec |
| Bulk Operations | 10 req/sec |
| Screenshots | 10 req/sec |
| Scans | 10 req/sec |
| Monitoring | 10 req/sec |
| Change Tracking | 10 req/sec |
| AI Operations | 5 req/min |

Rate limits return HTTP 429 with a `Retry-After` header.

---

## Documentation

- **API Documentation**: [docs.whisper.security](https://docs.whisper.security)
- **API Reference**: [developer.whisper.security](https://developer.whisper.security)
- **Python Docs**: See the `docs/` directory

---

## Other SDKs

- **TypeScript/JavaScript**: [github.com/whisper-sec/sdk-typescript](https://github.com/whisper-sec/sdk-typescript)
- **Java**: [github.com/whisper-sec/sdk-java](https://github.com/whisper-sec/sdk-java)
- **C#/.NET**: [github.com/whisper-sec/sdk-csharp](https://github.com/whisper-sec/sdk-csharp)
- **Rust**: [github.com/whisper-sec/sdk-rust](https://github.com/whisper-sec/sdk-rust)

---

## Support

- **Email**: [support@whisper.security](mailto:support@whisper.security)
- **Issues**: [github.com/whisper-sec/sdk-python/issues](https://github.com/whisper-sec/sdk-python/issues)

---

## License

MIT License - See [LICENSE](LICENSE) file for details.

---

*Built with Python by [Whisper Security](https://whisper.security)*
