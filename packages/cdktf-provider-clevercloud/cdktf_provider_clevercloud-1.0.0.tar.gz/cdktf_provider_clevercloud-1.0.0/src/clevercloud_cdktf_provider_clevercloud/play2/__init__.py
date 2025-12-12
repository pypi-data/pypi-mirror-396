r'''
# `clevercloud_play2`

Refer to the Terraform Registry for docs: [`clevercloud_play2`](https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2).
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


class Play2(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.play2.Play2",
):
    '''Represents a {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2 clevercloud_play2}.'''

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
        deployment: typing.Optional[typing.Union["Play2Deployment", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        exposed_environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        hooks: typing.Optional[typing.Union["Play2Hooks", typing.Dict[builtins.str, typing.Any]]] = None,
        networkgroups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["Play2Networkgroups", typing.Dict[builtins.str, typing.Any]]]]] = None,
        redirect_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        region: typing.Optional[builtins.str] = None,
        sticky_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vhosts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["Play2Vhosts", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2 clevercloud_play2} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param biggest_flavor: Biggest instance flavor, if different from smallest, enable auto-scaling. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#biggest_flavor Play2#biggest_flavor}
        :param max_instance_count: Maximum instance count, if different from min value, enable auto-scaling. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#max_instance_count Play2#max_instance_count}
        :param min_instance_count: Minimum instance count. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#min_instance_count Play2#min_instance_count}
        :param name: Application name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#name Play2#name}
        :param smallest_flavor: Smallest instance flavor. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#smallest_flavor Play2#smallest_flavor}
        :param app_folder: Folder in which the application is located (inside the git repository). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#app_folder Play2#app_folder}
        :param build_flavor: Use dedicated instance with given flavor for build phase. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#build_flavor Play2#build_flavor}
        :param dependencies: A list of application or add-ons required to run this application. Can be either app_xxx or postgres_yyy ID format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#dependencies Play2#dependencies}
        :param deployment: deployment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#deployment Play2#deployment}
        :param description: Application description. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#description Play2#description}
        :param environment: Environment variables injected into the application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#environment Play2#environment}
        :param exposed_environment: Environment variables other linked applications will be able to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#exposed_environment Play2#exposed_environment}
        :param hooks: hooks block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#hooks Play2#hooks}
        :param networkgroups: List of networkgroups the application must be part of. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#networkgroups Play2#networkgroups}
        :param redirect_https: Redirect client from plain to TLS port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#redirect_https Play2#redirect_https}
        :param region: Geographical region where the database will be deployed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#region Play2#region}
        :param sticky_sessions: Enable sticky sessions, use it when your client sessions are instances scoped. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#sticky_sessions Play2#sticky_sessions}
        :param vhosts: List of virtual hosts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#vhosts Play2#vhosts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8eef2c0efef81e7de1f902e36d5c3a7b56931087b664b8a6a11f08cbee919b95)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = Play2Config(
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
        '''Generates CDKTF code for importing a Play2 resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the Play2 to import.
        :param import_from_id: The id of the existing Play2 that should be imported. Refer to the {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the Play2 to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb750810e003e8f121212e748dc6ca1ca161ad42c531b42d8e29a547f12c89d5)
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
        :param authentication_basic: user ans password ':' separated, (PersonalAccessToken in Github case). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#authentication_basic Play2#authentication_basic}
        :param commit: Support multiple syntax like ``refs/heads/[BRANCH]``, ``github_hook`` or ``[COMMIT]``, when using the special value ``github_hook``, we will link the application to the Github repository. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#commit Play2#commit}
        :param repository: The repository URL to deploy, can be 'https://...', 'file://...'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#repository Play2#repository}
        '''
        value = Play2Deployment(
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
        :param post_build: `CC_POST_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#post-build>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#post_build Play2#post_build}
        :param pre_build: `CC_PRE_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-build>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#pre_build Play2#pre_build}
        :param pre_run: `CC_PRE_RUN_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-run>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#pre_run Play2#pre_run}
        :param run_failed: `CC_RUN_FAILED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#run_failed Play2#run_failed}
        :param run_succeed: `CC_RUN_SUCCEEDED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#run_succeed Play2#run_succeed}
        '''
        value = Play2Hooks(
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
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["Play2Networkgroups", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0e2411a1eb7fb30e1f29fea03f38c68d0846b324251bf1978e4907496b471d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetworkgroups", [value]))

    @jsii.member(jsii_name="putVhosts")
    def put_vhosts(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["Play2Vhosts", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e07ae4c272b77803147204b00101fdd49ed5ee5ea480cd34fb080a6daba55a0d)
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
    def deployment(self) -> "Play2DeploymentOutputReference":
        return typing.cast("Play2DeploymentOutputReference", jsii.get(self, "deployment"))

    @builtins.property
    @jsii.member(jsii_name="deployUrl")
    def deploy_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deployUrl"))

    @builtins.property
    @jsii.member(jsii_name="hooks")
    def hooks(self) -> "Play2HooksOutputReference":
        return typing.cast("Play2HooksOutputReference", jsii.get(self, "hooks"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="networkgroups")
    def networkgroups(self) -> "Play2NetworkgroupsList":
        return typing.cast("Play2NetworkgroupsList", jsii.get(self, "networkgroups"))

    @builtins.property
    @jsii.member(jsii_name="vhosts")
    def vhosts(self) -> "Play2VhostsList":
        return typing.cast("Play2VhostsList", jsii.get(self, "vhosts"))

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
    ) -> typing.Optional[typing.Union["Play2Deployment", _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["Play2Deployment", _cdktf_9a9027ec.IResolvable]], jsii.get(self, "deploymentInput"))

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
    ) -> typing.Optional[typing.Union["Play2Hooks", _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["Play2Hooks", _cdktf_9a9027ec.IResolvable]], jsii.get(self, "hooksInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["Play2Networkgroups"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["Play2Networkgroups"]]], jsii.get(self, "networkgroupsInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["Play2Vhosts"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["Play2Vhosts"]]], jsii.get(self, "vhostsInput"))

    @builtins.property
    @jsii.member(jsii_name="appFolder")
    def app_folder(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appFolder"))

    @app_folder.setter
    def app_folder(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69038100301da676136745aa72cb6ab94aafb174e60edcfb479358a3fb524814)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appFolder", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="biggestFlavor")
    def biggest_flavor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "biggestFlavor"))

    @biggest_flavor.setter
    def biggest_flavor(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9340e3f465b85a8106c18c66081e94795902b44278fa8fb2ff2947a66376a8e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "biggestFlavor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="buildFlavor")
    def build_flavor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "buildFlavor"))

    @build_flavor.setter
    def build_flavor(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c8e08ee65adf1c9f238a2e0582bf28ef51d1ace33b05859ff417aa143ba7b47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "buildFlavor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dependencies")
    def dependencies(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dependencies"))

    @dependencies.setter
    def dependencies(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8fb3626dbb5f3d7038c3e50fa378f784af4dad530ac02f79fdf7d9ed6ec95012)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dependencies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c2215b28a314b376145dee7aadbfba3a2512ad9b3e4131e7409f2c7af7811ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "environment"))

    @environment.setter
    def environment(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6aa63cf5ceb3ca2475147fb9a27c7634f5294a77d95aa6a97d992e9de219cc2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__73ad8bf23fd370ecca51f35d59ed9b7b135305fd034709c00159dfb8de93db2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exposedEnvironment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxInstanceCount")
    def max_instance_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxInstanceCount"))

    @max_instance_count.setter
    def max_instance_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f94d88afe800f46613310da5e42cd01abc8d22058b3b6165d92f618f6debe6fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxInstanceCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minInstanceCount")
    def min_instance_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minInstanceCount"))

    @min_instance_count.setter
    def min_instance_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__872b41b70d205ab26fb2c1e45a2d719b729cc4293b67c7bf8126ed9696c83aea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minInstanceCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afb4b79c2629c7633cc40a1b62463ffd05d679f7745ffbb0e6fb1588471000ac)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5d712a78b1ef4c2c3cc72ca318955477befca9c180159212dedde46385c9b25b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "redirectHttps", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9c5b207602378e920f30cb5fe55b61b98626a449a440e0216a9cc060607bc01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="smallestFlavor")
    def smallest_flavor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "smallestFlavor"))

    @smallest_flavor.setter
    def smallest_flavor(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ae91950786e3327a7f47a4d7898854689dafb508e4a4d2f5d4b73cb48cbf230)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e5e82d966d21e1213bd0e2fae265cda27e018b3daaaf74845385fd548a6378a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stickySessions", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.play2.Play2Config",
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
        "redirect_https": "redirectHttps",
        "region": "region",
        "sticky_sessions": "stickySessions",
        "vhosts": "vhosts",
    },
)
class Play2Config(_cdktf_9a9027ec.TerraformMetaArguments):
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
        deployment: typing.Optional[typing.Union["Play2Deployment", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        exposed_environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        hooks: typing.Optional[typing.Union["Play2Hooks", typing.Dict[builtins.str, typing.Any]]] = None,
        networkgroups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["Play2Networkgroups", typing.Dict[builtins.str, typing.Any]]]]] = None,
        redirect_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        region: typing.Optional[builtins.str] = None,
        sticky_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vhosts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["Play2Vhosts", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param biggest_flavor: Biggest instance flavor, if different from smallest, enable auto-scaling. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#biggest_flavor Play2#biggest_flavor}
        :param max_instance_count: Maximum instance count, if different from min value, enable auto-scaling. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#max_instance_count Play2#max_instance_count}
        :param min_instance_count: Minimum instance count. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#min_instance_count Play2#min_instance_count}
        :param name: Application name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#name Play2#name}
        :param smallest_flavor: Smallest instance flavor. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#smallest_flavor Play2#smallest_flavor}
        :param app_folder: Folder in which the application is located (inside the git repository). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#app_folder Play2#app_folder}
        :param build_flavor: Use dedicated instance with given flavor for build phase. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#build_flavor Play2#build_flavor}
        :param dependencies: A list of application or add-ons required to run this application. Can be either app_xxx or postgres_yyy ID format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#dependencies Play2#dependencies}
        :param deployment: deployment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#deployment Play2#deployment}
        :param description: Application description. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#description Play2#description}
        :param environment: Environment variables injected into the application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#environment Play2#environment}
        :param exposed_environment: Environment variables other linked applications will be able to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#exposed_environment Play2#exposed_environment}
        :param hooks: hooks block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#hooks Play2#hooks}
        :param networkgroups: List of networkgroups the application must be part of. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#networkgroups Play2#networkgroups}
        :param redirect_https: Redirect client from plain to TLS port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#redirect_https Play2#redirect_https}
        :param region: Geographical region where the database will be deployed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#region Play2#region}
        :param sticky_sessions: Enable sticky sessions, use it when your client sessions are instances scoped. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#sticky_sessions Play2#sticky_sessions}
        :param vhosts: List of virtual hosts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#vhosts Play2#vhosts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(deployment, dict):
            deployment = Play2Deployment(**deployment)
        if isinstance(hooks, dict):
            hooks = Play2Hooks(**hooks)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e265ad5905d2815e65305b92e56ed3e23798b617e44f23e15ce8c967e0a1d37)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#biggest_flavor Play2#biggest_flavor}
        '''
        result = self._values.get("biggest_flavor")
        assert result is not None, "Required property 'biggest_flavor' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def max_instance_count(self) -> jsii.Number:
        '''Maximum instance count, if different from min value, enable auto-scaling.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#max_instance_count Play2#max_instance_count}
        '''
        result = self._values.get("max_instance_count")
        assert result is not None, "Required property 'max_instance_count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_instance_count(self) -> jsii.Number:
        '''Minimum instance count.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#min_instance_count Play2#min_instance_count}
        '''
        result = self._values.get("min_instance_count")
        assert result is not None, "Required property 'min_instance_count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Application name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#name Play2#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def smallest_flavor(self) -> builtins.str:
        '''Smallest instance flavor.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#smallest_flavor Play2#smallest_flavor}
        '''
        result = self._values.get("smallest_flavor")
        assert result is not None, "Required property 'smallest_flavor' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def app_folder(self) -> typing.Optional[builtins.str]:
        '''Folder in which the application is located (inside the git repository).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#app_folder Play2#app_folder}
        '''
        result = self._values.get("app_folder")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_flavor(self) -> typing.Optional[builtins.str]:
        '''Use dedicated instance with given flavor for build phase.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#build_flavor Play2#build_flavor}
        '''
        result = self._values.get("build_flavor")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dependencies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of application or add-ons required to run this application. Can be either app_xxx or postgres_yyy ID format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#dependencies Play2#dependencies}
        '''
        result = self._values.get("dependencies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def deployment(self) -> typing.Optional["Play2Deployment"]:
        '''deployment block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#deployment Play2#deployment}
        '''
        result = self._values.get("deployment")
        return typing.cast(typing.Optional["Play2Deployment"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Application description.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#description Play2#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Environment variables injected into the application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#environment Play2#environment}
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def exposed_environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Environment variables other linked applications will be able to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#exposed_environment Play2#exposed_environment}
        '''
        result = self._values.get("exposed_environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def hooks(self) -> typing.Optional["Play2Hooks"]:
        '''hooks block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#hooks Play2#hooks}
        '''
        result = self._values.get("hooks")
        return typing.cast(typing.Optional["Play2Hooks"], result)

    @builtins.property
    def networkgroups(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["Play2Networkgroups"]]]:
        '''List of networkgroups the application must be part of.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#networkgroups Play2#networkgroups}
        '''
        result = self._values.get("networkgroups")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["Play2Networkgroups"]]], result)

    @builtins.property
    def redirect_https(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Redirect client from plain to TLS port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#redirect_https Play2#redirect_https}
        '''
        result = self._values.get("redirect_https")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Geographical region where the database will be deployed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#region Play2#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sticky_sessions(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable sticky sessions, use it when your client sessions are instances scoped.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#sticky_sessions Play2#sticky_sessions}
        '''
        result = self._values.get("sticky_sessions")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def vhosts(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["Play2Vhosts"]]]:
        '''List of virtual hosts.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#vhosts Play2#vhosts}
        '''
        result = self._values.get("vhosts")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["Play2Vhosts"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Play2Config(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.play2.Play2Deployment",
    jsii_struct_bases=[],
    name_mapping={
        "authentication_basic": "authenticationBasic",
        "commit": "commit",
        "repository": "repository",
    },
)
class Play2Deployment:
    def __init__(
        self,
        *,
        authentication_basic: typing.Optional[builtins.str] = None,
        commit: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param authentication_basic: user ans password ':' separated, (PersonalAccessToken in Github case). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#authentication_basic Play2#authentication_basic}
        :param commit: Support multiple syntax like ``refs/heads/[BRANCH]``, ``github_hook`` or ``[COMMIT]``, when using the special value ``github_hook``, we will link the application to the Github repository. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#commit Play2#commit}
        :param repository: The repository URL to deploy, can be 'https://...', 'file://...'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#repository Play2#repository}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c4da16250b350fed500689fd25159cef58f1bddc913ff6ec4cf1bc3206faaf0)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#authentication_basic Play2#authentication_basic}
        '''
        result = self._values.get("authentication_basic")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def commit(self) -> typing.Optional[builtins.str]:
        '''Support multiple syntax like ``refs/heads/[BRANCH]``, ``github_hook`` or ``[COMMIT]``, when using the special value ``github_hook``, we will link the application to the Github repository.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#commit Play2#commit}
        '''
        result = self._values.get("commit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''The repository URL to deploy, can be 'https://...', 'file://...'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#repository Play2#repository}
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Play2Deployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Play2DeploymentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.play2.Play2DeploymentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__044f4c86b9bc8dffc42c53eae5ad9b2b239bc775bae3beff197008e48089adef)
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
            type_hints = typing.get_type_hints(_typecheckingstub__eeab5609c5be85dd416de297f50b07f7e8968bb879aec63f5f2c7dfd8848fbaf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authenticationBasic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="commit")
    def commit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commit"))

    @commit.setter
    def commit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdea4f65e8f4be5f1131df9b7bb51d32fbe4d1a4585d29d3a968b7daf540310a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c77c98b006773ad40994bb4f3554ebb70b83b154fff3307b013a12e1e058013)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "repository", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[Play2Deployment, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[Play2Deployment, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[Play2Deployment, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94c1c1d84a622b6db99c91ef1f25b7be9115c478a999f26e07b813d2501dd114)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.play2.Play2Hooks",
    jsii_struct_bases=[],
    name_mapping={
        "post_build": "postBuild",
        "pre_build": "preBuild",
        "pre_run": "preRun",
        "run_failed": "runFailed",
        "run_succeed": "runSucceed",
    },
)
class Play2Hooks:
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
        :param post_build: `CC_POST_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#post-build>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#post_build Play2#post_build}
        :param pre_build: `CC_PRE_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-build>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#pre_build Play2#pre_build}
        :param pre_run: `CC_PRE_RUN_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-run>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#pre_run Play2#pre_run}
        :param run_failed: `CC_RUN_FAILED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#run_failed Play2#run_failed}
        :param run_succeed: `CC_RUN_SUCCEEDED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#run_succeed Play2#run_succeed}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c936cd214d1ccb644f833fb4b92b9ed926a376ccea0a52fdb3b358d4b2a8246f)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#post_build Play2#post_build}
        '''
        result = self._values.get("post_build")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_build(self) -> typing.Optional[builtins.str]:
        '''`CC_PRE_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-build>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#pre_build Play2#pre_build}
        '''
        result = self._values.get("pre_build")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_run(self) -> typing.Optional[builtins.str]:
        '''`CC_PRE_RUN_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-run>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#pre_run Play2#pre_run}
        '''
        result = self._values.get("pre_run")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run_failed(self) -> typing.Optional[builtins.str]:
        '''`CC_RUN_FAILED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#run_failed Play2#run_failed}
        '''
        result = self._values.get("run_failed")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run_succeed(self) -> typing.Optional[builtins.str]:
        '''`CC_RUN_SUCCEEDED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#run_succeed Play2#run_succeed}
        '''
        result = self._values.get("run_succeed")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Play2Hooks(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Play2HooksOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.play2.Play2HooksOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5de76c4099b8ddb8c39afaa03bae9592a3cb57190dba57dfa741be6899e6be62)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1d54e4a746e38a03aa8c309c3ecd9cb4f8f9bcef28b953fff255def04f82f1c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postBuild", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preBuild")
    def pre_build(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preBuild"))

    @pre_build.setter
    def pre_build(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3a392869eaffbbfdb69a30c74e93c511db08b41fc208235320af2904f5c778a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preBuild", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preRun")
    def pre_run(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preRun"))

    @pre_run.setter
    def pre_run(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4bd256ea1ff6f64151cbd686832adbc1da2bb769c6439906a53d6f65358cf36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runFailed")
    def run_failed(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runFailed"))

    @run_failed.setter
    def run_failed(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1f647dadbf82512cace8161a93652e53fd17c37a628e350247cf442d39598cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runFailed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runSucceed")
    def run_succeed(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runSucceed"))

    @run_succeed.setter
    def run_succeed(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fab5f5eb311d8ac929e9a4cc51d40fa3e9b603fcd0a76da6933129bea25ef4e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runSucceed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[Play2Hooks, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[Play2Hooks, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[Play2Hooks, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be32dc87e657874984fbe860db5ff0d2c6381f039ce2e69e2828673b0f22023c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.play2.Play2Networkgroups",
    jsii_struct_bases=[],
    name_mapping={"fqdn": "fqdn", "networkgroup_id": "networkgroupId"},
)
class Play2Networkgroups:
    def __init__(self, *, fqdn: builtins.str, networkgroup_id: builtins.str) -> None:
        '''
        :param fqdn: domain name which will resolve to application instances inside the networkgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#fqdn Play2#fqdn}
        :param networkgroup_id: ID of the networkgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#networkgroup_id Play2#networkgroup_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da7f8be6133ec78ed1d536e648bf83877da5601591ecc7f7c698fa6b05c088cb)
            check_type(argname="argument fqdn", value=fqdn, expected_type=type_hints["fqdn"])
            check_type(argname="argument networkgroup_id", value=networkgroup_id, expected_type=type_hints["networkgroup_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "fqdn": fqdn,
            "networkgroup_id": networkgroup_id,
        }

    @builtins.property
    def fqdn(self) -> builtins.str:
        '''domain name which will resolve to application instances inside the networkgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#fqdn Play2#fqdn}
        '''
        result = self._values.get("fqdn")
        assert result is not None, "Required property 'fqdn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def networkgroup_id(self) -> builtins.str:
        '''ID of the networkgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#networkgroup_id Play2#networkgroup_id}
        '''
        result = self._values.get("networkgroup_id")
        assert result is not None, "Required property 'networkgroup_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Play2Networkgroups(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Play2NetworkgroupsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.play2.Play2NetworkgroupsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f4dd0f1bccc8655adbf3041b0cafd0afbd9bea5fef81f919b931474eb6408315)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "Play2NetworkgroupsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f6e53a2f7dc7635e7adb2f52ad2f41b2e9a2fc011822bd4f04f66add25a29f6)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("Play2NetworkgroupsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd21fcf9829ac1b58135a5319b5708cf1a4579389660fc8ecf1dee3d3805e8b4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c67cbf5d5e2b2a67dd409e6499d7cb245287e36ced54718af0299df21f1d2f85)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0f3c96cf97af8e1bd423046fa3a73dbc1e6858a37b4d6ba1964b8a2f2388310c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[Play2Networkgroups]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[Play2Networkgroups]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[Play2Networkgroups]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b451a5a535ae3882920c2f7af67eaaed0c09645c8704debef6b8b4b90494498f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class Play2NetworkgroupsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.play2.Play2NetworkgroupsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8357b353222576900510544d66f27fc314c1638371c7fa518f206b8cb0d392aa)
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
            type_hints = typing.get_type_hints(_typecheckingstub__09ad43277a9f733088df5ed0bc3d7457bc7c6295e5f36f52da1d086fd5eb15e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fqdn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkgroupId")
    def networkgroup_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkgroupId"))

    @networkgroup_id.setter
    def networkgroup_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24a09c71678279be20f45592b2e7daa261b0c16267dbf24e2a8b856e010c9c0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkgroupId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[Play2Networkgroups, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[Play2Networkgroups, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[Play2Networkgroups, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ac5aeaf3680e3404ba4cb90ca588c167852d26467a2474f5c82e435339f441d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.play2.Play2Vhosts",
    jsii_struct_bases=[],
    name_mapping={"fqdn": "fqdn", "path_begin": "pathBegin"},
)
class Play2Vhosts:
    def __init__(
        self,
        *,
        fqdn: builtins.str,
        path_begin: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param fqdn: Fully qualified domain name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#fqdn Play2#fqdn}
        :param path_begin: Any HTTP request starting with this path will be sent to this application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#path_begin Play2#path_begin}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0d837f11109d7e262a77abeda7343745eb809875315bcbef118a909e4ef7e22)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#fqdn Play2#fqdn}
        '''
        result = self._values.get("fqdn")
        assert result is not None, "Required property 'fqdn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path_begin(self) -> typing.Optional[builtins.str]:
        '''Any HTTP request starting with this path will be sent to this application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/play2#path_begin Play2#path_begin}
        '''
        result = self._values.get("path_begin")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "Play2Vhosts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Play2VhostsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.play2.Play2VhostsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9bef1b9c0e982cb60e666865d1291c75f2b85d9067c0371ba692f53005883868)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "Play2VhostsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6352bcfdaf8c45e465ae109b8564eddc7272cd4af730fda56a95545402545b9a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("Play2VhostsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f84224b89fd2256050a5438ddd692519c903f4670c8ff29eeaec731da0430473)
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
            type_hints = typing.get_type_hints(_typecheckingstub__80f986c1ba6683bed5f211e9c96b840adf8e241be37e7c530a939596c33fbdb6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8caf43707d4b7a13d829931aeca77bb59e13c4ba3c58f481b014c1d059d0721)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[Play2Vhosts]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[Play2Vhosts]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[Play2Vhosts]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcb3bf461e4bdc372c29441fd94c35560ee88e1eca331ddbabd1fe0e1eb983a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class Play2VhostsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.play2.Play2VhostsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f2f235f43ce5b5806c04c685876234d360d7af8d1c4bb7dd1712c89bed328713)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4e66f43b02328a3b751e18258502de68817b8a799dc3f30a362a61e46eda91ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fqdn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pathBegin")
    def path_begin(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pathBegin"))

    @path_begin.setter
    def path_begin(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5baf955f210e5c9015527f32fde970af767994dd4ee825a9314dadbbac3d90e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pathBegin", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[Play2Vhosts, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[Play2Vhosts, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[Play2Vhosts, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39855948b7cb7371e92acb643199d0376063567f7af584919120f5d8ed87b2cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "Play2",
    "Play2Config",
    "Play2Deployment",
    "Play2DeploymentOutputReference",
    "Play2Hooks",
    "Play2HooksOutputReference",
    "Play2Networkgroups",
    "Play2NetworkgroupsList",
    "Play2NetworkgroupsOutputReference",
    "Play2Vhosts",
    "Play2VhostsList",
    "Play2VhostsOutputReference",
]

publication.publish()

def _typecheckingstub__8eef2c0efef81e7de1f902e36d5c3a7b56931087b664b8a6a11f08cbee919b95(
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
    deployment: typing.Optional[typing.Union[Play2Deployment, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    exposed_environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    hooks: typing.Optional[typing.Union[Play2Hooks, typing.Dict[builtins.str, typing.Any]]] = None,
    networkgroups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[Play2Networkgroups, typing.Dict[builtins.str, typing.Any]]]]] = None,
    redirect_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    region: typing.Optional[builtins.str] = None,
    sticky_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    vhosts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[Play2Vhosts, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__cb750810e003e8f121212e748dc6ca1ca161ad42c531b42d8e29a547f12c89d5(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0e2411a1eb7fb30e1f29fea03f38c68d0846b324251bf1978e4907496b471d5(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[Play2Networkgroups, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e07ae4c272b77803147204b00101fdd49ed5ee5ea480cd34fb080a6daba55a0d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[Play2Vhosts, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69038100301da676136745aa72cb6ab94aafb174e60edcfb479358a3fb524814(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9340e3f465b85a8106c18c66081e94795902b44278fa8fb2ff2947a66376a8e5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c8e08ee65adf1c9f238a2e0582bf28ef51d1ace33b05859ff417aa143ba7b47(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fb3626dbb5f3d7038c3e50fa378f784af4dad530ac02f79fdf7d9ed6ec95012(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c2215b28a314b376145dee7aadbfba3a2512ad9b3e4131e7409f2c7af7811ff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6aa63cf5ceb3ca2475147fb9a27c7634f5294a77d95aa6a97d992e9de219cc2(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73ad8bf23fd370ecca51f35d59ed9b7b135305fd034709c00159dfb8de93db2d(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f94d88afe800f46613310da5e42cd01abc8d22058b3b6165d92f618f6debe6fc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__872b41b70d205ab26fb2c1e45a2d719b729cc4293b67c7bf8126ed9696c83aea(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afb4b79c2629c7633cc40a1b62463ffd05d679f7745ffbb0e6fb1588471000ac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d712a78b1ef4c2c3cc72ca318955477befca9c180159212dedde46385c9b25b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9c5b207602378e920f30cb5fe55b61b98626a449a440e0216a9cc060607bc01(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ae91950786e3327a7f47a4d7898854689dafb508e4a4d2f5d4b73cb48cbf230(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5e82d966d21e1213bd0e2fae265cda27e018b3daaaf74845385fd548a6378a9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e265ad5905d2815e65305b92e56ed3e23798b617e44f23e15ce8c967e0a1d37(
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
    deployment: typing.Optional[typing.Union[Play2Deployment, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    exposed_environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    hooks: typing.Optional[typing.Union[Play2Hooks, typing.Dict[builtins.str, typing.Any]]] = None,
    networkgroups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[Play2Networkgroups, typing.Dict[builtins.str, typing.Any]]]]] = None,
    redirect_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    region: typing.Optional[builtins.str] = None,
    sticky_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    vhosts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[Play2Vhosts, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c4da16250b350fed500689fd25159cef58f1bddc913ff6ec4cf1bc3206faaf0(
    *,
    authentication_basic: typing.Optional[builtins.str] = None,
    commit: typing.Optional[builtins.str] = None,
    repository: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__044f4c86b9bc8dffc42c53eae5ad9b2b239bc775bae3beff197008e48089adef(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eeab5609c5be85dd416de297f50b07f7e8968bb879aec63f5f2c7dfd8848fbaf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdea4f65e8f4be5f1131df9b7bb51d32fbe4d1a4585d29d3a968b7daf540310a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c77c98b006773ad40994bb4f3554ebb70b83b154fff3307b013a12e1e058013(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94c1c1d84a622b6db99c91ef1f25b7be9115c478a999f26e07b813d2501dd114(
    value: typing.Optional[typing.Union[Play2Deployment, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c936cd214d1ccb644f833fb4b92b9ed926a376ccea0a52fdb3b358d4b2a8246f(
    *,
    post_build: typing.Optional[builtins.str] = None,
    pre_build: typing.Optional[builtins.str] = None,
    pre_run: typing.Optional[builtins.str] = None,
    run_failed: typing.Optional[builtins.str] = None,
    run_succeed: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5de76c4099b8ddb8c39afaa03bae9592a3cb57190dba57dfa741be6899e6be62(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d54e4a746e38a03aa8c309c3ecd9cb4f8f9bcef28b953fff255def04f82f1c4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3a392869eaffbbfdb69a30c74e93c511db08b41fc208235320af2904f5c778a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4bd256ea1ff6f64151cbd686832adbc1da2bb769c6439906a53d6f65358cf36(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1f647dadbf82512cace8161a93652e53fd17c37a628e350247cf442d39598cf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fab5f5eb311d8ac929e9a4cc51d40fa3e9b603fcd0a76da6933129bea25ef4e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be32dc87e657874984fbe860db5ff0d2c6381f039ce2e69e2828673b0f22023c(
    value: typing.Optional[typing.Union[Play2Hooks, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da7f8be6133ec78ed1d536e648bf83877da5601591ecc7f7c698fa6b05c088cb(
    *,
    fqdn: builtins.str,
    networkgroup_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4dd0f1bccc8655adbf3041b0cafd0afbd9bea5fef81f919b931474eb6408315(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f6e53a2f7dc7635e7adb2f52ad2f41b2e9a2fc011822bd4f04f66add25a29f6(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd21fcf9829ac1b58135a5319b5708cf1a4579389660fc8ecf1dee3d3805e8b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c67cbf5d5e2b2a67dd409e6499d7cb245287e36ced54718af0299df21f1d2f85(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f3c96cf97af8e1bd423046fa3a73dbc1e6858a37b4d6ba1964b8a2f2388310c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b451a5a535ae3882920c2f7af67eaaed0c09645c8704debef6b8b4b90494498f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[Play2Networkgroups]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8357b353222576900510544d66f27fc314c1638371c7fa518f206b8cb0d392aa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09ad43277a9f733088df5ed0bc3d7457bc7c6295e5f36f52da1d086fd5eb15e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24a09c71678279be20f45592b2e7daa261b0c16267dbf24e2a8b856e010c9c0a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ac5aeaf3680e3404ba4cb90ca588c167852d26467a2474f5c82e435339f441d(
    value: typing.Optional[typing.Union[Play2Networkgroups, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0d837f11109d7e262a77abeda7343745eb809875315bcbef118a909e4ef7e22(
    *,
    fqdn: builtins.str,
    path_begin: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bef1b9c0e982cb60e666865d1291c75f2b85d9067c0371ba692f53005883868(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6352bcfdaf8c45e465ae109b8564eddc7272cd4af730fda56a95545402545b9a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f84224b89fd2256050a5438ddd692519c903f4670c8ff29eeaec731da0430473(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80f986c1ba6683bed5f211e9c96b840adf8e241be37e7c530a939596c33fbdb6(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8caf43707d4b7a13d829931aeca77bb59e13c4ba3c58f481b014c1d059d0721(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcb3bf461e4bdc372c29441fd94c35560ee88e1eca331ddbabd1fe0e1eb983a1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[Play2Vhosts]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2f235f43ce5b5806c04c685876234d360d7af8d1c4bb7dd1712c89bed328713(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e66f43b02328a3b751e18258502de68817b8a799dc3f30a362a61e46eda91ea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5baf955f210e5c9015527f32fde970af767994dd4ee825a9314dadbbac3d90e5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39855948b7cb7371e92acb643199d0376063567f7af584919120f5d8ed87b2cb(
    value: typing.Optional[typing.Union[Play2Vhosts, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass
