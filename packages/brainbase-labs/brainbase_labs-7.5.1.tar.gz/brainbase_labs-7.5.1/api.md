# Shared Types

```python
from brainbase_labs.types import (
    Flow,
    Integration,
    Log,
    Resource,
    VoiceDeployment,
    VoiceV1Deployment,
    Worker,
)
```

# Team

Types:

```python
from brainbase_labs.types import TeamRetrieveResponse
```

Methods:

- <code title="get /api/team">client.team.<a href="./src/brainbase_labs/resources/team/team.py">retrieve</a>(\*\*<a href="src/brainbase_labs/types/team_retrieve_params.py">params</a>) -> <a href="./src/brainbase_labs/types/team_retrieve_response.py">TeamRetrieveResponse</a></code>

## Assets

Types:

```python
from brainbase_labs.types.team import (
    AssetListPhoneNumbersResponse,
    AssetRegisterPhoneNumberResponse,
)
```

Methods:

- <code title="delete /api/team/assets/phone_numbers/{phoneNumberId}/delete">client.team.assets.<a href="./src/brainbase_labs/resources/team/assets.py">delete_phone_number</a>(phone_number_id) -> None</code>
- <code title="get /api/team/assets/phone_numbers">client.team.assets.<a href="./src/brainbase_labs/resources/team/assets.py">list_phone_numbers</a>(\*\*<a href="src/brainbase_labs/types/team/asset_list_phone_numbers_params.py">params</a>) -> <a href="./src/brainbase_labs/types/team/asset_list_phone_numbers_response.py">AssetListPhoneNumbersResponse</a></code>
- <code title="post /api/team/assets/register_phone_number">client.team.assets.<a href="./src/brainbase_labs/resources/team/assets.py">register_phone_number</a>(\*\*<a href="src/brainbase_labs/types/team/asset_register_phone_number_params.py">params</a>) -> <a href="./src/brainbase_labs/types/team/asset_register_phone_number_response.py">AssetRegisterPhoneNumberResponse</a></code>

## Integrations

Types:

```python
from brainbase_labs.types.team import IntegrationListResponse
```

Methods:

- <code title="get /api/team/integrations/{integrationId}">client.team.integrations.<a href="./src/brainbase_labs/resources/team/integrations/integrations.py">retrieve</a>(integration_id) -> <a href="./src/brainbase_labs/types/shared/integration.py">Integration</a></code>
- <code title="get /api/team/integrations">client.team.integrations.<a href="./src/brainbase_labs/resources/team/integrations/integrations.py">list</a>() -> <a href="./src/brainbase_labs/types/team/integration_list_response.py">IntegrationListResponse</a></code>

### Twilio

Methods:

- <code title="post /api/team/integrations/twilio/create">client.team.integrations.twilio.<a href="./src/brainbase_labs/resources/team/integrations/twilio.py">create</a>(\*\*<a href="src/brainbase_labs/types/team/integrations/twilio_create_params.py">params</a>) -> <a href="./src/brainbase_labs/types/shared/integration.py">Integration</a></code>
- <code title="delete /api/team/integrations/twilio/{integrationId}/delete">client.team.integrations.twilio.<a href="./src/brainbase_labs/resources/team/integrations/twilio.py">delete</a>(integration_id) -> None</code>

# Workers

Types:

```python
from brainbase_labs.types import WorkerListResponse
```

Methods:

- <code title="post /api/workers">client.workers.<a href="./src/brainbase_labs/resources/workers/workers.py">create</a>(\*\*<a href="src/brainbase_labs/types/worker_create_params.py">params</a>) -> <a href="./src/brainbase_labs/types/shared/worker.py">Worker</a></code>
- <code title="get /api/workers/{id}">client.workers.<a href="./src/brainbase_labs/resources/workers/workers.py">retrieve</a>(id) -> <a href="./src/brainbase_labs/types/shared/worker.py">Worker</a></code>
- <code title="patch /api/workers/{id}">client.workers.<a href="./src/brainbase_labs/resources/workers/workers.py">update</a>(id, \*\*<a href="src/brainbase_labs/types/worker_update_params.py">params</a>) -> <a href="./src/brainbase_labs/types/shared/worker.py">Worker</a></code>
- <code title="get /api/workers">client.workers.<a href="./src/brainbase_labs/resources/workers/workers.py">list</a>() -> <a href="./src/brainbase_labs/types/worker_list_response.py">WorkerListResponse</a></code>
- <code title="delete /api/workers/{id}">client.workers.<a href="./src/brainbase_labs/resources/workers/workers.py">delete</a>(id) -> None</code>

