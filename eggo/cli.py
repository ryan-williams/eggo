# Licensed to Big Data Genomics (BDG) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The BDG licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os.path as osp

from click import group, option, Choice
from fabric.api import execute, get

import eggo.director as director


DEFAULT_DIRECTOR_CONF_PATH = osp.join(
    osp.dirname(__file__), 'resources', 'aws.conf')
DEFAULT_CF_TEMPLATE_PATH = osp.join(
    osp.dirname(__file__), 'resources', 'cloudformation.template')


# reusable options
option_region = option(
    '--region', default='us-east-1', show_default=True, help='AWS Region')
option_stack_name = option(
    '--stack-name', default='bdg-eggo', show_default=True,
    help='Stack name for CloudFormation and cluster name')


@group(context_settings={'help_option_names': ['-h', '--help']})
def main():
    """eggo -- provisions Hadoop clusters and processes genomics datasets"""
    pass


@main.group()
def cluster():
    """eggo cluster -- provisions Hadoop clusters using Cloudera Director"""
    pass


@main.group()
def datasets():
    """eggo datasets -- manages prebaked common genomics datasets"""
    pass


# ================
# CLUSTER COMMANDS
# ================


@cluster.command()
@option_region
@option_stack_name
@option('--availability-zone', default='us-east-1b', show_default=True,
        help='AWS Availability Zone')
@option('--cf-template-path', default=DEFAULT_CF_TEMPLATE_PATH,
        show_default=True, help='Path to AWS Cloudformation Template')
@option('--launcher-ami', default='ami-00a11e68', show_default=True,
        help='The AMI to use for the launcher node')
@option('--launcher-instance-type', default='m3.medium', show_default=True,
        help='The instance type to use for the launcher node')
@option('--director-conf-path', default=DEFAULT_DIRECTOR_CONF_PATH,
        show_default=True, help='Path to Director conf for AWS cloud')
@option('--cluster-ami', default='ami-00a11e68', show_default=True,
        help='The AMI to use for the worker nodes')
@option('-n', '--num-workers', default=3, show_default=True,
        help='The total number of worker nodes to provision')
def provision(region, availability_zone, stack_name, cf_template_path,
              launcher_ami, launcher_instance_type,
              director_conf_path, cluster_ami, num_workers):
    """Provision a new cluster on AWS"""
    director.provision(
        region, availability_zone, stack_name, cf_template_path, launcher_ami,
        launcher_instance_type, director_conf_path, cluster_ami, num_workers)


@cluster.command()
@option_region
@option_stack_name
def config_cluster(region, stack_name):
    """Configure cluster for genomics, incl. ADAM, OpenCB, Quince, etc"""
    director.config_cluster(region, stack_name)


@cluster.command()
@option_region
@option_stack_name
def teardown(region, stack_name):
    """Tear down a cluster and stack on AWS"""
    director.teardown(region, stack_name)


@cluster.command()
@option_region
@option_stack_name
@option('-n', '--node', default='master', show_default=True,
        type=Choice(['master', 'manager', 'launcher']),
        help='The node to login to')
def login(region, stack_name, node):
    """Login to the cluster"""
    director.login(region, stack_name, node)


@cluster.command()
@option_region
@option_stack_name
def describe(region, stack_name):
    """Describe the EC2 instances in the cluster"""
    director.describe(region, stack_name)


@cluster.command()
@option_region
@option_stack_name
def web_proxy(region, stack_name):
    """Set up ssh tunnels to web UIs"""
    director.web_proxy(region, stack_name)


@cluster.command()
@option_region
@option_stack_name
def get_director_log(region, stack_name):
    """DEBUG: get the Director application log from the launcher instance"""
    ec2_conn = director.create_ec2_connection(region)
    hosts = [director.get_launcher_instance(ec2_conn, stack_name).ip_address]
    execute(
        get, hosts=hosts, local_path='application.log',
        remote_path='/home/ec2-user/.cloudera-director/logs/application.log')


@cluster.command()
@option_region
@option_stack_name
@option('-f', '--fork', default='bigdatagenomics', show_default=True)
@option('-b', '--branch', default='master', show_default=True)
def reinstall_eggo(region, stack_name, fork, branch):
    """DEBUG: reinstall a specific version of eggo"""
    ec2_conn = director.create_ec2_connection(region)
    hosts = [director.get_master_instance(ec2_conn, stack_name).ip_address]
    execute(
        director.install_eggo, hosts=hosts, fork=fork, branch=branch,
        reinstall=True)


# =================
# DATASETS COMMANDS
# =================

@datasets.command()
def available():
    """List eggo datasets available at s3://bdg-eggo"""
    pass


@datasets.command()
def register():
    """Register dataset with Hive Metastore (for Hive/Impala)"""
    pass


@datasets.command()
def getblah():
    """Get a dataset from S3 (using Hadoop distcp)"""
    pass
