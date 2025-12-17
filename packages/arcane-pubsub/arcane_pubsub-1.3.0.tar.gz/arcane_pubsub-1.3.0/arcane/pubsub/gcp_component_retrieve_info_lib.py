import os
from enum import Enum

class GCPEnvironment(Enum):
    CLOUD_RUN = "cloud_run"
    CLOUD_FUNCTION_V2 = "cloud_function_v2"
    CLOUD_FUNCTION_V1 = "cloud_function_v1"
    UNKNOWN = "unknown"

def get_gcp_environment() -> GCPEnvironment:
    """
    Detect whether we're running in Cloud Run, Cloud Functions v1, or v2.
    """
    # Cloud Functions v2 runs on Cloud Run but has FUNCTION_TARGET
    if os.getenv('FUNCTION_TARGET'):
        return GCPEnvironment.CLOUD_FUNCTION_V2

    # Cloud Functions v1 has FUNCTION_NAME but not K_SERVICE
    if os.getenv('FUNCTION_NAME') and not os.getenv('K_SERVICE'):
        return GCPEnvironment.CLOUD_FUNCTION_V1

    # Cloud Run has K_SERVICE but not FUNCTION_TARGET
    if os.getenv('K_SERVICE'):
        return GCPEnvironment.CLOUD_RUN

    return GCPEnvironment.UNKNOWN

def get_service_name() -> str:
    """
    Retrieve the service name from the current GCP environment.
    """
    return os.getenv('K_SERVICE') or os.getenv('FUNCTION_NAME') or 'unknown-service'

def get_log_explorer_resource_type() -> str:
    """
    Get the resource type for Log Explorer queries.
    """
    env = get_gcp_environment()

    if env == GCPEnvironment.CLOUD_RUN:
        return "cloud_run_revision"
    elif env == GCPEnvironment.CLOUD_FUNCTION_V2:
        return "cloud_run_revision"  # v2 uses Cloud Run
    elif env == GCPEnvironment.CLOUD_FUNCTION_V1:
        return "cloud_function"

    return "global"
