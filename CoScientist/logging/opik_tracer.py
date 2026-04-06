from CoScientist.config import get_settings
import os

settings = get_settings()
os.environ['OPIK_API_KEY'] = settings.opik.api_key

import opik
opik.configure(use_local=False)

from opik.integrations.adk import OpikTracer

multi_agent_tracer = OpikTracer(
    name="multi-agent-orchestrator",
    metadata=settings.model_dump(),
    project_name="adk-coscientist"
)