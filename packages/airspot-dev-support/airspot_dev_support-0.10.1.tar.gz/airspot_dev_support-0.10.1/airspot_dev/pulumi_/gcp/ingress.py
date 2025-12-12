from typing import Optional, Dict, List, Any, Union
from pydantic import Field, model_validator, BaseModel
import pulumi
import pulumi_kubernetes as k8s
from airspot_dev.pulumi_ import BaseResourceConfig
from airspot_dev import container
import warnings


class PathMapping(BaseModel):
    """Single path-to-service mapping for multi-path Ingress.

    Represents a single routing rule that maps a URL path to a Kubernetes Service.
    Used for configuring multi-service Ingress with different paths routing to different backends.

    Example:
        PathMapping(
            path="/auth",
            service_name="keycloak",
            service_port=8080,
            path_type="Prefix"
        )

        # Using named port instead of port number
        PathMapping(
            path="/api",
            service_name="api-service",
            service_port_name="http",
            path_type="Prefix"
        )

    Note:
        backend_config_name is for documentation only. BackendConfig must be
        configured on the Service itself via ApplicationConfig.backend_config,
        as it is applied through Service annotations, not Ingress configuration.
    """
    path: str = Field(
        ...,
        description="URL path (e.g., '/auth', '/api', '/') that will route to this service"
    )
    service_name: str = Field(
        ...,
        description="Name of the Kubernetes Service to route traffic to"
    )
    service_port: Optional[int] = Field(
        None,
        description="Service port number (e.g., 8080). Mutually exclusive with service_port_name."
    )
    service_port_name: Optional[str] = Field(
        None,
        description="Service port name (e.g., 'http'). Mutually exclusive with service_port."
    )
    path_type: str = Field(
        "Prefix",
        description="Path match type: 'Prefix' (matches /path/*) or 'Exact' (matches /path only)"
    )
    backend_config_name: Optional[str] = Field(
        None,
        description="Reference to BackendConfig name (documentation only - configure via Service annotations)"
    )

    @model_validator(mode='after')
    def validate_port(self):
        """Ensure either service_port or service_port_name is specified, but not both."""
        has_port = self.service_port is not None
        has_port_name = self.service_port_name is not None

        if not has_port and not has_port_name:
            raise ValueError(
                f"PathMapping for '{self.path}': Must specify either service_port or service_port_name"
            )
        if has_port and has_port_name:
            raise ValueError(
                f"PathMapping for '{self.path}': Cannot specify both service_port and service_port_name"
            )

        return self


class GCEIngressConfig(BaseResourceConfig):
    """GCE Ingress with Managed Certificate.

    Supports two modes:
    1. Single-service mode (legacy): Routes all traffic to one service
    2. Multi-path mode: Routes different paths to different services

    Single-service example:
        GCEIngressConfig(
            name="my-app",
            domain="app.example.com",
            service_name="my-service",
            service_port=8080
        )

    Multi-path example:
        GCEIngressConfig(
            name="my-app",
            domain="app.example.com",
            path_mappings=[
                PathMapping(path="/auth", service_name="keycloak", service_port=8080),
                PathMapping(path="/api", service_name="api", service_port=8000),
                PathMapping(path="/", service_name="frontend", service_port=3000),
            ]
        )
    """
    domain: str

    # Static IP configuration
    static_ip_name: Optional[Union[str, pulumi.Output]] = None  # Nome IP statico - opzionale, popolato automaticamente

    # Single-service mode (legacy, deprecated but kept for backward compatibility)
    service_name: Optional[str] = None  # Nome service - opzionale, popolato automaticamente
    service_port: Optional[int] = None

    # Multi-path mode (new)
    path_mappings: Optional[List[PathMapping]] = Field(
        None,
        description="List of path-to-service mappings for multi-service routing. Mutually exclusive with service_name/service_port."
    )

    # Certificate options
    use_managed_cert: bool = True
    cert_domains: Optional[List[str]] = None  # Default: [domain]

    # Load balancer type
    use_regional_ip: bool = False  # If True, use regional IP instead of global

    # Advanced options
    additional_annotations: Dict[str, str] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True}

    @model_validator(mode='after')
    def validate_routing_mode(self):
        """Validate that either single-service or multi-path mode is used, but not both."""
        has_multi = self.path_mappings is not None and len(self.path_mappings) > 0
        has_single = self.service_name is not None

        if has_multi and has_single:
            raise ValueError(
                "Cannot use both path_mappings (multi-service mode) and "
                "service_name/service_port (single-service mode). Choose one routing mode."
            )
        if not has_multi and not has_single:
            raise ValueError(
                "Must provide either path_mappings (multi-service mode) or "
                "service_name/service_port (single-service mode)."
            )

        # Validate path_mappings not empty if provided
        if self.path_mappings is not None and len(self.path_mappings) == 0:
            raise ValueError(
                "path_mappings cannot be empty. Provide at least one PathMapping or use single-service mode."
            )

        # Validate service_port is provided in single-service mode
        if has_single and self.service_port is None:
            raise ValueError(
                "service_port is required when using single-service mode (service_name provided)."
            )

        return self

    @model_validator(mode='after')
    def sort_paths_by_specificity(self):
        """Auto-sort paths from most specific to least specific for correct routing.

        GKE Ingress controller uses longest prefix matching. Paths must be ordered
        from most specific to least specific to ensure correct routing behavior.
        """
        if self.path_mappings is None or len(self.path_mappings) == 0:
            return self

        # Sort by path length (descending), then alphabetically for stability
        sorted_mappings = sorted(
            self.path_mappings,
            key=lambda m: (-len(m.path), m.path)
        )

        # Warn user if order was changed
        original_paths = [m.path for m in self.path_mappings]
        sorted_paths = [m.path for m in sorted_mappings]

        if original_paths != sorted_paths:
            warnings.warn(
                f"path_mappings auto-sorted for correct routing (longest prefix first): {sorted_paths}. "
                f"Original order was: {original_paths}",
                UserWarning
            )

        self.path_mappings = sorted_mappings
        return self


