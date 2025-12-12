def get_provider_info():
    """Entry point for Airflow ProvidersManager."""
    return {
        "package-name": "airflow-providers-glassdome-waypoint",
        "name": "Glassdome Waypoint",
        "description": "Airflow provider for Glassdome Waypoint API https://developers.glassdome.dev/waypoint",
        "hooks": [
            {
                "integration-name": "Glassdome Waypoint",
                "python-modules": ["glassdome_waypoint.hooks.waypoint"],
            }
        ],
        "connection-types": [
            {
                "hook-class-name": "glassdome_waypoint.hooks.waypoint.WaypointHook",
                "connection-type": "glassdome-waypoint",
            }
        ],
    }
