r'''
# EZ Constructs

A collection of heaviliy opinionated AWS CDK highlevel constructs.
[construct.dev](https://constructs.dev/packages/ez-constructs/) || [npmjs](https://www.npmjs.com/package/ez-constructs)

## Installation

> The library requires AWS CDK version >= 2.92.0.

` npm install ez-constructs` or ` yarn add ez-constructs`

## Constructs

1. [SecureBucket](src/secure-bucket) - Creates an S3 bucket that is secure, encrypted at rest along with object retention and intelligent transition rules
2. [SimpleCodeBuildProject](src/codebuild-ci) - Creates Codebuild projects the easy way.
3. [SimpleStepFunction](src/stepfunctions) - Creates a simple step function user supplied workflow definition file.
4. [SimpleServerlessSparkJob](src/stepfunctions#simpleserverlesssparkjob) - Creates a step function that can be used to submit a spark job to EMR.
5. [SimpleServerlessApplication](src/emr) - Creates an EMR Serverless Application.

## Libraries

1. Utils - A collection of utility functions
2. CustomSynthesizer - A custom CDK synthesizer that will alter the default service roles that CDK uses.

## Aspects

1. [PermissionsBoundaryAspect](src/aspects) - A custom aspect that can be used to apply a permission boundary to all roles created in the contex.
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_codebuild as _aws_cdk_aws_codebuild_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_emrserverless as _aws_cdk_aws_emrserverless_ceddda9d
import aws_cdk.aws_events as _aws_cdk_aws_events_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_kms as _aws_cdk_aws_kms_ceddda9d
import aws_cdk.aws_lambda as _aws_cdk_aws_lambda_ceddda9d
import aws_cdk.aws_logs as _aws_cdk_aws_logs_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_stepfunctions as _aws_cdk_aws_stepfunctions_ceddda9d
import aws_cdk.aws_stepfunctions_tasks as _aws_cdk_aws_stepfunctions_tasks_ceddda9d
import constructs as _constructs_77d1e7e8


class CustomSynthesizer(
    _aws_cdk_ceddda9d.DefaultStackSynthesizer,
    metaclass=jsii.JSIIMeta,
    jsii_type="ez-constructs.CustomSynthesizer",
):
    '''As a best practice organizations enforce policies which require all custom IAM Roles created to be defined under a specific path and permission boundary.

    In order to adhere with such compliance requirements, the CDK bootstrapping is often customized
    (refer: https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html#bootstrapping-customizing).
    So, we need to ensure that parallel customization is applied during synthesis phase.
    This Custom Synthesizer is used to modify the default path of the following IAM Roles internally used by CDK:

    - deploy role
    - file-publishing-role
    - image-publishing-role
    - cfn-exec-role
    - lookup-role

    :see:

    PermissionsBoundaryAspect *
    Example Usage::

    new DbStack(app, config.id('apiDbStack'), {
    env: {account: '123456789012', region: 'us-east-1'},
    synthesizer: new CustomSynthesizer('/banking/dev/'),
    });
    '''

    def __init__(self, role_path: builtins.str) -> None:
        '''
        :param role_path: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f080045a2d1faf66d212813fbca2f476c782734821039529b5317ec84381ea0)
            check_type(argname="argument role_path", value=role_path, expected_type=type_hints["role_path"])
        jsii.create(self.__class__, self, [role_path])


class EzConstruct(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="ez-constructs.EzConstruct",
):
    '''A marker base class for EzConstructs.'''

    def __init__(self, scope: _constructs_77d1e7e8.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fdbf166d776c14fb424ae19c70a3dd70710fd6ab1b72891c40c48c6bf133669)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])


