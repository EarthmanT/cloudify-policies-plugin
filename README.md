# Cloudify Policy Plugin POC

This plugin allows users to set up "policies" for monitoring their deployments.

The plugin will create a deployment that monitors deployments in its tenants.

The user provides a "policy" in the form of a script. The plugin will schedule a workflow to run the script according to the prescribed frequency.

If the policy passes a new check is scheduled.

If the policy fails, the policy action is executed in the form of a workflow, e.g. scale. A new check is scheduled anyways.

## Demo

** Upload the plugin

`cfy plugins upload https://github.com/EarthmanT/cloudify-policies-plugin/releases/download/0.1/cloudify_policies_plugin-0.1-py27-none-linux_x86_64-centos-Core.wgn -y https://github.com/EarthmanT/cloudify-policies-plugin/releases/download/0.1/plugin.yaml`

** Create the "policy manager"

`cfy install examples/manage.yaml -b policy_manager`

** Install a deployment with a "policy"

`cfy install examples/policy.yaml -b policy -i policy_manager_id=[POLICY MANAGER NODE INSTANCE ID]`

** See that the check is scheduled:

`cfy exec list`

```shell


```

** See that the check is constantly rescheduled:

```shell


```