## Deployments

### Voice

Types:

```python
from brainbase_labs.types.workers.deployments import VoiceListResponse
```

Methods:

- <code title="post /api/workers/{workerId}/deployments/voice">client.workers.deployments.voice.<a href="./src/brainbase_labs/resources/workers/deployments/voice.py">create</a>(worker_id, \*\*<a href="src/brainbase_labs/types/workers/deployments/voice_create_params.py">params</a>) -> <a href="./src/brainbase_labs/types/shared/voice_deployment.py">VoiceDeployment</a></code>
- <code title="get /api/workers/{workerId}/deployments/voice/{deploymentId}">client.workers.deployments.voice.<a href="./src/brainbase_labs/resources/workers/deployments/voice.py">retrieve</a>(deployment_id, \*, worker_id) -> <a href="./src/brainbase_labs/types/shared/voice_deployment.py">VoiceDeployment</a></code>
- <code title="put /api/workers/{workerId}/deployments/voice/{deploymentId}">client.workers.deployments.voice.<a href="./src/brainbase_labs/resources/workers/deployments/voice.py">update</a>(deployment_id, \*, worker_id, \*\*<a href="src/brainbase_labs/types/workers/deployments/voice_update_params.py">params</a>) -> <a href="./src/brainbase_labs/types/shared/voice_deployment.py">VoiceDeployment</a></code>
- <code title="get /api/workers/{workerId}/deployments/voice">client.workers.deployments.voice.<a href="./src/brainbase_labs/resources/workers/deployments/voice.py">list</a>(worker_id) -> <a href="./src/brainbase_labs/types/workers/deployments/voice_list_response.py">VoiceListResponse</a></code>
- <code title="delete /api/workers/{workerId}/deployments/voice/{deploymentId}">client.workers.deployments.voice.<a href="./src/brainbase_labs/resources/workers/deployments/voice.py">delete</a>(deployment_id, \*, worker_id) -> None</code>

### Voicev1

Types:

```python
from brainbase_labs.types.workers.deployments import Voicev1ListResponse
```

Methods:

- <code title="post /api/workers/{workerId}/deployments/voicev1">client.workers.deployments.voicev1.<a href="./src/brainbase_labs/resources/workers/deployments/voicev1/voicev1.py">create</a>(worker_id, \*\*<a href="src/brainbase_labs/types/workers/deployments/voicev1_create_params.py">params</a>) -> <a href="./src/brainbase_labs/types/shared/voice_v1_deployment.py">VoiceV1Deployment</a></code>
- <code title="get /api/workers/{workerId}/deployments/voicev1/{deploymentId}">client.workers.deployments.voicev1.<a href="./src/brainbase_labs/resources/workers/deployments/voicev1/voicev1.py">retrieve</a>(deployment_id, \*, worker_id) -> <a href="./src/brainbase_labs/types/shared/voice_v1_deployment.py">VoiceV1Deployment</a></code>
- <code title="put /api/workers/{workerId}/deployments/voicev1/{deploymentId}">client.workers.deployments.voicev1.<a href="./src/brainbase_labs/resources/workers/deployments/voicev1/voicev1.py">update</a>(deployment_id, \*, worker_id, \*\*<a href="src/brainbase_labs/types/workers/deployments/voicev1_update_params.py">params</a>) -> <a href="./src/brainbase_labs/types/shared/voice_v1_deployment.py">VoiceV1Deployment</a></code>
- <code title="get /api/workers/{workerId}/deployments/voicev1">client.workers.deployments.voicev1.<a href="./src/brainbase_labs/resources/workers/deployments/voicev1/voicev1.py">list</a>(worker_id) -> <a href="./src/brainbase_labs/types/workers/deployments/voicev1_list_response.py">Voicev1ListResponse</a></code>
- <code title="delete /api/workers/{workerId}/deployments/voicev1/{deploymentId}">client.workers.deployments.voicev1.<a href="./src/brainbase_labs/resources/workers/deployments/voicev1/voicev1.py">delete</a>(deployment_id, \*, worker_id) -> None</code>
- <code title="post /api/workers/{workerId}/deployments/voicev1/{deploymentId}/make-batch-calls">client.workers.deployments.voicev1.<a href="./src/brainbase_labs/resources/workers/deployments/voicev1/voicev1.py">make_batch_calls</a>(deployment_id, \*, worker_id, \*\*<a href="src/brainbase_labs/types/workers/deployments/voicev1_make_batch_calls_params.py">params</a>) -> None</code>