def get_gce_ingress(config: GCEIngressConfig, static_ip_name: Union[str, pulumi.Output] = None, service_name: str = None, service_port_name: str = None) -> Dict[str, Any]:
    """Create GCE Ingress with ManagedCertificate.

    Supports both single-service and multi-path modes:
    - Single-service: Routes all traffic (path "/") to one service
    - Multi-path: Routes different paths to different services

    Args:
        config: GCEIngressConfig with routing configuration
        static_ip_name: Optional static IP name (overrides config.static_ip_name)
        service_name: Optional service name for single-service mode (overrides config.service_name)
        service_port_name: Optional named port for single-service mode

    Returns:
        Dict containing created resources (ingress, managed_certificate if enabled)
    """

    # Determine routing mode
    is_multi_path = config.path_mappings is not None and len(config.path_mappings) > 0

    # Use provided parameters or fall back to config values
    ingress_static_ip_name = static_ip_name if static_ip_name is not None else config.static_ip_name

    # Validate static IP (required for both modes)
    if ingress_static_ip_name is None:
        raise ValueError("static_ip_name must be provided either in config or as parameter")

    # Validate single-service mode parameters (only if not multi-path)
    if not is_multi_path:
        ingress_service_name = service_name if service_name is not None else config.service_name
        if ingress_service_name is None:
            raise ValueError(
                "Single-service mode: service_name must be provided either in config or as parameter. "
                "For multi-path routing, use config.path_mappings instead."
            )
    
    resources = {}
    
    if config.use_managed_cert:
        cert_domains = config.cert_domains or [config.domain]
        
        managed_cert = k8s.apiextensions.CustomResource(
            f"{config.name}-managed-cert",
            api_version="networking.gke.io/v1",
            kind="ManagedCertificate",
            metadata={"name": f"{config.name}-managed-cert"},
            spec={"domains": cert_domains},
            opts=pulumi.ResourceOptions(provider=container.k8s.namespaced_provider())
        )
        resources["managed_certificate"] = managed_cert
    
    # Ingress annotations
    annotations = {
        "kubernetes.io/ingress.class": "gce",
        **config.additional_annotations
    }
    
    # Add appropriate IP annotation based on type
    if config.use_regional_ip:
        annotations["kubernetes.io/ingress.regional-static-ip-name"] = ingress_static_ip_name
    else:
        annotations["kubernetes.io/ingress.global-static-ip-name"] = ingress_static_ip_name
    
    if config.use_managed_cert:
        annotations["networking.gke.io/managed-certificates"] = f"{config.name}-managed-cert"

    # Build paths configuration based on routing mode
    if is_multi_path:
        # Multi-path mode: use path_mappings
        paths = [
            {
                "path": mapping.path,
                "pathType": mapping.path_type,
                "backend": {
                    "service": {
                        "name": mapping.service_name,
                        "port": (
                            {"name": mapping.service_port_name}
                            if mapping.service_port_name
                            else {"number": mapping.service_port}
                        )
                    }
                }
            }
            for mapping in config.path_mappings
        ]
    else:
        # Single-service mode (legacy): route all traffic to one service
        paths = [{
            "path": "/",
            "pathType": "Prefix",
            "backend": {
                "service": {
                    "name": ingress_service_name,
                    "port": (
                        {"name": service_port_name}
                        if service_port_name
                        else {"number": config.service_port}
                    )
                }
            }
        }]

    # Create Ingress
    ingress = k8s.networking.v1.Ingress(
        f"{config.name}-ingress",
        metadata={
            "name": f"{config.name}-ingress",
            "annotations": annotations
        },
        spec={
            "rules": [{
                "host": config.domain,
                "http": {"paths": paths}
            }]
        },
        opts=pulumi.ResourceOptions(
            provider=container.k8s.namespaced_provider(),
            depends_on=list(resources.values())
        )
    )
    resources["ingress"] = ingress

    return resources
