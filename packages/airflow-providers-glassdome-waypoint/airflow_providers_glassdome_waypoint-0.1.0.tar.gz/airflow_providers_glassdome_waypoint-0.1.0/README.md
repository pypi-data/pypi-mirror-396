# Glassdome Waypoint Airflow Provider

Airflow provider for the [Glassdome Waypoint API](https://developers.glassdome.dev/waypoint). This provider integrates the [Glassdome Waypoint SDK](https://pypi.org/project/glassdome-waypoint-sdk/) with Airflow.

## Installation

```bash
pip install airflow-providers-glassdome-waypoint
```

## Requirements

- Python >= 3.10
- apache-airflow >= 2.11.0
- apache-airflow-providers-common-compat >= 1.8.0
- glassdome-waypoint-sdk >= 0.1.0

## Quick Start

### Connection Configuration

The provider supports below connection configuration:

- **Connection Type**: `glassdome-waypoint` (displayed as `Glassdome Waypoint` in Airflow UI)
- **Base URL**: Your Waypoint API endpoint
- **Auth Type**: `api_key`
- **API Key**: Your Glassdome API key
- **Timeout Seconds**: Optional request timeout

```python
from glassdome_waypoint.hooks.waypoint import WaypointHook

hook = WaypointHook(your_connection_id)
client = hook.get_client() # WaypointClient instance
```

## Usage Examples

- [Listing Sites](https://developers.glassdome.dev/waypoint/sites#airflow-provider)
- [Managing Products](https://developers.glassdome.dev/waypoint/products#airflow-provider)
- [Running PCF Pipeline](https://developers.glassdome.dev/waypoint/pcf#airflow-provider)

## API Reference

### WaypointHook

Main entrypoint that provides an authenticated `WaypointClient` for an Airflow connection.

#### Methods

- `get_conn()`: returns a configured `WaypointClient` instance.
- `get_client()`: alias for `get_conn()`
- `test_connection()`: validates credentials and base URL by calling a lightweight API method.

### WaypointClient

Client for interacting with the Waypoint API.
More details available in the [Waypoint SDK docs](https://pypi.org/project/glassdome-waypoint-sdk/).

#### Attributes

- `client.operation`: long-running operations
- `client.site`: site APIs
- `client.product`: product APIs
- `client.pcf`: PCF APIs

### Long-Running Operations

Batch import operations return `Operation` object.

```python
op = client.product.create_products(requests=[...])

# Block until done or timeout
op.wait()

# With return options
op.wait(return_options=OperationReturnOptions(response=True))

# Check for error
if err := op.error():
    print(err.code, err.message)

# Access the response
if resp := op.response():
    # Process response
    pass
```

## Error Handling

The SDK defines these error classes:

- `WaypointError`: Base SDK error
- `WaypointHTTPError`: HTTP errors
- `AnyUnpackError`: Protobuf Any unpacking errors

```python
from glassdome_waypoint_sdk import WaypointError, WaypointHTTPError

try:
    # Your API call
    pass
except WaypointHTTPError as e:
    print(f"HTTP error: {e}")
except WaypointError as e:
    print(f"SDK error: {e}")
```

## License

This SDK is proprietary and may be used only under agreement with Glassdome Inc.

## Support

For questions or support, contact: <developer@glassdomeinc.com>
