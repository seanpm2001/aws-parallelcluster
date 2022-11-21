# Copyright 2022 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance
# with the License. A copy of the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "LICENSE.txt" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES
# OR CONDITIONS OF ANY KIND, express or implied. See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from assertpy import assert_that

from pcluster.schemas.cluster_schema import ClusterSchema
from pcluster.templates.cdk_builder import CDKTemplateBuilder
from pcluster.utils import load_yaml_dict
from tests.pcluster.aws.dummy_aws_api import mock_aws_api
from tests.pcluster.models.dummy_s3_bucket import dummy_cluster_bucket
from tests.pcluster.utils import get_head_node_policy, get_statement_by_sid


@pytest.mark.parametrize(
    "config_file_name",
    [
        ("config.yaml"),
    ],
)
def test_head_node_permissions(mocker, test_datadir, config_file_name):
    mock_aws_api(mocker)

    input_yaml = load_yaml_dict(test_datadir / config_file_name)

    cluster_config = ClusterSchema(cluster_name="clustername").load(input_yaml)

    generated_template = CDKTemplateBuilder().build_cluster_template(
        cluster_config=cluster_config, bucket=dummy_cluster_bucket(), stack_name="clustername"
    )

    head_node_policy = get_head_node_policy(generated_template)
    statement = get_statement_by_sid(policy=head_node_policy, sid="AllowGettingDirectorySecretValue")
    assert_that(statement["Effect"]).is_equal_to("Allow")
    assert_that(statement["Action"]).is_equal_to("secretsmanager:GetSecretValue")
    assert_that(statement["Resource"]).is_equal_to("arn:aws:secretsmanager:eu-west-1:123456789:secret:a-secret-name")