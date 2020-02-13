# Copyright (c) 2020 Cloudify Platform Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from cloudify import ctx
from cloudify.workflows import ctx as wtx
from cloudify.manager import get_rest_client

from policy import CloudifyPolicy

POLICIES_KEY = 'policies'


def update_policy_action(action):
    if not action['deployment_id']:
        action['deployment_id'] = ctx.deployment.id
    if action['workflow_id'] == 'scale' \
            and not action['parameters'].get('node_id'):
        action['parameters']['scalable_entity_name'] = ctx.node.id
    elif action['workflow_id'] == 'heal' \
            and not action['parameters'].get('node_instance_id'):
        action['parameters']['node_instance_id'] = ctx.instance.id


def add_policy(policy, **_):
    ctx.logger.info('Adding policy to policy manager...')
    update_policy_action(policy['action'])
    target_node_instance_id = policy.get('policy_manager_node_instance_id')
    client = get_rest_client()
    ni = client.node_instances.get(
        target_node_instance_id)
    policy_obj = CloudifyPolicy(
        target_node_instance_id, ctx.instance.id, policy)
    policy_obj.schedule(ctx.deployment.id)
    ni.runtime_properties[POLICIES_KEY].update(policy_obj.to_dict())
    client.node_instances.update(
        target_node_instance_id,
        runtime_properties=ni.runtime_properties,
        version=ni.version + 1)


def initialize(default_policies=None, **_):
    ctx.logger.info('Initializing policy manager...')
    default_policies = default_policies or {}
    if not ctx.instance.runtime_properties.get(POLICIES_KEY):
        ctx.instance.runtime_properties[POLICIES_KEY] = {}
    for policy_name, policy_definition in default_policies.iteritems():
        ctx.instance.runtime_properties[POLICIES_KEY].update(
            CloudifyPolicy(
                ctx.deployment.id, policy_name, policy_definition).to_dict())


def terminate(**_):
    ctx.logger.info('Terminating policy manager...')


def check_policy(policy_manager_id, policy_id, **_):
    wtx.logger.info('Starting policy management process...')
    client = get_rest_client()
    ni = client.node_instances.get(
        policy_manager_id)
    policy_definition = ni.runtime_properties[POLICIES_KEY][policy_id]
    policy_obj = CloudifyPolicy(
        policy_manager_id, policy_id, policy_definition, wtx)
    policy_obj.check_policy(ni.deployment_id)
    ni.runtime_properties[POLICIES_KEY].update(policy_obj.to_dict())
    client.node_instances.update(
        policy_manager_id,
        runtime_properties=ni.runtime_properties,
        version=ni.version + 1)
