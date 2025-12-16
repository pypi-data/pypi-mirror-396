# Repo

Types:

```python
from aibread.types import RepoResponse, RepoListResponse, RepoGetTreeResponse
```

Methods:

- <code title="post /v1/repo">client.repo.<a href="./src/aibread/resources/repo.py">create</a>(\*\*<a href="src/aibread/types/repo_create_params.py">params</a>) -> <a href="./src/aibread/types/repo_response.py">RepoResponse</a></code>
- <code title="get /v1/repo">client.repo.<a href="./src/aibread/resources/repo.py">list</a>(\*\*<a href="src/aibread/types/repo_list_params.py">params</a>) -> <a href="./src/aibread/types/repo_list_response.py">RepoListResponse</a></code>
- <code title="get /v1/repo/{repo_name}">client.repo.<a href="./src/aibread/resources/repo.py">get</a>(repo_name, \*\*<a href="src/aibread/types/repo_get_params.py">params</a>) -> <a href="./src/aibread/types/repo_response.py">RepoResponse</a></code>
- <code title="get /v1/repo/{repo_name}/tree">client.repo.<a href="./src/aibread/resources/repo.py">get_tree</a>(repo_name, \*\*<a href="src/aibread/types/repo_get_tree_params.py">params</a>) -> <a href="./src/aibread/types/repo_get_tree_response.py">RepoGetTreeResponse</a></code>
- <code title="put /v1/repo">client.repo.<a href="./src/aibread/resources/repo.py">set</a>(\*\*<a href="src/aibread/types/repo_set_params.py">params</a>) -> <a href="./src/aibread/types/repo_response.py">RepoResponse</a></code>

# Prompts

Types:

```python
from aibread.types import (
    DeleteResponse,
    Message,
    PromptResponse,
    PromptListResponse,
    PromptBatchSetResponse,
    PromptCreateBatchResponse,
)
```

Methods:

- <code title="post /v1/repo/{repo_name}/prompts">client.prompts.<a href="./src/aibread/resources/prompts.py">create</a>(repo_name, \*\*<a href="src/aibread/types/prompt_create_params.py">params</a>) -> <a href="./src/aibread/types/prompt_response.py">PromptResponse</a></code>
- <code title="get /v1/repo/{repo_name}/prompts">client.prompts.<a href="./src/aibread/resources/prompts.py">list</a>(repo_name, \*\*<a href="src/aibread/types/prompt_list_params.py">params</a>) -> <a href="./src/aibread/types/prompt_list_response.py">PromptListResponse</a></code>
- <code title="put /v1/repo/{repo_name}/prompts/batch">client.prompts.<a href="./src/aibread/resources/prompts.py">batch_set</a>(repo_name, \*\*<a href="src/aibread/types/prompt_batch_set_params.py">params</a>) -> <a href="./src/aibread/types/prompt_batch_set_response.py">PromptBatchSetResponse</a></code>
- <code title="post /v1/repo/{repo_name}/prompts/batch">client.prompts.<a href="./src/aibread/resources/prompts.py">create_batch</a>(repo_name, \*\*<a href="src/aibread/types/prompt_create_batch_params.py">params</a>) -> <a href="./src/aibread/types/prompt_create_batch_response.py">PromptCreateBatchResponse</a></code>
- <code title="get /v1/repo/{repo_name}/prompts/{prompt_name}">client.prompts.<a href="./src/aibread/resources/prompts.py">get</a>(prompt_name, \*, repo_name, \*\*<a href="src/aibread/types/prompt_get_params.py">params</a>) -> <a href="./src/aibread/types/prompt_response.py">PromptResponse</a></code>
- <code title="put /v1/repo/{repo_name}/prompts/{prompt_name}">client.prompts.<a href="./src/aibread/resources/prompts.py">set</a>(prompt_name, \*, repo_name, \*\*<a href="src/aibread/types/prompt_set_params.py">params</a>) -> <a href="./src/aibread/types/prompt_response.py">PromptResponse</a></code>

# Targets

Types:

```python
from aibread.types import (
    Generator,
    TargetConfigBase,
    TargetResponse,
    TargetListResponse,
    TargetBatchSetResponse,
    TargetCreateBatchResponse,
)
```

Methods:

- <code title="post /v1/repo/{repo_name}/targets">client.targets.<a href="./src/aibread/resources/targets/targets.py">create</a>(repo_name, \*\*<a href="src/aibread/types/target_create_params.py">params</a>) -> <a href="./src/aibread/types/target_response.py">TargetResponse</a></code>
- <code title="get /v1/repo/{repo_name}/targets">client.targets.<a href="./src/aibread/resources/targets/targets.py">list</a>(repo_name, \*\*<a href="src/aibread/types/target_list_params.py">params</a>) -> <a href="./src/aibread/types/target_list_response.py">TargetListResponse</a></code>
- <code title="delete /v1/repo/{repo_name}/targets/{target_name}">client.targets.<a href="./src/aibread/resources/targets/targets.py">delete</a>(target_name, \*, repo_name, \*\*<a href="src/aibread/types/target_delete_params.py">params</a>) -> <a href="./src/aibread/types/delete_response.py">DeleteResponse</a></code>
- <code title="put /v1/repo/{repo_name}/targets/batch">client.targets.<a href="./src/aibread/resources/targets/targets.py">batch_set</a>(repo_name, \*\*<a href="src/aibread/types/target_batch_set_params.py">params</a>) -> <a href="./src/aibread/types/target_batch_set_response.py">TargetBatchSetResponse</a></code>
- <code title="post /v1/repo/{repo_name}/targets/batch">client.targets.<a href="./src/aibread/resources/targets/targets.py">create_batch</a>(repo_name, \*\*<a href="src/aibread/types/target_create_batch_params.py">params</a>) -> <a href="./src/aibread/types/target_create_batch_response.py">TargetCreateBatchResponse</a></code>
- <code title="get /v1/repo/{repo_name}/targets/{target_name}">client.targets.<a href="./src/aibread/resources/targets/targets.py">get</a>(target_name, \*, repo_name, \*\*<a href="src/aibread/types/target_get_params.py">params</a>) -> <a href="./src/aibread/types/target_response.py">TargetResponse</a></code>
- <code title="put /v1/repo/{repo_name}/targets/{target_name}">client.targets.<a href="./src/aibread/resources/targets/targets.py">set</a>(target_name, \*, repo_name, \*\*<a href="src/aibread/types/target_set_params.py">params</a>) -> <a href="./src/aibread/types/target_response.py">TargetResponse</a></code>

## Stim

Types:

```python
from aibread.types.targets import StimResponse, StimGetOutputResponse
```

Methods:

- <code title="get /v1/repo/{repo_name}/targets/{target_name}/stim">client.targets.stim.<a href="./src/aibread/resources/targets/stim.py">get</a>(target_name, \*, repo_name, \*\*<a href="src/aibread/types/targets/stim_get_params.py">params</a>) -> <a href="./src/aibread/types/targets/stim_response.py">StimResponse</a></code>
- <code title="get /v1/repo/{repo_name}/targets/{target_name}/stim/output">client.targets.stim.<a href="./src/aibread/resources/targets/stim.py">get_output</a>(target_name, \*, repo_name, \*\*<a href="src/aibread/types/targets/stim_get_output_params.py">params</a>) -> <a href="./src/aibread/types/targets/stim_get_output_response.py">StimGetOutputResponse</a></code>
- <code title="post /v1/repo/{repo_name}/targets/{target_name}/stim">client.targets.stim.<a href="./src/aibread/resources/targets/stim.py">run</a>(target_name, \*, repo_name, \*\*<a href="src/aibread/types/targets/stim_run_params.py">params</a>) -> <a href="./src/aibread/types/targets/stim_response.py">StimResponse</a></code>

## Rollout

Types:

```python
from aibread.types.targets import RolloutResponse, RolloutGetOutputResponse
```

Methods:

- <code title="get /v1/repo/{repo_name}/targets/{target_name}/rollout">client.targets.rollout.<a href="./src/aibread/resources/targets/rollout.py">get</a>(target_name, \*, repo_name, \*\*<a href="src/aibread/types/targets/rollout_get_params.py">params</a>) -> <a href="./src/aibread/types/targets/rollout_response.py">RolloutResponse</a></code>
- <code title="get /v1/repo/{repo_name}/targets/{target_name}/rollout/output">client.targets.rollout.<a href="./src/aibread/resources/targets/rollout.py">get_output</a>(target_name, \*, repo_name, \*\*<a href="src/aibread/types/targets/rollout_get_output_params.py">params</a>) -> <a href="./src/aibread/types/targets/rollout_get_output_response.py">RolloutGetOutputResponse</a></code>
- <code title="post /v1/repo/{repo_name}/targets/{target_name}/rollout">client.targets.rollout.<a href="./src/aibread/resources/targets/rollout.py">run</a>(target_name, \*, repo_name, \*\*<a href="src/aibread/types/targets/rollout_run_params.py">params</a>) -> <a href="./src/aibread/types/targets/rollout_response.py">RolloutResponse</a></code>

# Bakes

Types:

```python
from aibread.types import (
    BakeConfigBase,
    BakeResponse,
    CheckpointConfig,
    DataConfig,
    DataSource,
    DatasetItem,
    DeepspeedConfig,
    ModelConfig,
    OptimizerConfig,
    SchedulerConfig,
    WandbConfig,
    BakeListResponse,
    BakeBatchSetResponse,
    BakeCreateBatchResponse,
    BakeDownloadResponse,
    BakeGetMetricsResponse,
)
```

Methods:

