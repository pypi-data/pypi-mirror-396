# Shared Types

```python
from SearchPilot.types import (
    Account,
    Customer,
    Experiment,
    Rule,
    Section,
    SeoExperimentResult,
    Step,
    Value,
)
```

# Customers

Methods:

- <code title="get /api/external/v1/customers/{customer_slug}/">client.customers.<a href="./src/SearchPilot/resources/customers.py">retrieve</a>(customer_slug) -> <a href="./src/SearchPilot/types/shared/customer.py">Customer</a></code>
- <code title="get /api/external/v1/customers/">client.customers.<a href="./src/SearchPilot/resources/customers.py">list</a>(\*\*<a href="src/SearchPilot/types/customer_list_params.py">params</a>) -> <a href="./src/SearchPilot/types/shared/customer.py">SyncCursorURLPage[Customer]</a></code>

# Accounts

Methods:

- <code title="get /api/external/v1/accounts/{account_slug}/">client.accounts.<a href="./src/SearchPilot/resources/accounts.py">retrieve</a>(account_slug) -> <a href="./src/SearchPilot/types/shared/account.py">Account</a></code>
- <code title="get /api/external/v1/accounts/">client.accounts.<a href="./src/SearchPilot/resources/accounts.py">list</a>(\*\*<a href="src/SearchPilot/types/account_list_params.py">params</a>) -> <a href="./src/SearchPilot/types/shared/account.py">SyncCursorURLPage[Account]</a></code>

# Sections

Methods:

- <code title="get /api/external/v1/sections/{section_id}/">client.sections.<a href="./src/SearchPilot/resources/sections.py">retrieve</a>(section_id) -> <a href="./src/SearchPilot/types/shared/section.py">Section</a></code>
- <code title="get /api/external/v1/sections/">client.sections.<a href="./src/SearchPilot/resources/sections.py">list</a>(\*\*<a href="src/SearchPilot/types/section_list_params.py">params</a>) -> <a href="./src/SearchPilot/types/shared/section.py">SyncCursorURLPage[Section]</a></code>

# Rules

Methods:

- <code title="get /api/external/v1/rules/{rule_id}/">client.rules.<a href="./src/SearchPilot/resources/rules.py">retrieve</a>(rule_id) -> <a href="./src/SearchPilot/types/shared/rule.py">Rule</a></code>
- <code title="get /api/external/v1/rules/">client.rules.<a href="./src/SearchPilot/resources/rules.py">list</a>(\*\*<a href="src/SearchPilot/types/rule_list_params.py">params</a>) -> <a href="./src/SearchPilot/types/shared/rule.py">SyncCursorURLPage[Rule]</a></code>

# Steps

Methods:

- <code title="get /api/external/v1/steps/{step_id}/">client.steps.<a href="./src/SearchPilot/resources/steps.py">retrieve</a>(step_id) -> <a href="./src/SearchPilot/types/shared/step.py">Step</a></code>
- <code title="get /api/external/v1/steps/">client.steps.<a href="./src/SearchPilot/resources/steps.py">list</a>(\*\*<a href="src/SearchPilot/types/step_list_params.py">params</a>) -> <a href="./src/SearchPilot/types/shared/step.py">SyncCursorURLPage[Step]</a></code>

# Values

Methods:

- <code title="get /api/external/v1/values/{value_id}/">client.values.<a href="./src/SearchPilot/resources/values.py">retrieve</a>(value_id) -> <a href="./src/SearchPilot/types/shared/value.py">Value</a></code>
- <code title="get /api/external/v1/values/">client.values.<a href="./src/SearchPilot/resources/values.py">list</a>(\*\*<a href="src/SearchPilot/types/value_list_params.py">params</a>) -> <a href="./src/SearchPilot/types/shared/value.py">SyncCursorURLPage[Value]</a></code>

# Experiments

Methods:

- <code title="get /api/external/v1/experiments/{experiment_id}/">client.experiments.<a href="./src/SearchPilot/resources/experiments.py">retrieve</a>(experiment_id) -> <a href="./src/SearchPilot/types/shared/experiment.py">Experiment</a></code>
- <code title="get /api/external/v1/experiments/">client.experiments.<a href="./src/SearchPilot/resources/experiments.py">list</a>(\*\*<a href="src/SearchPilot/types/experiment_list_params.py">params</a>) -> <a href="./src/SearchPilot/types/shared/experiment.py">SyncCursorURLPage[Experiment]</a></code>

# SeoExperimentResults

Methods:

- <code title="get /api/external/v1/seo_experiment_results/{seo_experiment_result_id}/">client.seo_experiment_results.<a href="./src/SearchPilot/resources/seo_experiment_results.py">retrieve</a>(seo_experiment_result_id) -> <a href="./src/SearchPilot/types/shared/seo_experiment_result.py">SeoExperimentResult</a></code>
- <code title="get /api/external/v1/seo_experiment_results/">client.seo_experiment_results.<a href="./src/SearchPilot/resources/seo_experiment_results.py">list</a>(\*\*<a href="src/SearchPilot/types/seo_experiment_result_list_params.py">params</a>) -> <a href="./src/SearchPilot/types/shared/seo_experiment_result.py">SyncCursorURLPage[SeoExperimentResult]</a></code>