#### Campaigns

Types:

```python
from brainbase_labs.types.workers.deployments.voicev1 import CampaignCreateResponse
```

Methods:

- <code title="post /api/workers/{workerId}/deployments/voicev1/{deploymentId}/campaigns">client.workers.deployments.voicev1.campaigns.<a href="./src/brainbase_labs/resources/workers/deployments/voicev1/campaigns/campaigns.py">create</a>(deployment_id, \*, worker_id, \*\*<a href="src/brainbase_labs/types/workers/deployments/voicev1/campaign_create_params.py">params</a>) -> <a href="./src/brainbase_labs/types/workers/deployments/voicev1/campaign_create_response.py">CampaignCreateResponse</a></code>
- <code title="get /api/workers/{workerId}/deployments/voicev1/{deploymentId}/campaigns/{campaignId}">client.workers.deployments.voicev1.campaigns.<a href="./src/brainbase_labs/resources/workers/deployments/voicev1/campaigns/campaigns.py">retrieve</a>(campaign_id, \*, worker_id, deployment_id) -> None</code>
- <code title="post /api/workers/{workerId}/deployments/voicev1/{deploymentId}/campaigns/{campaignId}/run">client.workers.deployments.voicev1.campaigns.<a href="./src/brainbase_labs/resources/workers/deployments/voicev1/campaigns/campaigns.py">run</a>(campaign_id, \*, worker_id, deployment_id, \*\*<a href="src/brainbase_labs/types/workers/deployments/voicev1/campaign_run_params.py">params</a>) -> None</code>

##### Data

Methods:

- <code title="get /api/workers/{workerId}/deployments/voicev1/{deploymentId}/campaigns/{campaignId}/data/{dataId}">client.workers.deployments.voicev1.campaigns.data.<a href="./src/brainbase_labs/resources/workers/deployments/voicev1/campaigns/data.py">retrieve</a>(data_id, \*, worker_id, deployment_id, campaign_id) -> None</code>
- <code title="put /api/workers/{workerId}/deployments/voicev1/{deploymentId}/campaigns/{campaignId}/data/{dataId}">client.workers.deployments.voicev1.campaigns.data.<a href="./src/brainbase_labs/resources/workers/deployments/voicev1/campaigns/data.py">update</a>(data_id, \*, worker_id, deployment_id, campaign_id, \*\*<a href="src/brainbase_labs/types/workers/deployments/voicev1/campaigns/data_update_params.py">params</a>) -> None</code>

## Flows

Types:

```python
from brainbase_labs.types.workers import FlowListResponse
```

Methods:

- <code title="post /api/workers/{workerId}/flows">client.workers.flows.<a href="./src/brainbase_labs/resources/workers/flows.py">create</a>(worker_id, \*\*<a href="src/brainbase_labs/types/workers/flow_create_params.py">params</a>) -> <a href="./src/brainbase_labs/types/shared/flow.py">Flow</a></code>
- <code title="get /api/workers/{workerId}/flows/{flowId}">client.workers.flows.<a href="./src/brainbase_labs/resources/workers/flows.py">retrieve</a>(flow_id, \*, worker_id) -> <a href="./src/brainbase_labs/types/shared/flow.py">Flow</a></code>
- <code title="put /api/workers/{workerId}/flows/{flowId}">client.workers.flows.<a href="./src/brainbase_labs/resources/workers/flows.py">update</a>(flow_id, \*, worker_id, \*\*<a href="src/brainbase_labs/types/workers/flow_update_params.py">params</a>) -> <a href="./src/brainbase_labs/types/shared/flow.py">Flow</a></code>
- <code title="get /api/workers/{workerId}/flows">client.workers.flows.<a href="./src/brainbase_labs/resources/workers/flows.py">list</a>(worker_id) -> <a href="./src/brainbase_labs/types/workers/flow_list_response.py">FlowListResponse</a></code>
- <code title="delete /api/workers/{workerId}/flows/{flowId}">client.workers.flows.<a href="./src/brainbase_labs/resources/workers/flows.py">delete</a>(flow_id, \*, worker_id) -> None</code>

## Resources

Methods:

- <code title="get /api/workers/{workerId}/resources/{resourceId}">client.workers.resources.<a href="./src/brainbase_labs/resources/workers/resources/resources.py">retrieve</a>(resource_id, \*, worker_id) -> <a href="./src/brainbase_labs/types/shared/resource.py">Resource</a></code>
- <code title="delete /api/workers/{workerId}/resources/{resourceId}">client.workers.resources.<a href="./src/brainbase_labs/resources/workers/resources/resources.py">delete</a>(resource_id, \*, worker_id) -> None</code>

### Link

Types:

```python
from brainbase_labs.types.workers.resources import LinkListResponse
```

Methods:

- <code title="post /api/workers/{workerId}/resources/link">client.workers.resources.link.<a href="./src/brainbase_labs/resources/workers/resources/link.py">create</a>(worker_id, \*\*<a href="src/brainbase_labs/types/workers/resources/link_create_params.py">params</a>) -> <a href="./src/brainbase_labs/types/shared/resource.py">Resource</a></code>
- <code title="get /api/workers/{workerId}/resources/link">client.workers.resources.link.<a href="./src/brainbase_labs/resources/workers/resources/link.py">list</a>(worker_id) -> <a href="./src/brainbase_labs/types/workers/resources/link_list_response.py">LinkListResponse</a></code>

### File

Types:

```python
from brainbase_labs.types.workers.resources import FileListResponse
```

Methods:

- <code title="post /api/workers/{workerId}/resources/file">client.workers.resources.file.<a href="./src/brainbase_labs/resources/workers/resources/file.py">create</a>(worker_id, \*\*<a href="src/brainbase_labs/types/workers/resources/file_create_params.py">params</a>) -> <a href="./src/brainbase_labs/types/shared/resource.py">Resource</a></code>
- <code title="get /api/workers/{workerId}/resources/file">client.workers.resources.file.<a href="./src/brainbase_labs/resources/workers/resources/file.py">list</a>(worker_id) -> <a href="./src/brainbase_labs/types/workers/resources/file_list_response.py">FileListResponse</a></code>

## Tests

Types:

```python
from brainbase_labs.types.workers import TestCreateResponse
```

Methods:

- <code title="post /api/workers/{workerId}/tests">client.workers.tests.<a href="./src/brainbase_labs/resources/workers/tests.py">create</a>(worker_id, \*\*<a href="src/brainbase_labs/types/workers/test_create_params.py">params</a>) -> <a href="./src/brainbase_labs/types/workers/test_create_response.py">TestCreateResponse</a></code>
- <code title="put /api/workers/{workerId}/tests/{testId}">client.workers.tests.<a href="./src/brainbase_labs/resources/workers/tests.py">update</a>(test_id, \*, worker_id, \*\*<a href="src/brainbase_labs/types/workers/test_update_params.py">params</a>) -> None</code>
- <code title="delete /api/workers/{workerId}/tests/{testId}">client.workers.tests.<a href="./src/brainbase_labs/resources/workers/tests.py">delete</a>(test_id, \*, worker_id) -> None</code>
- <code title="get /api/workers/{workerId}/tests/{testId}/runs">client.workers.tests.<a href="./src/brainbase_labs/resources/workers/tests.py">list_runs</a>(test_id, \*, worker_id) -> None</code>
- <code title="post /api/workers/{workerId}/tests/{testId}/run">client.workers.tests.<a href="./src/brainbase_labs/resources/workers/tests.py">run</a>(test_id, \*, worker_id) -> None</code>

## DeploymentLogs

### Voice

Types:

```python
from brainbase_labs.types.workers.deployment_logs import VoiceListResponse
```

Methods:

- <code title="get /api/workers/{workerId}/deploymentLogs/voice/{logId}">client.workers.deployment_logs.voice.<a href="./src/brainbase_labs/resources/workers/deployment_logs/voice.py">retrieve</a>(log_id, \*, worker_id) -> <a href="./src/brainbase_labs/types/shared/log.py">Log</a></code>
- <code title="get /api/workers/{workerId}/deploymentLogs/voice">client.workers.deployment_logs.voice.<a href="./src/brainbase_labs/resources/workers/deployment_logs/voice.py">list</a>(worker_id, \*\*<a href="src/brainbase_labs/types/workers/deployment_logs/voice_list_params.py">params</a>) -> <a href="./src/brainbase_labs/types/workers/deployment_logs/voice_list_response.py">VoiceListResponse</a></code>
