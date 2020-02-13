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


from setuptools import setup

setup(
    name='cloudify-policies-plugin',
    version='0.1',
    author='Cloudify Platform Ltd.',
    author_email='hello@cloudify.co',
    description='Plugin provides tenant-wide monitoring solution',
    packages=['cloudify_policies'],
    license='LICENSE',
    install_requires=[
        'cloudify-common==5.0.5.1',
    ]
)
