
from dependency_injector import containers, providers

import pulumi_kubernetes as k8s

def get_kubeconfig(core):
    """
    Retrieves kubeconfig with fallback support for self-contained mode.

    Priority:
    1. base_stack output (backward compatibility)
    2. core.exports()["kubeconfig"] (self-contained mode)
    3. Error if not found (kubeconfig is mandatory for K8s components)

    Raises:
        ValueError: If kubeconfig not found in either source
    """
    # Try base_stack first (backward compatibility)
    if core.base_stack() is not None:
        kubeconfig = core.base_stack().get_output("kubeconfig")
    # Fallback to exports (self-contained mode)
    else:
        kubeconfig = core.exports().get("kubeconfig")
        if kubeconfig is None:
            raise ValueError(
                "kubeconfig not found. Either configure base_stack "
                "or set kubeconfig in container.core.exports() before using K8s components"
            )

    # Store in exports for consistency
    core.exports()['kubeconfig'] = kubeconfig
    return kubeconfig


# Cache to store provider instances per namespace
_provider_cache = {}


def create_namespaced_provider(kubeconfig, namespace):
    """
    Factory function with caching to create/reuse K8s provider per namespace.

    This prevents Pulumi URN collisions in two scenarios:
    1. Multiple namespaces (each gets uniquely named provider)
    2. Multiple resources in same namespace (reuses cached provider)

    The cache ensures only ONE provider instance per namespace, regardless of
    how many resources are created in that namespace.
    """
    # Generate unique provider name based on namespace
    provider_name = f"k8s-provider-{namespace}"

    # Return cached provider if exists
    if provider_name in _provider_cache:
        return _provider_cache[provider_name]

    # Create new provider and cache it
    provider = k8s.Provider(
        provider_name,
        kubeconfig=kubeconfig,
        namespace=namespace,
    )
    _provider_cache[provider_name] = provider

    return provider


class Kubernetes(containers.DeclarativeContainer):
    """
    Kubernetes dependency injection container.

    Usage for multiple namespaces in the same stack (override pattern):

        from dependency_injector import providers
        from airspot_dev import container

        # Default namespace (from config or base_stack)
        app = get_application(ApplicationConfig(name="aida-app"))

        # Override namespace for specific service
        container.k8s.namespace.override(providers.Object("valkey"))
        valkey = get_stateful_application(StatefulAppConfig(name="valkey"))
        container.k8s.namespace.reset_override()

        # Or deploy multiple services with different namespaces
        container.k8s.namespace.override(providers.Object("postgresql"))
        postgres = get_stateful_application(StatefulAppConfig(name="postgres"))
        container.k8s.namespace.reset_override()

    Note: namespaced_provider is a Factory (not Singleton) to respect namespace overrides.
    Each namespace gets a uniquely named provider (k8s-provider-{namespace}) with caching
    to prevent URN conflicts when:
    - Multiple resources are created in the same namespace (reuses cached provider)
    - Multiple namespaces are used via override pattern (separate cached providers)
    """

    core = providers.DependenciesContainer()

    kubeconfig = providers.Singleton(
        get_kubeconfig,
        core=core
    )

    namespace = providers.Factory(
        core.get_stack_var,
        "namespace",
    )

    namespaced_provider = providers.Factory(
        create_namespaced_provider,
        kubeconfig=kubeconfig,
        namespace=namespace,
    )

    cluster_provider = providers.Singleton(
        k8s.Provider,
        "k8s-cluster-provider",
        kubeconfig=kubeconfig,
    )