class FileUtils(metaclass=jsii.JSIIMeta, jsii_type="ez-constructs.FileUtils"):
    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="readFile")
    @builtins.classmethod
    def read_file(cls, path: builtins.str) -> builtins.str:
        '''Will read the file from the given path and return the content as a string.

        :param path: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7314fbbf5bb43741eaf334764ec86040d581a9f15dd42b8b0170d8dd0bab1e80)
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "readFile", [path]))


@jsii.enum(jsii_type="ez-constructs.GitEvent")
class GitEvent(enum.Enum):
    '''The Github events which should trigger this build.'''

    PULL_REQUEST = "PULL_REQUEST"
    PULL_REQUEST_MERGED = "PULL_REQUEST_MERGED"
    PUSH = "PUSH"
    ALL = "ALL"


@jsii.implements(_aws_cdk_ceddda9d.IAspect)
class PermissionsBoundaryAspect(
    metaclass=jsii.JSIIMeta,
    jsii_type="ez-constructs.PermissionsBoundaryAspect",
):
    '''As a best practice organizations enforce policies which require all custom IAM Roles created to be defined under a specific path and permission boundary.

    Well, this allows better governance and also prevents unintended privilege escalation.
    AWS CDK high level constructs and patterns encapsulates the role creation from end users.
    So it is a laborious and at times impossible to get a handle of newly created roles within a stack.
    This aspect will scan all roles within the given scope and will attach the right permission boundary and path to them.
    Example::

          const app = new App();
          const mystack = new MyStack(app, 'MyConstruct'); // assuming this will create a role by name `myCodeBuildRole` with admin access.
          Aspects.of(app).add(new PermissionsBoundaryAspect('/my/devroles/', 'boundary/dev-max'));
    '''

    def __init__(
        self,
        role_path: builtins.str,
        role_permission_boundary: builtins.str,
    ) -> None:
        '''Constructs a new PermissionsBoundaryAspect.

        :param role_path: - the role path to attach to newly created roles.
        :param role_permission_boundary: - the permission boundary to attach to newly created roles.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e21146239f529d4c7c7573ff7851541b6758a3373877082ded397d2b42f7191b)
            check_type(argname="argument role_path", value=role_path, expected_type=type_hints["role_path"])
            check_type(argname="argument role_permission_boundary", value=role_permission_boundary, expected_type=type_hints["role_permission_boundary"])
        jsii.create(self.__class__, self, [role_path, role_permission_boundary])

    @jsii.member(jsii_name="modifyRolePath")
    def modify_role_path(
        self,
        role_resource: _aws_cdk_aws_iam_ceddda9d.CfnRole,
        stack: _aws_cdk_ceddda9d.Stack,
        skip_boundary: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param role_resource: -
        :param stack: -
        :param skip_boundary: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7536cb2f448fe953474186dc0747e81f4d8f437faec613ad0a8043185cb2e13a)
            check_type(argname="argument role_resource", value=role_resource, expected_type=type_hints["role_resource"])
            check_type(argname="argument stack", value=stack, expected_type=type_hints["stack"])
            check_type(argname="argument skip_boundary", value=skip_boundary, expected_type=type_hints["skip_boundary"])
        return typing.cast(None, jsii.invoke(self, "modifyRolePath", [role_resource, stack, skip_boundary]))

    @jsii.member(jsii_name="visit")
    def visit(self, node: _constructs_77d1e7e8.IConstruct) -> None:
        '''All aspects can visit an IConstruct.

        :param node: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e22d8b07bcff8691c4b3e0419e521f885cbcdc51a7ee4787a7d6d0c199db0c73)
            check_type(argname="argument node", value=node, expected_type=type_hints["node"])
        return typing.cast(None, jsii.invoke(self, "visit", [node]))

    @builtins.property
    @jsii.member(jsii_name="rolePath")
    def role_path(self) -> builtins.str:
        '''The role path to attach to newly created roles.'''
        return typing.cast(builtins.str, jsii.get(self, "rolePath"))

    @role_path.setter
    def role_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8cd0f21c19e2033b3e7c69c2b0a81c07accb873a289c961a3d7df6dd2e442bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rolePath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rolePermissionBoundary")
    def role_permission_boundary(self) -> builtins.str:
        '''The permission boundary to attach to newly created roles.'''
        return typing.cast(builtins.str, jsii.get(self, "rolePermissionBoundary"))

    @role_permission_boundary.setter
    def role_permission_boundary(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__546fd68c81f3db699e725f4e6c53647bf8bf3f2b58c323bb577c2708a254b991)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rolePermissionBoundary", value) # pyright: ignore[reportArgumentType]


class SecureBucket(
    EzConstruct,
    metaclass=jsii.JSIIMeta,
    jsii_type="ez-constructs.SecureBucket",
):
    '''Will create a secure bucket with the following features: - Bucket name will be modified to include account and region.

    - Access limited to the owner
    - Object Versioning
    - Encryption at rest
    - Object expiration max limit to 10 years
    - Object will transition to IA after 60 days and later to deep archive after 365 days

    Example::

          let aBucket = new SecureBucket(mystack, 'secureBucket', {
            bucketName: 'mybucket',
            objectsExpireInDays: 500,
            enforceSSL: false,
           });
    '''

    def __init__(self, scope: _constructs_77d1e7e8.Construct, id: builtins.str) -> None:
        '''Creates the SecureBucket.

        :param scope: - the stack in which the construct is defined.
        :param id: - a unique identifier for the construct.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__908e4c242f627a2e004696fc9dbe99afa6a4112ac0e26b914170bfea97fc7fc7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])

    @jsii.member(jsii_name="accessLogsBucket")
    def access_logs_bucket(
        self,
        logs_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
    ) -> "SecureBucket":
        '''Will enable the access logs to the given bucket.

        :param logs_bucket: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ccfc3f6bd60df58bb7810e394c201fe635df2767a76adcfdd30a87b1f821d7b)
            check_type(argname="argument logs_bucket", value=logs_bucket, expected_type=type_hints["logs_bucket"])
        return typing.cast("SecureBucket", jsii.invoke(self, "accessLogsBucket", [logs_bucket]))

    @jsii.member(jsii_name="assemble")
    def assemble(self) -> "SecureBucket":
        '''Creates the underlying S3 bucket.'''
        return typing.cast("SecureBucket", jsii.invoke(self, "assemble", []))

    @jsii.member(jsii_name="bucketName")
    def bucket_name(self, name: builtins.str) -> "SecureBucket":
        '''The name of the bucket.

        Internally the bucket name will be modified to include the account and region.

        :param name: - the name of the bucket to use.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05ad85e4cdbe8d1a4cbe881e16b9abc01d7592c4fbf6a27a9cd06ebfa2992c0d)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("SecureBucket", jsii.invoke(self, "bucketName", [name]))

    @jsii.member(jsii_name="moveToGlacierDeepArchive")
    def move_to_glacier_deep_archive(
        self,
        move: typing.Optional[builtins.bool] = None,
    ) -> "SecureBucket":
        '''Use only for buckets that have archiving data.

        CAUTION, once the object is archived, a temporary bucket copy is needed to restore the data.

        :param move: -

        :default: false

        :return: SecureBucket
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__385f51ace5c56604c3705866b979d82d67f1112e15faa48b4d7490adf0fe2182)
            check_type(argname="argument move", value=move, expected_type=type_hints["move"])
        return typing.cast("SecureBucket", jsii.invoke(self, "moveToGlacierDeepArchive", [move]))

    @jsii.member(jsii_name="moveToGlacierInstantRetrieval")
    def move_to_glacier_instant_retrieval(
        self,
        move: typing.Optional[builtins.bool] = None,
    ) -> "SecureBucket":
        '''Use only for buckets that have archiving data.

        :param move: -

        :default: false

        :return: SecureBucket
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41a07b4dc22f8f19c599262439319cec99aeab5b86d259b1551d3d62ca00c05e)
            check_type(argname="argument move", value=move, expected_type=type_hints["move"])
        return typing.cast("SecureBucket", jsii.invoke(self, "moveToGlacierInstantRetrieval", [move]))

    @jsii.member(jsii_name="nonCurrentObjectsExpireInDays")
    def non_current_objects_expire_in_days(
        self,
        expiry_in_days: jsii.Number,
    ) -> "SecureBucket":
        '''The number of days that non current version of object will be kept.

        :param expiry_in_days: -

        :default: 90 days

        :return: SecureBucket
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b99889e8c8ea63918a0bc91f89e16239fbca36497a57daca7cbf301f2a4b301f)
            check_type(argname="argument expiry_in_days", value=expiry_in_days, expected_type=type_hints["expiry_in_days"])
        return typing.cast("SecureBucket", jsii.invoke(self, "nonCurrentObjectsExpireInDays", [expiry_in_days]))

    @jsii.member(jsii_name="objectsExpireInDays")
    def objects_expire_in_days(self, expiry_in_days: jsii.Number) -> "SecureBucket":
        '''The number of days that object will be kept.

        :param expiry_in_days: -

        :default: 3650 - 10 years

        :return: SecureBucket
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cd6f17f0446b65acf762c42683c8d61188c3ab03c4255e81be9306df2208e84)
            check_type(argname="argument expiry_in_days", value=expiry_in_days, expected_type=type_hints["expiry_in_days"])
        return typing.cast("SecureBucket", jsii.invoke(self, "objectsExpireInDays", [expiry_in_days]))

    @jsii.member(jsii_name="overrideBucketProperties")
    def override_bucket_properties(
        self,
        *,
        access_control: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketAccessControl] = None,
        auto_delete_objects: typing.Optional[builtins.bool] = None,
        block_public_access: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BlockPublicAccess] = None,
        bucket_key_enabled: typing.Optional[builtins.bool] = None,
        bucket_name: typing.Optional[builtins.str] = None,
        cors: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.CorsRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        encryption: typing.Optional[_aws_cdk_aws_s3_ceddda9d.BucketEncryption] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        enforce_ssl: typing.Optional[builtins.bool] = None,
        event_bridge_enabled: typing.Optional[builtins.bool] = None,
        intelligent_tiering_configurations: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.IntelligentTieringConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
        inventories: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.Inventory, typing.Dict[builtins.str, typing.Any]]]] = None,
        lifecycle_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.LifecycleRule, typing.Dict[builtins.str, typing.Any]]]] = None,
        metrics: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.BucketMetrics, typing.Dict[builtins.str, typing.Any]]]] = None,
        minimum_tls_version: typing.Optional[jsii.Number] = None,
        notifications_handler_role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        notifications_skip_destination_validation: typing.Optional[builtins.bool] = None,
        object_lock_default_retention: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectLockRetention] = None,
        object_lock_enabled: typing.Optional[builtins.bool] = None,
        object_ownership: typing.Optional[_aws_cdk_aws_s3_ceddda9d.ObjectOwnership] = None,
        public_read_access: typing.Optional[builtins.bool] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        server_access_logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
        server_access_logs_prefix: typing.Optional[builtins.str] = None,
        target_object_key_format: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TargetObjectKeyFormat] = None,
        transfer_acceleration: typing.Optional[builtins.bool] = None,
        transition_default_minimum_object_size: typing.Optional[_aws_cdk_aws_s3_ceddda9d.TransitionDefaultMinimumObjectSize] = None,
        versioned: typing.Optional[builtins.bool] = None,
        website_error_document: typing.Optional[builtins.str] = None,
        website_index_document: typing.Optional[builtins.str] = None,
        website_redirect: typing.Optional[typing.Union[_aws_cdk_aws_s3_ceddda9d.RedirectTarget, typing.Dict[builtins.str, typing.Any]]] = None,
        website_routing_rules: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_s3_ceddda9d.RoutingRule, typing.Dict[builtins.str, typing.Any]]]] = None,
    ) -> "SecureBucket":
        '''This function allows users to override the defaults calculated by this construct and is only recommended for advanced usecases.

        The values supplied via props superseeds the defaults that are calculated.

        :param access_control: Specifies a canned ACL that grants predefined permissions to the bucket. Default: BucketAccessControl.PRIVATE
        :param auto_delete_objects: Whether all objects should be automatically deleted when the bucket is removed from the stack or when the stack is deleted. Requires the ``removalPolicy`` to be set to ``RemovalPolicy.DESTROY``. **Warning** if you have deployed a bucket with ``autoDeleteObjects: true``, switching this to ``false`` in a CDK version *before* ``1.126.0`` will lead to all objects in the bucket being deleted. Be sure to update your bucket resources by deploying with CDK version ``1.126.0`` or later **before** switching this value to ``false``. Setting ``autoDeleteObjects`` to true on a bucket will add ``s3:PutBucketPolicy`` to the bucket policy. This is because during bucket deletion, the custom resource provider needs to update the bucket policy by adding a deny policy for ``s3:PutObject`` to prevent race conditions with external bucket writers. Default: false
        :param block_public_access: The block public access configuration of this bucket. Default: - CloudFormation defaults will apply. New buckets and objects don't allow public access, but users can modify bucket policies or object permissions to allow public access
        :param bucket_key_enabled: Whether Amazon S3 should use its own intermediary key to generate data keys. Only relevant when using KMS for encryption. - If not enabled, every object GET and PUT will cause an API call to KMS (with the attendant cost implications of that). - If enabled, S3 will use its own time-limited key instead. Only relevant, when Encryption is not set to ``BucketEncryption.UNENCRYPTED``. Default: - false
        :param bucket_name: Physical name of this bucket. Default: - Assigned by CloudFormation (recommended).
        :param cors: The CORS configuration of this bucket. Default: - No CORS configuration.
        :param encryption: The kind of server-side encryption to apply to this bucket. If you choose KMS, you can specify a KMS key via ``encryptionKey``. If encryption key is not specified, a key will automatically be created. Default: - ``KMS`` if ``encryptionKey`` is specified, or ``UNENCRYPTED`` otherwise. But if ``UNENCRYPTED`` is specified, the bucket will be encrypted as ``S3_MANAGED`` automatically.
        :param encryption_key: External KMS key to use for bucket encryption. The ``encryption`` property must be either not specified or set to ``KMS`` or ``DSSE``. An error will be emitted if ``encryption`` is set to ``UNENCRYPTED`` or ``S3_MANAGED``. Default: - If ``encryption`` is set to ``KMS`` and this property is undefined, a new KMS key will be created and associated with this bucket.
        :param enforce_ssl: Enforces SSL for requests. S3.5 of the AWS Foundational Security Best Practices Regarding S3. Default: false
        :param event_bridge_enabled: Whether this bucket should send notifications to Amazon EventBridge or not. Default: false
        :param intelligent_tiering_configurations: Inteligent Tiering Configurations. Default: No Intelligent Tiiering Configurations.
        :param inventories: The inventory configuration of the bucket. Default: - No inventory configuration
        :param lifecycle_rules: Rules that define how Amazon S3 manages objects during their lifetime. Default: - No lifecycle rules.
        :param metrics: The metrics configuration of this bucket. Default: - No metrics configuration.
        :param minimum_tls_version: Enforces minimum TLS version for requests. Requires ``enforceSSL`` to be enabled. Default: No minimum TLS version is enforced.
        :param notifications_handler_role: The role to be used by the notifications handler. Default: - a new role will be created.
        :param notifications_skip_destination_validation: Skips notification validation of Amazon SQS, Amazon SNS, and Lambda destinations. Default: false
        :param object_lock_default_retention: The default retention mode and rules for S3 Object Lock. Default retention can be configured after a bucket is created if the bucket already has object lock enabled. Enabling object lock for existing buckets is not supported. Default: no default retention period
        :param object_lock_enabled: Enable object lock on the bucket. Enabling object lock for existing buckets is not supported. Object lock must be enabled when the bucket is created. Default: false, unless objectLockDefaultRetention is set (then, true)
        :param object_ownership: The objectOwnership of the bucket. Default: - No ObjectOwnership configuration. By default, Amazon S3 sets Object Ownership to ``Bucket owner enforced``. This means ACLs are disabled and the bucket owner will own every object.
        :param public_read_access: Grants public read access to all objects in the bucket. Similar to calling ``bucket.grantPublicAccess()`` Default: false
        :param removal_policy: Policy to apply when the bucket is removed from this stack. Default: - The bucket will be orphaned.
        :param server_access_logs_bucket: Destination bucket for the server access logs. Default: - If "serverAccessLogsPrefix" undefined - access logs disabled, otherwise - log to current bucket.
        :param server_access_logs_prefix: Optional log file prefix to use for the bucket's access logs. If defined without "serverAccessLogsBucket", enables access logs to current bucket with this prefix. Default: - No log file prefix
        :param target_object_key_format: Optional key format for log objects. Default: - the default key format is: [DestinationPrefix][YYYY]-[MM]-[DD]-[hh]-[mm]-[ss]-[UniqueString]
        :param transfer_acceleration: Whether this bucket should have transfer acceleration turned on or not. Default: false
        :param transition_default_minimum_object_size: Indicates which default minimum object size behavior is applied to the lifecycle configuration. To customize the minimum object size for any transition you can add a filter that specifies a custom ``objectSizeGreaterThan`` or ``objectSizeLessThan`` for ``lifecycleRules`` property. Custom filters always take precedence over the default transition behavior. Default: - TransitionDefaultMinimumObjectSize.VARIES_BY_STORAGE_CLASS before September 2024, otherwise TransitionDefaultMinimumObjectSize.ALL_STORAGE_CLASSES_128_K.
        :param versioned: Whether this bucket should have versioning turned on or not. Default: false (unless object lock is enabled, then true)
        :param website_error_document: The name of the error document (e.g. "404.html") for the website. ``websiteIndexDocument`` must also be set if this is set. Default: - No error document.
        :param website_index_document: The name of the index document (e.g. "index.html") for the website. Enables static website hosting for this bucket. Default: - No index document.
        :param website_redirect: Specifies the redirect behavior of all requests to a website endpoint of a bucket. If you specify this property, you can't specify "websiteIndexDocument", "websiteErrorDocument" nor , "websiteRoutingRules". Default: - No redirection.
        :param website_routing_rules: Rules that define when a redirect is applied and the redirect behavior. Default: - No redirection rules.

        :return: SecureBucket
        '''
        props = _aws_cdk_aws_s3_ceddda9d.BucketProps(
            access_control=access_control,
            auto_delete_objects=auto_delete_objects,
            block_public_access=block_public_access,
            bucket_key_enabled=bucket_key_enabled,
            bucket_name=bucket_name,
            cors=cors,
            encryption=encryption,
            encryption_key=encryption_key,
            enforce_ssl=enforce_ssl,
            event_bridge_enabled=event_bridge_enabled,
            intelligent_tiering_configurations=intelligent_tiering_configurations,
            inventories=inventories,
            lifecycle_rules=lifecycle_rules,
            metrics=metrics,
            minimum_tls_version=minimum_tls_version,
            notifications_handler_role=notifications_handler_role,
            notifications_skip_destination_validation=notifications_skip_destination_validation,
            object_lock_default_retention=object_lock_default_retention,
            object_lock_enabled=object_lock_enabled,
            object_ownership=object_ownership,
            public_read_access=public_read_access,
            removal_policy=removal_policy,
            server_access_logs_bucket=server_access_logs_bucket,
            server_access_logs_prefix=server_access_logs_prefix,
            target_object_key_format=target_object_key_format,
            transfer_acceleration=transfer_acceleration,
            transition_default_minimum_object_size=transition_default_minimum_object_size,
            versioned=versioned,
            website_error_document=website_error_document,
            website_index_document=website_index_document,
            website_redirect=website_redirect,
            website_routing_rules=website_routing_rules,
        )

        return typing.cast("SecureBucket", jsii.invoke(self, "overrideBucketProperties", [props]))

    @jsii.member(jsii_name="restrictAccessToIpOrCidrs")
    def restrict_access_to_ip_or_cidrs(
        self,
        ips_or_cidrs: typing.Sequence[builtins.str],
    ) -> "SecureBucket":
        '''Adds access restrictions so that the access is allowed from the following IP ranges.

        :param ips_or_cidrs: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a445329aae83234eb25a7889436044ae72824479be7f6dd3a0dd43bb43e13f18)
            check_type(argname="argument ips_or_cidrs", value=ips_or_cidrs, expected_type=type_hints["ips_or_cidrs"])
        return typing.cast("SecureBucket", jsii.invoke(self, "restrictAccessToIpOrCidrs", [ips_or_cidrs]))

    @jsii.member(jsii_name="restrictAccessToVpcs")
    def restrict_access_to_vpcs(
        self,
        vpc_ids: typing.Sequence[builtins.str],
    ) -> "SecureBucket":
        '''Adds access restrictions so that the access is allowed from the following VPCs.

        :param vpc_ids: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9df2fc6a514b96d44abe5a4affe599356f0f6ed5ba8b2a76fda9f0f63e17182)
            check_type(argname="argument vpc_ids", value=vpc_ids, expected_type=type_hints["vpc_ids"])
        return typing.cast("SecureBucket", jsii.invoke(self, "restrictAccessToVpcs", [vpc_ids]))

    @jsii.member(jsii_name="restrictWritesToPaths")
    def restrict_writes_to_paths(
        self,
        dirs: typing.Sequence[builtins.str],
    ) -> "SecureBucket":
        '''Will only allow writes to the following path prefixes mentioned.

        :param dirs: , a list of path prefixes to allow.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c1f36bf4d3de6f150b4bafdb564c15b8a5f08088e92f67b625ae0bbe1f39285)
            check_type(argname="argument dirs", value=dirs, expected_type=type_hints["dirs"])
        return typing.cast("SecureBucket", jsii.invoke(self, "restrictWritesToPaths", [dirs]))

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket]:
        '''The underlying S3 bucket created by this construct.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_s3_ceddda9d.Bucket], jsii.get(self, "bucket"))


