
import pulumi
from pulumi.dynamic import Resource, ResourceProvider, CreateResult
from dataclasses import dataclass
from typing import Optional
import re

def _get_slug(s: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]+', '-', s.lower()).strip('-')

@dataclass
class AgentEngineConfig:
    """
    Configuration for the Vertex AI Agent Engine dynamic resource.
    """
    name: str
    project_id: str
    location: str
    opts: Optional[pulumi.ResourceOptions] = None


class _AgentEngineProvider(ResourceProvider):
    """
    Dynamic provider for managing the lifecycle of a Vertex AI Agent Engine.
    """

    def create(self, inputs):
        from vertexai import init, agent_engines

        name = inputs['display_name']
        project = inputs['project_id']
        location = inputs['location']

        # Initialize the Vertex AI SDK within the provider
        init(project=project, location=location)

        slug_display_name = _get_slug(name)
        try:
            # Check if an engine with the same display name already exists
            engine = next(iter(agent_engines.list(filter=f"display_name='{slug_display_name}'")))
            pulumi.log.info(f"Using existing Vertex AI Agent Engine: {engine.gca_resource.name}")
        except StopIteration:
            # If not, create a new one
            engine = agent_engines.create(display_name=slug_display_name)
            pulumi.log.info(f"Created new Vertex AI Agent Engine: {engine.gca_resource.name}")

        # The ID of the resource is its full resource name
        agent_engine_id = engine.gca_resource.name

        # Persist all properties needed by the delete method in the resource's state.
        outs = {
#            'resource_name': agent_engine_id,
            'project_id': project,
            'location': location,
            'name': name
        }
        return CreateResult(id_=agent_engine_id, outs=outs)

    def delete(self, id, props):
        from vertexai import init, agent_engines

        # The 'id' of the resource is the full resource name
 #       resource_name = id
        project = props['project_id']
        location = props['location']

        # Initialize the SDK to ensure authentication
        init(project=project, location=location)

        try:
            # Deleting is a fire-and-forget operation in this context
            agent_engines.delete(resource_name=id, force=True)
            pulumi.log.info(f"Successfully initiated deletion for Agent Engine: {id}")
        except Exception as e:
            # Log errors but don't fail the destroy operation
            pulumi.log.warn(f"Could not delete Agent Engine {id}: {str(e)}")


class _AgentEngine(Resource):
    """
    A Pulumi dynamic resource representing a Vertex AI Agent Engine.
    """
#    resource_name: pulumi.Output[str]

    def __init__(self, name: str, props: dict, opts: pulumi.ResourceOptions = None):
        super().__init__(_AgentEngineProvider(), name, props, opts)
        # The primary ID of this resource IS the agent_engine_id.
        # We assign it to the declared output property to make it accessible.
#        self.resource_name = self.id


def get_agent_engine(config: AgentEngineConfig) -> _AgentEngine:
    """
    Creates and manages a Vertex AI Agent Engine as a Pulumi dynamic resource.

    :param config: Configuration for the agent engine.
    :return: An instance of the _AgentEngine resource.
    """
    return _AgentEngine(
        f"{_get_slug(config.name)}-agent-engine",
        props={
            'display_name': config.name,
            'project_id': config.project_id,
            'location': config.location,
        },
        opts=config.opts
    )
