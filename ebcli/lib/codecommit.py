# Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
import datetime
import sys

if sys.version_info >= (3, 0):
    from urllib.parse import urlsplit
if sys.version_info < (3, 0) and sys.version_info >= (2, 5):
    from urlparse import urlsplit

from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from cement.utils.misc import minimal_logger

from . import aws
from ..core import io
from ..lib import utils
from ..objects.exceptions import ServiceError

LOG = minimal_logger(__name__)


SUPPORTED_REGIONS = [
    "ca-central-1",    # Canada (Central)
    "us-east-1",       # US East (N. Virginia)
    "us-east-2",       # US East (Ohio)
    "us-west-1",       # US West (N. California)
    "us-west-2",       # US West (Oregon)
    "eu-west-1",       # EU (Ireland)
    "eu-west-2",       # EU (London)
    "eu-west-3",       # EU (Paris)
    "eu-central-1",    # EU (Frankfurt)
    "ap-northeast-1",  # Asia Pacific (Tokyo)
    "ap-northeast-2",  # Asia Pacific (Seoul)
    "ap-southeast-1",  # Asia Pacific (Singapore)
    "ap-southeast-2",  # Asia Pacific (Sydney)
    "ap-south-1",      # Asia Pacific (Mumbai)
    "sa-east-1"        # South America (Sao Paulo)
]


def _make_api_call(operation_name, **operation_options):
    try:
        result = aws.make_api_call('codecommit', operation_name, **operation_options)
    except ServiceError as ex:
        if ex.code == 'AccessDeniedException':
            io.echo("EB CLI does not have the right permissions to access CodeCommit."
                    " List of IAM policies needed by EB CLI, please configure and try again.\n "
                    "codecommit:CreateRepository\n codecommit:CreateBranch\n codecommit:GetRepository\n "
                    "codecommit:ListRepositories\n codecommit:ListBranches\n"
                    "To learn more, see Docs: http://docs.aws.amazon.com/codecommit/latest/userguide/access-permissions.html")
        raise ex
    return result


def create_repository(repo_name, repo_description=None):
    params = dict(repositoryName=repo_name)

    if repo_description is not None:
        params['repositoryDescription'] = repo_description

    result = _make_api_call('create_repository', **params)
    return result


def create_branch(repo_name, branch_name, commit_id):
    params = dict(repositoryName=repo_name, branchName=branch_name, commitId=commit_id)

    _make_api_call('create_branch', **params)


def get_repository(repo_name):
    params = dict(repositoryName=repo_name)

    result = _make_api_call('get_repository', **params)
    return result


def get_branch(repo_name, branch_name):
    params = dict(repositoryName=repo_name, branchName=branch_name)

    result = _make_api_call('get_branch', **params)
    return result


def list_repositories(next_token=None, sort_by='lastModifiedDate', order='descending'):
    params = dict()

    if next_token is not None:
        params['nextToken'] = next_token

    if sort_by is not None:
        params['sortBy'] = sort_by

    if order is not None:
        params['order'] = order

    result = _make_api_call('list_repositories', **params)
    return result


def list_branches(repo_name, next_token=None):
    params = dict(repositoryName=repo_name)

    if next_token is not None:
        params['nextToken'] = next_token

    result = _make_api_call('list_branches', **params)
    return result


def region_supported(region):
    if region is not None and region in SUPPORTED_REGIONS:
        return True

    return False