class SimpleCodebuildProject(
    EzConstruct,
    metaclass=jsii.JSIIMeta,
    jsii_type="ez-constructs.SimpleCodebuildProject",
):
    '''Most of the cases,a developer will use CodeBuild setup to perform simple CI tasks such as: - Build and test your code on a PR - Run a specific script based on a cron schedule.

    Also, they might want:

    - artifacts like testcase reports to be available via Reports UI and/or S3.
    - logs to be available via CloudWatch Logs.

    However, there can be additional organizational retention policies, for example retaining logs for a particular period of time.
    With this construct, you can easily create a basic CodeBuild project with many opinated defaults that are compliant with FISMA and NIST.

    Example, creates a project named ``my-project``, with artifacts going to my-project-artifacts--
    and logs going to ``/aws/codebuild/my-project`` log group with a retention period of 90 days and 14 months respectively::

          new SimpleCodebuildProject(stack, 'MyProject')
            .projectName('myproject')
            .gitRepoUrl('https://github.com/bijujoseph/cloudbiolinux.git')
            .gitBaseBranch('main')
            .triggerEvent(GitEvent.PULL_REQUEST)
            .buildSpecPath('buildspecs/my-pr-checker.yml')
            .assemble();
    '''

    def __init__(self, scope: _constructs_77d1e7e8.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a66fcdf6f2af25f3154e1a4b1df934ba9eff1e3f587a04803cc119aab6a986d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])

    @jsii.member(jsii_name="addEnv")
    def add_env(
        self,
        name: builtins.str,
        *,
        value: typing.Any,
        type: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironmentVariableType] = None,
    ) -> "SimpleCodebuildProject":
        '''A convenient way to set the project environment variables.

        The values set here will be presnted on the UI when build with overriding is used.

        :param name: - The environment variable name.
        :param value: The value of the environment variable. For plain-text variables (the default), this is the literal value of variable. For SSM parameter variables, pass the name of the parameter here (``parameterName`` property of ``IParameter``). For SecretsManager variables secrets, pass either the secret name (``secretName`` property of ``ISecret``) or the secret ARN (``secretArn`` property of ``ISecret``) here, along with optional SecretsManager qualifiers separated by ':', like the JSON key, or the version or stage (see https://docs.aws.amazon.com/codebuild/latest/userguide/build-spec-ref.html#build-spec.env.secrets-manager for details).
        :param type: The type of environment variable. Default: PlainText
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3733264320f290806ce522f27e6c23161f8f2f6da49f36230c02fe8ea66873a4)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        env_var = _aws_cdk_aws_codebuild_ceddda9d.BuildEnvironmentVariable(
            value=value, type=type
        )

        return typing.cast("SimpleCodebuildProject", jsii.invoke(self, "addEnv", [name, env_var]))

    @jsii.member(jsii_name="artifactBucket")
    def artifact_bucket(
        self,
        artifact_bucket: typing.Union[builtins.str, _aws_cdk_aws_s3_ceddda9d.IBucket],
    ) -> "SimpleCodebuildProject":
        '''The name of the bucket to store the artifacts.

        By default the buckets will get stored in ``<project-name>-artifacts`` bucket.
        This function can be used to ovrride the default behavior.

        :param artifact_bucket: - a valid existing Bucket reference or bucket name to use.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdc95533cf1c5cf2eab607fe9ba11252f53631e12a644443f836c8f9cf47a021)
            check_type(argname="argument artifact_bucket", value=artifact_bucket, expected_type=type_hints["artifact_bucket"])
        return typing.cast("SimpleCodebuildProject", jsii.invoke(self, "artifactBucket", [artifact_bucket]))

    @jsii.member(jsii_name="assemble")
    def assemble(
        self,
        *,
        artifacts: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IArtifacts] = None,
        secondary_artifacts: typing.Optional[typing.Sequence[_aws_cdk_aws_codebuild_ceddda9d.IArtifacts]] = None,
        secondary_sources: typing.Optional[typing.Sequence[_aws_cdk_aws_codebuild_ceddda9d.ISource]] = None,
        source: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.ISource] = None,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        badge: typing.Optional[builtins.bool] = None,
        build_spec: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.BuildSpec] = None,
        cache: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.Cache] = None,
        check_secrets_in_plain_text_env_variables: typing.Optional[builtins.bool] = None,
        concurrent_build_limit: typing.Optional[jsii.Number] = None,
        description: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        environment: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironmentVariable, typing.Dict[builtins.str, typing.Any]]]] = None,
        file_system_locations: typing.Optional[typing.Sequence[_aws_cdk_aws_codebuild_ceddda9d.IFileSystemLocation]] = None,
        grant_report_group_permissions: typing.Optional[builtins.bool] = None,
        logging: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        project_name: typing.Optional[builtins.str] = None,
        queued_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        ssm_session_permissions: typing.Optional[builtins.bool] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        visibility: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.ProjectVisibility] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> "SimpleCodebuildProject":
        '''
        :param artifacts: Defines where build artifacts will be stored. Could be: PipelineBuildArtifacts, NoArtifacts and S3Artifacts. Default: NoArtifacts
        :param secondary_artifacts: The secondary artifacts for the Project. Can also be added after the Project has been created by using the ``Project#addSecondaryArtifact`` method. Default: - No secondary artifacts.
        :param secondary_sources: The secondary sources for the Project. Can be also added after the Project has been created by using the ``Project#addSecondarySource`` method. Default: - No secondary sources.
        :param source: The source of the build. *Note*: if ``NoSource`` is given as the source, then you need to provide an explicit ``buildSpec``. Default: - NoSource
        :param allow_all_outbound: Whether to allow the CodeBuild to send all network traffic. If set to false, you must individually add traffic rules to allow the CodeBuild project to connect to network targets. Only used if 'vpc' is supplied. Default: true
        :param badge: Indicates whether AWS CodeBuild generates a publicly accessible URL for your project's build badge. For more information, see Build Badges Sample in the AWS CodeBuild User Guide. Default: false
        :param build_spec: Filename or contents of buildspec in JSON format. Default: - Empty buildspec.
        :param cache: Caching strategy to use. Default: Cache.none
        :param check_secrets_in_plain_text_env_variables: Whether to check for the presence of any secrets in the environment variables of the default type, BuildEnvironmentVariableType.PLAINTEXT. Since using a secret for the value of that kind of variable would result in it being displayed in plain text in the AWS Console, the construct will throw an exception if it detects a secret was passed there. Pass this property as false if you want to skip this validation, and keep using a secret in a plain text environment variable. Default: true
        :param concurrent_build_limit: Maximum number of concurrent builds. Minimum value is 1 and maximum is account build limit. Default: - no explicit limit is set
        :param description: A description of the project. Use the description to identify the purpose of the project. Default: - No description.
        :param encryption_key: Encryption key to use to read and write artifacts. Default: - The AWS-managed CMK for Amazon Simple Storage Service (Amazon S3) is used.
        :param environment: Build environment to use for the build. Default: BuildEnvironment.LinuxBuildImage.STANDARD_7_0
        :param environment_variables: Additional environment variables to add to the build environment. Default: - No additional environment variables are specified.
        :param file_system_locations: An ProjectFileSystemLocation objects for a CodeBuild build project. A ProjectFileSystemLocation object specifies the identifier, location, mountOptions, mountPoint, and type of a file system created using Amazon Elastic File System. Default: - no file system locations
        :param grant_report_group_permissions: Add permissions to this project's role to create and use test report groups with name starting with the name of this project. That is the standard report group that gets created when a simple name (in contrast to an ARN) is used in the 'reports' section of the buildspec of this project. This is usually harmless, but you can turn these off if you don't plan on using test reports in this project. Default: true
        :param logging: Information about logs for the build project. A project can create logs in Amazon CloudWatch Logs, an S3 bucket, or both. Default: - no log configuration is set
        :param project_name: The physical, human-readable name of the CodeBuild Project. Default: - Name is automatically generated.
        :param queued_timeout: The number of minutes after which AWS CodeBuild stops the build if it's still in queue. For valid values, see the timeoutInMinutes field in the AWS CodeBuild User Guide. Default: - no queue timeout is set
        :param role: Service Role to assume while running the build. Default: - A role will be created.
        :param security_groups: What security group to associate with the codebuild project's network interfaces. If no security group is identified, one will be created automatically. Only used if 'vpc' is supplied. Default: - Security group will be automatically created.
        :param ssm_session_permissions: Add the permissions necessary for debugging builds with SSM Session Manager. If the following prerequisites have been met: - The necessary permissions have been added by setting this flag to true. - The build image has the SSM agent installed (true for default CodeBuild images). - The build is started with `debugSessionEnabled <https://docs.aws.amazon.com/codebuild/latest/APIReference/API_StartBuild.html#CodeBuild-StartBuild-request-debugSessionEnabled>`_ set to true. Then the build container can be paused and inspected using Session Manager by invoking the ``codebuild-breakpoint`` command somewhere during the build. ``codebuild-breakpoint`` commands will be ignored if the build is not started with ``debugSessionEnabled=true``. Default: false
        :param subnet_selection: Where to place the network interfaces within the VPC. To access AWS services, your CodeBuild project needs to be in one of the following types of subnets: 1. Subnets with access to the internet (of type PRIVATE_WITH_EGRESS). 2. Private subnets unconnected to the internet, but with `VPC endpoints <https://docs.aws.amazon.com/codebuild/latest/userguide/use-vpc-endpoints-with-codebuild.html>`_ for the necessary services. If you don't specify a subnet selection, the default behavior is to use PRIVATE_WITH_EGRESS subnets first if they exist, then PRIVATE_WITHOUT_EGRESS, and finally PUBLIC subnets. If your VPC doesn't have PRIVATE_WITH_EGRESS subnets but you need AWS service access, add VPC Endpoints to your private subnets. Default: - private subnets if available else public subnets
        :param timeout: The number of minutes after which AWS CodeBuild stops the build if it's not complete. For valid values, see the timeoutInMinutes field in the AWS CodeBuild User Guide. Default: Duration.hours(1)
        :param visibility: Specifies the visibility of the project's builds. Default: - no visibility is set
        :param vpc: VPC network to place codebuild network interfaces. Specify this if the codebuild project needs to access resources in a VPC. Default: - No VPC is specified.
        '''
        default_props = _aws_cdk_aws_codebuild_ceddda9d.ProjectProps(
            artifacts=artifacts,
            secondary_artifacts=secondary_artifacts,
            secondary_sources=secondary_sources,
            source=source,
            allow_all_outbound=allow_all_outbound,
            badge=badge,
            build_spec=build_spec,
            cache=cache,
            check_secrets_in_plain_text_env_variables=check_secrets_in_plain_text_env_variables,
            concurrent_build_limit=concurrent_build_limit,
            description=description,
            encryption_key=encryption_key,
            environment=environment,
            environment_variables=environment_variables,
            file_system_locations=file_system_locations,
            grant_report_group_permissions=grant_report_group_permissions,
            logging=logging,
            project_name=project_name,
            queued_timeout=queued_timeout,
            role=role,
            security_groups=security_groups,
            ssm_session_permissions=ssm_session_permissions,
            subnet_selection=subnet_selection,
            timeout=timeout,
            visibility=visibility,
            vpc=vpc,
        )

        return typing.cast("SimpleCodebuildProject", jsii.invoke(self, "assemble", [default_props]))

    @jsii.member(jsii_name="buildImage")
    def build_image(
        self,
        build_image: _aws_cdk_aws_codebuild_ceddda9d.IBuildImage,
    ) -> "SimpleCodebuildProject":
        '''The build image to use.

        :param build_image: -

        :see: https://docs.aws.amazon.com/cdk/api/v1/docs/@aws-cdk_aws-codebuild.IBuildImage.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cf56db7e7ceadd109b72955351f50aa4ade48fd0defb958d11bf0f86b40ea3f)
            check_type(argname="argument build_image", value=build_image, expected_type=type_hints["build_image"])
        return typing.cast("SimpleCodebuildProject", jsii.invoke(self, "buildImage", [build_image]))

    @jsii.member(jsii_name="buildSpecPath")
    def build_spec_path(
        self,
        build_spec_path: builtins.str,
    ) -> "SimpleCodebuildProject":
        '''The build spec file path.

        :param build_spec_path: - relative location of the build spec file.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1bb98c3cfc225986b950e6f83f0e796b4a823a143028aedc3b930054e71514d)
            check_type(argname="argument build_spec_path", value=build_spec_path, expected_type=type_hints["build_spec_path"])
        return typing.cast("SimpleCodebuildProject", jsii.invoke(self, "buildSpecPath", [build_spec_path]))

    @jsii.member(jsii_name="computeType")
    def compute_type(
        self,
        compute_type: _aws_cdk_aws_codebuild_ceddda9d.ComputeType,
    ) -> "SimpleCodebuildProject":
        '''The compute type to use.

        :param compute_type: -

        :see: https://docs.aws.amazon.com/codebuild/latest/userguide/build-env-ref-compute-types.html
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2cd9097c8359b9f10b12297798c0fb088fd2bbf92300417ac595d9d2f1033cb)
            check_type(argname="argument compute_type", value=compute_type, expected_type=type_hints["compute_type"])
        return typing.cast("SimpleCodebuildProject", jsii.invoke(self, "computeType", [compute_type]))

    @jsii.member(jsii_name="ecrBuildImage")
    def ecr_build_image(
        self,
        ecr_repo_name: builtins.str,
        image_tag: builtins.str,
    ) -> "SimpleCodebuildProject":
        '''The build image to use.

        :param ecr_repo_name: - the ecr repository name.
        :param image_tag: - the image tag.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa9f0b42fab79908b5cac6faf51d6b3eab50111ac8cf2227689fff40dc06b3bf)
            check_type(argname="argument ecr_repo_name", value=ecr_repo_name, expected_type=type_hints["ecr_repo_name"])
            check_type(argname="argument image_tag", value=image_tag, expected_type=type_hints["image_tag"])
        return typing.cast("SimpleCodebuildProject", jsii.invoke(self, "ecrBuildImage", [ecr_repo_name, image_tag]))

    @jsii.member(jsii_name="filterByGithubUserIds")
    def filter_by_github_user_ids(
        self,
        user_ids: typing.Sequence[jsii.Number],
    ) -> "SimpleCodebuildProject":
        '''Filter webhook events by GitHub user IDs.

        :param user_ids: - array of GitHub user IDs (not usernames, but id values).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__827464ea6e67ad493e29dc006a79f18bbfd78c047fbb3c05c8521c7e9682c1fb)
            check_type(argname="argument user_ids", value=user_ids, expected_type=type_hints["user_ids"])
        return typing.cast("SimpleCodebuildProject", jsii.invoke(self, "filterByGithubUserIds", [user_ids]))

    @jsii.member(jsii_name="gitBaseBranch")
    def git_base_branch(self, branch: builtins.str) -> "SimpleCodebuildProject":
        '''The main branch of the github project.

        :param branch: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c95f063a065ad74e68c7ae6e353999d36d70da844c234c01d1eae907d50ac116)
            check_type(argname="argument branch", value=branch, expected_type=type_hints["branch"])
        return typing.cast("SimpleCodebuildProject", jsii.invoke(self, "gitBaseBranch", [branch]))

    @jsii.member(jsii_name="gitRepoUrl")
    def git_repo_url(self, git_repo_url: builtins.str) -> "SimpleCodebuildProject":
        '''The github or enterprise github repository url.

        :param git_repo_url: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff9fa5a15e686d115ee6fc23bb85d6942edfd12793e7d8cdfb51b12c7bd91d58)
            check_type(argname="argument git_repo_url", value=git_repo_url, expected_type=type_hints["git_repo_url"])
        return typing.cast("SimpleCodebuildProject", jsii.invoke(self, "gitRepoUrl", [git_repo_url]))

    @jsii.member(jsii_name="inVpc")
    def in_vpc(self, vpc_id: builtins.str) -> "SimpleCodebuildProject":
        '''The vpc network interfaces to add to the codebuild.

        :param vpc_id: -

        :see: https://docs.aws.amazon.com/cdk/api/v1/docs/aws-codebuild-readme.html#definition-of-vpc-configuration-in-codebuild-project
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__457187e968eb632c4dc3501b812b4f38e0dbe9a0ba3ce22b6deca7c3e3f550ea)
            check_type(argname="argument vpc_id", value=vpc_id, expected_type=type_hints["vpc_id"])
        return typing.cast("SimpleCodebuildProject", jsii.invoke(self, "inVpc", [vpc_id]))

    @jsii.member(jsii_name="overrideProjectProps")
    def override_project_props(
        self,
        *,
        artifacts: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.IArtifacts] = None,
        secondary_artifacts: typing.Optional[typing.Sequence[_aws_cdk_aws_codebuild_ceddda9d.IArtifacts]] = None,
        secondary_sources: typing.Optional[typing.Sequence[_aws_cdk_aws_codebuild_ceddda9d.ISource]] = None,
        source: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.ISource] = None,
        allow_all_outbound: typing.Optional[builtins.bool] = None,
        badge: typing.Optional[builtins.bool] = None,
        build_spec: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.BuildSpec] = None,
        cache: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.Cache] = None,
        check_secrets_in_plain_text_env_variables: typing.Optional[builtins.bool] = None,
        concurrent_build_limit: typing.Optional[jsii.Number] = None,
        description: typing.Optional[builtins.str] = None,
        encryption_key: typing.Optional[_aws_cdk_aws_kms_ceddda9d.IKey] = None,
        environment: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironment, typing.Dict[builtins.str, typing.Any]]] = None,
        environment_variables: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironmentVariable, typing.Dict[builtins.str, typing.Any]]]] = None,
        file_system_locations: typing.Optional[typing.Sequence[_aws_cdk_aws_codebuild_ceddda9d.IFileSystemLocation]] = None,
        grant_report_group_permissions: typing.Optional[builtins.bool] = None,
        logging: typing.Optional[typing.Union[_aws_cdk_aws_codebuild_ceddda9d.LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        project_name: typing.Optional[builtins.str] = None,
        queued_timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        ssm_session_permissions: typing.Optional[builtins.bool] = None,
        subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        visibility: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.ProjectVisibility] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    ) -> "SimpleCodebuildProject":
        '''
        :param artifacts: Defines where build artifacts will be stored. Could be: PipelineBuildArtifacts, NoArtifacts and S3Artifacts. Default: NoArtifacts
        :param secondary_artifacts: The secondary artifacts for the Project. Can also be added after the Project has been created by using the ``Project#addSecondaryArtifact`` method. Default: - No secondary artifacts.
        :param secondary_sources: The secondary sources for the Project. Can be also added after the Project has been created by using the ``Project#addSecondarySource`` method. Default: - No secondary sources.
        :param source: The source of the build. *Note*: if ``NoSource`` is given as the source, then you need to provide an explicit ``buildSpec``. Default: - NoSource
        :param allow_all_outbound: Whether to allow the CodeBuild to send all network traffic. If set to false, you must individually add traffic rules to allow the CodeBuild project to connect to network targets. Only used if 'vpc' is supplied. Default: true
        :param badge: Indicates whether AWS CodeBuild generates a publicly accessible URL for your project's build badge. For more information, see Build Badges Sample in the AWS CodeBuild User Guide. Default: false
        :param build_spec: Filename or contents of buildspec in JSON format. Default: - Empty buildspec.
        :param cache: Caching strategy to use. Default: Cache.none
        :param check_secrets_in_plain_text_env_variables: Whether to check for the presence of any secrets in the environment variables of the default type, BuildEnvironmentVariableType.PLAINTEXT. Since using a secret for the value of that kind of variable would result in it being displayed in plain text in the AWS Console, the construct will throw an exception if it detects a secret was passed there. Pass this property as false if you want to skip this validation, and keep using a secret in a plain text environment variable. Default: true
        :param concurrent_build_limit: Maximum number of concurrent builds. Minimum value is 1 and maximum is account build limit. Default: - no explicit limit is set
        :param description: A description of the project. Use the description to identify the purpose of the project. Default: - No description.
        :param encryption_key: Encryption key to use to read and write artifacts. Default: - The AWS-managed CMK for Amazon Simple Storage Service (Amazon S3) is used.
        :param environment: Build environment to use for the build. Default: BuildEnvironment.LinuxBuildImage.STANDARD_7_0
        :param environment_variables: Additional environment variables to add to the build environment. Default: - No additional environment variables are specified.
        :param file_system_locations: An ProjectFileSystemLocation objects for a CodeBuild build project. A ProjectFileSystemLocation object specifies the identifier, location, mountOptions, mountPoint, and type of a file system created using Amazon Elastic File System. Default: - no file system locations
        :param grant_report_group_permissions: Add permissions to this project's role to create and use test report groups with name starting with the name of this project. That is the standard report group that gets created when a simple name (in contrast to an ARN) is used in the 'reports' section of the buildspec of this project. This is usually harmless, but you can turn these off if you don't plan on using test reports in this project. Default: true
        :param logging: Information about logs for the build project. A project can create logs in Amazon CloudWatch Logs, an S3 bucket, or both. Default: - no log configuration is set
        :param project_name: The physical, human-readable name of the CodeBuild Project. Default: - Name is automatically generated.
        :param queued_timeout: The number of minutes after which AWS CodeBuild stops the build if it's still in queue. For valid values, see the timeoutInMinutes field in the AWS CodeBuild User Guide. Default: - no queue timeout is set
        :param role: Service Role to assume while running the build. Default: - A role will be created.
        :param security_groups: What security group to associate with the codebuild project's network interfaces. If no security group is identified, one will be created automatically. Only used if 'vpc' is supplied. Default: - Security group will be automatically created.
        :param ssm_session_permissions: Add the permissions necessary for debugging builds with SSM Session Manager. If the following prerequisites have been met: - The necessary permissions have been added by setting this flag to true. - The build image has the SSM agent installed (true for default CodeBuild images). - The build is started with `debugSessionEnabled <https://docs.aws.amazon.com/codebuild/latest/APIReference/API_StartBuild.html#CodeBuild-StartBuild-request-debugSessionEnabled>`_ set to true. Then the build container can be paused and inspected using Session Manager by invoking the ``codebuild-breakpoint`` command somewhere during the build. ``codebuild-breakpoint`` commands will be ignored if the build is not started with ``debugSessionEnabled=true``. Default: false
        :param subnet_selection: Where to place the network interfaces within the VPC. To access AWS services, your CodeBuild project needs to be in one of the following types of subnets: 1. Subnets with access to the internet (of type PRIVATE_WITH_EGRESS). 2. Private subnets unconnected to the internet, but with `VPC endpoints <https://docs.aws.amazon.com/codebuild/latest/userguide/use-vpc-endpoints-with-codebuild.html>`_ for the necessary services. If you don't specify a subnet selection, the default behavior is to use PRIVATE_WITH_EGRESS subnets first if they exist, then PRIVATE_WITHOUT_EGRESS, and finally PUBLIC subnets. If your VPC doesn't have PRIVATE_WITH_EGRESS subnets but you need AWS service access, add VPC Endpoints to your private subnets. Default: - private subnets if available else public subnets
        :param timeout: The number of minutes after which AWS CodeBuild stops the build if it's not complete. For valid values, see the timeoutInMinutes field in the AWS CodeBuild User Guide. Default: Duration.hours(1)
        :param visibility: Specifies the visibility of the project's builds. Default: - no visibility is set
        :param vpc: VPC network to place codebuild network interfaces. Specify this if the codebuild project needs to access resources in a VPC. Default: - No VPC is specified.
        '''
        props = _aws_cdk_aws_codebuild_ceddda9d.ProjectProps(
            artifacts=artifacts,
            secondary_artifacts=secondary_artifacts,
            secondary_sources=secondary_sources,
            source=source,
            allow_all_outbound=allow_all_outbound,
            badge=badge,
            build_spec=build_spec,
            cache=cache,
            check_secrets_in_plain_text_env_variables=check_secrets_in_plain_text_env_variables,
            concurrent_build_limit=concurrent_build_limit,
            description=description,
            encryption_key=encryption_key,
            environment=environment,
            environment_variables=environment_variables,
            file_system_locations=file_system_locations,
            grant_report_group_permissions=grant_report_group_permissions,
            logging=logging,
            project_name=project_name,
            queued_timeout=queued_timeout,
            role=role,
            security_groups=security_groups,
            ssm_session_permissions=ssm_session_permissions,
            subnet_selection=subnet_selection,
            timeout=timeout,
            visibility=visibility,
            vpc=vpc,
        )

        return typing.cast("SimpleCodebuildProject", jsii.invoke(self, "overrideProjectProps", [props]))

    @jsii.member(jsii_name="privileged")
    def privileged(self, p: builtins.bool) -> "SimpleCodebuildProject":
        '''Set privileged mode of execution.

        Usually needed if this project builds Docker images,
        and the build environment image you chose is not provided by CodeBuild with Docker support.
        By default, Docker containers do not allow access to any devices.
        Privileged mode grants a build project's Docker container access to all devices
        https://docs.aws.amazon.com/codebuild/latest/userguide/change-project-console.html#change-project-console-environment

        :param p: - true/false.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49a1de8fe00c26dbdd5f0353f96b074e2154998cb331e299fb76a9a1a2bc4919)
            check_type(argname="argument p", value=p, expected_type=type_hints["p"])
        return typing.cast("SimpleCodebuildProject", jsii.invoke(self, "privileged", [p]))

    @jsii.member(jsii_name="projectDescription")
    def project_description(
        self,
        project_description: builtins.str,
    ) -> "SimpleCodebuildProject":
        '''The description of the codebuild project.

        :param project_description: - a valid description string.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3cec20d71b6e66d417a7cbbf29f4582feb6048ded9c9a511d16e02645e8bed25)
            check_type(argname="argument project_description", value=project_description, expected_type=type_hints["project_description"])
        return typing.cast("SimpleCodebuildProject", jsii.invoke(self, "projectDescription", [project_description]))

    @jsii.member(jsii_name="projectName")
    def project_name(self, project_name: builtins.str) -> "SimpleCodebuildProject":
        '''The name of the codebuild project.

        :param project_name: - a valid name string.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47c7b8991f69deb3dce291d9511e8c90ad87a5c51470a6a7dc10efb61019d78f)
            check_type(argname="argument project_name", value=project_name, expected_type=type_hints["project_name"])
        return typing.cast("SimpleCodebuildProject", jsii.invoke(self, "projectName", [project_name]))

    @jsii.member(jsii_name="skipArtifacts")
    def skip_artifacts(self, skip: builtins.bool) -> "SimpleCodebuildProject":
        '''If set, will skip artifact creation.

        :param skip: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e37747562d9f082cf7c617861f9aeee59885ac9c2a9a21689e7099223585635)
            check_type(argname="argument skip", value=skip, expected_type=type_hints["skip"])
        return typing.cast("SimpleCodebuildProject", jsii.invoke(self, "skipArtifacts", [skip]))

    @jsii.member(jsii_name="triggerBuildOnGitEvent")
    def trigger_build_on_git_event(self, event: GitEvent) -> "SimpleCodebuildProject":
        '''The Github events that can trigger this build.

        :param event: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d751bc8805262cceaff1945b81da131bd1b279a3e8970c0bfffcaa08d1a9518)
            check_type(argname="argument event", value=event, expected_type=type_hints["event"])
        return typing.cast("SimpleCodebuildProject", jsii.invoke(self, "triggerBuildOnGitEvent", [event]))

    @jsii.member(jsii_name="triggerBuildOnSchedule")
    def trigger_build_on_schedule(
        self,
        schedule: _aws_cdk_aws_events_ceddda9d.Schedule,
    ) -> "SimpleCodebuildProject":
        '''The cron schedule on which this build gets triggerd.

        :param schedule: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70a2d54e99153d760066833565fc99621b594db93de0feeee3bd192a25a7cd90)
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
        return typing.cast("SimpleCodebuildProject", jsii.invoke(self, "triggerBuildOnSchedule", [schedule]))

    @jsii.member(jsii_name="triggerOnPushToBranches")
    def trigger_on_push_to_branches(
        self,
        branches: typing.Sequence[builtins.str],
    ) -> "SimpleCodebuildProject":
        '''Triggers build on push to specified branches.

        :param branches: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__371ef1a2fffc32327bc9a3d0ae0bb69ceb73341de5c1a9bc545eb466594723b5)
            check_type(argname="argument branches", value=branches, expected_type=type_hints["branches"])
        return typing.cast("SimpleCodebuildProject", jsii.invoke(self, "triggerOnPushToBranches", [branches]))

    @builtins.property
    @jsii.member(jsii_name="project")
    def project(self) -> typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.Project]:
        '''The underlying codebuild project that is created by this construct.'''
        return typing.cast(typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.Project], jsii.get(self, "project"))


class SimpleServerlessApplication(
    EzConstruct,
    metaclass=jsii.JSIIMeta,
    jsii_type="ez-constructs.SimpleServerlessApplication",
):
    def __init__(self, scope: _constructs_77d1e7e8.Construct, id: builtins.str) -> None:
        '''
        :param scope: -
        :param id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__427d21faf66ae413b27d0e2f557322e765c3cce7e4c69da95fc958226eaa47d6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        jsii.create(self.__class__, self, [scope, id])

    @jsii.member(jsii_name="assemble")
    def assemble(
        self,
        *,
        release_label: builtins.str,
        type: builtins.str,
        architecture: typing.Optional[builtins.str] = None,
        auto_start_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStartConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        auto_stop_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.AutoStopConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        image_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ImageConfigurationInputProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        initial_capacity: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.InitialCapacityConfigKeyValuePairProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
        interactive_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.InteractiveConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        maximum_capacity: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.MaximumAllowedResourcesProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        monitoring_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.MonitoringConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        name: typing.Optional[builtins.str] = None,
        network_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.NetworkConfigurationProperty, typing.Dict[builtins.str, typing.Any]]]] = None,
        runtime_configuration: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Sequence[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.ConfigurationObjectProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
        tags: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_ceddda9d.CfnTag, typing.Dict[builtins.str, typing.Any]]]] = None,
        worker_type_specifications: typing.Optional[typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Mapping[builtins.str, typing.Union[_aws_cdk_ceddda9d.IResolvable, typing.Union[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication.WorkerTypeSpecificationInputProperty, typing.Dict[builtins.str, typing.Any]]]]]] = None,
    ) -> "SimpleServerlessApplication":
        '''
        :param release_label: The EMR release associated with the application.
        :param type: The type of application, such as Spark or Hive.
        :param architecture: The CPU architecture of an application.
        :param auto_start_configuration: The configuration for an application to automatically start on job submission.
        :param auto_stop_configuration: The configuration for an application to automatically stop after a certain amount of time being idle.
        :param image_configuration: The image configuration applied to all worker types.
        :param initial_capacity: The initial capacity of the application.
        :param interactive_configuration: The interactive configuration object that enables the interactive use cases for an application.
        :param maximum_capacity: The maximum capacity of the application. This is cumulative across all workers at any given point in time during the lifespan of the application is created. No new resources will be created once any one of the defined limits is hit.
        :param monitoring_configuration: A configuration specification to be used when provisioning an application. A configuration consists of a classification, properties, and optional nested configurations. A classification refers to an application-specific configuration file. Properties are the settings you want to change in that file.
        :param name: The name of the application.
        :param network_configuration: The network configuration for customer VPC connectivity for the application.
        :param runtime_configuration: The `Configuration <https://docs.aws.amazon.com/emr-serverless/latest/APIReference/API_Configuration.html>`_ specifications of an application. Each configuration consists of a classification and properties. You use this parameter when creating or updating an application. To see the runtimeConfiguration object of an application, run the `GetApplication <https://docs.aws.amazon.com/emr-serverless/latest/APIReference/API_GetApplication.html>`_ API operation.
        :param tags: The tags assigned to the application.
        :param worker_type_specifications: The specification applied to each worker type.
        '''
        props = _aws_cdk_aws_emrserverless_ceddda9d.CfnApplicationProps(
            release_label=release_label,
            type=type,
            architecture=architecture,
            auto_start_configuration=auto_start_configuration,
            auto_stop_configuration=auto_stop_configuration,
            image_configuration=image_configuration,
            initial_capacity=initial_capacity,
            interactive_configuration=interactive_configuration,
            maximum_capacity=maximum_capacity,
            monitoring_configuration=monitoring_configuration,
            name=name,
            network_configuration=network_configuration,
            runtime_configuration=runtime_configuration,
            tags=tags,
            worker_type_specifications=worker_type_specifications,
        )

        return typing.cast("SimpleServerlessApplication", jsii.invoke(self, "assemble", [props]))

    @jsii.member(jsii_name="name")
    def name(self, name: builtins.str) -> "SimpleServerlessApplication":
        '''
        :param name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1190a3eae1024d413f1acb261e579683fcaec9bc111ce45f59fe7da637340213)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("SimpleServerlessApplication", jsii.invoke(self, "name", [name]))

    @jsii.member(jsii_name="skipDashboard")
    def skip_dashboard(self, skip: builtins.bool) -> "SimpleServerlessApplication":
        '''
        :param skip: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2162d4a42d79e188e22d80088c6cc8ab767afca08881b610a8869ef88e8145a0)
            check_type(argname="argument skip", value=skip, expected_type=type_hints["skip"])
        return typing.cast("SimpleServerlessApplication", jsii.invoke(self, "skipDashboard", [skip]))

    @jsii.member(jsii_name="vpc")
    def vpc(
        self,
        v: typing.Union[builtins.str, _aws_cdk_aws_ec2_ceddda9d.IVpc],
    ) -> "SimpleServerlessApplication":
        '''
        :param v: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f93562d5a720e1137f8348db81d5a1237148340f3170ec32684ce8aff87f5b75)
            check_type(argname="argument v", value=v, expected_type=type_hints["v"])
        return typing.cast("SimpleServerlessApplication", jsii.invoke(self, "vpc", [v]))

    @builtins.property
    @jsii.member(jsii_name="application")
    def application(
        self,
    ) -> typing.Optional[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication]:
        return typing.cast(typing.Optional[_aws_cdk_aws_emrserverless_ceddda9d.CfnApplication], jsii.get(self, "application"))


class SimpleStepFunction(
    EzConstruct,
    metaclass=jsii.JSIIMeta,
    jsii_type="ez-constructs.SimpleStepFunction",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        step_function_name: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param step_function_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__809b0993ca7d88030c00cec2bb9a1b67194e98b952735763ba9ac91b5404e4e3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument step_function_name", value=step_function_name, expected_type=type_hints["step_function_name"])
        jsii.create(self.__class__, self, [scope, id, step_function_name])

    @jsii.member(jsii_name="addPolicy")
    def add_policy(
        self,
        policy: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
    ) -> "SimpleStepFunction":
        '''
        :param policy: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea9cc5c805fdc9d028560daae6dc5363527edf8061cc52db2cb2c6daa598d9d5)
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
        return typing.cast("SimpleStepFunction", jsii.invoke(self, "addPolicy", [policy]))

    @jsii.member(jsii_name="assemble")
    def assemble(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        definition: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IChainable] = None,
        definition_body: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.DefinitionBody] = None,
        definition_substitutions: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        encryption_configuration: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.EncryptionConfiguration] = None,
        logs: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.LogOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        state_machine_type: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.StateMachineType] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        tracing_enabled: typing.Optional[builtins.bool] = None,
    ) -> "SimpleStepFunction":
        '''Assembles the state machine.

        :param comment: Comment that describes this state machine. Default: - No comment
        :param definition: (deprecated) Definition for this state machine.
        :param definition_body: Definition for this state machine.
        :param definition_substitutions: substitutions for the definition body as a key-value map.
        :param encryption_configuration: Configures server-side encryption of the state machine definition and execution history. Default: - data is transparently encrypted using an AWS owned key
        :param logs: Defines what execution history events are logged and where they are logged. Default: No logging
        :param removal_policy: The removal policy to apply to state machine. Default: RemovalPolicy.DESTROY
        :param role: The execution role for the state machine service. Default: A role is automatically created
        :param state_machine_name: A name for the state machine. Default: A name is automatically generated
        :param state_machine_type: Type of the state machine. Default: StateMachineType.STANDARD
        :param timeout: Maximum run time for this state machine. Default: No timeout
        :param tracing_enabled: Specifies whether Amazon X-Ray tracing is enabled for this state machine. Default: false
        '''
        state_machine_props = _aws_cdk_aws_stepfunctions_ceddda9d.StateMachineProps(
            comment=comment,
            definition=definition,
            definition_body=definition_body,
            definition_substitutions=definition_substitutions,
            encryption_configuration=encryption_configuration,
            logs=logs,
            removal_policy=removal_policy,
            role=role,
            state_machine_name=state_machine_name,
            state_machine_type=state_machine_type,
            timeout=timeout,
            tracing_enabled=tracing_enabled,
        )

        return typing.cast("SimpleStepFunction", jsii.invoke(self, "assemble", [state_machine_props]))

    @jsii.member(jsii_name="createDefaultStateMachineProps")
    def create_default_state_machine_props(
        self,
        state_machine_name: builtins.str,
        state_machine_role: _aws_cdk_aws_iam_ceddda9d.IRole,
        definition_body: _aws_cdk_aws_stepfunctions_ceddda9d.DefinitionBody,
        log_group: _aws_cdk_aws_logs_ceddda9d.ILogGroup,
    ) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachineProps:
        '''
        :param state_machine_name: -
        :param state_machine_role: -
        :param definition_body: -
        :param log_group: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6dca9fe60b24cc62a5003cc57b490bf818bed86bb1473755fcc59f39d404dfd5)
            check_type(argname="argument state_machine_name", value=state_machine_name, expected_type=type_hints["state_machine_name"])
            check_type(argname="argument state_machine_role", value=state_machine_role, expected_type=type_hints["state_machine_role"])
            check_type(argname="argument definition_body", value=definition_body, expected_type=type_hints["definition_body"])
            check_type(argname="argument log_group", value=log_group, expected_type=type_hints["log_group"])
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachineProps, jsii.invoke(self, "createDefaultStateMachineProps", [state_machine_name, state_machine_role, definition_body, log_group]))

    @jsii.member(jsii_name="createStateMachine")
    def create_state_machine(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        definition: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IChainable] = None,
        definition_body: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.DefinitionBody] = None,
        definition_substitutions: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        encryption_configuration: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.EncryptionConfiguration] = None,
        logs: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.LogOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        state_machine_type: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.StateMachineType] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        tracing_enabled: typing.Optional[builtins.bool] = None,
    ) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        '''Creates state machine from the given props.

        :param comment: Comment that describes this state machine. Default: - No comment
        :param definition: (deprecated) Definition for this state machine.
        :param definition_body: Definition for this state machine.
        :param definition_substitutions: substitutions for the definition body as a key-value map.
        :param encryption_configuration: Configures server-side encryption of the state machine definition and execution history. Default: - data is transparently encrypted using an AWS owned key
        :param logs: Defines what execution history events are logged and where they are logged. Default: No logging
        :param removal_policy: The removal policy to apply to state machine. Default: RemovalPolicy.DESTROY
        :param role: The execution role for the state machine service. Default: A role is automatically created
        :param state_machine_name: A name for the state machine. Default: A name is automatically generated
        :param state_machine_type: Type of the state machine. Default: StateMachineType.STANDARD
        :param timeout: Maximum run time for this state machine. Default: No timeout
        :param tracing_enabled: Specifies whether Amazon X-Ray tracing is enabled for this state machine. Default: false
        '''
        state_machine_props = _aws_cdk_aws_stepfunctions_ceddda9d.StateMachineProps(
            comment=comment,
            definition=definition,
            definition_body=definition_body,
            definition_substitutions=definition_substitutions,
            encryption_configuration=encryption_configuration,
            logs=logs,
            removal_policy=removal_policy,
            role=role,
            state_machine_name=state_machine_name,
            state_machine_type=state_machine_type,
            timeout=timeout,
            tracing_enabled=tracing_enabled,
        )

        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, jsii.invoke(self, "createStateMachine", [state_machine_props]))

    @jsii.member(jsii_name="createStateMachineCloudWatchLogGroup")
    def create_state_machine_cloud_watch_log_group(
        self,
    ) -> _aws_cdk_aws_logs_ceddda9d.ILogGroup:
        '''creates bucket to store state machine logs.'''
        return typing.cast(_aws_cdk_aws_logs_ceddda9d.ILogGroup, jsii.invoke(self, "createStateMachineCloudWatchLogGroup", []))

    @jsii.member(jsii_name="createStateMachineRole")
    def create_state_machine_role(
        self,
        state_machine_name: builtins.str,
    ) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        '''creates state machine role.

        :param state_machine_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f744e545b5472206ad09a260929339a79c09e0386cb900e85e8e6db5531492d6)
            check_type(argname="argument state_machine_name", value=state_machine_name, expected_type=type_hints["state_machine_name"])
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.invoke(self, "createStateMachineRole", [state_machine_name]))

    @jsii.member(jsii_name="generateDefaultStateMachinePermissions")
    def generate_default_state_machine_permissions(self) -> None:
        '''Will add default permissions to the step function role.'''
        return typing.cast(None, jsii.invoke(self, "generateDefaultStateMachinePermissions", []))

    @jsii.member(jsii_name="grantPassRole")
    def grant_pass_role(
        self,
        role: _aws_cdk_aws_iam_ceddda9d.IRole,
    ) -> "SimpleStepFunction":
        '''Grants pass role permissions to the state machine role.

        :param role: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5794489b9545219391ee33d07a3d1cc85541a08e3a21f1be46946e09db39ec24)
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
        return typing.cast("SimpleStepFunction", jsii.invoke(self, "grantPassRole", [role]))

    @jsii.member(jsii_name="logGroupName")
    def log_group_name(self, value: builtins.str) -> "SimpleStepFunction":
        '''Sets the logGroupName.

        :param value: - name of the log group.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab1d87a2e6e162b4005a10e397a06a6be863dcb7d01b3c6344093fe6dbbf27e9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast("SimpleStepFunction", jsii.invoke(self, "logGroupName", [value]))

    @jsii.member(jsii_name="modifyStateDefinition")
    def modify_state_definition(self, state_def: builtins.str) -> builtins.str:
        '''Modifies the supplied state definition string version of workflow defintion to include logging and tracing.

        :param state_def: - the state definition string.

        :private: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddff48b19cc2a3d965da83997f8cecab103e7717fa75bb40c8b58963278a0442)
            check_type(argname="argument state_def", value=state_def, expected_type=type_hints["state_def"])
        return typing.cast(builtins.str, jsii.invoke(self, "modifyStateDefinition", [state_def]))

    @jsii.member(jsii_name="usingChainableDefinition")
    def using_chainable_definition(
        self,
        state_definition: _aws_cdk_aws_stepfunctions_ceddda9d.IChainable,
    ) -> "SimpleStepFunction":
        '''
        :param state_definition: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a14e530fc3421406403716945cb2dfde68f33c10ac739e1558433fd0e344343)
            check_type(argname="argument state_definition", value=state_definition, expected_type=type_hints["state_definition"])
        return typing.cast("SimpleStepFunction", jsii.invoke(self, "usingChainableDefinition", [state_definition]))

    @jsii.member(jsii_name="usingStringDefinition")
    def using_string_definition(
        self,
        state_definition: builtins.str,
    ) -> "SimpleStepFunction":
        '''
        :param state_definition: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c09f391c332d571a8ef9f82c8d9e5677dd6bf151620bc802fd1ddac7fd67348e)
            check_type(argname="argument state_definition", value=state_definition, expected_type=type_hints["state_definition"])
        return typing.cast("SimpleStepFunction", jsii.invoke(self, "usingStringDefinition", [state_definition]))

    @jsii.member(jsii_name="withDefaultInputs")
    def with_default_inputs(self, params: typing.Any) -> "SimpleStepFunction":
        '''Default inputs of the spark jobs.

        Example:::

           .withDefaultInputs({
               "SparkSubmitParameters": {
                 "--conf spark.executor.memory=2g",
                 "--conf spark.executor.cores=2"
               },
               "greetings": "Good morning",
               "personal": {
                 "name": "John Doe",
                 "age": 30
               }
            })

        :param params: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1671fd3716e92b0696491c21e3f02b82aef16753581387acf8b3bfd9dfc9526f)
            check_type(argname="argument params", value=params, expected_type=type_hints["params"])
        return typing.cast("SimpleStepFunction", jsii.invoke(self, "withDefaultInputs", [params]))

    @builtins.property
    @jsii.member(jsii_name="account")
    def account(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "account"))

    @builtins.property
    @jsii.member(jsii_name="defaultInputs")
    def default_inputs(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "defaultInputs"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="policies")
    def policies(self) -> typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]:
        return typing.cast(typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement], jsii.get(self, "policies"))

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @builtins.property
    @jsii.member(jsii_name="scope")
    def scope(self) -> _constructs_77d1e7e8.Construct:
        return typing.cast(_constructs_77d1e7e8.Construct, jsii.get(self, "scope"))

    @builtins.property
    @jsii.member(jsii_name="stateDefinitionAsString")
    def state_definition_as_string(self) -> builtins.str:
        '''Returns the state definition as a string if the original state definition used was string.

        Otherwise returns empty string.
        '''
        return typing.cast(builtins.str, jsii.get(self, "stateDefinitionAsString"))

    @builtins.property
    @jsii.member(jsii_name="stateDefinitionBody")
    def state_definition_body(
        self,
    ) -> _aws_cdk_aws_stepfunctions_ceddda9d.DefinitionBody:
        '''Returns the state definition body object.'''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.DefinitionBody, jsii.get(self, "stateDefinitionBody"))

    @builtins.property
    @jsii.member(jsii_name="stateMachine")
    def state_machine(self) -> _aws_cdk_aws_stepfunctions_ceddda9d.StateMachine:
        '''The state machine instance created by this construct.'''
        return typing.cast(_aws_cdk_aws_stepfunctions_ceddda9d.StateMachine, jsii.get(self, "stateMachine"))

    @builtins.property
    @jsii.member(jsii_name="stateMachineRole")
    def state_machine_role(self) -> _aws_cdk_aws_iam_ceddda9d.IRole:
        return typing.cast(_aws_cdk_aws_iam_ceddda9d.IRole, jsii.get(self, "stateMachineRole"))

    @builtins.property
    @jsii.member(jsii_name="stateDefinition")
    def state_definition(
        self,
    ) -> typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable]:
        '''Sets the state definition, and if type of the value passed is a string, will also set the stateDefinition when it is a string.'''
        return typing.cast(typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable], jsii.get(self, "stateDefinition"))

    @state_definition.setter
    def state_definition(
        self,
        value: typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0d5878650df6939dfdda6e68598c3471d4f40c91c9dda0dc8f3a088391421c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stateDefinition", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="ez-constructs.StandardSparkSubmitJobTemplate",
    jsii_struct_bases=[],
    name_mapping={
        "entry_point": "entryPoint",
        "job_name": "jobName",
        "application_configuration": "applicationConfiguration",
        "enable_monitoring": "enableMonitoring",
        "entry_point_argument_names": "entryPointArgumentNames",
        "main_class": "mainClass",
        "spark_submit_parameters": "sparkSubmitParameters",
    },
)
class StandardSparkSubmitJobTemplate:
    def __init__(
        self,
        *,
        entry_point: builtins.str,
        job_name: builtins.str,
        application_configuration: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.ApplicationConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
        enable_monitoring: typing.Optional[builtins.bool] = None,
        entry_point_argument_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        main_class: typing.Optional[builtins.str] = None,
        spark_submit_parameters: typing.Optional[builtins.str] = None,
    ) -> None:
        '''A standard spark submit job template.

        :param entry_point: The S3 URL of the spark application's main file in Amazon S3. A jar file for Scala and Java Spark applications and a Python file for pySpark applications.
        :param job_name: The name of the job.*required*.
        :param application_configuration: Any version of overrides to use while provisioning EMR job.
        :param enable_monitoring: True if monitoring must be enabled. Defaults to true.
        :param entry_point_argument_names: The names of the arguments to pass to the application. The actual argument value should be specified during step funciton execution time.
        :param main_class: The name of the application's main class,only applicable for Java/Scala Spark applications.
        :param spark_submit_parameters: The arguments to pass to the application.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__134b4b55d02ec5ddf5e27369b51284d729f389ace4861fe8e19cf717678b3293)
            check_type(argname="argument entry_point", value=entry_point, expected_type=type_hints["entry_point"])
            check_type(argname="argument job_name", value=job_name, expected_type=type_hints["job_name"])
            check_type(argname="argument application_configuration", value=application_configuration, expected_type=type_hints["application_configuration"])
            check_type(argname="argument enable_monitoring", value=enable_monitoring, expected_type=type_hints["enable_monitoring"])
            check_type(argname="argument entry_point_argument_names", value=entry_point_argument_names, expected_type=type_hints["entry_point_argument_names"])
            check_type(argname="argument main_class", value=main_class, expected_type=type_hints["main_class"])
            check_type(argname="argument spark_submit_parameters", value=spark_submit_parameters, expected_type=type_hints["spark_submit_parameters"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "entry_point": entry_point,
            "job_name": job_name,
        }
        if application_configuration is not None:
            self._values["application_configuration"] = application_configuration
        if enable_monitoring is not None:
            self._values["enable_monitoring"] = enable_monitoring
        if entry_point_argument_names is not None:
            self._values["entry_point_argument_names"] = entry_point_argument_names
        if main_class is not None:
            self._values["main_class"] = main_class
        if spark_submit_parameters is not None:
            self._values["spark_submit_parameters"] = spark_submit_parameters

    @builtins.property
    def entry_point(self) -> builtins.str:
        '''The S3 URL of the spark application's main file in Amazon S3.

        A jar file for Scala and Java Spark applications and a Python file for pySpark applications.
        '''
        result = self._values.get("entry_point")
        assert result is not None, "Required property 'entry_point' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def job_name(self) -> builtins.str:
        '''The name of the job.*required*.'''
        result = self._values.get("job_name")
        assert result is not None, "Required property 'job_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def application_configuration(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.ApplicationConfiguration]]:
        '''Any version of overrides to use while provisioning EMR job.'''
        result = self._values.get("application_configuration")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.ApplicationConfiguration]], result)

    @builtins.property
    def enable_monitoring(self) -> typing.Optional[builtins.bool]:
        '''True if monitoring must be enabled.

        Defaults to true.
        '''
        result = self._values.get("enable_monitoring")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def entry_point_argument_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The names of the arguments to pass to the application.

        The actual argument value should be specified during step funciton execution time.
        '''
        result = self._values.get("entry_point_argument_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def main_class(self) -> typing.Optional[builtins.str]:
        '''The name of the application's main class,only applicable for Java/Scala Spark applications.'''
        result = self._values.get("main_class")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spark_submit_parameters(self) -> typing.Optional[builtins.str]:
        '''The arguments to pass to the application.'''
        result = self._values.get("spark_submit_parameters")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StandardSparkSubmitJobTemplate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Utils(metaclass=jsii.JSIIMeta, jsii_type="ez-constructs.Utils"):
    '''A utility class that have common functions.'''

    def __init__(self) -> None:
        jsii.create(self.__class__, self, [])

    @jsii.member(jsii_name="appendIfNecessary")
    @builtins.classmethod
    def append_if_necessary(
        cls,
        name: builtins.str,
        *suffixes: builtins.str,
    ) -> builtins.str:
        '''Will append the suffix to the given name if the name do not contain the suffix.

        :param name: - a string.
        :param suffixes: - the string to append.

        :return: the name with the suffix appended if necessary delimited by a hyphen
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab7d624c4b17ae5798d2698454d6664a420296e02d5be3d3594785bdcecf3128)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument suffixes", value=suffixes, expected_type=typing.Tuple[type_hints["suffixes"], ...]) # pyright: ignore [reportGeneralTypeIssues]
        return typing.cast(builtins.str, jsii.sinvoke(cls, "appendIfNecessary", [name, *suffixes]))

    @jsii.member(jsii_name="camelCase")
    @builtins.classmethod
    def camel_case(cls, str: builtins.str) -> builtins.str:
        '''Will convert the given string to camel case.

        :param str: - a string.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9987188fc354940a8663ace12af8640d76d87148b14d9d1d356e29d9bfb0741)
            check_type(argname="argument str", value=str, expected_type=type_hints["str"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "camelCase", [str]))

    @jsii.member(jsii_name="contains")
    @builtins.classmethod
    def contains(cls, str: builtins.str, s: builtins.str) -> builtins.bool:
        '''Will check if the given string is contained in another string.

        :param str: - a string.
        :param s: - the string to check for.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f74143e8140659067393d5758eceff773c35ac52f0e6a2496cbf8d7795b9a68)
            check_type(argname="argument str", value=str, expected_type=type_hints["str"])
            check_type(argname="argument s", value=s, expected_type=type_hints["s"])
        return typing.cast(builtins.bool, jsii.sinvoke(cls, "contains", [str, s]))

    @jsii.member(jsii_name="endsWith")
    @builtins.classmethod
    def ends_with(cls, str: builtins.str, s: builtins.str) -> builtins.bool:
        '''Will check if the given string ends with the given suffix.

        :param str: - a string.
        :param s: - suffix to check.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2992ae92902d8b81668ae7355ad4ea4ac8db2b07a12cd50a42be7f9e50929264)
            check_type(argname="argument str", value=str, expected_type=type_hints["str"])
            check_type(argname="argument s", value=s, expected_type=type_hints["s"])
        return typing.cast(builtins.bool, jsii.sinvoke(cls, "endsWith", [str, s]))

    @jsii.member(jsii_name="escapeDoubleQuotes")
    @builtins.classmethod
    def escape_double_quotes(cls, str: builtins.str) -> builtins.str:
        '''Will escape double quotes in the given string.

        :param str: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57d21adeb89a229e698b88368d71ea6c45cf66ed53f7b9d127e4a0084a35988e)
            check_type(argname="argument str", value=str, expected_type=type_hints["str"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "escapeDoubleQuotes", [str]))

    @jsii.member(jsii_name="fetchStepFuncitonStateDefinition")
    @builtins.classmethod
    def fetch_step_funciton_state_definition(
        cls,
        stack: _aws_cdk_ceddda9d.Stack,
    ) -> typing.Any:
        '''A utility function that will obtain the first state machine definition from the given stack.

        :param stack: - a stack that contains at least one state machine resource.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55fcfa0db2550eb7697a6ce5cd81370ec17688b1a7dc8581c4c04306276bb146)
            check_type(argname="argument stack", value=stack, expected_type=type_hints["stack"])
        return typing.cast(typing.Any, jsii.sinvoke(cls, "fetchStepFuncitonStateDefinition", [stack]))

    @jsii.member(jsii_name="isEmpty")
    @builtins.classmethod
    def is_empty(cls, value: typing.Any = None) -> builtins.bool:
        '''Will check if the given object is empty.

        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__350c5bb98e107eee6ee21ce2e7e012972cbae0b757a37bd6ee1f5e66025eec9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(builtins.bool, jsii.sinvoke(cls, "isEmpty", [value]))

    @jsii.member(jsii_name="join")
    @builtins.classmethod
    def join(
        cls,
        arr: typing.Optional[typing.Sequence[builtins.str]] = None,
        separator: typing.Optional[builtins.str] = None,
    ) -> builtins.str:
        '''joins a string array using the given seperator.

        :param arr: -
        :param separator: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3ac8da41f19d2a59abdf352ae94a21e2dda439f4d6a34e879f4e6228f1603a6)
            check_type(argname="argument arr", value=arr, expected_type=type_hints["arr"])
            check_type(argname="argument separator", value=separator, expected_type=type_hints["separator"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "join", [arr, separator]))

    @jsii.member(jsii_name="kebabCase")
    @builtins.classmethod
    def kebab_case(cls, str: builtins.str) -> builtins.str:
        '''Will convert the given string to lower case and transform any spaces to hyphens.

        :param str: - a string.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0e4526132686dd17a76cbc5266bbd91f6ff16cdccfd3fd6245f1061a6ff514d)
            check_type(argname="argument str", value=str, expected_type=type_hints["str"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "kebabCase", [str]))

    @jsii.member(jsii_name="merge")
    @builtins.classmethod
    def merge(cls, obj1: typing.Any, obj2: typing.Any) -> typing.Any:
        '''Merges two objects.

        :param obj1: -
        :param obj2: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db5d559c708a0d9516ae8ba3a450d3980c4ab8174f25a21bf74c78da5460a09d)
            check_type(argname="argument obj1", value=obj1, expected_type=type_hints["obj1"])
            check_type(argname="argument obj2", value=obj2, expected_type=type_hints["obj2"])
        return typing.cast(typing.Any, jsii.sinvoke(cls, "merge", [obj1, obj2]))

    @jsii.member(jsii_name="parseGithubUrl")
    @builtins.classmethod
    def parse_github_url(cls, url: builtins.str) -> typing.Any:
        '''Splits a given Github URL and extracts the owner and repo name.

        :param url: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a691b7ad10e5308aff51aa2082dc54b2a1b1cc77ade0cae68b1ecf78fba856a)
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
        return typing.cast(typing.Any, jsii.sinvoke(cls, "parseGithubUrl", [url]))

    @jsii.member(jsii_name="prettyPrintStack")
    @builtins.classmethod
    def pretty_print_stack(
        cls,
        stack: _aws_cdk_ceddda9d.Stack,
        persist: typing.Optional[builtins.bool] = None,
        path: typing.Optional[builtins.str] = None,
    ) -> None:
        '''A utility function that will print the content of a CDK stack.

        :param stack: - a valid stack.
        :param persist: -
        :param path: -

        :warning: This function is only used for debugging purpose.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e64ebb7228e613203bd98f40a1ff8cfe6b40703167a883bb3f0a0c727a79d2e7)
            check_type(argname="argument stack", value=stack, expected_type=type_hints["stack"])
            check_type(argname="argument persist", value=persist, expected_type=type_hints["persist"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
        return typing.cast(None, jsii.sinvoke(cls, "prettyPrintStack", [stack, persist, path]))

    @jsii.member(jsii_name="startsWith")
    @builtins.classmethod
    def starts_with(cls, str: builtins.str, s: builtins.str) -> builtins.bool:
        '''Will check if the given string starts with the given prefix.

        :param str: - a string.
        :param s: - the prefix to check.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4503a468a48cac5f6781501429a0ca70194cff93e94a9f9c1b72e64161ff096f)
            check_type(argname="argument str", value=str, expected_type=type_hints["str"])
            check_type(argname="argument s", value=s, expected_type=type_hints["s"])
        return typing.cast(builtins.bool, jsii.sinvoke(cls, "startsWith", [str, s]))

    @jsii.member(jsii_name="suppressNagRule")
    @builtins.classmethod
    def suppress_nag_rule(
        cls,
        scope: _constructs_77d1e7e8.IConstruct,
        rule_id: builtins.str,
        reason: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Will disable the CDK NAG rule for the given construct and its children.

        :param scope: - the scope to disable the rule for.
        :param rule_id: - the rule id to disable.
        :param reason: - reason for disabling the rule.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2d5b06f249e7a0f41e6e205451860c1add18aeaa6bef4e833f655e2b1694860)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument rule_id", value=rule_id, expected_type=type_hints["rule_id"])
            check_type(argname="argument reason", value=reason, expected_type=type_hints["reason"])
        return typing.cast(None, jsii.sinvoke(cls, "suppressNagRule", [scope, rule_id, reason]))

    @jsii.member(jsii_name="wrap")
    @builtins.classmethod
    def wrap(cls, str: builtins.str, delimiter: builtins.str) -> builtins.str:
        '''Will wrap the given string using the given delimiter.

        :param str: - the string to wrap.
        :param delimiter: - the delimiter to use.

        :return: the wrapped string
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8335787277838180e459986b4f0f134fb3f147e37b0038a91887173bd63c7ecc)
            check_type(argname="argument str", value=str, expected_type=type_hints["str"])
            check_type(argname="argument delimiter", value=delimiter, expected_type=type_hints["delimiter"])
        return typing.cast(builtins.str, jsii.sinvoke(cls, "wrap", [str, delimiter]))


class SimpleServerlessSparkJob(
    SimpleStepFunction,
    metaclass=jsii.JSIIMeta,
    jsii_type="ez-constructs.SimpleServerlessSparkJob",
):
    '''This construct will create a Step function workflow that can submit spark job.

    If you utilize the

    :see:

    StandardSparkSubmitJobTemplate. *  The ``usingDefinition`` method will take care of capturing variables, like ``entryPoint``, ``mainClass`` etc .
    By default the step function during execution utilize those variable values as default.
    It is quite common that the JAR files used for the spark job may be different. To address that, 'EntryPoint``and``SparkSubmitParameters` variables are externalized and can be overriden during execution::

    new SimpleServerlessSparkJob(mystack, 'SingleFly', 'MyTestETL)
    .jobRole('delegatedadmin/developer/blames-emr-serverless-job-role')
    .applicationId('12345676')
    .logBucket('mylogbucket-name')
    .usingDefinition({
    jobName: 'mytestjob',
    entryPoint: 's3://aws-cms-amg-qpp-costscoring-artifact-dev-222224444433-us-east-1/biju_test_files/myspark-assembly.jar',
    mainClass: 'serverless.SimpleSparkApp',
    enableMonitoring: true,
    })
    .assemble();

    Having seen the above simple example, let us look at a more elaborate example, where the step function workflow is complex.
    It is possible to author the step function workflow JSON file and provide it as a string to the ``usingDefinition`` method::

    new SimpleServerlessSparkJob(mystackObj, 'MultiFly', 'MyAwesomeETL)
    .jobRole('delegatedadmin/developer/blames-emr-serverless-job-role')
    .applicationId('12345676')
    .logBucket('mylogbucket-name')
    .usingDefinition("{...json step function string.... }")
    .assemble();

    If we have to read differnent input parameters for the spark job, we can have variables that extract values from the context::

    new SimpleServerlessSparkJob(mystackObj, 'MultiFly')
    .name('MyAwesomeETL')
    .jobRole('delegatedadmin/developer/blames-emr-serverless-job-role')
    .applicationId('12345676')
    .logBucket('mylogbucket-name')
    .usingDefinition("{...json step function string.... }")
    .withDefaultInputs({"some":"thing", "other": "thing"})
    .assemble();

    Example::

        There are many instances where an ETL job may only have a single spark job. In such cases, you can use the
    '''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        step_function_name: builtins.str,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param step_function_name: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__964efb3914fb0773ef4ac64364b720ab9c3806f11f7062b828774bd33732cc4d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument step_function_name", value=step_function_name, expected_type=type_hints["step_function_name"])
        jsii.create(self.__class__, self, [scope, id, step_function_name])

    @jsii.member(jsii_name="applicationId")
    def application_id(
        self,
        applicaiton_id: builtins.str,
    ) -> "SimpleServerlessSparkJob":
        '''The serverless application ID, and to that application the jobs will be submitted.

        :param applicaiton_id: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__400ac1a0064811c360f0c863f9ce36aa974beeae0f960dc8f2f6bae816a5fa79)
            check_type(argname="argument applicaiton_id", value=applicaiton_id, expected_type=type_hints["applicaiton_id"])
        return typing.cast("SimpleServerlessSparkJob", jsii.invoke(self, "applicationId", [applicaiton_id]))

    @jsii.member(jsii_name="assemble")
    def assemble(
        self,
        *,
        comment: typing.Optional[builtins.str] = None,
        definition: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.IChainable] = None,
        definition_body: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.DefinitionBody] = None,
        definition_substitutions: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        encryption_configuration: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.EncryptionConfiguration] = None,
        logs: typing.Optional[typing.Union[_aws_cdk_aws_stepfunctions_ceddda9d.LogOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        role: typing.Optional[_aws_cdk_aws_iam_ceddda9d.IRole] = None,
        state_machine_name: typing.Optional[builtins.str] = None,
        state_machine_type: typing.Optional[_aws_cdk_aws_stepfunctions_ceddda9d.StateMachineType] = None,
        timeout: typing.Optional[_aws_cdk_ceddda9d.Duration] = None,
        tracing_enabled: typing.Optional[builtins.bool] = None,
    ) -> SimpleStepFunction:
        '''Assembles the state machine.

        :param comment: Comment that describes this state machine. Default: - No comment
        :param definition: (deprecated) Definition for this state machine.
        :param definition_body: Definition for this state machine.
        :param definition_substitutions: substitutions for the definition body as a key-value map.
        :param encryption_configuration: Configures server-side encryption of the state machine definition and execution history. Default: - data is transparently encrypted using an AWS owned key
        :param logs: Defines what execution history events are logged and where they are logged. Default: No logging
        :param removal_policy: The removal policy to apply to state machine. Default: RemovalPolicy.DESTROY
        :param role: The execution role for the state machine service. Default: A role is automatically created
        :param state_machine_name: A name for the state machine. Default: A name is automatically generated
        :param state_machine_type: Type of the state machine. Default: StateMachineType.STANDARD
        :param timeout: Maximum run time for this state machine. Default: No timeout
        :param tracing_enabled: Specifies whether Amazon X-Ray tracing is enabled for this state machine. Default: false
        '''
        state_machine_props = _aws_cdk_aws_stepfunctions_ceddda9d.StateMachineProps(
            comment=comment,
            definition=definition,
            definition_body=definition_body,
            definition_substitutions=definition_substitutions,
            encryption_configuration=encryption_configuration,
            logs=logs,
            removal_policy=removal_policy,
            role=role,
            state_machine_name=state_machine_name,
            state_machine_type=state_machine_type,
            timeout=timeout,
            tracing_enabled=tracing_enabled,
        )

        return typing.cast(SimpleStepFunction, jsii.invoke(self, "assemble", [state_machine_props]))

    @jsii.member(jsii_name="generateDefaultStateMachinePermissions")
    def generate_default_state_machine_permissions(self) -> None:
        '''Will add default permisisons to the step function role.'''
        return typing.cast(None, jsii.invoke(self, "generateDefaultStateMachinePermissions", []))

    @jsii.member(jsii_name="jobRole")
    def job_role(self, name: builtins.str) -> "SimpleServerlessSparkJob":
        '''The role the spark job will assume while executing jobs in EMR.

        :param name: - a qualified name including the path. e.g. ``path/to/roleName``
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f93a27b16e83ed876915b3202828f273e27791ab40f9b2bd3ae0d6a9e10142d3)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        return typing.cast("SimpleServerlessSparkJob", jsii.invoke(self, "jobRole", [name]))

    @jsii.member(jsii_name="logBucket")
    def log_bucket(
        self,
        bucket: typing.Union[builtins.str, _aws_cdk_aws_s3_ceddda9d.IBucket],
    ) -> "SimpleServerlessSparkJob":
        '''A bucket to store the logs producee by the Spark jobs.

        :param bucket: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb8f8278f452b81473475aa06ba97c026c76ae212582ec51af529678e3227f39)
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
        return typing.cast("SimpleServerlessSparkJob", jsii.invoke(self, "logBucket", [bucket]))

    @jsii.member(jsii_name="modifyStateDefinition")
    def modify_state_definition(self, a_def: builtins.str) -> builtins.str:
        '''Modifies the supplied state definition string version of workflow defintion to include logging and tracing.

        :param a_def: - the state definition string.

        :private: true
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdec246523bddaa90a758dd76d3888d182090115b2f5598f8b38c3c55c1b007d)
            check_type(argname="argument a_def", value=a_def, expected_type=type_hints["a_def"])
        return typing.cast(builtins.str, jsii.invoke(self, "modifyStateDefinition", [a_def]))

    @jsii.member(jsii_name="usingSparkJobTemplate")
    def using_spark_job_template(
        self,
        *,
        entry_point: builtins.str,
        job_name: builtins.str,
        application_configuration: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.ApplicationConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
        enable_monitoring: typing.Optional[builtins.bool] = None,
        entry_point_argument_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        main_class: typing.Optional[builtins.str] = None,
        spark_submit_parameters: typing.Optional[builtins.str] = None,
    ) -> "SimpleServerlessSparkJob":
        '''Will create a state definition object based on the supplied StandardSparkSubmitJobTemplate object.

        :param entry_point: The S3 URL of the spark application's main file in Amazon S3. A jar file for Scala and Java Spark applications and a Python file for pySpark applications.
        :param job_name: The name of the job.*required*.
        :param application_configuration: Any version of overrides to use while provisioning EMR job.
        :param enable_monitoring: True if monitoring must be enabled. Defaults to true.
        :param entry_point_argument_names: The names of the arguments to pass to the application. The actual argument value should be specified during step funciton execution time.
        :param main_class: The name of the application's main class,only applicable for Java/Scala Spark applications.
        :param spark_submit_parameters: The arguments to pass to the application.
        '''
        spark_job_template = StandardSparkSubmitJobTemplate(
            entry_point=entry_point,
            job_name=job_name,
            application_configuration=application_configuration,
            enable_monitoring=enable_monitoring,
            entry_point_argument_names=entry_point_argument_names,
            main_class=main_class,
            spark_submit_parameters=spark_submit_parameters,
        )

        return typing.cast("SimpleServerlessSparkJob", jsii.invoke(self, "usingSparkJobTemplate", [spark_job_template]))

    @builtins.property
    @jsii.member(jsii_name="replacerLambdaFn")
    def replacer_lambda_fn(self) -> _aws_cdk_aws_lambda_ceddda9d.SingletonFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.SingletonFunction, jsii.get(self, "replacerLambdaFn"))

    @builtins.property
    @jsii.member(jsii_name="validatorLambdaFn")
    def validator_lambda_fn(self) -> _aws_cdk_aws_lambda_ceddda9d.SingletonFunction:
        return typing.cast(_aws_cdk_aws_lambda_ceddda9d.SingletonFunction, jsii.get(self, "validatorLambdaFn"))


