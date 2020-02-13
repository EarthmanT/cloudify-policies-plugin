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

import base64
import datetime
import subprocess
import threading
from tempfile import TemporaryFile

from cloudify import ctx
from cloudify.manager import get_rest_client

DT_FORMAT = '%Y-%m-%d %H:%M:%S.%f'
SCHED_FORMAT = '%Y%m%d%H%M'


class PolicyFailed(Exception):
    def __init__(self, message, errors):
        super(PolicyFailed, self).__init__(message)
        self.errors = errors


class CloudifyPolicy(object):

    def __init__(self, policy_manager_id, policy_name, policy_definition, context=None):
        self.ctx = context or ctx
        self.process = None
        # All private properties are strings.
        self.policy_manager_id = policy_manager_id
        self._name = policy_name
        self._definition = policy_definition
        self._frequency = policy_definition['frequency']
        self._policy = self.encode_policy(policy_definition['policy'])
        self._created = \
            self._definition.get('created', datetime.datetime.now().__str__())
        self._last_execution = self._set_last_execution()

    @property
    def name(self):
        return self._name

    @property
    def policy(self):
        return self._policy

    @property
    def execution_method(self):
        return self._definition['execution_method']

    @property
    def timeout(self):
        return self._definition['timeout']

    @property
    def frequency(self):
        return datetime.timedelta(seconds=self._frequency)

    @property
    def action(self):
        return self._definition['action']

    @property
    def created(self):
        return self._get_datetime(self._created)

    @property
    def last_execution(self):
        return self._get_datetime(self._last_execution)

    @property
    def next_execution(self):
        return datetime.datetime.now() + self.frequency

    @staticmethod
    def _get_datetime(string):
        return datetime.datetime.strptime(string, DT_FORMAT)

    def encode_policy(self, policy):
        self.ctx.logger.info('Encoding policy: {0}'.format(policy))
        if isinstance(policy, basestring):
            return policy
        elif isinstance(policy, dict):
            policy_source = ctx.download_resource_and_render(**policy)
            with open(policy_source, 'r') as infile:
                return base64.b64encode(infile.read())
        raise TypeError(
            'The policy {0} is neither a dict of type '
            'cloudify.types.policies.File, nor a base64 encoded string.')

    def _set_last_execution(self):
        if self._definition.get('last_execution'):
            return self._definition['last_execution']
        else:
            return self._created

    def get_policy_content(self):
        return self.policy.decode('base64')

    def to_dict(self):
        return {
            self.name: {
                'policy': self.policy,
                'execution_method': self.execution_method,
                'timeout': self.timeout,
                'frequency': self._frequency,
                'action': self.action,
                'created': self._created,
                'last_execution': self._last_execution
            }
        }

    def is_execution_due(self):
        self.ctx.logger.info('Checking if execution is due...')
        now = datetime.datetime.now()
        next_exec = self.last_execution + self.frequency
        if next_exec >= now:
            self.ctx.logger.info('Execution due: {0}'.format(next_exec - now))
            return True
        self.ctx.logger.info('Execution not due: {0}'.format(next_exec - now))
        return False

    def executable(self):
        with TemporaryFile() as tmp:
            tmp.write(self.get_policy_content())
            command = [self.execution_method, tmp.name]
            self.ctx.logger.info('Starting execution thread.')
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            self.process.communicate()
            for line in iter(self.process.stdout.readline, ''):
                self.ctx.logger.info('STDOUT: {0}'.format(line.rstrip()))
            self.ctx.logger.info('Finished execution thread.')

    def execute(self):
        self.ctx.logger.info('Starting policy execution...')
        thread = threading.Thread(target=self.executable)
        thread.start()
        thread.join(self.timeout)
        if thread.is_alive():
            self.ctx.logger.info('Terminating policy execution...')
            self.process.terminate()
            thread.join()
            self.ctx.logger.info('Execution return code: {0}'.format(
                self.process.returncode))
            raise PolicyFailed('Execution failed...', self.process.stderr)

    def check_policy(self, deployment_id):
        if self.is_execution_due():
            self._last_execution = datetime.datetime.now().__str__()
            try:
                self.execute()
            except PolicyFailed:
                self.enforce_policy()
        self.schedule(deployment_id)

    def enforce_policy(self):
        client = get_rest_client()
        client.executions.start(**self.action)

    def schedule(self, deployment_id):
        client = get_rest_client()
        workflow_args = {
            'deployment_id': deployment_id,
            'workflow_id': 'check_policy',
            'parameters': {
              'policy_manager_id': self.policy_manager_id,
              'policy_id': self.name,
            },
            'schedule': '{0}-0000'.format(self.next_execution.strftime(SCHED_FORMAT))
        }
        client.executions.start(**workflow_args)
