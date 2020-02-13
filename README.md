# Cloudify Policy Plugin POC

This plugin allows users to set up "policies" for monitoring their deployments.

The plugin will create a deployment that monitors deployments in its tenants.

The user provides a "policy" in the form of a script. The plugin will schedule a workflow to run the script according to the prescribed frequency.

If the policy passes a new check is scheduled.

If the policy fails, the policy action is executed in the form of a workflow, e.g. scale. A new check is scheduled anyways.

## Demo

Video located here: [demo video](https://github.com/EarthmanT/cloudify-policies-plugin/releases/download/0.1/demovideo.mov).

** Upload the plugin

`cfy plugins upload https://github.com/EarthmanT/cloudify-policies-plugin/releases/download/0.1/cloudify_policies_plugin-0.1-py27-none-linux_x86_64-centos-Core.wgn -y https://github.com/EarthmanT/cloudify-policies-plugin/releases/download/0.1/plugin.yaml`

** Create the "policy manager"

`cfy install examples/manage.yaml -b policy_manager`

** Install a deployment with a "policy"

`cfy install examples/policy.yaml -b policy -i policy_manager_id=[POLICY MANAGER NODE INSTANCE ID]`

** See that the check is scheduled:

`cfy exec list`

```shell
Executions:
+--------------------------------------+-------------------------------+-----------+------------+----------------+--------------------------+--------------------------+--------------------------+------------+----------------+------------+
|                  id                  |          workflow_id          |   status  | is_dry_run | deployment_id  |        created_at        |        started_at        |      scheduled_for       | visibility |  tenant_name   | created_by |
+--------------------------------------+-------------------------------+-----------+------------+----------------+--------------------------+--------------------------+--------------------------+------------+----------------+------------+
| 544c1f94-6153-465a-aab9-770e13af3b71 | create_deployment_environment | completed |   False    | policy_manager | 2020-02-13 12:12:34.918  | 2020-02-13 12:12:34.922  |                          |   tenant   | default_tenant |   admin    |
| c0db4bc5-7a81-44c4-9929-d1e14684e3a9 |            install            | completed |   False    | policy_manager | 2020-02-13 12:12:38.781  | 2020-02-13 12:12:38.782  |                          |   tenant   | default_tenant |   admin    |
| b4b2c478-1c71-4d46-98fd-5c18a1a906f0 | create_deployment_environment | completed |   False    |     policy     | 2020-02-13 12:13:04.834  | 2020-02-13 12:13:04.840  |                          |   tenant   | default_tenant |   admin    |
| 521c3a9c-20a9-4310-8f10-750c01a9e291 |            install            | completed |   False    |     policy     | 2020-02-13 12:13:08.996  | 2020-02-13 12:13:08.996  |                          |   tenant   | default_tenant |   admin    |
| 2472c8c0-fa1a-4776-a805-e79b2b7729be |          check_policy         | scheduled |   False    |     policy     | 2020-02-13 12:13:12.878  | 2020-02-13 12:14:01.469  | 2020-02-13 12:14:00.000  |   tenant   | default_tenant |   admin    |
+--------------------------------------+-------------------------------+-----------+------------+----------------+--------------------------+--------------------------+--------------------------+------------+----------------+------------+
```

** See that the check is constantly rescheduled:

```shell

Executions:
+--------------------------------------+-------------------------------+-----------+------------+----------------+--------------------------+--------------------------+--------------------------+------------+----------------+------------+
|                  id                  |          workflow_id          |   status  | is_dry_run | deployment_id  |        created_at        |        started_at        |      scheduled_for       | visibility |  tenant_name   | created_by |
+--------------------------------------+-------------------------------+-----------+------------+----------------+--------------------------+--------------------------+--------------------------+------------+----------------+------------+
| 544c1f94-6153-465a-aab9-770e13af3b71 | create_deployment_environment | completed |   False    | policy_manager | 2020-02-13 12:12:34.918  | 2020-02-13 12:12:34.922  |                          |   tenant   | default_tenant |   admin    |
| c0db4bc5-7a81-44c4-9929-d1e14684e3a9 |            install            | completed |   False    | policy_manager | 2020-02-13 12:12:38.781  | 2020-02-13 12:12:38.782  |                          |   tenant   | default_tenant |   admin    |
| b4b2c478-1c71-4d46-98fd-5c18a1a906f0 | create_deployment_environment | completed |   False    |     policy     | 2020-02-13 12:13:04.834  | 2020-02-13 12:13:04.840  |                          |   tenant   | default_tenant |   admin    |
| 521c3a9c-20a9-4310-8f10-750c01a9e291 |            install            | completed |   False    |     policy     | 2020-02-13 12:13:08.996  | 2020-02-13 12:13:08.996  |                          |   tenant   | default_tenant |   admin    |
| 2472c8c0-fa1a-4776-a805-e79b2b7729be |          check_policy         | completed |   False    |     policy     | 2020-02-13 12:13:12.878  | 2020-02-13 12:14:01.469  | 2020-02-13 12:14:00.000  |   tenant   | default_tenant |   admin    |
| 7461ac3b-3962-473c-9b7d-122a50297a34 |          check_policy         | scheduled |   False    | policy_manager | 2020-02-13 12:14:01.577  |                          | 2020-02-13 12:15:00.000  |   tenant   | default_tenant |   admin    |
+--------------------------------------+-------------------------------+-----------+------------+----------------+--------------------------+--------------------------+--------------------------+------------+----------------+------------+

```

At the end of the video, you will see that `scale` or action doesn't actually get executed. Some problem in the plugin I guess.

## Changes

I would actually have the user define a workflow in the blueprint that is the desired policy check, instead of a script in the policy.

Then I would have the plugin call that workflow and poll it. If the workflow failed, we execute the policy action, and if not we just reschedule.

There's a few other corners that I cut in the code that I would fix.