__all__ = [
    "CustomSynthesizer",
    "EzConstruct",
    "FileUtils",
    "GitEvent",
    "PermissionsBoundaryAspect",
    "SecureBucket",
    "SimpleCodebuildProject",
    "SimpleServerlessApplication",
    "SimpleServerlessSparkJob",
    "SimpleStepFunction",
    "StandardSparkSubmitJobTemplate",
    "Utils",
]

publication.publish()

def _typecheckingstub__4f080045a2d1faf66d212813fbca2f476c782734821039529b5317ec84381ea0(
    role_path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fdbf166d776c14fb424ae19c70a3dd70710fd6ab1b72891c40c48c6bf133669(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7314fbbf5bb43741eaf334764ec86040d581a9f15dd42b8b0170d8dd0bab1e80(
    path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e21146239f529d4c7c7573ff7851541b6758a3373877082ded397d2b42f7191b(
    role_path: builtins.str,
    role_permission_boundary: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7536cb2f448fe953474186dc0747e81f4d8f437faec613ad0a8043185cb2e13a(
    role_resource: _aws_cdk_aws_iam_ceddda9d.CfnRole,
    stack: _aws_cdk_ceddda9d.Stack,
    skip_boundary: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e22d8b07bcff8691c4b3e0419e521f885cbcdc51a7ee4787a7d6d0c199db0c73(
    node: _constructs_77d1e7e8.IConstruct,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8cd0f21c19e2033b3e7c69c2b0a81c07accb873a289c961a3d7df6dd2e442bf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__546fd68c81f3db699e725f4e6c53647bf8bf3f2b58c323bb577c2708a254b991(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__908e4c242f627a2e004696fc9dbe99afa6a4112ac0e26b914170bfea97fc7fc7(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ccfc3f6bd60df58bb7810e394c201fe635df2767a76adcfdd30a87b1f821d7b(
    logs_bucket: _aws_cdk_aws_s3_ceddda9d.IBucket,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05ad85e4cdbe8d1a4cbe881e16b9abc01d7592c4fbf6a27a9cd06ebfa2992c0d(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__385f51ace5c56604c3705866b979d82d67f1112e15faa48b4d7490adf0fe2182(
    move: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41a07b4dc22f8f19c599262439319cec99aeab5b86d259b1551d3d62ca00c05e(
    move: typing.Optional[builtins.bool] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b99889e8c8ea63918a0bc91f89e16239fbca36497a57daca7cbf301f2a4b301f(
    expiry_in_days: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cd6f17f0446b65acf762c42683c8d61188c3ab03c4255e81be9306df2208e84(
    expiry_in_days: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a445329aae83234eb25a7889436044ae72824479be7f6dd3a0dd43bb43e13f18(
    ips_or_cidrs: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9df2fc6a514b96d44abe5a4affe599356f0f6ed5ba8b2a76fda9f0f63e17182(
    vpc_ids: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c1f36bf4d3de6f150b4bafdb564c15b8a5f08088e92f67b625ae0bbe1f39285(
    dirs: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a66fcdf6f2af25f3154e1a4b1df934ba9eff1e3f587a04803cc119aab6a986d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3733264320f290806ce522f27e6c23161f8f2f6da49f36230c02fe8ea66873a4(
    name: builtins.str,
    *,
    value: typing.Any,
    type: typing.Optional[_aws_cdk_aws_codebuild_ceddda9d.BuildEnvironmentVariableType] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdc95533cf1c5cf2eab607fe9ba11252f53631e12a644443f836c8f9cf47a021(
    artifact_bucket: typing.Union[builtins.str, _aws_cdk_aws_s3_ceddda9d.IBucket],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cf56db7e7ceadd109b72955351f50aa4ade48fd0defb958d11bf0f86b40ea3f(
    build_image: _aws_cdk_aws_codebuild_ceddda9d.IBuildImage,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1bb98c3cfc225986b950e6f83f0e796b4a823a143028aedc3b930054e71514d(
    build_spec_path: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2cd9097c8359b9f10b12297798c0fb088fd2bbf92300417ac595d9d2f1033cb(
    compute_type: _aws_cdk_aws_codebuild_ceddda9d.ComputeType,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa9f0b42fab79908b5cac6faf51d6b3eab50111ac8cf2227689fff40dc06b3bf(
    ecr_repo_name: builtins.str,
    image_tag: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__827464ea6e67ad493e29dc006a79f18bbfd78c047fbb3c05c8521c7e9682c1fb(
    user_ids: typing.Sequence[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c95f063a065ad74e68c7ae6e353999d36d70da844c234c01d1eae907d50ac116(
    branch: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff9fa5a15e686d115ee6fc23bb85d6942edfd12793e7d8cdfb51b12c7bd91d58(
    git_repo_url: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__457187e968eb632c4dc3501b812b4f38e0dbe9a0ba3ce22b6deca7c3e3f550ea(
    vpc_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49a1de8fe00c26dbdd5f0353f96b074e2154998cb331e299fb76a9a1a2bc4919(
    p: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cec20d71b6e66d417a7cbbf29f4582feb6048ded9c9a511d16e02645e8bed25(
    project_description: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47c7b8991f69deb3dce291d9511e8c90ad87a5c51470a6a7dc10efb61019d78f(
    project_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e37747562d9f082cf7c617861f9aeee59885ac9c2a9a21689e7099223585635(
    skip: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d751bc8805262cceaff1945b81da131bd1b279a3e8970c0bfffcaa08d1a9518(
    event: GitEvent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70a2d54e99153d760066833565fc99621b594db93de0feeee3bd192a25a7cd90(
    schedule: _aws_cdk_aws_events_ceddda9d.Schedule,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__371ef1a2fffc32327bc9a3d0ae0bb69ceb73341de5c1a9bc545eb466594723b5(
    branches: typing.Sequence[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__427d21faf66ae413b27d0e2f557322e765c3cce7e4c69da95fc958226eaa47d6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1190a3eae1024d413f1acb261e579683fcaec9bc111ce45f59fe7da637340213(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2162d4a42d79e188e22d80088c6cc8ab767afca08881b610a8869ef88e8145a0(
    skip: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f93562d5a720e1137f8348db81d5a1237148340f3170ec32684ce8aff87f5b75(
    v: typing.Union[builtins.str, _aws_cdk_aws_ec2_ceddda9d.IVpc],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__809b0993ca7d88030c00cec2bb9a1b67194e98b952735763ba9ac91b5404e4e3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    step_function_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea9cc5c805fdc9d028560daae6dc5363527edf8061cc52db2cb2c6daa598d9d5(
    policy: _aws_cdk_aws_iam_ceddda9d.PolicyStatement,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6dca9fe60b24cc62a5003cc57b490bf818bed86bb1473755fcc59f39d404dfd5(
    state_machine_name: builtins.str,
    state_machine_role: _aws_cdk_aws_iam_ceddda9d.IRole,
    definition_body: _aws_cdk_aws_stepfunctions_ceddda9d.DefinitionBody,
    log_group: _aws_cdk_aws_logs_ceddda9d.ILogGroup,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f744e545b5472206ad09a260929339a79c09e0386cb900e85e8e6db5531492d6(
    state_machine_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5794489b9545219391ee33d07a3d1cc85541a08e3a21f1be46946e09db39ec24(
    role: _aws_cdk_aws_iam_ceddda9d.IRole,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab1d87a2e6e162b4005a10e397a06a6be863dcb7d01b3c6344093fe6dbbf27e9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddff48b19cc2a3d965da83997f8cecab103e7717fa75bb40c8b58963278a0442(
    state_def: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a14e530fc3421406403716945cb2dfde68f33c10ac739e1558433fd0e344343(
    state_definition: _aws_cdk_aws_stepfunctions_ceddda9d.IChainable,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c09f391c332d571a8ef9f82c8d9e5677dd6bf151620bc802fd1ddac7fd67348e(
    state_definition: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1671fd3716e92b0696491c21e3f02b82aef16753581387acf8b3bfd9dfc9526f(
    params: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0d5878650df6939dfdda6e68598c3471d4f40c91c9dda0dc8f3a088391421c3(
    value: typing.Union[builtins.str, _aws_cdk_aws_stepfunctions_ceddda9d.IChainable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__134b4b55d02ec5ddf5e27369b51284d729f389ace4861fe8e19cf717678b3293(
    *,
    entry_point: builtins.str,
    job_name: builtins.str,
    application_configuration: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_stepfunctions_tasks_ceddda9d.ApplicationConfiguration, typing.Dict[builtins.str, typing.Any]]]] = None,
    enable_monitoring: typing.Optional[builtins.bool] = None,
    entry_point_argument_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    main_class: typing.Optional[builtins.str] = None,
    spark_submit_parameters: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab7d624c4b17ae5798d2698454d6664a420296e02d5be3d3594785bdcecf3128(
    name: builtins.str,
    *suffixes: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9987188fc354940a8663ace12af8640d76d87148b14d9d1d356e29d9bfb0741(
    str: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f74143e8140659067393d5758eceff773c35ac52f0e6a2496cbf8d7795b9a68(
    str: builtins.str,
    s: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2992ae92902d8b81668ae7355ad4ea4ac8db2b07a12cd50a42be7f9e50929264(
    str: builtins.str,
    s: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57d21adeb89a229e698b88368d71ea6c45cf66ed53f7b9d127e4a0084a35988e(
    str: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55fcfa0db2550eb7697a6ce5cd81370ec17688b1a7dc8581c4c04306276bb146(
    stack: _aws_cdk_ceddda9d.Stack,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__350c5bb98e107eee6ee21ce2e7e012972cbae0b757a37bd6ee1f5e66025eec9c(
    value: typing.Any = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3ac8da41f19d2a59abdf352ae94a21e2dda439f4d6a34e879f4e6228f1603a6(
    arr: typing.Optional[typing.Sequence[builtins.str]] = None,
    separator: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0e4526132686dd17a76cbc5266bbd91f6ff16cdccfd3fd6245f1061a6ff514d(
    str: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db5d559c708a0d9516ae8ba3a450d3980c4ab8174f25a21bf74c78da5460a09d(
    obj1: typing.Any,
    obj2: typing.Any,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a691b7ad10e5308aff51aa2082dc54b2a1b1cc77ade0cae68b1ecf78fba856a(
    url: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e64ebb7228e613203bd98f40a1ff8cfe6b40703167a883bb3f0a0c727a79d2e7(
    stack: _aws_cdk_ceddda9d.Stack,
    persist: typing.Optional[builtins.bool] = None,
    path: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4503a468a48cac5f6781501429a0ca70194cff93e94a9f9c1b72e64161ff096f(
    str: builtins.str,
    s: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2d5b06f249e7a0f41e6e205451860c1add18aeaa6bef4e833f655e2b1694860(
    scope: _constructs_77d1e7e8.IConstruct,
    rule_id: builtins.str,
    reason: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8335787277838180e459986b4f0f134fb3f147e37b0038a91887173bd63c7ecc(
    str: builtins.str,
    delimiter: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__964efb3914fb0773ef4ac64364b720ab9c3806f11f7062b828774bd33732cc4d(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    step_function_name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__400ac1a0064811c360f0c863f9ce36aa974beeae0f960dc8f2f6bae816a5fa79(
    applicaiton_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f93a27b16e83ed876915b3202828f273e27791ab40f9b2bd3ae0d6a9e10142d3(
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb8f8278f452b81473475aa06ba97c026c76ae212582ec51af529678e3227f39(
    bucket: typing.Union[builtins.str, _aws_cdk_aws_s3_ceddda9d.IBucket],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdec246523bddaa90a758dd76d3888d182090115b2f5598f8b38c3c55c1b007d(
    a_def: builtins.str,
) -> None:
    """Type checking stubs"""
    pass