- <code title="post /v1/repo/{repo_name}/bakes">client.bakes.<a href="./src/aibread/resources/bakes.py">create</a>(repo_name, \*\*<a href="src/aibread/types/bake_create_params.py">params</a>) -> <a href="./src/aibread/types/bake_response.py">BakeResponse</a></code>
- <code title="get /v1/repo/{repo_name}/bakes">client.bakes.<a href="./src/aibread/resources/bakes.py">list</a>(repo_name, \*\*<a href="src/aibread/types/bake_list_params.py">params</a>) -> <a href="./src/aibread/types/bake_list_response.py">BakeListResponse</a></code>
- <code title="delete /v1/repo/{repo_name}/bakes/{bake_name}">client.bakes.<a href="./src/aibread/resources/bakes.py">delete</a>(bake_name, \*, repo_name, \*\*<a href="src/aibread/types/bake_delete_params.py">params</a>) -> <a href="./src/aibread/types/delete_response.py">DeleteResponse</a></code>
- <code title="put /v1/repo/{repo_name}/bakes/batch">client.bakes.<a href="./src/aibread/resources/bakes.py">batch_set</a>(repo_name, \*\*<a href="src/aibread/types/bake_batch_set_params.py">params</a>) -> <a href="./src/aibread/types/bake_batch_set_response.py">BakeBatchSetResponse</a></code>
- <code title="post /v1/repo/{repo_name}/bakes/batch">client.bakes.<a href="./src/aibread/resources/bakes.py">create_batch</a>(repo_name, \*\*<a href="src/aibread/types/bake_create_batch_params.py">params</a>) -> <a href="./src/aibread/types/bake_create_batch_response.py">BakeCreateBatchResponse</a></code>
- <code title="get /v1/repo/{repo_name}/bakes/{bake_name}/download">client.bakes.<a href="./src/aibread/resources/bakes.py">download</a>(bake_name, \*, repo_name, \*\*<a href="src/aibread/types/bake_download_params.py">params</a>) -> <a href="./src/aibread/types/bake_download_response.py">BakeDownloadResponse</a></code>
- <code title="get /v1/repo/{repo_name}/bakes/{bake_name}">client.bakes.<a href="./src/aibread/resources/bakes.py">get</a>(bake_name, \*, repo_name, \*\*<a href="src/aibread/types/bake_get_params.py">params</a>) -> <a href="./src/aibread/types/bake_response.py">BakeResponse</a></code>
- <code title="get /v1/repo/{repo_name}/bakes/{bake_name}/metrics">client.bakes.<a href="./src/aibread/resources/bakes.py">get_metrics</a>(bake_name, \*, repo_name, \*\*<a href="src/aibread/types/bake_get_metrics_params.py">params</a>) -> <a href="./src/aibread/types/bake_get_metrics_response.py">BakeGetMetricsResponse</a></code>
- <code title="post /v1/repo/{repo_name}/bakes/{bake_name}">client.bakes.<a href="./src/aibread/resources/bakes.py">run</a>(bake_name, \*, repo_name, \*\*<a href="src/aibread/types/bake_run_params.py">params</a>) -> <a href="./src/aibread/types/bake_response.py">BakeResponse</a></code>
- <code title="put /v1/repo/{repo_name}/bakes/{bake_name}">client.bakes.<a href="./src/aibread/resources/bakes.py">set</a>(bake_name, \*, repo_name, \*\*<a href="src/aibread/types/bake_set_params.py">params</a>) -> <a href="./src/aibread/types/bake_response.py">BakeResponse</a></code>

# Recipes

Types:

```python
from aibread.types import RecipeGetDependencyGraphResponse, RecipeGetRecreationPlanResponse
```

Methods:

- <code title="get /v1/repo/{repo_name}/recipe/{bake_name}/dependency-graph">client.recipes.<a href="./src/aibread/resources/recipes.py">get_dependency_graph</a>(bake_name, \*, repo_name, \*\*<a href="src/aibread/types/recipe_get_dependency_graph_params.py">params</a>) -> <a href="./src/aibread/types/recipe_get_dependency_graph_response.py">RecipeGetDependencyGraphResponse</a></code>
- <code title="get /v1/repo/{repo_name}/recipe/{bake_name}/recreation-plan">client.recipes.<a href="./src/aibread/resources/recipes.py">get_recreation_plan</a>(bake_name, \*, repo_name, \*\*<a href="src/aibread/types/recipe_get_recreation_plan_params.py">params</a>) -> <a href="./src/aibread/types/recipe_get_recreation_plan_response.py">RecipeGetRecreationPlanResponse</a></code>

# Health

Types:

```python
from aibread.types import HealthCheckResponse
```

Methods:

- <code title="get /v1/health">client.health.<a href="./src/aibread/resources/health.py">check</a>() -> <a href="./src/aibread/types/health_check_response.py">HealthCheckResponse</a></code>
