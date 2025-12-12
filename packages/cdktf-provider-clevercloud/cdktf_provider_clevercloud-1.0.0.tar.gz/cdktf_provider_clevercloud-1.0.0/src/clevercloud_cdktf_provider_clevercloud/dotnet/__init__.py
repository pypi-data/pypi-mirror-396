r'''
# `clevercloud_dotnet`

Refer to the Terraform Registry for docs: [`clevercloud_dotnet`](https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet).
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


class Dotnet(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.dotnet.Dotnet",
):
    '''Represents a {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet clevercloud_dotnet}.'''

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
        build_flavor: typing.Optional[builtins.str] = None,
        dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        deployment: typing.Optional[typing.Union["DotnetDeployment", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        exposed_environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        hooks: typing.Optional[typing.Union["DotnetHooks", typing.Dict[builtins.str, typing.Any]]] = None,
        networkgroups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DotnetNetworkgroups", typing.Dict[builtins.str, typing.Any]]]]] = None,
        profile: typing.Optional[builtins.str] = None,
        proj: typing.Optional[builtins.str] = None,
        redirect_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        region: typing.Optional[builtins.str] = None,
        sticky_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tfm: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
        vhosts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DotnetVhosts", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet clevercloud_dotnet} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param biggest_flavor: Biggest instance flavor, if different from smallest, enable auto-scaling. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#biggest_flavor Dotnet#biggest_flavor}
        :param max_instance_count: Maximum instance count, if different from min value, enable auto-scaling. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#max_instance_count Dotnet#max_instance_count}
        :param min_instance_count: Minimum instance count. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#min_instance_count Dotnet#min_instance_count}
        :param name: Application name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#name Dotnet#name}
        :param smallest_flavor: Smallest instance flavor. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#smallest_flavor Dotnet#smallest_flavor}
        :param app_folder: Folder in which the application is located (inside the git repository). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#app_folder Dotnet#app_folder}
        :param build_flavor: Use dedicated instance with given flavor for build phase. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#build_flavor Dotnet#build_flavor}
        :param dependencies: A list of application or add-ons required to run this application. Can be either app_xxx or postgres_yyy ID format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#dependencies Dotnet#dependencies}
        :param deployment: deployment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#deployment Dotnet#deployment}
        :param description: Application description. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#description Dotnet#description}
        :param environment: Environment variables injected into the application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#environment Dotnet#environment}
        :param exposed_environment: Environment variables other linked applications will be able to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#exposed_environment Dotnet#exposed_environment}
        :param hooks: hooks block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#hooks Dotnet#hooks}
        :param networkgroups: List of networkgroups the application must be part of. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#networkgroups Dotnet#networkgroups}
        :param profile: Override the build configuration settings in your project. Default: Release. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#profile Dotnet#profile}
        :param proj: The name of your project file to use for the build, without the .csproj / .fsproj / .vbproj extension. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#proj Dotnet#proj}
        :param redirect_https: Redirect client from plain to TLS port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#redirect_https Dotnet#redirect_https}
        :param region: Geographical region where the database will be deployed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#region Dotnet#region}
        :param sticky_sessions: Enable sticky sessions, use it when your client sessions are instances scoped. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#sticky_sessions Dotnet#sticky_sessions}
        :param tfm: Compiles for a specific framework. The framework must be defined in the project file. Example : net5.0. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#tfm Dotnet#tfm}
        :param version: Choose the .NET Core version between 6.0, 8.0, 9.0. Default: '8.0'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#version Dotnet#version}
        :param vhosts: List of virtual hosts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#vhosts Dotnet#vhosts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__079edfc6d1761f284ccc0d85a2d33a66b852660fa7978a92f09a139558247d49)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DotnetConfig(
            biggest_flavor=biggest_flavor,
            max_instance_count=max_instance_count,
            min_instance_count=min_instance_count,
            name=name,
            smallest_flavor=smallest_flavor,
            app_folder=app_folder,
            build_flavor=build_flavor,
            dependencies=dependencies,
            deployment=deployment,
            description=description,
            environment=environment,
            exposed_environment=exposed_environment,
            hooks=hooks,
            networkgroups=networkgroups,
            profile=profile,
            proj=proj,
            redirect_https=redirect_https,
            region=region,
            sticky_sessions=sticky_sessions,
            tfm=tfm,
            version=version,
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
        '''Generates CDKTF code for importing a Dotnet resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the Dotnet to import.
        :param import_from_id: The id of the existing Dotnet that should be imported. Refer to the {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the Dotnet to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9f6c5e934026b164d75c4e263cb90958cd33320e84660d54691c97bdb67fdbf)
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
        :param authentication_basic: user ans password ':' separated, (PersonalAccessToken in Github case). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#authentication_basic Dotnet#authentication_basic}
        :param commit: Support multiple syntax like ``refs/heads/[BRANCH]``, ``github_hook`` or ``[COMMIT]``, when using the special value ``github_hook``, we will link the application to the Github repository. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#commit Dotnet#commit}
        :param repository: The repository URL to deploy, can be 'https://...', 'file://...'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#repository Dotnet#repository}
        '''
        value = DotnetDeployment(
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
        :param post_build: `CC_POST_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#post-build>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#post_build Dotnet#post_build}
        :param pre_build: `CC_PRE_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-build>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#pre_build Dotnet#pre_build}
        :param pre_run: `CC_PRE_RUN_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-run>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#pre_run Dotnet#pre_run}
        :param run_failed: `CC_RUN_FAILED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#run_failed Dotnet#run_failed}
        :param run_succeed: `CC_RUN_SUCCEEDED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#run_succeed Dotnet#run_succeed}
        '''
        value = DotnetHooks(
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
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DotnetNetworkgroups", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a74acbe6686ea3e3db3531bc303f1a01efd78a436141e4a14b82c43eeefa25e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetworkgroups", [value]))

    @jsii.member(jsii_name="putVhosts")
    def put_vhosts(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DotnetVhosts", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e9de03e1aa1c76e02480ae6495a09b73ad5f2594d6ee4c71f24685229df667a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putVhosts", [value]))

    @jsii.member(jsii_name="resetAppFolder")
    def reset_app_folder(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAppFolder", []))

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

    @jsii.member(jsii_name="resetProfile")
    def reset_profile(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProfile", []))

    @jsii.member(jsii_name="resetProj")
    def reset_proj(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProj", []))

    @jsii.member(jsii_name="resetRedirectHttps")
    def reset_redirect_https(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedirectHttps", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetStickySessions")
    def reset_sticky_sessions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStickySessions", []))

    @jsii.member(jsii_name="resetTfm")
    def reset_tfm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTfm", []))

    @jsii.member(jsii_name="resetVersion")
    def reset_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersion", []))

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
    def deployment(self) -> "DotnetDeploymentOutputReference":
        return typing.cast("DotnetDeploymentOutputReference", jsii.get(self, "deployment"))

    @builtins.property
    @jsii.member(jsii_name="deployUrl")
    def deploy_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deployUrl"))

    @builtins.property
    @jsii.member(jsii_name="hooks")
    def hooks(self) -> "DotnetHooksOutputReference":
        return typing.cast("DotnetHooksOutputReference", jsii.get(self, "hooks"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="networkgroups")
    def networkgroups(self) -> "DotnetNetworkgroupsList":
        return typing.cast("DotnetNetworkgroupsList", jsii.get(self, "networkgroups"))

    @builtins.property
    @jsii.member(jsii_name="vhosts")
    def vhosts(self) -> "DotnetVhostsList":
        return typing.cast("DotnetVhostsList", jsii.get(self, "vhosts"))

    @builtins.property
    @jsii.member(jsii_name="appFolderInput")
    def app_folder_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appFolderInput"))

    @builtins.property
    @jsii.member(jsii_name="biggestFlavorInput")
    def biggest_flavor_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "biggestFlavorInput"))

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
    ) -> typing.Optional[typing.Union["DotnetDeployment", _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["DotnetDeployment", _cdktf_9a9027ec.IResolvable]], jsii.get(self, "deploymentInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

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
    ) -> typing.Optional[typing.Union["DotnetHooks", _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["DotnetHooks", _cdktf_9a9027ec.IResolvable]], jsii.get(self, "hooksInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DotnetNetworkgroups"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DotnetNetworkgroups"]]], jsii.get(self, "networkgroupsInput"))

    @builtins.property
    @jsii.member(jsii_name="profileInput")
    def profile_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "profileInput"))

    @builtins.property
    @jsii.member(jsii_name="projInput")
    def proj_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projInput"))

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
    @jsii.member(jsii_name="tfmInput")
    def tfm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tfmInput"))

    @builtins.property
    @jsii.member(jsii_name="versionInput")
    def version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionInput"))

    @builtins.property
    @jsii.member(jsii_name="vhostsInput")
    def vhosts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DotnetVhosts"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DotnetVhosts"]]], jsii.get(self, "vhostsInput"))

    @builtins.property
    @jsii.member(jsii_name="appFolder")
    def app_folder(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appFolder"))

    @app_folder.setter
    def app_folder(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f63a95972cf41dd26099e2a83bcc01a6d87cd1ea68f5e2f2829eac016de62f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appFolder", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="biggestFlavor")
    def biggest_flavor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "biggestFlavor"))

    @biggest_flavor.setter
    def biggest_flavor(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bac19c35ca5a76fc7dd17cfd9c6cd039de59efcadc0bfd9cbff3af6f536a3224)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "biggestFlavor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="buildFlavor")
    def build_flavor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "buildFlavor"))

    @build_flavor.setter
    def build_flavor(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__adb3cf335a2f48329aabb97e26662ecb28968c2c9a069edc46c17d2e249ea870)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "buildFlavor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dependencies")
    def dependencies(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dependencies"))

    @dependencies.setter
    def dependencies(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a64e4d2ef7974228ccf9133a9fffef1cf59ec246792f109e3ad95ad3d807c172)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dependencies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17fe3e53363ab1eee24d0882ae48537d98172d65267de5ca7a64a085eb140934)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "environment"))

    @environment.setter
    def environment(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5886172031cf48a86e35091e522bbf706264ce0ec2d011626d8efd3a7aa24b6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1d23478ab584654bda3fb21913556b44e45f572913c9b38b92bb00e915c53306)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exposedEnvironment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxInstanceCount")
    def max_instance_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxInstanceCount"))

    @max_instance_count.setter
    def max_instance_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7da6f4772a60f83b98ffe45f79019eff7054438dee67d39741f8ad31dc3dc43f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxInstanceCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minInstanceCount")
    def min_instance_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minInstanceCount"))

    @min_instance_count.setter
    def min_instance_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__409f58b0ac148221ac0033430d53d15e997edf49b0ea26478f576a689b86c7a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minInstanceCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05024b7083a9c67ef76d4920f5439d6703efdf9e3612c7a0b7187a2b075f0a9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="profile")
    def profile(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "profile"))

    @profile.setter
    def profile(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acb5dbd933364a8fe334d70a7770ae9de4086b9e38da173db87c0a6e6edafca4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "profile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="proj")
    def proj(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "proj"))

    @proj.setter
    def proj(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ffc3a8c11b4550e114e1cb58232b49e227cd76253ca1baafd558c0e70dd3030)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "proj", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__0b2f641cad150a24887991b9e94bbaa77da75997df81d122f3f48461afa100a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "redirectHttps", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__302c4637b971c4417aa73fcc6eaf7e128a658149a9495616e8d270f674c8e453)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="smallestFlavor")
    def smallest_flavor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "smallestFlavor"))

    @smallest_flavor.setter
    def smallest_flavor(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17dff512ac6ff3767590a2f9854ec402823724bd3dfe05956a79839463b21119)
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
            type_hints = typing.get_type_hints(_typecheckingstub__84d9472d8560413ee73b84571734dd7c186f76b02673e093f3d6569c594a2c76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stickySessions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tfm")
    def tfm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tfm"))

    @tfm.setter
    def tfm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bb486f30e7de12a6d2ed337c976ce39419c64e4677f27aedab84c8f1c35a549)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tfm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @version.setter
    def version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2bedd5f2514a22a5dfd2a0f2e5319f5509d26d4443c898351d86a0f5359822d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "version", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.dotnet.DotnetConfig",
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
        "build_flavor": "buildFlavor",
        "dependencies": "dependencies",
        "deployment": "deployment",
        "description": "description",
        "environment": "environment",
        "exposed_environment": "exposedEnvironment",
        "hooks": "hooks",
        "networkgroups": "networkgroups",
        "profile": "profile",
        "proj": "proj",
        "redirect_https": "redirectHttps",
        "region": "region",
        "sticky_sessions": "stickySessions",
        "tfm": "tfm",
        "version": "version",
        "vhosts": "vhosts",
    },
)
class DotnetConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        build_flavor: typing.Optional[builtins.str] = None,
        dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        deployment: typing.Optional[typing.Union["DotnetDeployment", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        exposed_environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        hooks: typing.Optional[typing.Union["DotnetHooks", typing.Dict[builtins.str, typing.Any]]] = None,
        networkgroups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DotnetNetworkgroups", typing.Dict[builtins.str, typing.Any]]]]] = None,
        profile: typing.Optional[builtins.str] = None,
        proj: typing.Optional[builtins.str] = None,
        redirect_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        region: typing.Optional[builtins.str] = None,
        sticky_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tfm: typing.Optional[builtins.str] = None,
        version: typing.Optional[builtins.str] = None,
        vhosts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DotnetVhosts", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param biggest_flavor: Biggest instance flavor, if different from smallest, enable auto-scaling. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#biggest_flavor Dotnet#biggest_flavor}
        :param max_instance_count: Maximum instance count, if different from min value, enable auto-scaling. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#max_instance_count Dotnet#max_instance_count}
        :param min_instance_count: Minimum instance count. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#min_instance_count Dotnet#min_instance_count}
        :param name: Application name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#name Dotnet#name}
        :param smallest_flavor: Smallest instance flavor. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#smallest_flavor Dotnet#smallest_flavor}
        :param app_folder: Folder in which the application is located (inside the git repository). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#app_folder Dotnet#app_folder}
        :param build_flavor: Use dedicated instance with given flavor for build phase. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#build_flavor Dotnet#build_flavor}
        :param dependencies: A list of application or add-ons required to run this application. Can be either app_xxx or postgres_yyy ID format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#dependencies Dotnet#dependencies}
        :param deployment: deployment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#deployment Dotnet#deployment}
        :param description: Application description. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#description Dotnet#description}
        :param environment: Environment variables injected into the application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#environment Dotnet#environment}
        :param exposed_environment: Environment variables other linked applications will be able to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#exposed_environment Dotnet#exposed_environment}
        :param hooks: hooks block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#hooks Dotnet#hooks}
        :param networkgroups: List of networkgroups the application must be part of. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#networkgroups Dotnet#networkgroups}
        :param profile: Override the build configuration settings in your project. Default: Release. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#profile Dotnet#profile}
        :param proj: The name of your project file to use for the build, without the .csproj / .fsproj / .vbproj extension. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#proj Dotnet#proj}
        :param redirect_https: Redirect client from plain to TLS port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#redirect_https Dotnet#redirect_https}
        :param region: Geographical region where the database will be deployed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#region Dotnet#region}
        :param sticky_sessions: Enable sticky sessions, use it when your client sessions are instances scoped. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#sticky_sessions Dotnet#sticky_sessions}
        :param tfm: Compiles for a specific framework. The framework must be defined in the project file. Example : net5.0. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#tfm Dotnet#tfm}
        :param version: Choose the .NET Core version between 6.0, 8.0, 9.0. Default: '8.0'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#version Dotnet#version}
        :param vhosts: List of virtual hosts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#vhosts Dotnet#vhosts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(deployment, dict):
            deployment = DotnetDeployment(**deployment)
        if isinstance(hooks, dict):
            hooks = DotnetHooks(**hooks)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84914d8c9672ebc340dd34dc2f79140dfc241c1e3de0368790ffd31603b67b62)
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
            check_type(argname="argument build_flavor", value=build_flavor, expected_type=type_hints["build_flavor"])
            check_type(argname="argument dependencies", value=dependencies, expected_type=type_hints["dependencies"])
            check_type(argname="argument deployment", value=deployment, expected_type=type_hints["deployment"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument exposed_environment", value=exposed_environment, expected_type=type_hints["exposed_environment"])
            check_type(argname="argument hooks", value=hooks, expected_type=type_hints["hooks"])
            check_type(argname="argument networkgroups", value=networkgroups, expected_type=type_hints["networkgroups"])
            check_type(argname="argument profile", value=profile, expected_type=type_hints["profile"])
            check_type(argname="argument proj", value=proj, expected_type=type_hints["proj"])
            check_type(argname="argument redirect_https", value=redirect_https, expected_type=type_hints["redirect_https"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument sticky_sessions", value=sticky_sessions, expected_type=type_hints["sticky_sessions"])
            check_type(argname="argument tfm", value=tfm, expected_type=type_hints["tfm"])
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
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
        if build_flavor is not None:
            self._values["build_flavor"] = build_flavor
        if dependencies is not None:
            self._values["dependencies"] = dependencies
        if deployment is not None:
            self._values["deployment"] = deployment
        if description is not None:
            self._values["description"] = description
        if environment is not None:
            self._values["environment"] = environment
        if exposed_environment is not None:
            self._values["exposed_environment"] = exposed_environment
        if hooks is not None:
            self._values["hooks"] = hooks
        if networkgroups is not None:
            self._values["networkgroups"] = networkgroups
        if profile is not None:
            self._values["profile"] = profile
        if proj is not None:
            self._values["proj"] = proj
        if redirect_https is not None:
            self._values["redirect_https"] = redirect_https
        if region is not None:
            self._values["region"] = region
        if sticky_sessions is not None:
            self._values["sticky_sessions"] = sticky_sessions
        if tfm is not None:
            self._values["tfm"] = tfm
        if version is not None:
            self._values["version"] = version
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#biggest_flavor Dotnet#biggest_flavor}
        '''
        result = self._values.get("biggest_flavor")
        assert result is not None, "Required property 'biggest_flavor' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def max_instance_count(self) -> jsii.Number:
        '''Maximum instance count, if different from min value, enable auto-scaling.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#max_instance_count Dotnet#max_instance_count}
        '''
        result = self._values.get("max_instance_count")
        assert result is not None, "Required property 'max_instance_count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_instance_count(self) -> jsii.Number:
        '''Minimum instance count.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#min_instance_count Dotnet#min_instance_count}
        '''
        result = self._values.get("min_instance_count")
        assert result is not None, "Required property 'min_instance_count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Application name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#name Dotnet#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def smallest_flavor(self) -> builtins.str:
        '''Smallest instance flavor.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#smallest_flavor Dotnet#smallest_flavor}
        '''
        result = self._values.get("smallest_flavor")
        assert result is not None, "Required property 'smallest_flavor' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def app_folder(self) -> typing.Optional[builtins.str]:
        '''Folder in which the application is located (inside the git repository).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#app_folder Dotnet#app_folder}
        '''
        result = self._values.get("app_folder")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_flavor(self) -> typing.Optional[builtins.str]:
        '''Use dedicated instance with given flavor for build phase.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#build_flavor Dotnet#build_flavor}
        '''
        result = self._values.get("build_flavor")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dependencies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of application or add-ons required to run this application. Can be either app_xxx or postgres_yyy ID format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#dependencies Dotnet#dependencies}
        '''
        result = self._values.get("dependencies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def deployment(self) -> typing.Optional["DotnetDeployment"]:
        '''deployment block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#deployment Dotnet#deployment}
        '''
        result = self._values.get("deployment")
        return typing.cast(typing.Optional["DotnetDeployment"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Application description.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#description Dotnet#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Environment variables injected into the application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#environment Dotnet#environment}
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def exposed_environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Environment variables other linked applications will be able to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#exposed_environment Dotnet#exposed_environment}
        '''
        result = self._values.get("exposed_environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def hooks(self) -> typing.Optional["DotnetHooks"]:
        '''hooks block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#hooks Dotnet#hooks}
        '''
        result = self._values.get("hooks")
        return typing.cast(typing.Optional["DotnetHooks"], result)

    @builtins.property
    def networkgroups(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DotnetNetworkgroups"]]]:
        '''List of networkgroups the application must be part of.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#networkgroups Dotnet#networkgroups}
        '''
        result = self._values.get("networkgroups")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DotnetNetworkgroups"]]], result)

    @builtins.property
    def profile(self) -> typing.Optional[builtins.str]:
        '''Override the build configuration settings in your project. Default: Release.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#profile Dotnet#profile}
        '''
        result = self._values.get("profile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def proj(self) -> typing.Optional[builtins.str]:
        '''The name of your project file to use for the build, without the .csproj / .fsproj / .vbproj extension.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#proj Dotnet#proj}
        '''
        result = self._values.get("proj")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def redirect_https(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Redirect client from plain to TLS port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#redirect_https Dotnet#redirect_https}
        '''
        result = self._values.get("redirect_https")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Geographical region where the database will be deployed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#region Dotnet#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sticky_sessions(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable sticky sessions, use it when your client sessions are instances scoped.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#sticky_sessions Dotnet#sticky_sessions}
        '''
        result = self._values.get("sticky_sessions")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tfm(self) -> typing.Optional[builtins.str]:
        '''Compiles for a specific framework. The framework must be defined in the project file. Example : net5.0.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#tfm Dotnet#tfm}
        '''
        result = self._values.get("tfm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Choose the .NET Core version between 6.0, 8.0, 9.0. Default: '8.0'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#version Dotnet#version}
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vhosts(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DotnetVhosts"]]]:
        '''List of virtual hosts.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#vhosts Dotnet#vhosts}
        '''
        result = self._values.get("vhosts")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DotnetVhosts"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DotnetConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.dotnet.DotnetDeployment",
    jsii_struct_bases=[],
    name_mapping={
        "authentication_basic": "authenticationBasic",
        "commit": "commit",
        "repository": "repository",
    },
)
class DotnetDeployment:
    def __init__(
        self,
        *,
        authentication_basic: typing.Optional[builtins.str] = None,
        commit: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param authentication_basic: user ans password ':' separated, (PersonalAccessToken in Github case). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#authentication_basic Dotnet#authentication_basic}
        :param commit: Support multiple syntax like ``refs/heads/[BRANCH]``, ``github_hook`` or ``[COMMIT]``, when using the special value ``github_hook``, we will link the application to the Github repository. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#commit Dotnet#commit}
        :param repository: The repository URL to deploy, can be 'https://...', 'file://...'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#repository Dotnet#repository}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__841346e596e11f1060ab5432268be0bb9e20e4f3fff16e216b8d9211ee71cb65)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#authentication_basic Dotnet#authentication_basic}
        '''
        result = self._values.get("authentication_basic")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def commit(self) -> typing.Optional[builtins.str]:
        '''Support multiple syntax like ``refs/heads/[BRANCH]``, ``github_hook`` or ``[COMMIT]``, when using the special value ``github_hook``, we will link the application to the Github repository.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#commit Dotnet#commit}
        '''
        result = self._values.get("commit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''The repository URL to deploy, can be 'https://...', 'file://...'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#repository Dotnet#repository}
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DotnetDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DotnetDeploymentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.dotnet.DotnetDeploymentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cf015d286a414ae77861aeb192faf35b04eba1a16f8ade492a359f5548d6cbba)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2244856ef6393e0170107db301828c8c7fe4e49f6bd96f499fb5282cb82479bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authenticationBasic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="commit")
    def commit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commit"))

    @commit.setter
    def commit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05f54b374cbd73ba7e8f4d25b916fe679e306d819f79f70f66f4f72f54dc1c41)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40ba8da3092ee670ee9ad9cfb622a81320f77cbc472bbf108c25078c2c49496e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "repository", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DotnetDeployment, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DotnetDeployment, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DotnetDeployment, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1c432add72570c5772720ca861a24f4d4a350c3af7c4020a1dc552e0b16f81b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.dotnet.DotnetHooks",
    jsii_struct_bases=[],
    name_mapping={
        "post_build": "postBuild",
        "pre_build": "preBuild",
        "pre_run": "preRun",
        "run_failed": "runFailed",
        "run_succeed": "runSucceed",
    },
)
class DotnetHooks:
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
        :param post_build: `CC_POST_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#post-build>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#post_build Dotnet#post_build}
        :param pre_build: `CC_PRE_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-build>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#pre_build Dotnet#pre_build}
        :param pre_run: `CC_PRE_RUN_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-run>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#pre_run Dotnet#pre_run}
        :param run_failed: `CC_RUN_FAILED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#run_failed Dotnet#run_failed}
        :param run_succeed: `CC_RUN_SUCCEEDED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#run_succeed Dotnet#run_succeed}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2c04e9810e36e0c30dc1c789a2c371510b6ab4372285a845f97c6effcaefdc7)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#post_build Dotnet#post_build}
        '''
        result = self._values.get("post_build")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_build(self) -> typing.Optional[builtins.str]:
        '''`CC_PRE_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-build>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#pre_build Dotnet#pre_build}
        '''
        result = self._values.get("pre_build")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_run(self) -> typing.Optional[builtins.str]:
        '''`CC_PRE_RUN_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-run>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#pre_run Dotnet#pre_run}
        '''
        result = self._values.get("pre_run")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run_failed(self) -> typing.Optional[builtins.str]:
        '''`CC_RUN_FAILED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#run_failed Dotnet#run_failed}
        '''
        result = self._values.get("run_failed")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run_succeed(self) -> typing.Optional[builtins.str]:
        '''`CC_RUN_SUCCEEDED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#run_succeed Dotnet#run_succeed}
        '''
        result = self._values.get("run_succeed")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DotnetHooks(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DotnetHooksOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.dotnet.DotnetHooksOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b661bd523c745032fb1e2476d71be6d21d3f2f6a73a8d4b0802f17453106e6f0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1bd9ca6eba902e7a3bb683a9958583aa4b6def3b5c7664fc1edba6bc5a44b8ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postBuild", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preBuild")
    def pre_build(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preBuild"))

    @pre_build.setter
    def pre_build(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45cba6eb9cd2d0aa34c1ad55415cfa792a07339b621253bad60669f671f50ff9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preBuild", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preRun")
    def pre_run(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preRun"))

    @pre_run.setter
    def pre_run(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72d41450d4a89601e69eef8cba8866a4ff826e9fa14bf581158670f5a4e57191)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runFailed")
    def run_failed(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runFailed"))

    @run_failed.setter
    def run_failed(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4e398fa409657ae25ecf3fded9aac234b60e22cc673c46d92aadee477b0a189)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runFailed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runSucceed")
    def run_succeed(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runSucceed"))

    @run_succeed.setter
    def run_succeed(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c73d250539a0fdbe0d331ea17d1068a3523e0e57d126a7594acc47b6c98bae7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runSucceed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DotnetHooks, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DotnetHooks, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DotnetHooks, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb5ac5e6f660b639c10a5ab1c91215dcd0a52b5a853b4d7d72fe605a0b134959)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.dotnet.DotnetNetworkgroups",
    jsii_struct_bases=[],
    name_mapping={"fqdn": "fqdn", "networkgroup_id": "networkgroupId"},
)
class DotnetNetworkgroups:
    def __init__(self, *, fqdn: builtins.str, networkgroup_id: builtins.str) -> None:
        '''
        :param fqdn: domain name which will resolve to application instances inside the networkgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#fqdn Dotnet#fqdn}
        :param networkgroup_id: ID of the networkgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#networkgroup_id Dotnet#networkgroup_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ce0a630417cede564fb4158b22fd38fa5131110ca42a84a18d1cf59fb1859e5)
            check_type(argname="argument fqdn", value=fqdn, expected_type=type_hints["fqdn"])
            check_type(argname="argument networkgroup_id", value=networkgroup_id, expected_type=type_hints["networkgroup_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "fqdn": fqdn,
            "networkgroup_id": networkgroup_id,
        }

    @builtins.property
    def fqdn(self) -> builtins.str:
        '''domain name which will resolve to application instances inside the networkgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#fqdn Dotnet#fqdn}
        '''
        result = self._values.get("fqdn")
        assert result is not None, "Required property 'fqdn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def networkgroup_id(self) -> builtins.str:
        '''ID of the networkgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#networkgroup_id Dotnet#networkgroup_id}
        '''
        result = self._values.get("networkgroup_id")
        assert result is not None, "Required property 'networkgroup_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DotnetNetworkgroups(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DotnetNetworkgroupsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.dotnet.DotnetNetworkgroupsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__17e515f4e17339c61d04cf3ee89f4e65d7cfaab5fe58f913f0ec0cea1a1ede50)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DotnetNetworkgroupsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f35c79abc6fd7773aca4873ef12c300ec1ed14841795957621d744aaf754a4c8)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DotnetNetworkgroupsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f188bba85214b3ef372ff5c2c2dd2befd90d8c7cd10c0593d1e61ae8bd4d4857)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f7cdbfe7174f81ddd8cb024b56e20159aef85ff4bdef6659f85ee4303d9968db)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0f6d96b37b90b253b909eb88739a09f85def4a54f834040fa9d7ea4ca31f38df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DotnetNetworkgroups]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DotnetNetworkgroups]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DotnetNetworkgroups]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d1f1bc8dc2f48a55df16f75f43e819ac7b9c6f52fadd10c0f69460e15f8a827)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DotnetNetworkgroupsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.dotnet.DotnetNetworkgroupsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__81fa5c36cbc31f301283b0e74ce7920423b65b1a48e9bdeb19b2172fa26b8097)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d4645c2a8088518ef9cc127a47537013266bd71974838e984123abbb0367dff3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fqdn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkgroupId")
    def networkgroup_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkgroupId"))

    @networkgroup_id.setter
    def networkgroup_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__096f20c0708e101066db0507c69f56920fcf3e00079e24eab66d3bdb91fe9bd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkgroupId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DotnetNetworkgroups, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DotnetNetworkgroups, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DotnetNetworkgroups, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0015091de3e49089cedf1b7eaab3c71618aba83d66c5281c097b8f24448efc82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.dotnet.DotnetVhosts",
    jsii_struct_bases=[],
    name_mapping={"fqdn": "fqdn", "path_begin": "pathBegin"},
)
class DotnetVhosts:
    def __init__(
        self,
        *,
        fqdn: builtins.str,
        path_begin: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param fqdn: Fully qualified domain name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#fqdn Dotnet#fqdn}
        :param path_begin: Any HTTP request starting with this path will be sent to this application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#path_begin Dotnet#path_begin}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3a4c9ced23df1b8dcb82e5ffc54908f64fd3a19afbd3ea065026276e39e459d)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#fqdn Dotnet#fqdn}
        '''
        result = self._values.get("fqdn")
        assert result is not None, "Required property 'fqdn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path_begin(self) -> typing.Optional[builtins.str]:
        '''Any HTTP request starting with this path will be sent to this application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/dotnet#path_begin Dotnet#path_begin}
        '''
        result = self._values.get("path_begin")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DotnetVhosts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DotnetVhostsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.dotnet.DotnetVhostsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__80f19bbac57cbdd60bd0405b77f6cf5dac074e1236a1f151582b350f719a2ea7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DotnetVhostsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0909b3dea129a5bcc44ad15e5254dff62daf2acbc30e1942b0c0c964de4c4ef)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DotnetVhostsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__730e77ba344f257e5e71c618bb095fdf3d0d890fd71f3437731cf29aba7788e7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3027b1fe3e12c9ea95f6621eb133ffef226095a516a9f95121c4e7d1cb51f699)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f6c0b73b4c3986d43fd0aa87add73d488bc04b6feda9faee6a7cca758ef73d5c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DotnetVhosts]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DotnetVhosts]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DotnetVhosts]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30e5ddd55994756ed309221c426fe75e7c1e0f1f22a651c84d085c679110a8cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DotnetVhostsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.dotnet.DotnetVhostsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__de7c947a29df9cc606c43e3cc970444e40121fc5ca4c9358bc1922f2f5177c44)
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
            type_hints = typing.get_type_hints(_typecheckingstub__41f610b352c6b5a1fb98f3a5df84222c44e3bbae31c49b179e6d22e801f8a56f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fqdn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pathBegin")
    def path_begin(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pathBegin"))

    @path_begin.setter
    def path_begin(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f749186c79106939b0cf6ac04282c6a0a29c2f52fdf68236ad60414ed4f07d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pathBegin", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DotnetVhosts, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DotnetVhosts, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DotnetVhosts, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b858b2a8429cca01b5dd8527552e9fe6e9e3f60aad242212fd22f7fba70cd4e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "Dotnet",
    "DotnetConfig",
    "DotnetDeployment",
    "DotnetDeploymentOutputReference",
    "DotnetHooks",
    "DotnetHooksOutputReference",
    "DotnetNetworkgroups",
    "DotnetNetworkgroupsList",
    "DotnetNetworkgroupsOutputReference",
    "DotnetVhosts",
    "DotnetVhostsList",
    "DotnetVhostsOutputReference",
]

publication.publish()

def _typecheckingstub__079edfc6d1761f284ccc0d85a2d33a66b852660fa7978a92f09a139558247d49(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    biggest_flavor: builtins.str,
    max_instance_count: jsii.Number,
    min_instance_count: jsii.Number,
    name: builtins.str,
    smallest_flavor: builtins.str,
    app_folder: typing.Optional[builtins.str] = None,
    build_flavor: typing.Optional[builtins.str] = None,
    dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
    deployment: typing.Optional[typing.Union[DotnetDeployment, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    exposed_environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    hooks: typing.Optional[typing.Union[DotnetHooks, typing.Dict[builtins.str, typing.Any]]] = None,
    networkgroups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DotnetNetworkgroups, typing.Dict[builtins.str, typing.Any]]]]] = None,
    profile: typing.Optional[builtins.str] = None,
    proj: typing.Optional[builtins.str] = None,
    redirect_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    region: typing.Optional[builtins.str] = None,
    sticky_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tfm: typing.Optional[builtins.str] = None,
    version: typing.Optional[builtins.str] = None,
    vhosts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DotnetVhosts, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__e9f6c5e934026b164d75c4e263cb90958cd33320e84660d54691c97bdb67fdbf(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a74acbe6686ea3e3db3531bc303f1a01efd78a436141e4a14b82c43eeefa25e7(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DotnetNetworkgroups, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e9de03e1aa1c76e02480ae6495a09b73ad5f2594d6ee4c71f24685229df667a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DotnetVhosts, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f63a95972cf41dd26099e2a83bcc01a6d87cd1ea68f5e2f2829eac016de62f5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bac19c35ca5a76fc7dd17cfd9c6cd039de59efcadc0bfd9cbff3af6f536a3224(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__adb3cf335a2f48329aabb97e26662ecb28968c2c9a069edc46c17d2e249ea870(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a64e4d2ef7974228ccf9133a9fffef1cf59ec246792f109e3ad95ad3d807c172(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17fe3e53363ab1eee24d0882ae48537d98172d65267de5ca7a64a085eb140934(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5886172031cf48a86e35091e522bbf706264ce0ec2d011626d8efd3a7aa24b6(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d23478ab584654bda3fb21913556b44e45f572913c9b38b92bb00e915c53306(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7da6f4772a60f83b98ffe45f79019eff7054438dee67d39741f8ad31dc3dc43f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__409f58b0ac148221ac0033430d53d15e997edf49b0ea26478f576a689b86c7a9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05024b7083a9c67ef76d4920f5439d6703efdf9e3612c7a0b7187a2b075f0a9b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acb5dbd933364a8fe334d70a7770ae9de4086b9e38da173db87c0a6e6edafca4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ffc3a8c11b4550e114e1cb58232b49e227cd76253ca1baafd558c0e70dd3030(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b2f641cad150a24887991b9e94bbaa77da75997df81d122f3f48461afa100a7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__302c4637b971c4417aa73fcc6eaf7e128a658149a9495616e8d270f674c8e453(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17dff512ac6ff3767590a2f9854ec402823724bd3dfe05956a79839463b21119(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84d9472d8560413ee73b84571734dd7c186f76b02673e093f3d6569c594a2c76(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bb486f30e7de12a6d2ed337c976ce39419c64e4677f27aedab84c8f1c35a549(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2bedd5f2514a22a5dfd2a0f2e5319f5509d26d4443c898351d86a0f5359822d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84914d8c9672ebc340dd34dc2f79140dfc241c1e3de0368790ffd31603b67b62(
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
    build_flavor: typing.Optional[builtins.str] = None,
    dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
    deployment: typing.Optional[typing.Union[DotnetDeployment, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    exposed_environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    hooks: typing.Optional[typing.Union[DotnetHooks, typing.Dict[builtins.str, typing.Any]]] = None,
    networkgroups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DotnetNetworkgroups, typing.Dict[builtins.str, typing.Any]]]]] = None,
    profile: typing.Optional[builtins.str] = None,
    proj: typing.Optional[builtins.str] = None,
    redirect_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    region: typing.Optional[builtins.str] = None,
    sticky_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tfm: typing.Optional[builtins.str] = None,
    version: typing.Optional[builtins.str] = None,
    vhosts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DotnetVhosts, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__841346e596e11f1060ab5432268be0bb9e20e4f3fff16e216b8d9211ee71cb65(
    *,
    authentication_basic: typing.Optional[builtins.str] = None,
    commit: typing.Optional[builtins.str] = None,
    repository: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf015d286a414ae77861aeb192faf35b04eba1a16f8ade492a359f5548d6cbba(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2244856ef6393e0170107db301828c8c7fe4e49f6bd96f499fb5282cb82479bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05f54b374cbd73ba7e8f4d25b916fe679e306d819f79f70f66f4f72f54dc1c41(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40ba8da3092ee670ee9ad9cfb622a81320f77cbc472bbf108c25078c2c49496e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1c432add72570c5772720ca861a24f4d4a350c3af7c4020a1dc552e0b16f81b(
    value: typing.Optional[typing.Union[DotnetDeployment, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2c04e9810e36e0c30dc1c789a2c371510b6ab4372285a845f97c6effcaefdc7(
    *,
    post_build: typing.Optional[builtins.str] = None,
    pre_build: typing.Optional[builtins.str] = None,
    pre_run: typing.Optional[builtins.str] = None,
    run_failed: typing.Optional[builtins.str] = None,
    run_succeed: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b661bd523c745032fb1e2476d71be6d21d3f2f6a73a8d4b0802f17453106e6f0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bd9ca6eba902e7a3bb683a9958583aa4b6def3b5c7664fc1edba6bc5a44b8ea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45cba6eb9cd2d0aa34c1ad55415cfa792a07339b621253bad60669f671f50ff9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72d41450d4a89601e69eef8cba8866a4ff826e9fa14bf581158670f5a4e57191(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4e398fa409657ae25ecf3fded9aac234b60e22cc673c46d92aadee477b0a189(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c73d250539a0fdbe0d331ea17d1068a3523e0e57d126a7594acc47b6c98bae7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb5ac5e6f660b639c10a5ab1c91215dcd0a52b5a853b4d7d72fe605a0b134959(
    value: typing.Optional[typing.Union[DotnetHooks, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ce0a630417cede564fb4158b22fd38fa5131110ca42a84a18d1cf59fb1859e5(
    *,
    fqdn: builtins.str,
    networkgroup_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17e515f4e17339c61d04cf3ee89f4e65d7cfaab5fe58f913f0ec0cea1a1ede50(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f35c79abc6fd7773aca4873ef12c300ec1ed14841795957621d744aaf754a4c8(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f188bba85214b3ef372ff5c2c2dd2befd90d8c7cd10c0593d1e61ae8bd4d4857(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7cdbfe7174f81ddd8cb024b56e20159aef85ff4bdef6659f85ee4303d9968db(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f6d96b37b90b253b909eb88739a09f85def4a54f834040fa9d7ea4ca31f38df(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d1f1bc8dc2f48a55df16f75f43e819ac7b9c6f52fadd10c0f69460e15f8a827(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DotnetNetworkgroups]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81fa5c36cbc31f301283b0e74ce7920423b65b1a48e9bdeb19b2172fa26b8097(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4645c2a8088518ef9cc127a47537013266bd71974838e984123abbb0367dff3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__096f20c0708e101066db0507c69f56920fcf3e00079e24eab66d3bdb91fe9bd3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0015091de3e49089cedf1b7eaab3c71618aba83d66c5281c097b8f24448efc82(
    value: typing.Optional[typing.Union[DotnetNetworkgroups, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3a4c9ced23df1b8dcb82e5ffc54908f64fd3a19afbd3ea065026276e39e459d(
    *,
    fqdn: builtins.str,
    path_begin: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80f19bbac57cbdd60bd0405b77f6cf5dac074e1236a1f151582b350f719a2ea7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0909b3dea129a5bcc44ad15e5254dff62daf2acbc30e1942b0c0c964de4c4ef(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__730e77ba344f257e5e71c618bb095fdf3d0d890fd71f3437731cf29aba7788e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3027b1fe3e12c9ea95f6621eb133ffef226095a516a9f95121c4e7d1cb51f699(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6c0b73b4c3986d43fd0aa87add73d488bc04b6feda9faee6a7cca758ef73d5c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30e5ddd55994756ed309221c426fe75e7c1e0f1f22a651c84d085c679110a8cf(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DotnetVhosts]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de7c947a29df9cc606c43e3cc970444e40121fc5ca4c9358bc1922f2f5177c44(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41f610b352c6b5a1fb98f3a5df84222c44e3bbae31c49b179e6d22e801f8a56f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f749186c79106939b0cf6ac04282c6a0a29c2f52fdf68236ad60414ed4f07d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b858b2a8429cca01b5dd8527552e9fe6e9e3f60aad242212fd22f7fba70cd4e2(
    value: typing.Optional[typing.Union[DotnetVhosts, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass
