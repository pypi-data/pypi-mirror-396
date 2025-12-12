r'''
# `clevercloud_v`

Refer to the Terraform Registry for docs: [`clevercloud_v`](https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v).
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

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class V(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.v.V",
):
    '''Represents a {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v clevercloud_v}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        biggest_flavor: builtins.str,
        max_instance_count: jsii.Number,
        min_instance_count: jsii.Number,
        name: builtins.str,
        smallest_flavor: builtins.str,
        app_folder: typing.Optional[builtins.str] = None,
        binary: typing.Optional[builtins.str] = None,
        build_flavor: typing.Optional[builtins.str] = None,
        dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        deployment: typing.Optional[typing.Union["VDeployment", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        development_build: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        exposed_environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        hooks: typing.Optional[typing.Union["VHooks", typing.Dict[builtins.str, typing.Any]]] = None,
        networkgroups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VNetworkgroups", typing.Dict[builtins.str, typing.Any]]]]] = None,
        redirect_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        region: typing.Optional[builtins.str] = None,
        sticky_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vhosts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VVhosts", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v clevercloud_v} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param biggest_flavor: Biggest instance flavor, if different from smallest, enable auto-scaling. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#biggest_flavor V#biggest_flavor}
        :param max_instance_count: Maximum instance count, if different from min value, enable auto-scaling. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#max_instance_count V#max_instance_count}
        :param min_instance_count: Minimum instance count. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#min_instance_count V#min_instance_count}
        :param name: Application name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#name V#name}
        :param smallest_flavor: Smallest instance flavor. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#smallest_flavor V#smallest_flavor}
        :param app_folder: Folder in which the application is located (inside the git repository). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#app_folder V#app_folder}
        :param binary: The name of the output binary file. Default: ``${APP_HOME}/v_bin_${APP_ID}``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#binary V#binary}
        :param build_flavor: Use dedicated instance with given flavor for build phase. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#build_flavor V#build_flavor}
        :param dependencies: A list of application or add-ons required to run this application. Can be either app_xxx or postgres_yyy ID format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#dependencies V#dependencies}
        :param deployment: deployment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#deployment V#deployment}
        :param description: Application description. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#description V#description}
        :param development_build: Set to true to compile without the ``-prod`` flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#development_build V#development_build}
        :param environment: Environment variables injected into the application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#environment V#environment}
        :param exposed_environment: Environment variables other linked applications will be able to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#exposed_environment V#exposed_environment}
        :param hooks: hooks block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#hooks V#hooks}
        :param networkgroups: List of networkgroups the application must be part of. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#networkgroups V#networkgroups}
        :param redirect_https: Redirect client from plain to TLS port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#redirect_https V#redirect_https}
        :param region: Geographical region where the database will be deployed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#region V#region}
        :param sticky_sessions: Enable sticky sessions, use it when your client sessions are instances scoped. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#sticky_sessions V#sticky_sessions}
        :param vhosts: List of virtual hosts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#vhosts V#vhosts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0be89165938ff4e953a35e2b6f1152b17f05de0b39b1ca76ccf966d53f847ba6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = VConfig(
            biggest_flavor=biggest_flavor,
            max_instance_count=max_instance_count,
            min_instance_count=min_instance_count,
            name=name,
            smallest_flavor=smallest_flavor,
            app_folder=app_folder,
            binary=binary,
            build_flavor=build_flavor,
            dependencies=dependencies,
            deployment=deployment,
            description=description,
            development_build=development_build,
            environment=environment,
            exposed_environment=exposed_environment,
            hooks=hooks,
            networkgroups=networkgroups,
            redirect_https=redirect_https,
            region=region,
            sticky_sessions=sticky_sessions,
            vhosts=vhosts,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a V resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the V to import.
        :param import_from_id: The id of the existing V that should be imported. Refer to the {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the V to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83ee19f5792ebd6ab19714d07b816253b62aa556a92a87978aac7a498ca0f7e8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putDeployment")
    def put_deployment(
        self,
        *,
        authentication_basic: typing.Optional[builtins.str] = None,
        commit: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param authentication_basic: user ans password ':' separated, (PersonalAccessToken in Github case). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#authentication_basic V#authentication_basic}
        :param commit: Support multiple syntax like ``refs/heads/[BRANCH]``, ``github_hook`` or ``[COMMIT]``, when using the special value ``github_hook``, we will link the application to the Github repository. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#commit V#commit}
        :param repository: The repository URL to deploy, can be 'https://...', 'file://...'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#repository V#repository}
        '''
        value = VDeployment(
            authentication_basic=authentication_basic,
            commit=commit,
            repository=repository,
        )

        return typing.cast(None, jsii.invoke(self, "putDeployment", [value]))

    @jsii.member(jsii_name="putHooks")
    def put_hooks(
        self,
        *,
        post_build: typing.Optional[builtins.str] = None,
        pre_build: typing.Optional[builtins.str] = None,
        pre_run: typing.Optional[builtins.str] = None,
        run_failed: typing.Optional[builtins.str] = None,
        run_succeed: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param post_build: `CC_POST_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#post-build>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#post_build V#post_build}
        :param pre_build: `CC_PRE_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-build>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#pre_build V#pre_build}
        :param pre_run: `CC_PRE_RUN_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-run>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#pre_run V#pre_run}
        :param run_failed: `CC_RUN_FAILED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#run_failed V#run_failed}
        :param run_succeed: `CC_RUN_SUCCEEDED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#run_succeed V#run_succeed}
        '''
        value = VHooks(
            post_build=post_build,
            pre_build=pre_build,
            pre_run=pre_run,
            run_failed=run_failed,
            run_succeed=run_succeed,
        )

        return typing.cast(None, jsii.invoke(self, "putHooks", [value]))

    @jsii.member(jsii_name="putNetworkgroups")
    def put_networkgroups(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VNetworkgroups", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7bb5ae5d2c472703d7fd72fc50b4c8df42c1d128136ad17fffd3a17d9586f8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetworkgroups", [value]))

    @jsii.member(jsii_name="putVhosts")
    def put_vhosts(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VVhosts", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__736b03f855363f89e2d3ca725bf6b64a6f4288e02217b4580d452ae685ac6425)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putVhosts", [value]))

    @jsii.member(jsii_name="resetAppFolder")
    def reset_app_folder(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAppFolder", []))

    @jsii.member(jsii_name="resetBinary")
    def reset_binary(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBinary", []))

    @jsii.member(jsii_name="resetBuildFlavor")
    def reset_build_flavor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBuildFlavor", []))

    @jsii.member(jsii_name="resetDependencies")
    def reset_dependencies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDependencies", []))

    @jsii.member(jsii_name="resetDeployment")
    def reset_deployment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeployment", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDevelopmentBuild")
    def reset_development_build(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDevelopmentBuild", []))

    @jsii.member(jsii_name="resetEnvironment")
    def reset_environment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvironment", []))

    @jsii.member(jsii_name="resetExposedEnvironment")
    def reset_exposed_environment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExposedEnvironment", []))

    @jsii.member(jsii_name="resetHooks")
    def reset_hooks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHooks", []))

    @jsii.member(jsii_name="resetNetworkgroups")
    def reset_networkgroups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkgroups", []))

    @jsii.member(jsii_name="resetRedirectHttps")
    def reset_redirect_https(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedirectHttps", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetStickySessions")
    def reset_sticky_sessions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStickySessions", []))

    @jsii.member(jsii_name="resetVhosts")
    def reset_vhosts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVhosts", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="deployment")
    def deployment(self) -> "VDeploymentOutputReference":
        return typing.cast("VDeploymentOutputReference", jsii.get(self, "deployment"))

    @builtins.property
    @jsii.member(jsii_name="deployUrl")
    def deploy_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deployUrl"))

    @builtins.property
    @jsii.member(jsii_name="hooks")
    def hooks(self) -> "VHooksOutputReference":
        return typing.cast("VHooksOutputReference", jsii.get(self, "hooks"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="networkgroups")
    def networkgroups(self) -> "VNetworkgroupsList":
        return typing.cast("VNetworkgroupsList", jsii.get(self, "networkgroups"))

    @builtins.property
    @jsii.member(jsii_name="vhosts")
    def vhosts(self) -> "VVhostsList":
        return typing.cast("VVhostsList", jsii.get(self, "vhosts"))

    @builtins.property
    @jsii.member(jsii_name="appFolderInput")
    def app_folder_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appFolderInput"))

    @builtins.property
    @jsii.member(jsii_name="biggestFlavorInput")
    def biggest_flavor_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "biggestFlavorInput"))

    @builtins.property
    @jsii.member(jsii_name="binaryInput")
    def binary_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "binaryInput"))

    @builtins.property
    @jsii.member(jsii_name="buildFlavorInput")
    def build_flavor_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "buildFlavorInput"))

    @builtins.property
    @jsii.member(jsii_name="dependenciesInput")
    def dependencies_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dependenciesInput"))

    @builtins.property
    @jsii.member(jsii_name="deploymentInput")
    def deployment_input(
        self,
    ) -> typing.Optional[typing.Union["VDeployment", _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["VDeployment", _cdktf_9a9027ec.IResolvable]], jsii.get(self, "deploymentInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="developmentBuildInput")
    def development_build_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "developmentBuildInput"))

    @builtins.property
    @jsii.member(jsii_name="environmentInput")
    def environment_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "environmentInput"))

    @builtins.property
    @jsii.member(jsii_name="exposedEnvironmentInput")
    def exposed_environment_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "exposedEnvironmentInput"))

    @builtins.property
    @jsii.member(jsii_name="hooksInput")
    def hooks_input(
        self,
    ) -> typing.Optional[typing.Union["VHooks", _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["VHooks", _cdktf_9a9027ec.IResolvable]], jsii.get(self, "hooksInput"))

    @builtins.property
    @jsii.member(jsii_name="maxInstanceCountInput")
    def max_instance_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxInstanceCountInput"))

    @builtins.property
    @jsii.member(jsii_name="minInstanceCountInput")
    def min_instance_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minInstanceCountInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="networkgroupsInput")
    def networkgroups_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VNetworkgroups"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VNetworkgroups"]]], jsii.get(self, "networkgroupsInput"))

    @builtins.property
    @jsii.member(jsii_name="redirectHttpsInput")
    def redirect_https_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "redirectHttpsInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="smallestFlavorInput")
    def smallest_flavor_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "smallestFlavorInput"))

    @builtins.property
    @jsii.member(jsii_name="stickySessionsInput")
    def sticky_sessions_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "stickySessionsInput"))

    @builtins.property
    @jsii.member(jsii_name="vhostsInput")
    def vhosts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VVhosts"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VVhosts"]]], jsii.get(self, "vhostsInput"))

    @builtins.property
    @jsii.member(jsii_name="appFolder")
    def app_folder(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appFolder"))

    @app_folder.setter
    def app_folder(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__080c96f9990c14014ed5704718e9c8c25c76df5638bbe74610a7ba57e63492c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appFolder", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="biggestFlavor")
    def biggest_flavor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "biggestFlavor"))

    @biggest_flavor.setter
    def biggest_flavor(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4d55f603678e4790ba92fcf0ce95289cfd655795e9b5a64c0f11331c407f645)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "biggestFlavor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="binary")
    def binary(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "binary"))

    @binary.setter
    def binary(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e7e1261f48d8016b5ceecf43c889725f93c24d2e085d12f6cf6c417f5ffebd5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "binary", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="buildFlavor")
    def build_flavor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "buildFlavor"))

    @build_flavor.setter
    def build_flavor(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe7d2c86e4ac0ee3c5cfc772c222bc5ec52fe8b4ede87a727adbc59ccbf7a862)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "buildFlavor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dependencies")
    def dependencies(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dependencies"))

    @dependencies.setter
    def dependencies(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49a6360d8e4b88f1ff750bc1bc4e8049bb7c4d0d16cf402a6fde471c6a281491)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dependencies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65e0d987cad1a91ed46dbeb8f7fd3a1ceab74df6a9189341098d37ce2a30d0c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="developmentBuild")
    def development_build(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "developmentBuild"))

    @development_build.setter
    def development_build(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed090270c1accc2b60298751f3e26312a32853de2bb60c77ca51b1ca1194a52e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "developmentBuild", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "environment"))

    @environment.setter
    def environment(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__692be0eb2000203a9027c69ef3fdfaf7158704309b5ae9f6324795ad2b610842)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "environment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="exposedEnvironment")
    def exposed_environment(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "exposedEnvironment"))

    @exposed_environment.setter
    def exposed_environment(
        self,
        value: typing.Mapping[builtins.str, builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3f0f67ab6f9f7afe3235816bf6dc808a2bbcf02b53d5017763212b990f6f022)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exposedEnvironment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxInstanceCount")
    def max_instance_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxInstanceCount"))

    @max_instance_count.setter
    def max_instance_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1d92b12f3157290136d3c3615cf1138755d22fc45f297576e871742179381ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxInstanceCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minInstanceCount")
    def min_instance_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minInstanceCount"))

    @min_instance_count.setter
    def min_instance_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd582229bb233210f71b2d660d0da9444542ce38f90878896bd66565b5cf1d83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minInstanceCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f1f46a76a897da2bafd7f2069be91a8f8551b82751856ff458d167f4f9f9f36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="redirectHttps")
    def redirect_https(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "redirectHttps"))

    @redirect_https.setter
    def redirect_https(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3355813390c837c8b49ba9d8bb5cfb8b4a875a48c3a6d3d98a248e289c8eec85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "redirectHttps", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__724d3b5ccd1e1a7d5bfa890d0b2e103c4f26d914c3e4e5258407a9cda3758dae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="smallestFlavor")
    def smallest_flavor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "smallestFlavor"))

    @smallest_flavor.setter
    def smallest_flavor(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02f4de4c283d23e8be5bd66063bb2b06e59f048f3e66b7b70c7de0ed006e7a39)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "smallestFlavor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stickySessions")
    def sticky_sessions(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "stickySessions"))

    @sticky_sessions.setter
    def sticky_sessions(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e13af34a933ea59253dedde046de0230daf2d56a6cc78a12d17930d3004d9c8d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stickySessions", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.v.VConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "biggest_flavor": "biggestFlavor",
        "max_instance_count": "maxInstanceCount",
        "min_instance_count": "minInstanceCount",
        "name": "name",
        "smallest_flavor": "smallestFlavor",
        "app_folder": "appFolder",
        "binary": "binary",
        "build_flavor": "buildFlavor",
        "dependencies": "dependencies",
        "deployment": "deployment",
        "description": "description",
        "development_build": "developmentBuild",
        "environment": "environment",
        "exposed_environment": "exposedEnvironment",
        "hooks": "hooks",
        "networkgroups": "networkgroups",
        "redirect_https": "redirectHttps",
        "region": "region",
        "sticky_sessions": "stickySessions",
        "vhosts": "vhosts",
    },
)
class VConfig(_cdktf_9a9027ec.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        biggest_flavor: builtins.str,
        max_instance_count: jsii.Number,
        min_instance_count: jsii.Number,
        name: builtins.str,
        smallest_flavor: builtins.str,
        app_folder: typing.Optional[builtins.str] = None,
        binary: typing.Optional[builtins.str] = None,
        build_flavor: typing.Optional[builtins.str] = None,
        dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        deployment: typing.Optional[typing.Union["VDeployment", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        development_build: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        exposed_environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        hooks: typing.Optional[typing.Union["VHooks", typing.Dict[builtins.str, typing.Any]]] = None,
        networkgroups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VNetworkgroups", typing.Dict[builtins.str, typing.Any]]]]] = None,
        redirect_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        region: typing.Optional[builtins.str] = None,
        sticky_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vhosts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["VVhosts", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param biggest_flavor: Biggest instance flavor, if different from smallest, enable auto-scaling. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#biggest_flavor V#biggest_flavor}
        :param max_instance_count: Maximum instance count, if different from min value, enable auto-scaling. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#max_instance_count V#max_instance_count}
        :param min_instance_count: Minimum instance count. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#min_instance_count V#min_instance_count}
        :param name: Application name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#name V#name}
        :param smallest_flavor: Smallest instance flavor. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#smallest_flavor V#smallest_flavor}
        :param app_folder: Folder in which the application is located (inside the git repository). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#app_folder V#app_folder}
        :param binary: The name of the output binary file. Default: ``${APP_HOME}/v_bin_${APP_ID}``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#binary V#binary}
        :param build_flavor: Use dedicated instance with given flavor for build phase. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#build_flavor V#build_flavor}
        :param dependencies: A list of application or add-ons required to run this application. Can be either app_xxx or postgres_yyy ID format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#dependencies V#dependencies}
        :param deployment: deployment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#deployment V#deployment}
        :param description: Application description. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#description V#description}
        :param development_build: Set to true to compile without the ``-prod`` flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#development_build V#development_build}
        :param environment: Environment variables injected into the application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#environment V#environment}
        :param exposed_environment: Environment variables other linked applications will be able to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#exposed_environment V#exposed_environment}
        :param hooks: hooks block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#hooks V#hooks}
        :param networkgroups: List of networkgroups the application must be part of. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#networkgroups V#networkgroups}
        :param redirect_https: Redirect client from plain to TLS port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#redirect_https V#redirect_https}
        :param region: Geographical region where the database will be deployed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#region V#region}
        :param sticky_sessions: Enable sticky sessions, use it when your client sessions are instances scoped. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#sticky_sessions V#sticky_sessions}
        :param vhosts: List of virtual hosts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#vhosts V#vhosts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(deployment, dict):
            deployment = VDeployment(**deployment)
        if isinstance(hooks, dict):
            hooks = VHooks(**hooks)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e342bce7390dbebe6813752e21999473fb95ba5bed833120e5c2194eb972f3a)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument biggest_flavor", value=biggest_flavor, expected_type=type_hints["biggest_flavor"])
            check_type(argname="argument max_instance_count", value=max_instance_count, expected_type=type_hints["max_instance_count"])
            check_type(argname="argument min_instance_count", value=min_instance_count, expected_type=type_hints["min_instance_count"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument smallest_flavor", value=smallest_flavor, expected_type=type_hints["smallest_flavor"])
            check_type(argname="argument app_folder", value=app_folder, expected_type=type_hints["app_folder"])
            check_type(argname="argument binary", value=binary, expected_type=type_hints["binary"])
            check_type(argname="argument build_flavor", value=build_flavor, expected_type=type_hints["build_flavor"])
            check_type(argname="argument dependencies", value=dependencies, expected_type=type_hints["dependencies"])
            check_type(argname="argument deployment", value=deployment, expected_type=type_hints["deployment"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument development_build", value=development_build, expected_type=type_hints["development_build"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument exposed_environment", value=exposed_environment, expected_type=type_hints["exposed_environment"])
            check_type(argname="argument hooks", value=hooks, expected_type=type_hints["hooks"])
            check_type(argname="argument networkgroups", value=networkgroups, expected_type=type_hints["networkgroups"])
            check_type(argname="argument redirect_https", value=redirect_https, expected_type=type_hints["redirect_https"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument sticky_sessions", value=sticky_sessions, expected_type=type_hints["sticky_sessions"])
            check_type(argname="argument vhosts", value=vhosts, expected_type=type_hints["vhosts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "biggest_flavor": biggest_flavor,
            "max_instance_count": max_instance_count,
            "min_instance_count": min_instance_count,
            "name": name,
            "smallest_flavor": smallest_flavor,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if app_folder is not None:
            self._values["app_folder"] = app_folder
        if binary is not None:
            self._values["binary"] = binary
        if build_flavor is not None:
            self._values["build_flavor"] = build_flavor
        if dependencies is not None:
            self._values["dependencies"] = dependencies
        if deployment is not None:
            self._values["deployment"] = deployment
        if description is not None:
            self._values["description"] = description
        if development_build is not None:
            self._values["development_build"] = development_build
        if environment is not None:
            self._values["environment"] = environment
        if exposed_environment is not None:
            self._values["exposed_environment"] = exposed_environment
        if hooks is not None:
            self._values["hooks"] = hooks
        if networkgroups is not None:
            self._values["networkgroups"] = networkgroups
        if redirect_https is not None:
            self._values["redirect_https"] = redirect_https
        if region is not None:
            self._values["region"] = region
        if sticky_sessions is not None:
            self._values["sticky_sessions"] = sticky_sessions
        if vhosts is not None:
            self._values["vhosts"] = vhosts

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def biggest_flavor(self) -> builtins.str:
        '''Biggest instance flavor, if different from smallest, enable auto-scaling.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#biggest_flavor V#biggest_flavor}
        '''
        result = self._values.get("biggest_flavor")
        assert result is not None, "Required property 'biggest_flavor' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def max_instance_count(self) -> jsii.Number:
        '''Maximum instance count, if different from min value, enable auto-scaling.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#max_instance_count V#max_instance_count}
        '''
        result = self._values.get("max_instance_count")
        assert result is not None, "Required property 'max_instance_count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_instance_count(self) -> jsii.Number:
        '''Minimum instance count.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#min_instance_count V#min_instance_count}
        '''
        result = self._values.get("min_instance_count")
        assert result is not None, "Required property 'min_instance_count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Application name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#name V#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def smallest_flavor(self) -> builtins.str:
        '''Smallest instance flavor.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#smallest_flavor V#smallest_flavor}
        '''
        result = self._values.get("smallest_flavor")
        assert result is not None, "Required property 'smallest_flavor' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def app_folder(self) -> typing.Optional[builtins.str]:
        '''Folder in which the application is located (inside the git repository).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#app_folder V#app_folder}
        '''
        result = self._values.get("app_folder")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def binary(self) -> typing.Optional[builtins.str]:
        '''The name of the output binary file. Default: ``${APP_HOME}/v_bin_${APP_ID}``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#binary V#binary}
        '''
        result = self._values.get("binary")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_flavor(self) -> typing.Optional[builtins.str]:
        '''Use dedicated instance with given flavor for build phase.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#build_flavor V#build_flavor}
        '''
        result = self._values.get("build_flavor")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dependencies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of application or add-ons required to run this application. Can be either app_xxx or postgres_yyy ID format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#dependencies V#dependencies}
        '''
        result = self._values.get("dependencies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def deployment(self) -> typing.Optional["VDeployment"]:
        '''deployment block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#deployment V#deployment}
        '''
        result = self._values.get("deployment")
        return typing.cast(typing.Optional["VDeployment"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Application description.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#description V#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def development_build(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true to compile without the ``-prod`` flag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#development_build V#development_build}
        '''
        result = self._values.get("development_build")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Environment variables injected into the application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#environment V#environment}
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def exposed_environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Environment variables other linked applications will be able to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#exposed_environment V#exposed_environment}
        '''
        result = self._values.get("exposed_environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def hooks(self) -> typing.Optional["VHooks"]:
        '''hooks block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#hooks V#hooks}
        '''
        result = self._values.get("hooks")
        return typing.cast(typing.Optional["VHooks"], result)

    @builtins.property
    def networkgroups(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VNetworkgroups"]]]:
        '''List of networkgroups the application must be part of.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#networkgroups V#networkgroups}
        '''
        result = self._values.get("networkgroups")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VNetworkgroups"]]], result)

    @builtins.property
    def redirect_https(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Redirect client from plain to TLS port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#redirect_https V#redirect_https}
        '''
        result = self._values.get("redirect_https")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Geographical region where the database will be deployed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#region V#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sticky_sessions(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable sticky sessions, use it when your client sessions are instances scoped.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#sticky_sessions V#sticky_sessions}
        '''
        result = self._values.get("sticky_sessions")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def vhosts(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VVhosts"]]]:
        '''List of virtual hosts.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#vhosts V#vhosts}
        '''
        result = self._values.get("vhosts")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["VVhosts"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.v.VDeployment",
    jsii_struct_bases=[],
    name_mapping={
        "authentication_basic": "authenticationBasic",
        "commit": "commit",
        "repository": "repository",
    },
)
class VDeployment:
    def __init__(
        self,
        *,
        authentication_basic: typing.Optional[builtins.str] = None,
        commit: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param authentication_basic: user ans password ':' separated, (PersonalAccessToken in Github case). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#authentication_basic V#authentication_basic}
        :param commit: Support multiple syntax like ``refs/heads/[BRANCH]``, ``github_hook`` or ``[COMMIT]``, when using the special value ``github_hook``, we will link the application to the Github repository. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#commit V#commit}
        :param repository: The repository URL to deploy, can be 'https://...', 'file://...'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#repository V#repository}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83053c2350a68397b6754210aae9147dfeacddeacd9bbed9182e416a1b5c9f23)
            check_type(argname="argument authentication_basic", value=authentication_basic, expected_type=type_hints["authentication_basic"])
            check_type(argname="argument commit", value=commit, expected_type=type_hints["commit"])
            check_type(argname="argument repository", value=repository, expected_type=type_hints["repository"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if authentication_basic is not None:
            self._values["authentication_basic"] = authentication_basic
        if commit is not None:
            self._values["commit"] = commit
        if repository is not None:
            self._values["repository"] = repository

    @builtins.property
    def authentication_basic(self) -> typing.Optional[builtins.str]:
        '''user ans password ':' separated, (PersonalAccessToken in Github case).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#authentication_basic V#authentication_basic}
        '''
        result = self._values.get("authentication_basic")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def commit(self) -> typing.Optional[builtins.str]:
        '''Support multiple syntax like ``refs/heads/[BRANCH]``, ``github_hook`` or ``[COMMIT]``, when using the special value ``github_hook``, we will link the application to the Github repository.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#commit V#commit}
        '''
        result = self._values.get("commit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''The repository URL to deploy, can be 'https://...', 'file://...'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#repository V#repository}
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VDeploymentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.v.VDeploymentOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd07c778458fd9d71acd0b8364681a879485e7ab33647d793224117efbcc4523)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAuthenticationBasic")
    def reset_authentication_basic(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthenticationBasic", []))

    @jsii.member(jsii_name="resetCommit")
    def reset_commit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCommit", []))

    @jsii.member(jsii_name="resetRepository")
    def reset_repository(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRepository", []))

    @builtins.property
    @jsii.member(jsii_name="authenticationBasicInput")
    def authentication_basic_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authenticationBasicInput"))

    @builtins.property
    @jsii.member(jsii_name="commitInput")
    def commit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commitInput"))

    @builtins.property
    @jsii.member(jsii_name="repositoryInput")
    def repository_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "repositoryInput"))

    @builtins.property
    @jsii.member(jsii_name="authenticationBasic")
    def authentication_basic(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authenticationBasic"))

    @authentication_basic.setter
    def authentication_basic(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37265efcfecf9c4ee1f980c250f9b6edda9c6e14bdeb1c4ef2b31539f1fb69b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authenticationBasic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="commit")
    def commit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commit"))

    @commit.setter
    def commit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48fba627150d51b54c38ec30ab0bf6f15a5e46a2234f8845041c75cede3671dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df11554ca37f1aa3fb94293d22307d8cfee62f2e1bf92dac1fdb6f82ecb22e31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "repository", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[VDeployment, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[VDeployment, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[VDeployment, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__766b3fc8b8d9e44a26ebace16d23a41d4f4f5b06051f7b2f5a12e949074a1783)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.v.VHooks",
    jsii_struct_bases=[],
    name_mapping={
        "post_build": "postBuild",
        "pre_build": "preBuild",
        "pre_run": "preRun",
        "run_failed": "runFailed",
        "run_succeed": "runSucceed",
    },
)
class VHooks:
    def __init__(
        self,
        *,
        post_build: typing.Optional[builtins.str] = None,
        pre_build: typing.Optional[builtins.str] = None,
        pre_run: typing.Optional[builtins.str] = None,
        run_failed: typing.Optional[builtins.str] = None,
        run_succeed: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param post_build: `CC_POST_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#post-build>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#post_build V#post_build}
        :param pre_build: `CC_PRE_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-build>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#pre_build V#pre_build}
        :param pre_run: `CC_PRE_RUN_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-run>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#pre_run V#pre_run}
        :param run_failed: `CC_RUN_FAILED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#run_failed V#run_failed}
        :param run_succeed: `CC_RUN_SUCCEEDED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#run_succeed V#run_succeed}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12cd9ab521592cbf22e0258aceaa7f06f0c8e26d746a1eee16a502b3a01ae85d)
            check_type(argname="argument post_build", value=post_build, expected_type=type_hints["post_build"])
            check_type(argname="argument pre_build", value=pre_build, expected_type=type_hints["pre_build"])
            check_type(argname="argument pre_run", value=pre_run, expected_type=type_hints["pre_run"])
            check_type(argname="argument run_failed", value=run_failed, expected_type=type_hints["run_failed"])
            check_type(argname="argument run_succeed", value=run_succeed, expected_type=type_hints["run_succeed"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if post_build is not None:
            self._values["post_build"] = post_build
        if pre_build is not None:
            self._values["pre_build"] = pre_build
        if pre_run is not None:
            self._values["pre_run"] = pre_run
        if run_failed is not None:
            self._values["run_failed"] = run_failed
        if run_succeed is not None:
            self._values["run_succeed"] = run_succeed

    @builtins.property
    def post_build(self) -> typing.Optional[builtins.str]:
        '''`CC_POST_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#post-build>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#post_build V#post_build}
        '''
        result = self._values.get("post_build")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_build(self) -> typing.Optional[builtins.str]:
        '''`CC_PRE_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-build>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#pre_build V#pre_build}
        '''
        result = self._values.get("pre_build")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_run(self) -> typing.Optional[builtins.str]:
        '''`CC_PRE_RUN_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-run>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#pre_run V#pre_run}
        '''
        result = self._values.get("pre_run")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run_failed(self) -> typing.Optional[builtins.str]:
        '''`CC_RUN_FAILED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#run_failed V#run_failed}
        '''
        result = self._values.get("run_failed")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run_succeed(self) -> typing.Optional[builtins.str]:
        '''`CC_RUN_SUCCEEDED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#run_succeed V#run_succeed}
        '''
        result = self._values.get("run_succeed")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VHooks(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VHooksOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.v.VHooksOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4d5b3ab09ba353a7b60ab9e1d3fca5f004ceca8ac866208a0e9bf3363e160a6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPostBuild")
    def reset_post_build(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostBuild", []))

    @jsii.member(jsii_name="resetPreBuild")
    def reset_pre_build(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreBuild", []))

    @jsii.member(jsii_name="resetPreRun")
    def reset_pre_run(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreRun", []))

    @jsii.member(jsii_name="resetRunFailed")
    def reset_run_failed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunFailed", []))

    @jsii.member(jsii_name="resetRunSucceed")
    def reset_run_succeed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRunSucceed", []))

    @builtins.property
    @jsii.member(jsii_name="postBuildInput")
    def post_build_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "postBuildInput"))

    @builtins.property
    @jsii.member(jsii_name="preBuildInput")
    def pre_build_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preBuildInput"))

    @builtins.property
    @jsii.member(jsii_name="preRunInput")
    def pre_run_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preRunInput"))

    @builtins.property
    @jsii.member(jsii_name="runFailedInput")
    def run_failed_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runFailedInput"))

    @builtins.property
    @jsii.member(jsii_name="runSucceedInput")
    def run_succeed_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "runSucceedInput"))

    @builtins.property
    @jsii.member(jsii_name="postBuild")
    def post_build(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postBuild"))

    @post_build.setter
    def post_build(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59d706f15743b0dacd5f3e572645d061d28ec9b86441bd753744078ac7658aeb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postBuild", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preBuild")
    def pre_build(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preBuild"))

    @pre_build.setter
    def pre_build(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b07c0030e63b612a94ce2a46334b28268a7aaea429e22eeb8687365da3fe95a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preBuild", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preRun")
    def pre_run(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preRun"))

    @pre_run.setter
    def pre_run(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b558c4b9e2b4b3a05d5f7826a98975e44a1f5c9f601d2624ed4010d5ecf22a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runFailed")
    def run_failed(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runFailed"))

    @run_failed.setter
    def run_failed(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ba87dc0d4f410eb336fc5028a78dbed8ba2699ac9711569760c4be8d24adee4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runFailed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runSucceed")
    def run_succeed(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runSucceed"))

    @run_succeed.setter
    def run_succeed(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__461fbac61ef7aca3ac054c56bca6b8fec2d440e2e09cf98a6d3d47b7bba46bb5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runSucceed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[VHooks, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[VHooks, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[VHooks, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2b50412574c029f237b9de0dda5d7bd9b5dfc648ada993faaa6e64a1b355132)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.v.VNetworkgroups",
    jsii_struct_bases=[],
    name_mapping={"fqdn": "fqdn", "networkgroup_id": "networkgroupId"},
)
class VNetworkgroups:
    def __init__(self, *, fqdn: builtins.str, networkgroup_id: builtins.str) -> None:
        '''
        :param fqdn: domain name which will resolve to application instances inside the networkgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#fqdn V#fqdn}
        :param networkgroup_id: ID of the networkgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#networkgroup_id V#networkgroup_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c27eeb5f965d374f9e573c62a0e50bd9af80b9fefb047aa4b004ae00071c1831)
            check_type(argname="argument fqdn", value=fqdn, expected_type=type_hints["fqdn"])
            check_type(argname="argument networkgroup_id", value=networkgroup_id, expected_type=type_hints["networkgroup_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "fqdn": fqdn,
            "networkgroup_id": networkgroup_id,
        }

    @builtins.property
    def fqdn(self) -> builtins.str:
        '''domain name which will resolve to application instances inside the networkgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#fqdn V#fqdn}
        '''
        result = self._values.get("fqdn")
        assert result is not None, "Required property 'fqdn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def networkgroup_id(self) -> builtins.str:
        '''ID of the networkgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#networkgroup_id V#networkgroup_id}
        '''
        result = self._values.get("networkgroup_id")
        assert result is not None, "Required property 'networkgroup_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VNetworkgroups(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VNetworkgroupsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.v.VNetworkgroupsList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ad15fce2350f935296d0937621e7f687fd75de42992119076717817b74ef569)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "VNetworkgroupsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2307ec6c829dba68a5ba9ef249665935f77b704aa3e564817897e61404436856)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("VNetworkgroupsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02221834b58cabd91c73c0febff04e222b1a1462adaf4c0a91a3b344e7be3a07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bba8f8232e133d847511057c814f057985dab9e62f2a7fafe749fb0e49c125f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0949c1c1bc9ef300ec538c80d410eda9fc2ce6e98a79e23bd98e76d81476eee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VNetworkgroups]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VNetworkgroups]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VNetworkgroups]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2161e43c07868ba56a13edb0af3e764782a0e41ad58d501472f6f5d2f7f301e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class VNetworkgroupsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.v.VNetworkgroupsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc496f2fcf918efd6a1aa4b842eeaddf77c5828252536e8532c363175428ad16)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="fqdnInput")
    def fqdn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fqdnInput"))

    @builtins.property
    @jsii.member(jsii_name="networkgroupIdInput")
    def networkgroup_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkgroupIdInput"))

    @builtins.property
    @jsii.member(jsii_name="fqdn")
    def fqdn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fqdn"))

    @fqdn.setter
    def fqdn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72e1f41788a113d2df0c902de88af9bcbe08e93432699b90118c25fbd6d9017f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fqdn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkgroupId")
    def networkgroup_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkgroupId"))

    @networkgroup_id.setter
    def networkgroup_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09bfe8711bab892ed97804a0ec15123331c590bc0a2122c4db6a2b7308b3b0da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkgroupId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[VNetworkgroups, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[VNetworkgroups, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[VNetworkgroups, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9b70e65212d2ee2d5a51750ae6739de57e7bcb82afa046e308d46cdd57a02c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.v.VVhosts",
    jsii_struct_bases=[],
    name_mapping={"fqdn": "fqdn", "path_begin": "pathBegin"},
)
class VVhosts:
    def __init__(
        self,
        *,
        fqdn: builtins.str,
        path_begin: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param fqdn: Fully qualified domain name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#fqdn V#fqdn}
        :param path_begin: Any HTTP request starting with this path will be sent to this application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#path_begin V#path_begin}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3507e05ded9ec175ce9cd97d1db18925cde44c90eea95f9f6d5c2cbb466029c5)
            check_type(argname="argument fqdn", value=fqdn, expected_type=type_hints["fqdn"])
            check_type(argname="argument path_begin", value=path_begin, expected_type=type_hints["path_begin"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "fqdn": fqdn,
        }
        if path_begin is not None:
            self._values["path_begin"] = path_begin

    @builtins.property
    def fqdn(self) -> builtins.str:
        '''Fully qualified domain name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#fqdn V#fqdn}
        '''
        result = self._values.get("fqdn")
        assert result is not None, "Required property 'fqdn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path_begin(self) -> typing.Optional[builtins.str]:
        '''Any HTTP request starting with this path will be sent to this application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/v#path_begin V#path_begin}
        '''
        result = self._values.get("path_begin")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VVhosts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class VVhostsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.v.VVhostsList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f62d12b23fc9f67bdb303aa9c0a2c2ec02512386723c7117bb59805771e0f168)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "VVhostsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82c9127b52eff97c0a70d195d9a00c69f60113cd3e5b518a367f5a61993ddc78)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("VVhostsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5061a1c976a1a061efd27d35a0c50ba474fde2618a5b231b5ecea0a8e2d9ee1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__476acccc1950e8900cd93d1d6f2de92c5326fa525242c8b0b995b32fe64f65e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__daf31c1fa0d6d9b7ab8c47dddd5c32fb358cba892d1bbdda2f215ca8dc868464)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VVhosts]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VVhosts]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VVhosts]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98efae27907a529d543c3606d629ee1f2ba5bd9b77d6a34ee5ff88de24da29c9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class VVhostsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.v.VVhostsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc929574452d8e3dfeaf5ed92f01185de87e0465818103252023374fe342ae52)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetPathBegin")
    def reset_path_begin(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPathBegin", []))

    @builtins.property
    @jsii.member(jsii_name="fqdnInput")
    def fqdn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fqdnInput"))

    @builtins.property
    @jsii.member(jsii_name="pathBeginInput")
    def path_begin_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathBeginInput"))

    @builtins.property
    @jsii.member(jsii_name="fqdn")
    def fqdn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fqdn"))

    @fqdn.setter
    def fqdn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04485a6beaf860adef8aae35f87bb920bee4738df014dee3254392ef62a504d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fqdn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pathBegin")
    def path_begin(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pathBegin"))

    @path_begin.setter
    def path_begin(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ef47c38c5f78d8740feb84869da07696ce5b94869cd8c51802483bc5d59130b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pathBegin", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[VVhosts, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[VVhosts, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[VVhosts, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7b59426c9a34c6edc78c2fa44298f7eed0b93c547b342c4c2aa6afdc2da23a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "V",
    "VConfig",
    "VDeployment",
    "VDeploymentOutputReference",
    "VHooks",
    "VHooksOutputReference",
    "VNetworkgroups",
    "VNetworkgroupsList",
    "VNetworkgroupsOutputReference",
    "VVhosts",
    "VVhostsList",
    "VVhostsOutputReference",
]

publication.publish()

def _typecheckingstub__0be89165938ff4e953a35e2b6f1152b17f05de0b39b1ca76ccf966d53f847ba6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    biggest_flavor: builtins.str,
    max_instance_count: jsii.Number,
    min_instance_count: jsii.Number,
    name: builtins.str,
    smallest_flavor: builtins.str,
    app_folder: typing.Optional[builtins.str] = None,
    binary: typing.Optional[builtins.str] = None,
    build_flavor: typing.Optional[builtins.str] = None,
    dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
    deployment: typing.Optional[typing.Union[VDeployment, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    development_build: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    exposed_environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    hooks: typing.Optional[typing.Union[VHooks, typing.Dict[builtins.str, typing.Any]]] = None,
    networkgroups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VNetworkgroups, typing.Dict[builtins.str, typing.Any]]]]] = None,
    redirect_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    region: typing.Optional[builtins.str] = None,
    sticky_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    vhosts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VVhosts, typing.Dict[builtins.str, typing.Any]]]]] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83ee19f5792ebd6ab19714d07b816253b62aa556a92a87978aac7a498ca0f7e8(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7bb5ae5d2c472703d7fd72fc50b4c8df42c1d128136ad17fffd3a17d9586f8b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VNetworkgroups, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__736b03f855363f89e2d3ca725bf6b64a6f4288e02217b4580d452ae685ac6425(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VVhosts, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__080c96f9990c14014ed5704718e9c8c25c76df5638bbe74610a7ba57e63492c0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4d55f603678e4790ba92fcf0ce95289cfd655795e9b5a64c0f11331c407f645(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e7e1261f48d8016b5ceecf43c889725f93c24d2e085d12f6cf6c417f5ffebd5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe7d2c86e4ac0ee3c5cfc772c222bc5ec52fe8b4ede87a727adbc59ccbf7a862(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49a6360d8e4b88f1ff750bc1bc4e8049bb7c4d0d16cf402a6fde471c6a281491(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65e0d987cad1a91ed46dbeb8f7fd3a1ceab74df6a9189341098d37ce2a30d0c1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed090270c1accc2b60298751f3e26312a32853de2bb60c77ca51b1ca1194a52e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__692be0eb2000203a9027c69ef3fdfaf7158704309b5ae9f6324795ad2b610842(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3f0f67ab6f9f7afe3235816bf6dc808a2bbcf02b53d5017763212b990f6f022(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1d92b12f3157290136d3c3615cf1138755d22fc45f297576e871742179381ab(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd582229bb233210f71b2d660d0da9444542ce38f90878896bd66565b5cf1d83(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f1f46a76a897da2bafd7f2069be91a8f8551b82751856ff458d167f4f9f9f36(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3355813390c837c8b49ba9d8bb5cfb8b4a875a48c3a6d3d98a248e289c8eec85(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__724d3b5ccd1e1a7d5bfa890d0b2e103c4f26d914c3e4e5258407a9cda3758dae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02f4de4c283d23e8be5bd66063bb2b06e59f048f3e66b7b70c7de0ed006e7a39(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e13af34a933ea59253dedde046de0230daf2d56a6cc78a12d17930d3004d9c8d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e342bce7390dbebe6813752e21999473fb95ba5bed833120e5c2194eb972f3a(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    biggest_flavor: builtins.str,
    max_instance_count: jsii.Number,
    min_instance_count: jsii.Number,
    name: builtins.str,
    smallest_flavor: builtins.str,
    app_folder: typing.Optional[builtins.str] = None,
    binary: typing.Optional[builtins.str] = None,
    build_flavor: typing.Optional[builtins.str] = None,
    dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
    deployment: typing.Optional[typing.Union[VDeployment, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    development_build: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    exposed_environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    hooks: typing.Optional[typing.Union[VHooks, typing.Dict[builtins.str, typing.Any]]] = None,
    networkgroups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VNetworkgroups, typing.Dict[builtins.str, typing.Any]]]]] = None,
    redirect_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    region: typing.Optional[builtins.str] = None,
    sticky_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    vhosts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[VVhosts, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83053c2350a68397b6754210aae9147dfeacddeacd9bbed9182e416a1b5c9f23(
    *,
    authentication_basic: typing.Optional[builtins.str] = None,
    commit: typing.Optional[builtins.str] = None,
    repository: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd07c778458fd9d71acd0b8364681a879485e7ab33647d793224117efbcc4523(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37265efcfecf9c4ee1f980c250f9b6edda9c6e14bdeb1c4ef2b31539f1fb69b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48fba627150d51b54c38ec30ab0bf6f15a5e46a2234f8845041c75cede3671dc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df11554ca37f1aa3fb94293d22307d8cfee62f2e1bf92dac1fdb6f82ecb22e31(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__766b3fc8b8d9e44a26ebace16d23a41d4f4f5b06051f7b2f5a12e949074a1783(
    value: typing.Optional[typing.Union[VDeployment, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12cd9ab521592cbf22e0258aceaa7f06f0c8e26d746a1eee16a502b3a01ae85d(
    *,
    post_build: typing.Optional[builtins.str] = None,
    pre_build: typing.Optional[builtins.str] = None,
    pre_run: typing.Optional[builtins.str] = None,
    run_failed: typing.Optional[builtins.str] = None,
    run_succeed: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4d5b3ab09ba353a7b60ab9e1d3fca5f004ceca8ac866208a0e9bf3363e160a6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59d706f15743b0dacd5f3e572645d061d28ec9b86441bd753744078ac7658aeb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b07c0030e63b612a94ce2a46334b28268a7aaea429e22eeb8687365da3fe95a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b558c4b9e2b4b3a05d5f7826a98975e44a1f5c9f601d2624ed4010d5ecf22a7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ba87dc0d4f410eb336fc5028a78dbed8ba2699ac9711569760c4be8d24adee4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__461fbac61ef7aca3ac054c56bca6b8fec2d440e2e09cf98a6d3d47b7bba46bb5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2b50412574c029f237b9de0dda5d7bd9b5dfc648ada993faaa6e64a1b355132(
    value: typing.Optional[typing.Union[VHooks, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c27eeb5f965d374f9e573c62a0e50bd9af80b9fefb047aa4b004ae00071c1831(
    *,
    fqdn: builtins.str,
    networkgroup_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ad15fce2350f935296d0937621e7f687fd75de42992119076717817b74ef569(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2307ec6c829dba68a5ba9ef249665935f77b704aa3e564817897e61404436856(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02221834b58cabd91c73c0febff04e222b1a1462adaf4c0a91a3b344e7be3a07(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bba8f8232e133d847511057c814f057985dab9e62f2a7fafe749fb0e49c125f9(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0949c1c1bc9ef300ec538c80d410eda9fc2ce6e98a79e23bd98e76d81476eee(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2161e43c07868ba56a13edb0af3e764782a0e41ad58d501472f6f5d2f7f301e6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VNetworkgroups]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc496f2fcf918efd6a1aa4b842eeaddf77c5828252536e8532c363175428ad16(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72e1f41788a113d2df0c902de88af9bcbe08e93432699b90118c25fbd6d9017f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09bfe8711bab892ed97804a0ec15123331c590bc0a2122c4db6a2b7308b3b0da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9b70e65212d2ee2d5a51750ae6739de57e7bcb82afa046e308d46cdd57a02c2(
    value: typing.Optional[typing.Union[VNetworkgroups, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3507e05ded9ec175ce9cd97d1db18925cde44c90eea95f9f6d5c2cbb466029c5(
    *,
    fqdn: builtins.str,
    path_begin: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f62d12b23fc9f67bdb303aa9c0a2c2ec02512386723c7117bb59805771e0f168(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82c9127b52eff97c0a70d195d9a00c69f60113cd3e5b518a367f5a61993ddc78(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5061a1c976a1a061efd27d35a0c50ba474fde2618a5b231b5ecea0a8e2d9ee1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__476acccc1950e8900cd93d1d6f2de92c5326fa525242c8b0b995b32fe64f65e8(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__daf31c1fa0d6d9b7ab8c47dddd5c32fb358cba892d1bbdda2f215ca8dc868464(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98efae27907a529d543c3606d629ee1f2ba5bd9b77d6a34ee5ff88de24da29c9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[VVhosts]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc929574452d8e3dfeaf5ed92f01185de87e0465818103252023374fe342ae52(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04485a6beaf860adef8aae35f87bb920bee4738df014dee3254392ef62a504d1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ef47c38c5f78d8740feb84869da07696ce5b94869cd8c51802483bc5d59130b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7b59426c9a34c6edc78c2fa44298f7eed0b93c547b342c4c2aa6afdc2da23a3(
    value: typing.Optional[typing.Union[VVhosts, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass
