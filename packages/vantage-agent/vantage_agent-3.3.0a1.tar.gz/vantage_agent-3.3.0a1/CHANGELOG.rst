=========
Changelog
=========

Tracking of all notable changes to the Vantage Agent project.

Unreleased
----------

3.1.1 - 2025-09-12
------------------

- Sync version with the Vantage API.

3.1.0 - 2025-09-12
------------------


3.0.0 - 2025-08-22
------------------

- Update the *sync_partitions.py* script to modify the *gres.conf* file when new nodes have GPUs.
- Bump *python-jose* from 3.3.0 to 3.4.0.
- Implement functionality to track clusters' queue (`PENG-3043`_).
- Update pydantic to ^2.10.6.
- Implement mechanism to cancel jobs in the queue (`PENG-3069`_).

.. _PENG-3043: https://app.clickup.com/t/18022949/PENG-3043
.. _PENG-3069: https://app.clickup.com/t/18022949/PENG-3069

2.7.0 - 2025-03-10
------------------

- Modify the *sync_partitions.py* logical to handle partitions with GPU nodes (`PENG-2628`_).

.. _PENG-2628: https://app.clickup.com/t/18022949/PENG-2628

2.6.0 - 2025-02-10
------------------

- Pin *APScheduler* version to *3.10.4*.
- Fix how the agent gets the numbers of CPUs per node.
- Update sync partitions function to update the partitions.json file.
- Default the *TASK_SELF_UPDATE_INTERVAL_SECONDS* setting to *None*.
- Add a setting to indicate if the agent is operating in a cloud cluster.
- Add settings for customising Sentry's sample rates (`PENG-2592`_).
- Migrate Vantage domain to vantagecompute.ai (`PENG-2461`_).

.. _PENG-2592: https://app.clickup.com/t/18022949/PENG-2592
.. _PENG-2461: https://app.clickup.com/t/18022949/PENG-2461

2.5.0 - 2024-11-13
------------------

- Update Vantage API to support cloud clusters with multiple partitions (`PENG-2344`_).

.. _PENG-2344: https://app.clickup.com/t/18022949/PENG-2344


2.4.0 - 2024-10-02
------------------

- Initialize the Vantage Agent with the same version as the API (`PENG-2360`_).

.. _PENG-2360: https://app.clickup.com/t/18022949/PENG-2360
