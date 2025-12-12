r'''
# `clevercloud_docker`

Refer to the Terraform Registry for docs: [`clevercloud_docker`](https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker).
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


class Docker(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.docker.Docker",
):
    '''Represents a {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker clevercloud_docker}.'''

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
        container_port: typing.Optional[jsii.Number] = None,
        container_port_tcp: typing.Optional[jsii.Number] = None,
        daemon_socket_mount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        deployment: typing.Optional[typing.Union["DockerDeployment", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        dockerfile: typing.Optional[builtins.str] = None,
        enable_ipv6: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        exposed_environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        hooks: typing.Optional[typing.Union["DockerHooks", typing.Dict[builtins.str, typing.Any]]] = None,
        ipv6_cidr: typing.Optional[builtins.str] = None,
        networkgroups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DockerNetworkgroups", typing.Dict[builtins.str, typing.Any]]]]] = None,
        redirect_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        region: typing.Optional[builtins.str] = None,
        registry_password: typing.Optional[builtins.str] = None,
        registry_url: typing.Optional[builtins.str] = None,
        registry_user: typing.Optional[builtins.str] = None,
        sticky_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vhosts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DockerVhosts", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker clevercloud_docker} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param biggest_flavor: Biggest instance flavor, if different from smallest, enable auto-scaling. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#biggest_flavor Docker#biggest_flavor}
        :param max_instance_count: Maximum instance count, if different from min value, enable auto-scaling. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#max_instance_count Docker#max_instance_count}
        :param min_instance_count: Minimum instance count. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#min_instance_count Docker#min_instance_count}
        :param name: Application name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#name Docker#name}
        :param smallest_flavor: Smallest instance flavor. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#smallest_flavor Docker#smallest_flavor}
        :param app_folder: Folder in which the application is located (inside the git repository). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#app_folder Docker#app_folder}
        :param build_flavor: Use dedicated instance with given flavor for build phase. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#build_flavor Docker#build_flavor}
        :param container_port: Set to custom HTTP port if your Docker container runs on custom port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#container_port Docker#container_port}
        :param container_port_tcp: Set to custom TCP port if your Docker container runs on custom port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#container_port_tcp Docker#container_port_tcp}
        :param daemon_socket_mount: Set to true to access the host Docker socket from inside your container. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#daemon_socket_mount Docker#daemon_socket_mount}
        :param dependencies: A list of application or add-ons required to run this application. Can be either app_xxx or postgres_yyy ID format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#dependencies Docker#dependencies}
        :param deployment: deployment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#deployment Docker#deployment}
        :param description: Application description. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#description Docker#description}
        :param dockerfile: The name of the Dockerfile to build. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#dockerfile Docker#dockerfile}
        :param enable_ipv6: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#enable_ipv6 Docker#enable_ipv6}.
        :param environment: Environment variables injected into the application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#environment Docker#environment}
        :param exposed_environment: Environment variables other linked applications will be able to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#exposed_environment Docker#exposed_environment}
        :param hooks: hooks block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#hooks Docker#hooks}
        :param ipv6_cidr: Activate the support of IPv6 with an IPv6 subnet int the docker daemon. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#ipv6_cidr Docker#ipv6_cidr}
        :param networkgroups: List of networkgroups the application must be part of. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#networkgroups Docker#networkgroups}
        :param redirect_https: Redirect client from plain to TLS port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#redirect_https Docker#redirect_https}
        :param region: Geographical region where the database will be deployed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#region Docker#region}
        :param registry_password: The password of your username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#registry_password Docker#registry_password}
        :param registry_url: The server of your private registry (optional). Docker’s public registry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#registry_url Docker#registry_url}
        :param registry_user: The username to login to a private registry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#registry_user Docker#registry_user}
        :param sticky_sessions: Enable sticky sessions, use it when your client sessions are instances scoped. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#sticky_sessions Docker#sticky_sessions}
        :param vhosts: List of virtual hosts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#vhosts Docker#vhosts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__139f2e10a95fe520cea2619a885599ffe08b128f3ecf2e949b99aec550660714)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DockerConfig(
            biggest_flavor=biggest_flavor,
            max_instance_count=max_instance_count,
            min_instance_count=min_instance_count,
            name=name,
            smallest_flavor=smallest_flavor,
            app_folder=app_folder,
            build_flavor=build_flavor,
            container_port=container_port,
            container_port_tcp=container_port_tcp,
            daemon_socket_mount=daemon_socket_mount,
            dependencies=dependencies,
            deployment=deployment,
            description=description,
            dockerfile=dockerfile,
            enable_ipv6=enable_ipv6,
            environment=environment,
            exposed_environment=exposed_environment,
            hooks=hooks,
            ipv6_cidr=ipv6_cidr,
            networkgroups=networkgroups,
            redirect_https=redirect_https,
            region=region,
            registry_password=registry_password,
            registry_url=registry_url,
            registry_user=registry_user,
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
        '''Generates CDKTF code for importing a Docker resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the Docker to import.
        :param import_from_id: The id of the existing Docker that should be imported. Refer to the {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the Docker to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18f645304c0872e4649964fdbe570eb758a9e5b8f51aabd407337f61721aae70)
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
        :param authentication_basic: user ans password ':' separated, (PersonalAccessToken in Github case). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#authentication_basic Docker#authentication_basic}
        :param commit: Support multiple syntax like ``refs/heads/[BRANCH]``, ``github_hook`` or ``[COMMIT]``, when using the special value ``github_hook``, we will link the application to the Github repository. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#commit Docker#commit}
        :param repository: The repository URL to deploy, can be 'https://...', 'file://...'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#repository Docker#repository}
        '''
        value = DockerDeployment(
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
        :param post_build: `CC_POST_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#post-build>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#post_build Docker#post_build}
        :param pre_build: `CC_PRE_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-build>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#pre_build Docker#pre_build}
        :param pre_run: `CC_PRE_RUN_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-run>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#pre_run Docker#pre_run}
        :param run_failed: `CC_RUN_FAILED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#run_failed Docker#run_failed}
        :param run_succeed: `CC_RUN_SUCCEEDED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#run_succeed Docker#run_succeed}
        '''
        value = DockerHooks(
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
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DockerNetworkgroups", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ccac66ddde622ebd293618fc1b74c0ee3a0f77c58cba84ee16c4e9647adc5e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetworkgroups", [value]))

    @jsii.member(jsii_name="putVhosts")
    def put_vhosts(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DockerVhosts", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5b40fe4e0a0adf6f3e5c9a8dd0abb9b68a2095fc6ffe360cfd25ab4372af4f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putVhosts", [value]))

    @jsii.member(jsii_name="resetAppFolder")
    def reset_app_folder(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAppFolder", []))

    @jsii.member(jsii_name="resetBuildFlavor")
    def reset_build_flavor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBuildFlavor", []))

    @jsii.member(jsii_name="resetContainerPort")
    def reset_container_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContainerPort", []))

    @jsii.member(jsii_name="resetContainerPortTcp")
    def reset_container_port_tcp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContainerPortTcp", []))

    @jsii.member(jsii_name="resetDaemonSocketMount")
    def reset_daemon_socket_mount(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDaemonSocketMount", []))

    @jsii.member(jsii_name="resetDependencies")
    def reset_dependencies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDependencies", []))

    @jsii.member(jsii_name="resetDeployment")
    def reset_deployment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeployment", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetDockerfile")
    def reset_dockerfile(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDockerfile", []))

    @jsii.member(jsii_name="resetEnableIpv6")
    def reset_enable_ipv6(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableIpv6", []))

    @jsii.member(jsii_name="resetEnvironment")
    def reset_environment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvironment", []))

    @jsii.member(jsii_name="resetExposedEnvironment")
    def reset_exposed_environment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExposedEnvironment", []))

    @jsii.member(jsii_name="resetHooks")
    def reset_hooks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHooks", []))

    @jsii.member(jsii_name="resetIpv6Cidr")
    def reset_ipv6_cidr(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv6Cidr", []))

    @jsii.member(jsii_name="resetNetworkgroups")
    def reset_networkgroups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkgroups", []))

    @jsii.member(jsii_name="resetRedirectHttps")
    def reset_redirect_https(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedirectHttps", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetRegistryPassword")
    def reset_registry_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegistryPassword", []))

    @jsii.member(jsii_name="resetRegistryUrl")
    def reset_registry_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegistryUrl", []))

    @jsii.member(jsii_name="resetRegistryUser")
    def reset_registry_user(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegistryUser", []))

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
    def deployment(self) -> "DockerDeploymentOutputReference":
        return typing.cast("DockerDeploymentOutputReference", jsii.get(self, "deployment"))

    @builtins.property
    @jsii.member(jsii_name="deployUrl")
    def deploy_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deployUrl"))

    @builtins.property
    @jsii.member(jsii_name="hooks")
    def hooks(self) -> "DockerHooksOutputReference":
        return typing.cast("DockerHooksOutputReference", jsii.get(self, "hooks"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="networkgroups")
    def networkgroups(self) -> "DockerNetworkgroupsList":
        return typing.cast("DockerNetworkgroupsList", jsii.get(self, "networkgroups"))

    @builtins.property
    @jsii.member(jsii_name="vhosts")
    def vhosts(self) -> "DockerVhostsList":
        return typing.cast("DockerVhostsList", jsii.get(self, "vhosts"))

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
    @jsii.member(jsii_name="containerPortInput")
    def container_port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "containerPortInput"))

    @builtins.property
    @jsii.member(jsii_name="containerPortTcpInput")
    def container_port_tcp_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "containerPortTcpInput"))

    @builtins.property
    @jsii.member(jsii_name="daemonSocketMountInput")
    def daemon_socket_mount_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "daemonSocketMountInput"))

    @builtins.property
    @jsii.member(jsii_name="dependenciesInput")
    def dependencies_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dependenciesInput"))

    @builtins.property
    @jsii.member(jsii_name="deploymentInput")
    def deployment_input(
        self,
    ) -> typing.Optional[typing.Union["DockerDeployment", _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["DockerDeployment", _cdktf_9a9027ec.IResolvable]], jsii.get(self, "deploymentInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="dockerfileInput")
    def dockerfile_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dockerfileInput"))

    @builtins.property
    @jsii.member(jsii_name="enableIpv6Input")
    def enable_ipv6_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableIpv6Input"))

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
    ) -> typing.Optional[typing.Union["DockerHooks", _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["DockerHooks", _cdktf_9a9027ec.IResolvable]], jsii.get(self, "hooksInput"))

    @builtins.property
    @jsii.member(jsii_name="ipv6CidrInput")
    def ipv6_cidr_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipv6CidrInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DockerNetworkgroups"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DockerNetworkgroups"]]], jsii.get(self, "networkgroupsInput"))

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
    @jsii.member(jsii_name="registryPasswordInput")
    def registry_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "registryPasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="registryUrlInput")
    def registry_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "registryUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="registryUserInput")
    def registry_user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "registryUserInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DockerVhosts"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DockerVhosts"]]], jsii.get(self, "vhostsInput"))

    @builtins.property
    @jsii.member(jsii_name="appFolder")
    def app_folder(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appFolder"))

    @app_folder.setter
    def app_folder(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c0749711dcddc1e3d76f3498344c930c5f7c62fd780e41eef4222f8e266d710)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appFolder", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="biggestFlavor")
    def biggest_flavor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "biggestFlavor"))

    @biggest_flavor.setter
    def biggest_flavor(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__baeaddc2b86ac05ff6cce4b0a88c3bb8c3b2ee6b1a19fa85d74faf0ed7a4da90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "biggestFlavor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="buildFlavor")
    def build_flavor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "buildFlavor"))

    @build_flavor.setter
    def build_flavor(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7be519c5759bd465e19b4572c02ebddcec5243bf8c1ae9cc16fa531fa2eb5e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "buildFlavor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="containerPort")
    def container_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "containerPort"))

    @container_port.setter
    def container_port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81a3208c15656258c3588ec9c8b40478c81bb49a6e6f78a7918cef61a720727e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "containerPort", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="containerPortTcp")
    def container_port_tcp(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "containerPortTcp"))

    @container_port_tcp.setter
    def container_port_tcp(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0696c554bc6bb6965b9b6495d7a4179fba6a7561f37af247ca17e405e0645333)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "containerPortTcp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="daemonSocketMount")
    def daemon_socket_mount(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "daemonSocketMount"))

    @daemon_socket_mount.setter
    def daemon_socket_mount(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c043353e91e0eb6911cc881a0f96e25340d6c4ea3836cd98000de6808790104e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "daemonSocketMount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dependencies")
    def dependencies(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dependencies"))

    @dependencies.setter
    def dependencies(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88c4d9aca50bc7df610733e30ef8cb7841840c87af7bb871da576e892c41bc1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dependencies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1d78e7a061ce4f1bae8507c96bbe536e46656f7da1f98fe639c0f273a837772)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dockerfile")
    def dockerfile(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dockerfile"))

    @dockerfile.setter
    def dockerfile(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e049f2d16bc3935c8c85be9fba183c3c069008582d1b71a2f8725705d1e1693e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dockerfile", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableIpv6")
    def enable_ipv6(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableIpv6"))

    @enable_ipv6.setter
    def enable_ipv6(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__faa063eb97703f3457191714781fedc2d6e9017bc88a73adbb082723822326f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableIpv6", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "environment"))

    @environment.setter
    def environment(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d734ff3cfe24bee14181e875f7403548a3bf995c87b73d59825a8bc37aafe5bd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6462649b547b944b10d18050a69e3fbadd7104e29957b77d0eef6838b37614db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exposedEnvironment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv6Cidr")
    def ipv6_cidr(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv6Cidr"))

    @ipv6_cidr.setter
    def ipv6_cidr(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71818af7949e63e9634ce00fc4cd40285f5f2cb271b9a9a2a13f13bb283dd8b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv6Cidr", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxInstanceCount")
    def max_instance_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxInstanceCount"))

    @max_instance_count.setter
    def max_instance_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a46e5e5c131e45136f582c747bcf1de3467b6c714ded68f87e04395bff17831)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxInstanceCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minInstanceCount")
    def min_instance_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minInstanceCount"))

    @min_instance_count.setter
    def min_instance_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c241069f39bf5411eef12e7c84a04519a9a4f069f24b3b7eef817e7c337bdf54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minInstanceCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bef4f687e59280f3dfb28cae5eca82115a64eb3cc527ef35890258f1055bd3c8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5ed9da5142468842205cbd771e234408f0aa3774f656097798586c30af878170)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "redirectHttps", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64cd5b5a9d246e1bc221362c7e6ee626159c814852b11bee6f4937b5749278b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="registryPassword")
    def registry_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "registryPassword"))

    @registry_password.setter
    def registry_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e29eff9988c520079badb52a2f0d9933e28cd0de09f0f1f452b4906fcae9ff06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "registryPassword", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="registryUrl")
    def registry_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "registryUrl"))

    @registry_url.setter
    def registry_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31bc0b1a326dc093709f0b7ffa692e782f4059756277070a1984679da91d7fb9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "registryUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="registryUser")
    def registry_user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "registryUser"))

    @registry_user.setter
    def registry_user(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5ccbf07795a4fda08a6cff90bdb04edc4a9e8fa338e111c69ce1507c2b0e552)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "registryUser", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="smallestFlavor")
    def smallest_flavor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "smallestFlavor"))

    @smallest_flavor.setter
    def smallest_flavor(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0737c5ffd274bcae4b29c1e68ab04fc7f3a0378342be4eb5622a20abed689b2c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__265a5314bef679b90be11beaaf3a215aa5f3ce4a5e4311ee0d99339d4b58f7ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stickySessions", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.docker.DockerConfig",
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
        "container_port": "containerPort",
        "container_port_tcp": "containerPortTcp",
        "daemon_socket_mount": "daemonSocketMount",
        "dependencies": "dependencies",
        "deployment": "deployment",
        "description": "description",
        "dockerfile": "dockerfile",
        "enable_ipv6": "enableIpv6",
        "environment": "environment",
        "exposed_environment": "exposedEnvironment",
        "hooks": "hooks",
        "ipv6_cidr": "ipv6Cidr",
        "networkgroups": "networkgroups",
        "redirect_https": "redirectHttps",
        "region": "region",
        "registry_password": "registryPassword",
        "registry_url": "registryUrl",
        "registry_user": "registryUser",
        "sticky_sessions": "stickySessions",
        "vhosts": "vhosts",
    },
)
class DockerConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        container_port: typing.Optional[jsii.Number] = None,
        container_port_tcp: typing.Optional[jsii.Number] = None,
        daemon_socket_mount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        deployment: typing.Optional[typing.Union["DockerDeployment", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        dockerfile: typing.Optional[builtins.str] = None,
        enable_ipv6: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        exposed_environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        hooks: typing.Optional[typing.Union["DockerHooks", typing.Dict[builtins.str, typing.Any]]] = None,
        ipv6_cidr: typing.Optional[builtins.str] = None,
        networkgroups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DockerNetworkgroups", typing.Dict[builtins.str, typing.Any]]]]] = None,
        redirect_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        region: typing.Optional[builtins.str] = None,
        registry_password: typing.Optional[builtins.str] = None,
        registry_url: typing.Optional[builtins.str] = None,
        registry_user: typing.Optional[builtins.str] = None,
        sticky_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vhosts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DockerVhosts", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param biggest_flavor: Biggest instance flavor, if different from smallest, enable auto-scaling. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#biggest_flavor Docker#biggest_flavor}
        :param max_instance_count: Maximum instance count, if different from min value, enable auto-scaling. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#max_instance_count Docker#max_instance_count}
        :param min_instance_count: Minimum instance count. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#min_instance_count Docker#min_instance_count}
        :param name: Application name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#name Docker#name}
        :param smallest_flavor: Smallest instance flavor. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#smallest_flavor Docker#smallest_flavor}
        :param app_folder: Folder in which the application is located (inside the git repository). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#app_folder Docker#app_folder}
        :param build_flavor: Use dedicated instance with given flavor for build phase. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#build_flavor Docker#build_flavor}
        :param container_port: Set to custom HTTP port if your Docker container runs on custom port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#container_port Docker#container_port}
        :param container_port_tcp: Set to custom TCP port if your Docker container runs on custom port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#container_port_tcp Docker#container_port_tcp}
        :param daemon_socket_mount: Set to true to access the host Docker socket from inside your container. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#daemon_socket_mount Docker#daemon_socket_mount}
        :param dependencies: A list of application or add-ons required to run this application. Can be either app_xxx or postgres_yyy ID format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#dependencies Docker#dependencies}
        :param deployment: deployment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#deployment Docker#deployment}
        :param description: Application description. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#description Docker#description}
        :param dockerfile: The name of the Dockerfile to build. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#dockerfile Docker#dockerfile}
        :param enable_ipv6: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#enable_ipv6 Docker#enable_ipv6}.
        :param environment: Environment variables injected into the application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#environment Docker#environment}
        :param exposed_environment: Environment variables other linked applications will be able to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#exposed_environment Docker#exposed_environment}
        :param hooks: hooks block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#hooks Docker#hooks}
        :param ipv6_cidr: Activate the support of IPv6 with an IPv6 subnet int the docker daemon. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#ipv6_cidr Docker#ipv6_cidr}
        :param networkgroups: List of networkgroups the application must be part of. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#networkgroups Docker#networkgroups}
        :param redirect_https: Redirect client from plain to TLS port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#redirect_https Docker#redirect_https}
        :param region: Geographical region where the database will be deployed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#region Docker#region}
        :param registry_password: The password of your username. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#registry_password Docker#registry_password}
        :param registry_url: The server of your private registry (optional). Docker’s public registry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#registry_url Docker#registry_url}
        :param registry_user: The username to login to a private registry. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#registry_user Docker#registry_user}
        :param sticky_sessions: Enable sticky sessions, use it when your client sessions are instances scoped. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#sticky_sessions Docker#sticky_sessions}
        :param vhosts: List of virtual hosts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#vhosts Docker#vhosts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(deployment, dict):
            deployment = DockerDeployment(**deployment)
        if isinstance(hooks, dict):
            hooks = DockerHooks(**hooks)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__068985606a454df7c1c0a0fc91f5c3915d85afd9bdacc5b1ec324c35e4b8f568)
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
            check_type(argname="argument container_port", value=container_port, expected_type=type_hints["container_port"])
            check_type(argname="argument container_port_tcp", value=container_port_tcp, expected_type=type_hints["container_port_tcp"])
            check_type(argname="argument daemon_socket_mount", value=daemon_socket_mount, expected_type=type_hints["daemon_socket_mount"])
            check_type(argname="argument dependencies", value=dependencies, expected_type=type_hints["dependencies"])
            check_type(argname="argument deployment", value=deployment, expected_type=type_hints["deployment"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument dockerfile", value=dockerfile, expected_type=type_hints["dockerfile"])
            check_type(argname="argument enable_ipv6", value=enable_ipv6, expected_type=type_hints["enable_ipv6"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument exposed_environment", value=exposed_environment, expected_type=type_hints["exposed_environment"])
            check_type(argname="argument hooks", value=hooks, expected_type=type_hints["hooks"])
            check_type(argname="argument ipv6_cidr", value=ipv6_cidr, expected_type=type_hints["ipv6_cidr"])
            check_type(argname="argument networkgroups", value=networkgroups, expected_type=type_hints["networkgroups"])
            check_type(argname="argument redirect_https", value=redirect_https, expected_type=type_hints["redirect_https"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument registry_password", value=registry_password, expected_type=type_hints["registry_password"])
            check_type(argname="argument registry_url", value=registry_url, expected_type=type_hints["registry_url"])
            check_type(argname="argument registry_user", value=registry_user, expected_type=type_hints["registry_user"])
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
        if container_port is not None:
            self._values["container_port"] = container_port
        if container_port_tcp is not None:
            self._values["container_port_tcp"] = container_port_tcp
        if daemon_socket_mount is not None:
            self._values["daemon_socket_mount"] = daemon_socket_mount
        if dependencies is not None:
            self._values["dependencies"] = dependencies
        if deployment is not None:
            self._values["deployment"] = deployment
        if description is not None:
            self._values["description"] = description
        if dockerfile is not None:
            self._values["dockerfile"] = dockerfile
        if enable_ipv6 is not None:
            self._values["enable_ipv6"] = enable_ipv6
        if environment is not None:
            self._values["environment"] = environment
        if exposed_environment is not None:
            self._values["exposed_environment"] = exposed_environment
        if hooks is not None:
            self._values["hooks"] = hooks
        if ipv6_cidr is not None:
            self._values["ipv6_cidr"] = ipv6_cidr
        if networkgroups is not None:
            self._values["networkgroups"] = networkgroups
        if redirect_https is not None:
            self._values["redirect_https"] = redirect_https
        if region is not None:
            self._values["region"] = region
        if registry_password is not None:
            self._values["registry_password"] = registry_password
        if registry_url is not None:
            self._values["registry_url"] = registry_url
        if registry_user is not None:
            self._values["registry_user"] = registry_user
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#biggest_flavor Docker#biggest_flavor}
        '''
        result = self._values.get("biggest_flavor")
        assert result is not None, "Required property 'biggest_flavor' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def max_instance_count(self) -> jsii.Number:
        '''Maximum instance count, if different from min value, enable auto-scaling.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#max_instance_count Docker#max_instance_count}
        '''
        result = self._values.get("max_instance_count")
        assert result is not None, "Required property 'max_instance_count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_instance_count(self) -> jsii.Number:
        '''Minimum instance count.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#min_instance_count Docker#min_instance_count}
        '''
        result = self._values.get("min_instance_count")
        assert result is not None, "Required property 'min_instance_count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Application name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#name Docker#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def smallest_flavor(self) -> builtins.str:
        '''Smallest instance flavor.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#smallest_flavor Docker#smallest_flavor}
        '''
        result = self._values.get("smallest_flavor")
        assert result is not None, "Required property 'smallest_flavor' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def app_folder(self) -> typing.Optional[builtins.str]:
        '''Folder in which the application is located (inside the git repository).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#app_folder Docker#app_folder}
        '''
        result = self._values.get("app_folder")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_flavor(self) -> typing.Optional[builtins.str]:
        '''Use dedicated instance with given flavor for build phase.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#build_flavor Docker#build_flavor}
        '''
        result = self._values.get("build_flavor")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def container_port(self) -> typing.Optional[jsii.Number]:
        '''Set to custom HTTP port if your Docker container runs on custom port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#container_port Docker#container_port}
        '''
        result = self._values.get("container_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def container_port_tcp(self) -> typing.Optional[jsii.Number]:
        '''Set to custom TCP port if your Docker container runs on custom port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#container_port_tcp Docker#container_port_tcp}
        '''
        result = self._values.get("container_port_tcp")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def daemon_socket_mount(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true to access the host Docker socket from inside your container.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#daemon_socket_mount Docker#daemon_socket_mount}
        '''
        result = self._values.get("daemon_socket_mount")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def dependencies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of application or add-ons required to run this application. Can be either app_xxx or postgres_yyy ID format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#dependencies Docker#dependencies}
        '''
        result = self._values.get("dependencies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def deployment(self) -> typing.Optional["DockerDeployment"]:
        '''deployment block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#deployment Docker#deployment}
        '''
        result = self._values.get("deployment")
        return typing.cast(typing.Optional["DockerDeployment"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Application description.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#description Docker#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dockerfile(self) -> typing.Optional[builtins.str]:
        '''The name of the Dockerfile to build.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#dockerfile Docker#dockerfile}
        '''
        result = self._values.get("dockerfile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_ipv6(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#enable_ipv6 Docker#enable_ipv6}.'''
        result = self._values.get("enable_ipv6")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Environment variables injected into the application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#environment Docker#environment}
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def exposed_environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Environment variables other linked applications will be able to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#exposed_environment Docker#exposed_environment}
        '''
        result = self._values.get("exposed_environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def hooks(self) -> typing.Optional["DockerHooks"]:
        '''hooks block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#hooks Docker#hooks}
        '''
        result = self._values.get("hooks")
        return typing.cast(typing.Optional["DockerHooks"], result)

    @builtins.property
    def ipv6_cidr(self) -> typing.Optional[builtins.str]:
        '''Activate the support of IPv6 with an IPv6 subnet int the docker daemon.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#ipv6_cidr Docker#ipv6_cidr}
        '''
        result = self._values.get("ipv6_cidr")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def networkgroups(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DockerNetworkgroups"]]]:
        '''List of networkgroups the application must be part of.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#networkgroups Docker#networkgroups}
        '''
        result = self._values.get("networkgroups")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DockerNetworkgroups"]]], result)

    @builtins.property
    def redirect_https(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Redirect client from plain to TLS port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#redirect_https Docker#redirect_https}
        '''
        result = self._values.get("redirect_https")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Geographical region where the database will be deployed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#region Docker#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def registry_password(self) -> typing.Optional[builtins.str]:
        '''The password of your username.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#registry_password Docker#registry_password}
        '''
        result = self._values.get("registry_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def registry_url(self) -> typing.Optional[builtins.str]:
        '''The server of your private registry (optional).	Docker’s public registry.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#registry_url Docker#registry_url}
        '''
        result = self._values.get("registry_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def registry_user(self) -> typing.Optional[builtins.str]:
        '''The username to login to a private registry.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#registry_user Docker#registry_user}
        '''
        result = self._values.get("registry_user")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sticky_sessions(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable sticky sessions, use it when your client sessions are instances scoped.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#sticky_sessions Docker#sticky_sessions}
        '''
        result = self._values.get("sticky_sessions")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def vhosts(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DockerVhosts"]]]:
        '''List of virtual hosts.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#vhosts Docker#vhosts}
        '''
        result = self._values.get("vhosts")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DockerVhosts"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DockerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.docker.DockerDeployment",
    jsii_struct_bases=[],
    name_mapping={
        "authentication_basic": "authenticationBasic",
        "commit": "commit",
        "repository": "repository",
    },
)
class DockerDeployment:
    def __init__(
        self,
        *,
        authentication_basic: typing.Optional[builtins.str] = None,
        commit: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param authentication_basic: user ans password ':' separated, (PersonalAccessToken in Github case). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#authentication_basic Docker#authentication_basic}
        :param commit: Support multiple syntax like ``refs/heads/[BRANCH]``, ``github_hook`` or ``[COMMIT]``, when using the special value ``github_hook``, we will link the application to the Github repository. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#commit Docker#commit}
        :param repository: The repository URL to deploy, can be 'https://...', 'file://...'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#repository Docker#repository}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec45a5291509405d3f072317ccb59319253ad57b000e7f2964df29ce93e08292)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#authentication_basic Docker#authentication_basic}
        '''
        result = self._values.get("authentication_basic")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def commit(self) -> typing.Optional[builtins.str]:
        '''Support multiple syntax like ``refs/heads/[BRANCH]``, ``github_hook`` or ``[COMMIT]``, when using the special value ``github_hook``, we will link the application to the Github repository.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#commit Docker#commit}
        '''
        result = self._values.get("commit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''The repository URL to deploy, can be 'https://...', 'file://...'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#repository Docker#repository}
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DockerDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DockerDeploymentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.docker.DockerDeploymentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4e23093ea40bf6b5e3db10f9f835113aa5f4c3ec83effed11a0b2f2a6c23021e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__33160c14a5132f2a0ca02e3fcc0ca70e0bc076627e71000b5d11d4788f1de7fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authenticationBasic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="commit")
    def commit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commit"))

    @commit.setter
    def commit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff0db4e44e55551a37727358a383817119b26b3453a22a79e75c545b84fc625f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89e6931b456a0dd9f84e3c619d2a267ba02aabf5490489e2cbdbf83ffb197c04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "repository", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DockerDeployment, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DockerDeployment, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DockerDeployment, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__970c60d56b6ee2708ef4ad370e7d7cb768e852295d1bed6db5e51a10d7c026ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.docker.DockerHooks",
    jsii_struct_bases=[],
    name_mapping={
        "post_build": "postBuild",
        "pre_build": "preBuild",
        "pre_run": "preRun",
        "run_failed": "runFailed",
        "run_succeed": "runSucceed",
    },
)
class DockerHooks:
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
        :param post_build: `CC_POST_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#post-build>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#post_build Docker#post_build}
        :param pre_build: `CC_PRE_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-build>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#pre_build Docker#pre_build}
        :param pre_run: `CC_PRE_RUN_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-run>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#pre_run Docker#pre_run}
        :param run_failed: `CC_RUN_FAILED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#run_failed Docker#run_failed}
        :param run_succeed: `CC_RUN_SUCCEEDED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#run_succeed Docker#run_succeed}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9365a11bdc78065791d403ac409ff85f368e47d38c4c24a384df0d2b2c5aebde)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#post_build Docker#post_build}
        '''
        result = self._values.get("post_build")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_build(self) -> typing.Optional[builtins.str]:
        '''`CC_PRE_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-build>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#pre_build Docker#pre_build}
        '''
        result = self._values.get("pre_build")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_run(self) -> typing.Optional[builtins.str]:
        '''`CC_PRE_RUN_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-run>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#pre_run Docker#pre_run}
        '''
        result = self._values.get("pre_run")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run_failed(self) -> typing.Optional[builtins.str]:
        '''`CC_RUN_FAILED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#run_failed Docker#run_failed}
        '''
        result = self._values.get("run_failed")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run_succeed(self) -> typing.Optional[builtins.str]:
        '''`CC_RUN_SUCCEEDED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#run_succeed Docker#run_succeed}
        '''
        result = self._values.get("run_succeed")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DockerHooks(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DockerHooksOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.docker.DockerHooksOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7605ee5e1dce5a9e0dab95b344022ab62ee4a2494735dba87ac0737ad6f4be6f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9792d9fdd4b436ff3d5f6d0ba8923f63a19b7252f36a2d1c1b00087c59f5746b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postBuild", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preBuild")
    def pre_build(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preBuild"))

    @pre_build.setter
    def pre_build(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__919dcfe0af1c7d53c668cf1b8a647a0981f90aa8ecf562f4d69fcc00dd405584)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preBuild", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preRun")
    def pre_run(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preRun"))

    @pre_run.setter
    def pre_run(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c980c0324b87f16819e56b5c17d7e203ccb0963861ada222dd47e47bdc1cab74)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runFailed")
    def run_failed(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runFailed"))

    @run_failed.setter
    def run_failed(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__777ded38856f61d773f9defeac979848b2234029db813cee830eef283169798c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runFailed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runSucceed")
    def run_succeed(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runSucceed"))

    @run_succeed.setter
    def run_succeed(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc631bb445c8826af85d40f87f993dc91109f3a7f9b9bc7256f2b3bf9385b989)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runSucceed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DockerHooks, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DockerHooks, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DockerHooks, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68a0857d4d699b96e8fd08e4f7ae8e2085b46e66cc2b509e8ac8705538b56851)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.docker.DockerNetworkgroups",
    jsii_struct_bases=[],
    name_mapping={"fqdn": "fqdn", "networkgroup_id": "networkgroupId"},
)
class DockerNetworkgroups:
    def __init__(self, *, fqdn: builtins.str, networkgroup_id: builtins.str) -> None:
        '''
        :param fqdn: domain name which will resolve to application instances inside the networkgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#fqdn Docker#fqdn}
        :param networkgroup_id: ID of the networkgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#networkgroup_id Docker#networkgroup_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31107614c4bbaab3e34d09ceed787a1600c1919196ac74a83248c288a3d4605b)
            check_type(argname="argument fqdn", value=fqdn, expected_type=type_hints["fqdn"])
            check_type(argname="argument networkgroup_id", value=networkgroup_id, expected_type=type_hints["networkgroup_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "fqdn": fqdn,
            "networkgroup_id": networkgroup_id,
        }

    @builtins.property
    def fqdn(self) -> builtins.str:
        '''domain name which will resolve to application instances inside the networkgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#fqdn Docker#fqdn}
        '''
        result = self._values.get("fqdn")
        assert result is not None, "Required property 'fqdn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def networkgroup_id(self) -> builtins.str:
        '''ID of the networkgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#networkgroup_id Docker#networkgroup_id}
        '''
        result = self._values.get("networkgroup_id")
        assert result is not None, "Required property 'networkgroup_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DockerNetworkgroups(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DockerNetworkgroupsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.docker.DockerNetworkgroupsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f3ec838e10bcde7226bbfd6481f1e03bdb6a06477d583d0796e1e9981b3dd617)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DockerNetworkgroupsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb0c4bb9e0e9c3e4a489e34ac0bbbb791306c4bd10364bf61646ec7f25e06348)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DockerNetworkgroupsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb1e42840757be5cb54ffe343aa764e3d337e9327627d135f7385807a26876be)
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
            type_hints = typing.get_type_hints(_typecheckingstub__089a1bfd290759f30fe8502be833866dfa0f6bf701e2da7990603b3ba9d7a87e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ec24354ada261efc7d664d1a2146d8a84c7e72de1c2212f9f67dc59c2abfe113)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DockerNetworkgroups]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DockerNetworkgroups]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DockerNetworkgroups]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d0a6e62c0f79e691ad79132161f850bf7ad20b0f4daa368e10f51773d915b162)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DockerNetworkgroupsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.docker.DockerNetworkgroupsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9e4d87df880e2372fbf7e22d0fac1a576b841cdd40576d6052c35a4d98ed4879)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3429aaf245a67b093c596f5f89aba507bfb1042f1c633d0064626bf67d82de1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fqdn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkgroupId")
    def networkgroup_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkgroupId"))

    @networkgroup_id.setter
    def networkgroup_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__495b0d58c37a7eeca2de3f1668b37fc135dc5c99dbb9093f7b0a7fdc1a7a688d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkgroupId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DockerNetworkgroups, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DockerNetworkgroups, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DockerNetworkgroups, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__049a983148dfcda1c219f09e37c106b1248ca8ab90700b7168446c38929d5c54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.docker.DockerVhosts",
    jsii_struct_bases=[],
    name_mapping={"fqdn": "fqdn", "path_begin": "pathBegin"},
)
class DockerVhosts:
    def __init__(
        self,
        *,
        fqdn: builtins.str,
        path_begin: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param fqdn: Fully qualified domain name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#fqdn Docker#fqdn}
        :param path_begin: Any HTTP request starting with this path will be sent to this application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#path_begin Docker#path_begin}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf002207ed79c31bd2508666596d1a249cf212ae9ff84b7555900e2c24b656a4)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#fqdn Docker#fqdn}
        '''
        result = self._values.get("fqdn")
        assert result is not None, "Required property 'fqdn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path_begin(self) -> typing.Optional[builtins.str]:
        '''Any HTTP request starting with this path will be sent to this application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/docker#path_begin Docker#path_begin}
        '''
        result = self._values.get("path_begin")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DockerVhosts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DockerVhostsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.docker.DockerVhostsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__97c874772259180ec9d8628435cd8294b9fbead5f3eda9826a813b6458b5425d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DockerVhostsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f28f87de30b7ef8aa9e64b33d623b3306a4b74e0537ac5a2fffccfeb4b803c9a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DockerVhostsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be91410e2f927e7c4e0fc0b313d77298cd0de2db1dbd838a0cf072a7f41574d0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b0c6636a1c20b8c99973a827d12fef35d4e226e9dd8d4505e6b17f6b3ababfb6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__56cf2f0ae7831774acd080f4319e1a0c7d9c2e0ff45a81f3b796f282d2e3b659)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DockerVhosts]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DockerVhosts]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DockerVhosts]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38054c1d44fd6c5a0761291dbc1624ac2105ebee3571c6502186de1f14e43ee7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DockerVhostsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.docker.DockerVhostsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8282cb880ad67a1d5152c06168cb9c9e6adab53c4b3db2d9cb4cbc498a27679)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b05a6c8a141f6b52a49a64f002de222bfcda1c3af2fdf0e9c893d18f0be9f96a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fqdn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pathBegin")
    def path_begin(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pathBegin"))

    @path_begin.setter
    def path_begin(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f22a57139a5a1151510a2bc2571b63f4d086aa6b1f6c79d7761b73cd7a31ad6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pathBegin", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[DockerVhosts, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[DockerVhosts, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[DockerVhosts, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc1a0e5dc5b53c1448ab4ee6a3cb0601223277d03e6176eb6589be8790022ffe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "Docker",
    "DockerConfig",
    "DockerDeployment",
    "DockerDeploymentOutputReference",
    "DockerHooks",
    "DockerHooksOutputReference",
    "DockerNetworkgroups",
    "DockerNetworkgroupsList",
    "DockerNetworkgroupsOutputReference",
    "DockerVhosts",
    "DockerVhostsList",
    "DockerVhostsOutputReference",
]

publication.publish()

def _typecheckingstub__139f2e10a95fe520cea2619a885599ffe08b128f3ecf2e949b99aec550660714(
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
    container_port: typing.Optional[jsii.Number] = None,
    container_port_tcp: typing.Optional[jsii.Number] = None,
    daemon_socket_mount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
    deployment: typing.Optional[typing.Union[DockerDeployment, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    dockerfile: typing.Optional[builtins.str] = None,
    enable_ipv6: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    exposed_environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    hooks: typing.Optional[typing.Union[DockerHooks, typing.Dict[builtins.str, typing.Any]]] = None,
    ipv6_cidr: typing.Optional[builtins.str] = None,
    networkgroups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DockerNetworkgroups, typing.Dict[builtins.str, typing.Any]]]]] = None,
    redirect_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    region: typing.Optional[builtins.str] = None,
    registry_password: typing.Optional[builtins.str] = None,
    registry_url: typing.Optional[builtins.str] = None,
    registry_user: typing.Optional[builtins.str] = None,
    sticky_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    vhosts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DockerVhosts, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__18f645304c0872e4649964fdbe570eb758a9e5b8f51aabd407337f61721aae70(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ccac66ddde622ebd293618fc1b74c0ee3a0f77c58cba84ee16c4e9647adc5e0(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DockerNetworkgroups, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5b40fe4e0a0adf6f3e5c9a8dd0abb9b68a2095fc6ffe360cfd25ab4372af4f9(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DockerVhosts, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c0749711dcddc1e3d76f3498344c930c5f7c62fd780e41eef4222f8e266d710(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__baeaddc2b86ac05ff6cce4b0a88c3bb8c3b2ee6b1a19fa85d74faf0ed7a4da90(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7be519c5759bd465e19b4572c02ebddcec5243bf8c1ae9cc16fa531fa2eb5e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81a3208c15656258c3588ec9c8b40478c81bb49a6e6f78a7918cef61a720727e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0696c554bc6bb6965b9b6495d7a4179fba6a7561f37af247ca17e405e0645333(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c043353e91e0eb6911cc881a0f96e25340d6c4ea3836cd98000de6808790104e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88c4d9aca50bc7df610733e30ef8cb7841840c87af7bb871da576e892c41bc1d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1d78e7a061ce4f1bae8507c96bbe536e46656f7da1f98fe639c0f273a837772(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e049f2d16bc3935c8c85be9fba183c3c069008582d1b71a2f8725705d1e1693e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__faa063eb97703f3457191714781fedc2d6e9017bc88a73adbb082723822326f9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d734ff3cfe24bee14181e875f7403548a3bf995c87b73d59825a8bc37aafe5bd(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6462649b547b944b10d18050a69e3fbadd7104e29957b77d0eef6838b37614db(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71818af7949e63e9634ce00fc4cd40285f5f2cb271b9a9a2a13f13bb283dd8b3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a46e5e5c131e45136f582c747bcf1de3467b6c714ded68f87e04395bff17831(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c241069f39bf5411eef12e7c84a04519a9a4f069f24b3b7eef817e7c337bdf54(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bef4f687e59280f3dfb28cae5eca82115a64eb3cc527ef35890258f1055bd3c8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ed9da5142468842205cbd771e234408f0aa3774f656097798586c30af878170(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64cd5b5a9d246e1bc221362c7e6ee626159c814852b11bee6f4937b5749278b7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e29eff9988c520079badb52a2f0d9933e28cd0de09f0f1f452b4906fcae9ff06(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31bc0b1a326dc093709f0b7ffa692e782f4059756277070a1984679da91d7fb9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5ccbf07795a4fda08a6cff90bdb04edc4a9e8fa338e111c69ce1507c2b0e552(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0737c5ffd274bcae4b29c1e68ab04fc7f3a0378342be4eb5622a20abed689b2c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__265a5314bef679b90be11beaaf3a215aa5f3ce4a5e4311ee0d99339d4b58f7ff(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__068985606a454df7c1c0a0fc91f5c3915d85afd9bdacc5b1ec324c35e4b8f568(
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
    container_port: typing.Optional[jsii.Number] = None,
    container_port_tcp: typing.Optional[jsii.Number] = None,
    daemon_socket_mount: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    dependencies: typing.Optional[typing.Sequence[builtins.str]] = None,
    deployment: typing.Optional[typing.Union[DockerDeployment, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    dockerfile: typing.Optional[builtins.str] = None,
    enable_ipv6: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    exposed_environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    hooks: typing.Optional[typing.Union[DockerHooks, typing.Dict[builtins.str, typing.Any]]] = None,
    ipv6_cidr: typing.Optional[builtins.str] = None,
    networkgroups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DockerNetworkgroups, typing.Dict[builtins.str, typing.Any]]]]] = None,
    redirect_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    region: typing.Optional[builtins.str] = None,
    registry_password: typing.Optional[builtins.str] = None,
    registry_url: typing.Optional[builtins.str] = None,
    registry_user: typing.Optional[builtins.str] = None,
    sticky_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    vhosts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DockerVhosts, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec45a5291509405d3f072317ccb59319253ad57b000e7f2964df29ce93e08292(
    *,
    authentication_basic: typing.Optional[builtins.str] = None,
    commit: typing.Optional[builtins.str] = None,
    repository: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e23093ea40bf6b5e3db10f9f835113aa5f4c3ec83effed11a0b2f2a6c23021e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33160c14a5132f2a0ca02e3fcc0ca70e0bc076627e71000b5d11d4788f1de7fd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff0db4e44e55551a37727358a383817119b26b3453a22a79e75c545b84fc625f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89e6931b456a0dd9f84e3c619d2a267ba02aabf5490489e2cbdbf83ffb197c04(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__970c60d56b6ee2708ef4ad370e7d7cb768e852295d1bed6db5e51a10d7c026ae(
    value: typing.Optional[typing.Union[DockerDeployment, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9365a11bdc78065791d403ac409ff85f368e47d38c4c24a384df0d2b2c5aebde(
    *,
    post_build: typing.Optional[builtins.str] = None,
    pre_build: typing.Optional[builtins.str] = None,
    pre_run: typing.Optional[builtins.str] = None,
    run_failed: typing.Optional[builtins.str] = None,
    run_succeed: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7605ee5e1dce5a9e0dab95b344022ab62ee4a2494735dba87ac0737ad6f4be6f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9792d9fdd4b436ff3d5f6d0ba8923f63a19b7252f36a2d1c1b00087c59f5746b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__919dcfe0af1c7d53c668cf1b8a647a0981f90aa8ecf562f4d69fcc00dd405584(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c980c0324b87f16819e56b5c17d7e203ccb0963861ada222dd47e47bdc1cab74(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__777ded38856f61d773f9defeac979848b2234029db813cee830eef283169798c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc631bb445c8826af85d40f87f993dc91109f3a7f9b9bc7256f2b3bf9385b989(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68a0857d4d699b96e8fd08e4f7ae8e2085b46e66cc2b509e8ac8705538b56851(
    value: typing.Optional[typing.Union[DockerHooks, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31107614c4bbaab3e34d09ceed787a1600c1919196ac74a83248c288a3d4605b(
    *,
    fqdn: builtins.str,
    networkgroup_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3ec838e10bcde7226bbfd6481f1e03bdb6a06477d583d0796e1e9981b3dd617(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb0c4bb9e0e9c3e4a489e34ac0bbbb791306c4bd10364bf61646ec7f25e06348(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb1e42840757be5cb54ffe343aa764e3d337e9327627d135f7385807a26876be(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__089a1bfd290759f30fe8502be833866dfa0f6bf701e2da7990603b3ba9d7a87e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec24354ada261efc7d664d1a2146d8a84c7e72de1c2212f9f67dc59c2abfe113(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0a6e62c0f79e691ad79132161f850bf7ad20b0f4daa368e10f51773d915b162(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DockerNetworkgroups]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e4d87df880e2372fbf7e22d0fac1a576b841cdd40576d6052c35a4d98ed4879(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3429aaf245a67b093c596f5f89aba507bfb1042f1c633d0064626bf67d82de1d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__495b0d58c37a7eeca2de3f1668b37fc135dc5c99dbb9093f7b0a7fdc1a7a688d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__049a983148dfcda1c219f09e37c106b1248ca8ab90700b7168446c38929d5c54(
    value: typing.Optional[typing.Union[DockerNetworkgroups, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf002207ed79c31bd2508666596d1a249cf212ae9ff84b7555900e2c24b656a4(
    *,
    fqdn: builtins.str,
    path_begin: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97c874772259180ec9d8628435cd8294b9fbead5f3eda9826a813b6458b5425d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f28f87de30b7ef8aa9e64b33d623b3306a4b74e0537ac5a2fffccfeb4b803c9a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be91410e2f927e7c4e0fc0b313d77298cd0de2db1dbd838a0cf072a7f41574d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0c6636a1c20b8c99973a827d12fef35d4e226e9dd8d4505e6b17f6b3ababfb6(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56cf2f0ae7831774acd080f4319e1a0c7d9c2e0ff45a81f3b796f282d2e3b659(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38054c1d44fd6c5a0761291dbc1624ac2105ebee3571c6502186de1f14e43ee7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DockerVhosts]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8282cb880ad67a1d5152c06168cb9c9e6adab53c4b3db2d9cb4cbc498a27679(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b05a6c8a141f6b52a49a64f002de222bfcda1c3af2fdf0e9c893d18f0be9f96a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f22a57139a5a1151510a2bc2571b63f4d086aa6b1f6c79d7761b73cd7a31ad6d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc1a0e5dc5b53c1448ab4ee6a3cb0601223277d03e6176eb6589be8790022ffe(
    value: typing.Optional[typing.Union[DockerVhosts, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass
