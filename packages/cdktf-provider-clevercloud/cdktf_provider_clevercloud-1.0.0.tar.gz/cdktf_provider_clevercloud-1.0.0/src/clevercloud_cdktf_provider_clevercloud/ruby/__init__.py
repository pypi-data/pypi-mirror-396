r'''
# `clevercloud_ruby`

Refer to the Terraform Registry for docs: [`clevercloud_ruby`](https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby).
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


class Ruby(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.ruby.Ruby",
):
    '''Represents a {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby clevercloud_ruby}.'''

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
        deployment: typing.Optional[typing.Union["RubyDeployment", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        enable_gzip_compression: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_sidekiq: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        exposed_environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        gzip_types: typing.Optional[builtins.str] = None,
        hooks: typing.Optional[typing.Union["RubyHooks", typing.Dict[builtins.str, typing.Any]]] = None,
        http_basic_auth: typing.Optional[builtins.str] = None,
        networkgroups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["RubyNetworkgroups", typing.Dict[builtins.str, typing.Any]]]]] = None,
        nginx_proxy_buffers: typing.Optional[builtins.str] = None,
        nginx_proxy_buffer_size: typing.Optional[builtins.str] = None,
        nginx_read_timeout: typing.Optional[jsii.Number] = None,
        rack_env: typing.Optional[builtins.str] = None,
        rackup_server: typing.Optional[builtins.str] = None,
        rails_env: typing.Optional[builtins.str] = None,
        rake_goals: typing.Optional[builtins.str] = None,
        redirect_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        region: typing.Optional[builtins.str] = None,
        ruby_version: typing.Optional[builtins.str] = None,
        sidekiq_files: typing.Optional[builtins.str] = None,
        static_files_path: typing.Optional[builtins.str] = None,
        static_url_prefix: typing.Optional[builtins.str] = None,
        static_webroot: typing.Optional[builtins.str] = None,
        sticky_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vhosts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["RubyVhosts", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby clevercloud_ruby} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param biggest_flavor: Biggest instance flavor, if different from smallest, enable auto-scaling. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#biggest_flavor Ruby#biggest_flavor}
        :param max_instance_count: Maximum instance count, if different from min value, enable auto-scaling. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#max_instance_count Ruby#max_instance_count}
        :param min_instance_count: Minimum instance count. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#min_instance_count Ruby#min_instance_count}
        :param name: Application name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#name Ruby#name}
        :param smallest_flavor: Smallest instance flavor. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#smallest_flavor Ruby#smallest_flavor}
        :param app_folder: Folder in which the application is located (inside the git repository). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#app_folder Ruby#app_folder}
        :param build_flavor: Use dedicated instance with given flavor for build phase. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#build_flavor Ruby#build_flavor}
        :param dependencies: A list of application or add-ons required to run this application. Can be either app_xxx or postgres_yyy ID format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#dependencies Ruby#dependencies}
        :param deployment: deployment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#deployment Ruby#deployment}
        :param description: Application description. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#description Ruby#description}
        :param enable_gzip_compression: Set to true to gzip-compress through Nginx. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#enable_gzip_compression Ruby#enable_gzip_compression}
        :param enable_sidekiq: Enable Sidekiq background process. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#enable_sidekiq Ruby#enable_sidekiq}
        :param environment: Environment variables injected into the application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#environment Ruby#environment}
        :param exposed_environment: Environment variables other linked applications will be able to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#exposed_environment Ruby#exposed_environment}
        :param gzip_types: Set the mime types to compress (default: 'text/* application/json application/xml application/javascript image/svg+xml'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#gzip_types Ruby#gzip_types}
        :param hooks: hooks block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#hooks Ruby#hooks}
        :param http_basic_auth: Restrict HTTP access to your application (format: 'login:password'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#http_basic_auth Ruby#http_basic_auth}
        :param networkgroups: List of networkgroups the application must be part of. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#networkgroups Ruby#networkgroups}
        :param nginx_proxy_buffers: Sets the number and size of the buffers used for reading a response from the proxied server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#nginx_proxy_buffers Ruby#nginx_proxy_buffers}
        :param nginx_proxy_buffer_size: Sets the size of the buffer used for reading the first part of the response received from the proxied server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#nginx_proxy_buffer_size Ruby#nginx_proxy_buffer_size}
        :param nginx_read_timeout: Read timeout in seconds (default: 300). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#nginx_read_timeout Ruby#nginx_read_timeout}
        :param rack_env: Rack environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#rack_env Ruby#rack_env}
        :param rackup_server: Server to use for serving the Ruby application (default: puma). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#rackup_server Ruby#rackup_server}
        :param rails_env: Rails environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#rails_env Ruby#rails_env}
        :param rake_goals: Comma-separated list of rake goals to execute (e.g., 'db:migrate,assets:precompile'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#rake_goals Ruby#rake_goals}
        :param redirect_https: Redirect client from plain to TLS port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#redirect_https Ruby#redirect_https}
        :param region: Geographical region where the database will be deployed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#region Ruby#region}
        :param ruby_version: Ruby version to use (e.g., '3.3', '3.3.1'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#ruby_version Ruby#ruby_version}
        :param sidekiq_files: Specify a list of Sidekiq configuration files (e.g., './config/sidekiq_1.yml,./config/sidekiq_2.yml'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#sidekiq_files Ruby#sidekiq_files}
        :param static_files_path: Relative path to where your static files are stored. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#static_files_path Ruby#static_files_path}
        :param static_url_prefix: The URL path under which you want to serve static files, usually /public. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#static_url_prefix Ruby#static_url_prefix}
        :param static_webroot: Path to the web content to serve, relative to the root of your application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#static_webroot Ruby#static_webroot}
        :param sticky_sessions: Enable sticky sessions, use it when your client sessions are instances scoped. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#sticky_sessions Ruby#sticky_sessions}
        :param vhosts: List of virtual hosts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#vhosts Ruby#vhosts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__503494d7f6199feae3adb1a0f50e71da1b5cf701da8afa1b17cc3b1a13f36528)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = RubyConfig(
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
            enable_gzip_compression=enable_gzip_compression,
            enable_sidekiq=enable_sidekiq,
            environment=environment,
            exposed_environment=exposed_environment,
            gzip_types=gzip_types,
            hooks=hooks,
            http_basic_auth=http_basic_auth,
            networkgroups=networkgroups,
            nginx_proxy_buffers=nginx_proxy_buffers,
            nginx_proxy_buffer_size=nginx_proxy_buffer_size,
            nginx_read_timeout=nginx_read_timeout,
            rack_env=rack_env,
            rackup_server=rackup_server,
            rails_env=rails_env,
            rake_goals=rake_goals,
            redirect_https=redirect_https,
            region=region,
            ruby_version=ruby_version,
            sidekiq_files=sidekiq_files,
            static_files_path=static_files_path,
            static_url_prefix=static_url_prefix,
            static_webroot=static_webroot,
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
        '''Generates CDKTF code for importing a Ruby resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the Ruby to import.
        :param import_from_id: The id of the existing Ruby that should be imported. Refer to the {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the Ruby to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c109dd3db6f094373ca808ffb9cd9daac406ccc56ab7fc0d25fd447b51383324)
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
        :param authentication_basic: user ans password ':' separated, (PersonalAccessToken in Github case). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#authentication_basic Ruby#authentication_basic}
        :param commit: Support multiple syntax like ``refs/heads/[BRANCH]``, ``github_hook`` or ``[COMMIT]``, when using the special value ``github_hook``, we will link the application to the Github repository. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#commit Ruby#commit}
        :param repository: The repository URL to deploy, can be 'https://...', 'file://...'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#repository Ruby#repository}
        '''
        value = RubyDeployment(
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
        :param post_build: `CC_POST_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#post-build>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#post_build Ruby#post_build}
        :param pre_build: `CC_PRE_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-build>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#pre_build Ruby#pre_build}
        :param pre_run: `CC_PRE_RUN_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-run>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#pre_run Ruby#pre_run}
        :param run_failed: `CC_RUN_FAILED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#run_failed Ruby#run_failed}
        :param run_succeed: `CC_RUN_SUCCEEDED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#run_succeed Ruby#run_succeed}
        '''
        value = RubyHooks(
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
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["RubyNetworkgroups", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__832701dae3a771664ece7c25d8ca68eaefa04c67ec90f1c1135085b0d160f938)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNetworkgroups", [value]))

    @jsii.member(jsii_name="putVhosts")
    def put_vhosts(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["RubyVhosts", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ed63f27e9c1dea6d954e497ac8e152477d854332bc0faf01be41f846248ca4c)
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

    @jsii.member(jsii_name="resetEnableGzipCompression")
    def reset_enable_gzip_compression(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableGzipCompression", []))

    @jsii.member(jsii_name="resetEnableSidekiq")
    def reset_enable_sidekiq(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableSidekiq", []))

    @jsii.member(jsii_name="resetEnvironment")
    def reset_environment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnvironment", []))

    @jsii.member(jsii_name="resetExposedEnvironment")
    def reset_exposed_environment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExposedEnvironment", []))

    @jsii.member(jsii_name="resetGzipTypes")
    def reset_gzip_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGzipTypes", []))

    @jsii.member(jsii_name="resetHooks")
    def reset_hooks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHooks", []))

    @jsii.member(jsii_name="resetHttpBasicAuth")
    def reset_http_basic_auth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpBasicAuth", []))

    @jsii.member(jsii_name="resetNetworkgroups")
    def reset_networkgroups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkgroups", []))

    @jsii.member(jsii_name="resetNginxProxyBuffers")
    def reset_nginx_proxy_buffers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNginxProxyBuffers", []))

    @jsii.member(jsii_name="resetNginxProxyBufferSize")
    def reset_nginx_proxy_buffer_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNginxProxyBufferSize", []))

    @jsii.member(jsii_name="resetNginxReadTimeout")
    def reset_nginx_read_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNginxReadTimeout", []))

    @jsii.member(jsii_name="resetRackEnv")
    def reset_rack_env(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRackEnv", []))

    @jsii.member(jsii_name="resetRackupServer")
    def reset_rackup_server(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRackupServer", []))

    @jsii.member(jsii_name="resetRailsEnv")
    def reset_rails_env(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRailsEnv", []))

    @jsii.member(jsii_name="resetRakeGoals")
    def reset_rake_goals(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRakeGoals", []))

    @jsii.member(jsii_name="resetRedirectHttps")
    def reset_redirect_https(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedirectHttps", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetRubyVersion")
    def reset_ruby_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRubyVersion", []))

    @jsii.member(jsii_name="resetSidekiqFiles")
    def reset_sidekiq_files(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSidekiqFiles", []))

    @jsii.member(jsii_name="resetStaticFilesPath")
    def reset_static_files_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStaticFilesPath", []))

    @jsii.member(jsii_name="resetStaticUrlPrefix")
    def reset_static_url_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStaticUrlPrefix", []))

    @jsii.member(jsii_name="resetStaticWebroot")
    def reset_static_webroot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStaticWebroot", []))

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
    def deployment(self) -> "RubyDeploymentOutputReference":
        return typing.cast("RubyDeploymentOutputReference", jsii.get(self, "deployment"))

    @builtins.property
    @jsii.member(jsii_name="deployUrl")
    def deploy_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deployUrl"))

    @builtins.property
    @jsii.member(jsii_name="hooks")
    def hooks(self) -> "RubyHooksOutputReference":
        return typing.cast("RubyHooksOutputReference", jsii.get(self, "hooks"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="networkgroups")
    def networkgroups(self) -> "RubyNetworkgroupsList":
        return typing.cast("RubyNetworkgroupsList", jsii.get(self, "networkgroups"))

    @builtins.property
    @jsii.member(jsii_name="vhosts")
    def vhosts(self) -> "RubyVhostsList":
        return typing.cast("RubyVhostsList", jsii.get(self, "vhosts"))

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
    ) -> typing.Optional[typing.Union["RubyDeployment", _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["RubyDeployment", _cdktf_9a9027ec.IResolvable]], jsii.get(self, "deploymentInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="enableGzipCompressionInput")
    def enable_gzip_compression_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableGzipCompressionInput"))

    @builtins.property
    @jsii.member(jsii_name="enableSidekiqInput")
    def enable_sidekiq_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableSidekiqInput"))

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
    @jsii.member(jsii_name="gzipTypesInput")
    def gzip_types_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gzipTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="hooksInput")
    def hooks_input(
        self,
    ) -> typing.Optional[typing.Union["RubyHooks", _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union["RubyHooks", _cdktf_9a9027ec.IResolvable]], jsii.get(self, "hooksInput"))

    @builtins.property
    @jsii.member(jsii_name="httpBasicAuthInput")
    def http_basic_auth_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "httpBasicAuthInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RubyNetworkgroups"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RubyNetworkgroups"]]], jsii.get(self, "networkgroupsInput"))

    @builtins.property
    @jsii.member(jsii_name="nginxProxyBuffersInput")
    def nginx_proxy_buffers_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nginxProxyBuffersInput"))

    @builtins.property
    @jsii.member(jsii_name="nginxProxyBufferSizeInput")
    def nginx_proxy_buffer_size_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nginxProxyBufferSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="nginxReadTimeoutInput")
    def nginx_read_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "nginxReadTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="rackEnvInput")
    def rack_env_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rackEnvInput"))

    @builtins.property
    @jsii.member(jsii_name="rackupServerInput")
    def rackup_server_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rackupServerInput"))

    @builtins.property
    @jsii.member(jsii_name="railsEnvInput")
    def rails_env_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "railsEnvInput"))

    @builtins.property
    @jsii.member(jsii_name="rakeGoalsInput")
    def rake_goals_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rakeGoalsInput"))

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
    @jsii.member(jsii_name="rubyVersionInput")
    def ruby_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "rubyVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="sidekiqFilesInput")
    def sidekiq_files_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sidekiqFilesInput"))

    @builtins.property
    @jsii.member(jsii_name="smallestFlavorInput")
    def smallest_flavor_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "smallestFlavorInput"))

    @builtins.property
    @jsii.member(jsii_name="staticFilesPathInput")
    def static_files_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "staticFilesPathInput"))

    @builtins.property
    @jsii.member(jsii_name="staticUrlPrefixInput")
    def static_url_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "staticUrlPrefixInput"))

    @builtins.property
    @jsii.member(jsii_name="staticWebrootInput")
    def static_webroot_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "staticWebrootInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RubyVhosts"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RubyVhosts"]]], jsii.get(self, "vhostsInput"))

    @builtins.property
    @jsii.member(jsii_name="appFolder")
    def app_folder(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appFolder"))

    @app_folder.setter
    def app_folder(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23d6552cbc61c9e8a5ef8414d228ae52c7f66531e4bdda9b65909f4a5e2e1014)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appFolder", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="biggestFlavor")
    def biggest_flavor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "biggestFlavor"))

    @biggest_flavor.setter
    def biggest_flavor(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__faee2672584a161d92c31d7d22bf2676c9b34a93bfe58162d735811facd3b034)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "biggestFlavor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="buildFlavor")
    def build_flavor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "buildFlavor"))

    @build_flavor.setter
    def build_flavor(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bde0caf8baa1c216e1267345d826be6c72ad8cd5841c9556cea4a0d1d4f15c7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "buildFlavor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dependencies")
    def dependencies(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dependencies"))

    @dependencies.setter
    def dependencies(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b934131ffcfb39e19273c676efd4333d3fba24475a4c7207d2165fc94338f887)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dependencies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7253f0e3c2317ad162b8dff6f1f69a9942d614c5ef78dec825f40cd822a947d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableGzipCompression")
    def enable_gzip_compression(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableGzipCompression"))

    @enable_gzip_compression.setter
    def enable_gzip_compression(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b258b56cde2cd11617c90b09674c6435dea15ad9cec9f7a00b3b08d9e926a60a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableGzipCompression", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableSidekiq")
    def enable_sidekiq(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableSidekiq"))

    @enable_sidekiq.setter
    def enable_sidekiq(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7dfa05392fd37b28c9661155fc31e214c15bc2c7e468b56951be61cceecf2ef1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableSidekiq", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="environment")
    def environment(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "environment"))

    @environment.setter
    def environment(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f678fad51eafb3bab8a2411a56f6252af5fcaf7cb22c28006113d7411ebd645c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__efcd72aecee8b567e61686c89de54895adbcca54e37a20985935496bccda5a94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exposedEnvironment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gzipTypes")
    def gzip_types(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gzipTypes"))

    @gzip_types.setter
    def gzip_types(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8826818132763c864c4edf9304f452c79a56143d6aacd6c84b93279112205fa8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gzipTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpBasicAuth")
    def http_basic_auth(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "httpBasicAuth"))

    @http_basic_auth.setter
    def http_basic_auth(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f184a662fff17e23c625b764bc227b27bdcb7628f28dede51494faa4f72f0b58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpBasicAuth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxInstanceCount")
    def max_instance_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxInstanceCount"))

    @max_instance_count.setter
    def max_instance_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cafd0d8e23f87cfe9c8ac83dd7d0dc679e423866cb43964b5eb871aa77037c64)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxInstanceCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minInstanceCount")
    def min_instance_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minInstanceCount"))

    @min_instance_count.setter
    def min_instance_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c18825ee90d9d3708700040f9f8f81ce5813df1a3604759f60528f7b2020e680)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minInstanceCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0738b118edad9fe00edbac76f9f31c44cf922f7fb55f87df1e0cb728278346d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nginxProxyBuffers")
    def nginx_proxy_buffers(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nginxProxyBuffers"))

    @nginx_proxy_buffers.setter
    def nginx_proxy_buffers(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2779f8e1efaeb944e089dd256c30159d54dbe93dd22dffa87a3039fc9b8c1a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nginxProxyBuffers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nginxProxyBufferSize")
    def nginx_proxy_buffer_size(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nginxProxyBufferSize"))

    @nginx_proxy_buffer_size.setter
    def nginx_proxy_buffer_size(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6352690811198c6e1c038efb6f51bdcf32aa9ec5d3303423a89377405cd22151)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nginxProxyBufferSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="nginxReadTimeout")
    def nginx_read_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "nginxReadTimeout"))

    @nginx_read_timeout.setter
    def nginx_read_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d79d6fd3aff360d6415a5d2c4dd957b7aa8a006dc2f05c8f1acb1dcc5e4bc5c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "nginxReadTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rackEnv")
    def rack_env(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rackEnv"))

    @rack_env.setter
    def rack_env(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec88f4880a7d36255a0a91cd357d3f85518f47f101c364630842d97bc9a3ad4d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rackEnv", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rackupServer")
    def rackup_server(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rackupServer"))

    @rackup_server.setter
    def rackup_server(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39af4e4ea225733dd03a6331085e50d2b9f0dde01386670c3b2da284426f0559)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rackupServer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="railsEnv")
    def rails_env(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "railsEnv"))

    @rails_env.setter
    def rails_env(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdb890bdc8d1782fe7258e53181d6393fd2376ecbcb98177e9cc76e464eeada7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "railsEnv", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rakeGoals")
    def rake_goals(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rakeGoals"))

    @rake_goals.setter
    def rake_goals(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44f55806df519fd46f3adfdbb17b201d0eb0ca48cbe126b49b5b271d17a76370)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rakeGoals", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__6e317d1468fcc8ff379c888d6c6fecff40a105c679313ccec75a5a0913299c28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "redirectHttps", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efeb1a87a2843d8a51f158ea9da05174ca79d3e0cb139ed4b671978f10403268)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="rubyVersion")
    def ruby_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "rubyVersion"))

    @ruby_version.setter
    def ruby_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__743aeddb227dfce0d97f0ffd9dfbda7685e4ebedcc934d0c0cee94dd6803fff8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "rubyVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sidekiqFiles")
    def sidekiq_files(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sidekiqFiles"))

    @sidekiq_files.setter
    def sidekiq_files(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d81d50a4c86015044ae24e7a6fada5e8394d285ecd0a9f9ca2df9a42af6cfe32)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sidekiqFiles", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="smallestFlavor")
    def smallest_flavor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "smallestFlavor"))

    @smallest_flavor.setter
    def smallest_flavor(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7119137b2bcfa0bc1f79876132539e88be380ab3e3d0eaba581e34fd9fc456b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "smallestFlavor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="staticFilesPath")
    def static_files_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "staticFilesPath"))

    @static_files_path.setter
    def static_files_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__995f4193cfad05ad2c0190649420b044bec98603d2f59b744553625f3bbe83f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "staticFilesPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="staticUrlPrefix")
    def static_url_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "staticUrlPrefix"))

    @static_url_prefix.setter
    def static_url_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d1b3464487ec06c654f1124eb3444ae3654577cbeec4f90216ad88baaa97bf8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "staticUrlPrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="staticWebroot")
    def static_webroot(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "staticWebroot"))

    @static_webroot.setter
    def static_webroot(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c53be92c6c2746fd3e324ae0ec8abfcc31355edeccaf9814467f2cce4bb55a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "staticWebroot", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__a0a37ede2e791992cc6ee340f1321d682c33481db18540481da49f52d11fd09a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stickySessions", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.ruby.RubyConfig",
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
        "enable_gzip_compression": "enableGzipCompression",
        "enable_sidekiq": "enableSidekiq",
        "environment": "environment",
        "exposed_environment": "exposedEnvironment",
        "gzip_types": "gzipTypes",
        "hooks": "hooks",
        "http_basic_auth": "httpBasicAuth",
        "networkgroups": "networkgroups",
        "nginx_proxy_buffers": "nginxProxyBuffers",
        "nginx_proxy_buffer_size": "nginxProxyBufferSize",
        "nginx_read_timeout": "nginxReadTimeout",
        "rack_env": "rackEnv",
        "rackup_server": "rackupServer",
        "rails_env": "railsEnv",
        "rake_goals": "rakeGoals",
        "redirect_https": "redirectHttps",
        "region": "region",
        "ruby_version": "rubyVersion",
        "sidekiq_files": "sidekiqFiles",
        "static_files_path": "staticFilesPath",
        "static_url_prefix": "staticUrlPrefix",
        "static_webroot": "staticWebroot",
        "sticky_sessions": "stickySessions",
        "vhosts": "vhosts",
    },
)
class RubyConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        deployment: typing.Optional[typing.Union["RubyDeployment", typing.Dict[builtins.str, typing.Any]]] = None,
        description: typing.Optional[builtins.str] = None,
        enable_gzip_compression: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_sidekiq: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        exposed_environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        gzip_types: typing.Optional[builtins.str] = None,
        hooks: typing.Optional[typing.Union["RubyHooks", typing.Dict[builtins.str, typing.Any]]] = None,
        http_basic_auth: typing.Optional[builtins.str] = None,
        networkgroups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["RubyNetworkgroups", typing.Dict[builtins.str, typing.Any]]]]] = None,
        nginx_proxy_buffers: typing.Optional[builtins.str] = None,
        nginx_proxy_buffer_size: typing.Optional[builtins.str] = None,
        nginx_read_timeout: typing.Optional[jsii.Number] = None,
        rack_env: typing.Optional[builtins.str] = None,
        rackup_server: typing.Optional[builtins.str] = None,
        rails_env: typing.Optional[builtins.str] = None,
        rake_goals: typing.Optional[builtins.str] = None,
        redirect_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        region: typing.Optional[builtins.str] = None,
        ruby_version: typing.Optional[builtins.str] = None,
        sidekiq_files: typing.Optional[builtins.str] = None,
        static_files_path: typing.Optional[builtins.str] = None,
        static_url_prefix: typing.Optional[builtins.str] = None,
        static_webroot: typing.Optional[builtins.str] = None,
        sticky_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        vhosts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["RubyVhosts", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param biggest_flavor: Biggest instance flavor, if different from smallest, enable auto-scaling. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#biggest_flavor Ruby#biggest_flavor}
        :param max_instance_count: Maximum instance count, if different from min value, enable auto-scaling. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#max_instance_count Ruby#max_instance_count}
        :param min_instance_count: Minimum instance count. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#min_instance_count Ruby#min_instance_count}
        :param name: Application name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#name Ruby#name}
        :param smallest_flavor: Smallest instance flavor. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#smallest_flavor Ruby#smallest_flavor}
        :param app_folder: Folder in which the application is located (inside the git repository). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#app_folder Ruby#app_folder}
        :param build_flavor: Use dedicated instance with given flavor for build phase. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#build_flavor Ruby#build_flavor}
        :param dependencies: A list of application or add-ons required to run this application. Can be either app_xxx or postgres_yyy ID format. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#dependencies Ruby#dependencies}
        :param deployment: deployment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#deployment Ruby#deployment}
        :param description: Application description. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#description Ruby#description}
        :param enable_gzip_compression: Set to true to gzip-compress through Nginx. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#enable_gzip_compression Ruby#enable_gzip_compression}
        :param enable_sidekiq: Enable Sidekiq background process. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#enable_sidekiq Ruby#enable_sidekiq}
        :param environment: Environment variables injected into the application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#environment Ruby#environment}
        :param exposed_environment: Environment variables other linked applications will be able to use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#exposed_environment Ruby#exposed_environment}
        :param gzip_types: Set the mime types to compress (default: 'text/* application/json application/xml application/javascript image/svg+xml'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#gzip_types Ruby#gzip_types}
        :param hooks: hooks block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#hooks Ruby#hooks}
        :param http_basic_auth: Restrict HTTP access to your application (format: 'login:password'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#http_basic_auth Ruby#http_basic_auth}
        :param networkgroups: List of networkgroups the application must be part of. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#networkgroups Ruby#networkgroups}
        :param nginx_proxy_buffers: Sets the number and size of the buffers used for reading a response from the proxied server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#nginx_proxy_buffers Ruby#nginx_proxy_buffers}
        :param nginx_proxy_buffer_size: Sets the size of the buffer used for reading the first part of the response received from the proxied server. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#nginx_proxy_buffer_size Ruby#nginx_proxy_buffer_size}
        :param nginx_read_timeout: Read timeout in seconds (default: 300). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#nginx_read_timeout Ruby#nginx_read_timeout}
        :param rack_env: Rack environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#rack_env Ruby#rack_env}
        :param rackup_server: Server to use for serving the Ruby application (default: puma). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#rackup_server Ruby#rackup_server}
        :param rails_env: Rails environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#rails_env Ruby#rails_env}
        :param rake_goals: Comma-separated list of rake goals to execute (e.g., 'db:migrate,assets:precompile'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#rake_goals Ruby#rake_goals}
        :param redirect_https: Redirect client from plain to TLS port. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#redirect_https Ruby#redirect_https}
        :param region: Geographical region where the database will be deployed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#region Ruby#region}
        :param ruby_version: Ruby version to use (e.g., '3.3', '3.3.1'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#ruby_version Ruby#ruby_version}
        :param sidekiq_files: Specify a list of Sidekiq configuration files (e.g., './config/sidekiq_1.yml,./config/sidekiq_2.yml'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#sidekiq_files Ruby#sidekiq_files}
        :param static_files_path: Relative path to where your static files are stored. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#static_files_path Ruby#static_files_path}
        :param static_url_prefix: The URL path under which you want to serve static files, usually /public. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#static_url_prefix Ruby#static_url_prefix}
        :param static_webroot: Path to the web content to serve, relative to the root of your application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#static_webroot Ruby#static_webroot}
        :param sticky_sessions: Enable sticky sessions, use it when your client sessions are instances scoped. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#sticky_sessions Ruby#sticky_sessions}
        :param vhosts: List of virtual hosts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#vhosts Ruby#vhosts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(deployment, dict):
            deployment = RubyDeployment(**deployment)
        if isinstance(hooks, dict):
            hooks = RubyHooks(**hooks)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ea27122968680ec8354b0cb9f19048b9a1077097b9e19dc43dd93fc3747cb27)
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
            check_type(argname="argument enable_gzip_compression", value=enable_gzip_compression, expected_type=type_hints["enable_gzip_compression"])
            check_type(argname="argument enable_sidekiq", value=enable_sidekiq, expected_type=type_hints["enable_sidekiq"])
            check_type(argname="argument environment", value=environment, expected_type=type_hints["environment"])
            check_type(argname="argument exposed_environment", value=exposed_environment, expected_type=type_hints["exposed_environment"])
            check_type(argname="argument gzip_types", value=gzip_types, expected_type=type_hints["gzip_types"])
            check_type(argname="argument hooks", value=hooks, expected_type=type_hints["hooks"])
            check_type(argname="argument http_basic_auth", value=http_basic_auth, expected_type=type_hints["http_basic_auth"])
            check_type(argname="argument networkgroups", value=networkgroups, expected_type=type_hints["networkgroups"])
            check_type(argname="argument nginx_proxy_buffers", value=nginx_proxy_buffers, expected_type=type_hints["nginx_proxy_buffers"])
            check_type(argname="argument nginx_proxy_buffer_size", value=nginx_proxy_buffer_size, expected_type=type_hints["nginx_proxy_buffer_size"])
            check_type(argname="argument nginx_read_timeout", value=nginx_read_timeout, expected_type=type_hints["nginx_read_timeout"])
            check_type(argname="argument rack_env", value=rack_env, expected_type=type_hints["rack_env"])
            check_type(argname="argument rackup_server", value=rackup_server, expected_type=type_hints["rackup_server"])
            check_type(argname="argument rails_env", value=rails_env, expected_type=type_hints["rails_env"])
            check_type(argname="argument rake_goals", value=rake_goals, expected_type=type_hints["rake_goals"])
            check_type(argname="argument redirect_https", value=redirect_https, expected_type=type_hints["redirect_https"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument ruby_version", value=ruby_version, expected_type=type_hints["ruby_version"])
            check_type(argname="argument sidekiq_files", value=sidekiq_files, expected_type=type_hints["sidekiq_files"])
            check_type(argname="argument static_files_path", value=static_files_path, expected_type=type_hints["static_files_path"])
            check_type(argname="argument static_url_prefix", value=static_url_prefix, expected_type=type_hints["static_url_prefix"])
            check_type(argname="argument static_webroot", value=static_webroot, expected_type=type_hints["static_webroot"])
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
        if enable_gzip_compression is not None:
            self._values["enable_gzip_compression"] = enable_gzip_compression
        if enable_sidekiq is not None:
            self._values["enable_sidekiq"] = enable_sidekiq
        if environment is not None:
            self._values["environment"] = environment
        if exposed_environment is not None:
            self._values["exposed_environment"] = exposed_environment
        if gzip_types is not None:
            self._values["gzip_types"] = gzip_types
        if hooks is not None:
            self._values["hooks"] = hooks
        if http_basic_auth is not None:
            self._values["http_basic_auth"] = http_basic_auth
        if networkgroups is not None:
            self._values["networkgroups"] = networkgroups
        if nginx_proxy_buffers is not None:
            self._values["nginx_proxy_buffers"] = nginx_proxy_buffers
        if nginx_proxy_buffer_size is not None:
            self._values["nginx_proxy_buffer_size"] = nginx_proxy_buffer_size
        if nginx_read_timeout is not None:
            self._values["nginx_read_timeout"] = nginx_read_timeout
        if rack_env is not None:
            self._values["rack_env"] = rack_env
        if rackup_server is not None:
            self._values["rackup_server"] = rackup_server
        if rails_env is not None:
            self._values["rails_env"] = rails_env
        if rake_goals is not None:
            self._values["rake_goals"] = rake_goals
        if redirect_https is not None:
            self._values["redirect_https"] = redirect_https
        if region is not None:
            self._values["region"] = region
        if ruby_version is not None:
            self._values["ruby_version"] = ruby_version
        if sidekiq_files is not None:
            self._values["sidekiq_files"] = sidekiq_files
        if static_files_path is not None:
            self._values["static_files_path"] = static_files_path
        if static_url_prefix is not None:
            self._values["static_url_prefix"] = static_url_prefix
        if static_webroot is not None:
            self._values["static_webroot"] = static_webroot
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#biggest_flavor Ruby#biggest_flavor}
        '''
        result = self._values.get("biggest_flavor")
        assert result is not None, "Required property 'biggest_flavor' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def max_instance_count(self) -> jsii.Number:
        '''Maximum instance count, if different from min value, enable auto-scaling.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#max_instance_count Ruby#max_instance_count}
        '''
        result = self._values.get("max_instance_count")
        assert result is not None, "Required property 'max_instance_count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def min_instance_count(self) -> jsii.Number:
        '''Minimum instance count.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#min_instance_count Ruby#min_instance_count}
        '''
        result = self._values.get("min_instance_count")
        assert result is not None, "Required property 'min_instance_count' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Application name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#name Ruby#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def smallest_flavor(self) -> builtins.str:
        '''Smallest instance flavor.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#smallest_flavor Ruby#smallest_flavor}
        '''
        result = self._values.get("smallest_flavor")
        assert result is not None, "Required property 'smallest_flavor' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def app_folder(self) -> typing.Optional[builtins.str]:
        '''Folder in which the application is located (inside the git repository).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#app_folder Ruby#app_folder}
        '''
        result = self._values.get("app_folder")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def build_flavor(self) -> typing.Optional[builtins.str]:
        '''Use dedicated instance with given flavor for build phase.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#build_flavor Ruby#build_flavor}
        '''
        result = self._values.get("build_flavor")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dependencies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of application or add-ons required to run this application. Can be either app_xxx or postgres_yyy ID format.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#dependencies Ruby#dependencies}
        '''
        result = self._values.get("dependencies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def deployment(self) -> typing.Optional["RubyDeployment"]:
        '''deployment block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#deployment Ruby#deployment}
        '''
        result = self._values.get("deployment")
        return typing.cast(typing.Optional["RubyDeployment"], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Application description.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#description Ruby#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_gzip_compression(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Set to true to gzip-compress through Nginx.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#enable_gzip_compression Ruby#enable_gzip_compression}
        '''
        result = self._values.get("enable_gzip_compression")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enable_sidekiq(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable Sidekiq background process.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#enable_sidekiq Ruby#enable_sidekiq}
        '''
        result = self._values.get("enable_sidekiq")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Environment variables injected into the application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#environment Ruby#environment}
        '''
        result = self._values.get("environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def exposed_environment(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Environment variables other linked applications will be able to use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#exposed_environment Ruby#exposed_environment}
        '''
        result = self._values.get("exposed_environment")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def gzip_types(self) -> typing.Optional[builtins.str]:
        '''Set the mime types to compress (default: 'text/* application/json application/xml application/javascript image/svg+xml').

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#gzip_types Ruby#gzip_types}
        '''
        result = self._values.get("gzip_types")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hooks(self) -> typing.Optional["RubyHooks"]:
        '''hooks block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#hooks Ruby#hooks}
        '''
        result = self._values.get("hooks")
        return typing.cast(typing.Optional["RubyHooks"], result)

    @builtins.property
    def http_basic_auth(self) -> typing.Optional[builtins.str]:
        '''Restrict HTTP access to your application (format: 'login:password').

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#http_basic_auth Ruby#http_basic_auth}
        '''
        result = self._values.get("http_basic_auth")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def networkgroups(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RubyNetworkgroups"]]]:
        '''List of networkgroups the application must be part of.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#networkgroups Ruby#networkgroups}
        '''
        result = self._values.get("networkgroups")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RubyNetworkgroups"]]], result)

    @builtins.property
    def nginx_proxy_buffers(self) -> typing.Optional[builtins.str]:
        '''Sets the number and size of the buffers used for reading a response from the proxied server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#nginx_proxy_buffers Ruby#nginx_proxy_buffers}
        '''
        result = self._values.get("nginx_proxy_buffers")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nginx_proxy_buffer_size(self) -> typing.Optional[builtins.str]:
        '''Sets the size of the buffer used for reading the first part of the response received from the proxied server.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#nginx_proxy_buffer_size Ruby#nginx_proxy_buffer_size}
        '''
        result = self._values.get("nginx_proxy_buffer_size")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def nginx_read_timeout(self) -> typing.Optional[jsii.Number]:
        '''Read timeout in seconds (default: 300).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#nginx_read_timeout Ruby#nginx_read_timeout}
        '''
        result = self._values.get("nginx_read_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def rack_env(self) -> typing.Optional[builtins.str]:
        '''Rack environment variable.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#rack_env Ruby#rack_env}
        '''
        result = self._values.get("rack_env")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rackup_server(self) -> typing.Optional[builtins.str]:
        '''Server to use for serving the Ruby application (default: puma).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#rackup_server Ruby#rackup_server}
        '''
        result = self._values.get("rackup_server")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rails_env(self) -> typing.Optional[builtins.str]:
        '''Rails environment variable.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#rails_env Ruby#rails_env}
        '''
        result = self._values.get("rails_env")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rake_goals(self) -> typing.Optional[builtins.str]:
        '''Comma-separated list of rake goals to execute (e.g., 'db:migrate,assets:precompile').

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#rake_goals Ruby#rake_goals}
        '''
        result = self._values.get("rake_goals")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def redirect_https(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Redirect client from plain to TLS port.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#redirect_https Ruby#redirect_https}
        '''
        result = self._values.get("redirect_https")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Geographical region where the database will be deployed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#region Ruby#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ruby_version(self) -> typing.Optional[builtins.str]:
        '''Ruby version to use (e.g., '3.3', '3.3.1').

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#ruby_version Ruby#ruby_version}
        '''
        result = self._values.get("ruby_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sidekiq_files(self) -> typing.Optional[builtins.str]:
        '''Specify a list of Sidekiq configuration files (e.g., './config/sidekiq_1.yml,./config/sidekiq_2.yml').

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#sidekiq_files Ruby#sidekiq_files}
        '''
        result = self._values.get("sidekiq_files")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def static_files_path(self) -> typing.Optional[builtins.str]:
        '''Relative path to where your static files are stored.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#static_files_path Ruby#static_files_path}
        '''
        result = self._values.get("static_files_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def static_url_prefix(self) -> typing.Optional[builtins.str]:
        '''The URL path under which you want to serve static files, usually /public.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#static_url_prefix Ruby#static_url_prefix}
        '''
        result = self._values.get("static_url_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def static_webroot(self) -> typing.Optional[builtins.str]:
        '''Path to the web content to serve, relative to the root of your application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#static_webroot Ruby#static_webroot}
        '''
        result = self._values.get("static_webroot")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sticky_sessions(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable sticky sessions, use it when your client sessions are instances scoped.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#sticky_sessions Ruby#sticky_sessions}
        '''
        result = self._values.get("sticky_sessions")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def vhosts(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RubyVhosts"]]]:
        '''List of virtual hosts.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#vhosts Ruby#vhosts}
        '''
        result = self._values.get("vhosts")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["RubyVhosts"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RubyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.ruby.RubyDeployment",
    jsii_struct_bases=[],
    name_mapping={
        "authentication_basic": "authenticationBasic",
        "commit": "commit",
        "repository": "repository",
    },
)
class RubyDeployment:
    def __init__(
        self,
        *,
        authentication_basic: typing.Optional[builtins.str] = None,
        commit: typing.Optional[builtins.str] = None,
        repository: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param authentication_basic: user ans password ':' separated, (PersonalAccessToken in Github case). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#authentication_basic Ruby#authentication_basic}
        :param commit: Support multiple syntax like ``refs/heads/[BRANCH]``, ``github_hook`` or ``[COMMIT]``, when using the special value ``github_hook``, we will link the application to the Github repository. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#commit Ruby#commit}
        :param repository: The repository URL to deploy, can be 'https://...', 'file://...'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#repository Ruby#repository}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9499a3dc6d1488ad26c62097cf20dda8d289e57fddcc8c71abf2a4e1c80519b7)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#authentication_basic Ruby#authentication_basic}
        '''
        result = self._values.get("authentication_basic")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def commit(self) -> typing.Optional[builtins.str]:
        '''Support multiple syntax like ``refs/heads/[BRANCH]``, ``github_hook`` or ``[COMMIT]``, when using the special value ``github_hook``, we will link the application to the Github repository.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#commit Ruby#commit}
        '''
        result = self._values.get("commit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def repository(self) -> typing.Optional[builtins.str]:
        '''The repository URL to deploy, can be 'https://...', 'file://...'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#repository Ruby#repository}
        '''
        result = self._values.get("repository")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RubyDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RubyDeploymentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.ruby.RubyDeploymentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5258aaf802b04042f237e2336796231c356fbc628270120aefc3b8d574dcb436)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1a73b27447aaa32cc2158fada88f66fb7d3e31de80dcaca3a07c3eb71e2b6212)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authenticationBasic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="commit")
    def commit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commit"))

    @commit.setter
    def commit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b4b60226ac7ae5a82ea0ca9cbe6fb8324e32d26a9d4643b464bb4db623e8d76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="repository")
    def repository(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repository"))

    @repository.setter
    def repository(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c347855a270387de3539f9e2da104775378199a1526c46edb969cba70466707a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "repository", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[RubyDeployment, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[RubyDeployment, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[RubyDeployment, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__270f8e4d254f43cbd86a963f62d046921aaabee60a5984e5db1f51b570f83c6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.ruby.RubyHooks",
    jsii_struct_bases=[],
    name_mapping={
        "post_build": "postBuild",
        "pre_build": "preBuild",
        "pre_run": "preRun",
        "run_failed": "runFailed",
        "run_succeed": "runSucceed",
    },
)
class RubyHooks:
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
        :param post_build: `CC_POST_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#post-build>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#post_build Ruby#post_build}
        :param pre_build: `CC_PRE_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-build>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#pre_build Ruby#pre_build}
        :param pre_run: `CC_PRE_RUN_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-run>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#pre_run Ruby#pre_run}
        :param run_failed: `CC_RUN_FAILED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#run_failed Ruby#run_failed}
        :param run_succeed: `CC_RUN_SUCCEEDED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#run_succeed Ruby#run_succeed}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5cf1935f52ec04b3161481b3c69016b16a492d9781781c3317038e62096e2859)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#post_build Ruby#post_build}
        '''
        result = self._values.get("post_build")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_build(self) -> typing.Optional[builtins.str]:
        '''`CC_PRE_BUILD_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-build>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#pre_build Ruby#pre_build}
        '''
        result = self._values.get("pre_build")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pre_run(self) -> typing.Optional[builtins.str]:
        '''`CC_PRE_RUN_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#pre-run>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#pre_run Ruby#pre_run}
        '''
        result = self._values.get("pre_run")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run_failed(self) -> typing.Optional[builtins.str]:
        '''`CC_RUN_FAILED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#run_failed Ruby#run_failed}
        '''
        result = self._values.get("run_failed")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def run_succeed(self) -> typing.Optional[builtins.str]:
        '''`CC_RUN_SUCCEEDED_HOOK <https://www.clever.cloud/developers/doc/develop/build-hooks/#run-successfail>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#run_succeed Ruby#run_succeed}
        '''
        result = self._values.get("run_succeed")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RubyHooks(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RubyHooksOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.ruby.RubyHooksOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8594c7f0c040c70456cfcf5ed5260b3cffb22b8104adc48ba90d265b2ca96c73)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4a73f1a7f8fe21eb0cdd75fe9fbdf30fbfe5790aee07e5e7d9f49be5a6519f15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postBuild", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preBuild")
    def pre_build(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preBuild"))

    @pre_build.setter
    def pre_build(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61e61be42aba96952ae24d32839230782802fb9a04291f695ec48f5805226372)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preBuild", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preRun")
    def pre_run(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preRun"))

    @pre_run.setter
    def pre_run(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07dee12c88ce5e4466ce8dd58676b034731209216d6e7772cd47e3072408f685)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preRun", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runFailed")
    def run_failed(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runFailed"))

    @run_failed.setter
    def run_failed(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eacbfc0eab071edef83e11992070b33c2ea9645fca2c35c62a54884d9d4df4cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runFailed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="runSucceed")
    def run_succeed(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "runSucceed"))

    @run_succeed.setter
    def run_succeed(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76e825df4a0f8702a12ec77bed086da462ab8cf09612d05fdbc75b81739b1292)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "runSucceed", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[RubyHooks, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[RubyHooks, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[RubyHooks, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cd533d9bba9ae1823694e272c60a7058316fd4cf7a0f014e0ca5272e35053de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.ruby.RubyNetworkgroups",
    jsii_struct_bases=[],
    name_mapping={"fqdn": "fqdn", "networkgroup_id": "networkgroupId"},
)
class RubyNetworkgroups:
    def __init__(self, *, fqdn: builtins.str, networkgroup_id: builtins.str) -> None:
        '''
        :param fqdn: domain name which will resolve to application instances inside the networkgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#fqdn Ruby#fqdn}
        :param networkgroup_id: ID of the networkgroup. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#networkgroup_id Ruby#networkgroup_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61756ff60b4999035f50ed5b41736a31fae8de829af62980cadeed0fe59c6ff2)
            check_type(argname="argument fqdn", value=fqdn, expected_type=type_hints["fqdn"])
            check_type(argname="argument networkgroup_id", value=networkgroup_id, expected_type=type_hints["networkgroup_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "fqdn": fqdn,
            "networkgroup_id": networkgroup_id,
        }

    @builtins.property
    def fqdn(self) -> builtins.str:
        '''domain name which will resolve to application instances inside the networkgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#fqdn Ruby#fqdn}
        '''
        result = self._values.get("fqdn")
        assert result is not None, "Required property 'fqdn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def networkgroup_id(self) -> builtins.str:
        '''ID of the networkgroup.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#networkgroup_id Ruby#networkgroup_id}
        '''
        result = self._values.get("networkgroup_id")
        assert result is not None, "Required property 'networkgroup_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RubyNetworkgroups(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RubyNetworkgroupsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.ruby.RubyNetworkgroupsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cde84e1850858f5e52bd3e24c93d72a5da7b65e4fa3c622f3fab0104670e53a9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "RubyNetworkgroupsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ae978b2f3a156124c200d739eb0497a7e112068668aed1e72a0b4047d002c04)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("RubyNetworkgroupsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a482df0dd7b35af701c4a8bf314bc8fd16d94d1581dcc66c1fe2ece0ce88243a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__641d4138abd8c5300c3d6243248b733472d3b20a8056f6e832928cf91969d953)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1c74bb892e00e97f170039602bdf8c4a7e263c29a624dafff0133003b912083f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RubyNetworkgroups]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RubyNetworkgroups]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RubyNetworkgroups]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47a810df8b7206b6ae7f14a66038b12276b6179bf6ac99a53401accfe614c969)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class RubyNetworkgroupsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.ruby.RubyNetworkgroupsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__760f47b84cd4b448724b1c957fa58ec0b6be3a3a5910cf95cdb15b80529b2805)
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
            type_hints = typing.get_type_hints(_typecheckingstub__263c859441fd78e0c0255f5066dd13167b04cf39ab11407db16aa57a854a5404)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fqdn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkgroupId")
    def networkgroup_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkgroupId"))

    @networkgroup_id.setter
    def networkgroup_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0fa0dd5d42a9ac4488ef55e02644ee404861ba6564f0d9b7b21609e5d395313)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkgroupId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[RubyNetworkgroups, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[RubyNetworkgroups, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[RubyNetworkgroups, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8100e4710063c69bfd0d840c86dba6515b95b65d6d6e447eb0c962dd1fd9824c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.ruby.RubyVhosts",
    jsii_struct_bases=[],
    name_mapping={"fqdn": "fqdn", "path_begin": "pathBegin"},
)
class RubyVhosts:
    def __init__(
        self,
        *,
        fqdn: builtins.str,
        path_begin: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param fqdn: Fully qualified domain name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#fqdn Ruby#fqdn}
        :param path_begin: Any HTTP request starting with this path will be sent to this application. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#path_begin Ruby#path_begin}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__133ce86c56f6c4e74944a61e0b1222b062d1c6d32692b0e0751599aa0c847000)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#fqdn Ruby#fqdn}
        '''
        result = self._values.get("fqdn")
        assert result is not None, "Required property 'fqdn' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def path_begin(self) -> typing.Optional[builtins.str]:
        '''Any HTTP request starting with this path will be sent to this application.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs/resources/ruby#path_begin Ruby#path_begin}
        '''
        result = self._values.get("path_begin")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RubyVhosts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RubyVhostsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.ruby.RubyVhostsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7499619533bac3581b604247653afb61443fd91e6bae37f844bbf9e664a42188)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "RubyVhostsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efe4302bfd19a8a9e59e7d5ce7eaf492d3dcba744131dabc3a44581819cf086a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("RubyVhostsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e8b2f96d670b57f289f4ca011b9084228c3ebdd5738ac48e3c4028bcc71a651)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c251b1adb9415bb10e2c142e292abf6b88eb03a4292c958affbfd6c9ae00a6a6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a9653d77171fb838f422685d0fc2919685a0f5e1039799d466751348b7e89cfd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RubyVhosts]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RubyVhosts]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RubyVhosts]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__006c21fd6cde2df8534ec6405d85ad61ff2141d50eb3d1f6ab909b8b4a200794)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class RubyVhostsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.ruby.RubyVhostsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__af17642dd92e38994d0ba783dd1155b15dd25483e0a12f92509662d15d947fb3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c3c27a5a1cc1c4b1e23275efa2165821266887505f269bbf4a7aa989e08ed1b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fqdn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pathBegin")
    def path_begin(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pathBegin"))

    @path_begin.setter
    def path_begin(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b97da884d531b0ac50bf158b2977eb9c72c2baa39fa29f9f0a5832832ed68569)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pathBegin", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[RubyVhosts, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[RubyVhosts, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[RubyVhosts, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e906cd9b15304543997d4ba05b61e911eba7e1a2ed1b6cee93b29dace3bae8b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "Ruby",
    "RubyConfig",
    "RubyDeployment",
    "RubyDeploymentOutputReference",
    "RubyHooks",
    "RubyHooksOutputReference",
    "RubyNetworkgroups",
    "RubyNetworkgroupsList",
    "RubyNetworkgroupsOutputReference",
    "RubyVhosts",
    "RubyVhostsList",
    "RubyVhostsOutputReference",
]

publication.publish()

def _typecheckingstub__503494d7f6199feae3adb1a0f50e71da1b5cf701da8afa1b17cc3b1a13f36528(
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
    deployment: typing.Optional[typing.Union[RubyDeployment, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    enable_gzip_compression: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_sidekiq: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    exposed_environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    gzip_types: typing.Optional[builtins.str] = None,
    hooks: typing.Optional[typing.Union[RubyHooks, typing.Dict[builtins.str, typing.Any]]] = None,
    http_basic_auth: typing.Optional[builtins.str] = None,
    networkgroups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RubyNetworkgroups, typing.Dict[builtins.str, typing.Any]]]]] = None,
    nginx_proxy_buffers: typing.Optional[builtins.str] = None,
    nginx_proxy_buffer_size: typing.Optional[builtins.str] = None,
    nginx_read_timeout: typing.Optional[jsii.Number] = None,
    rack_env: typing.Optional[builtins.str] = None,
    rackup_server: typing.Optional[builtins.str] = None,
    rails_env: typing.Optional[builtins.str] = None,
    rake_goals: typing.Optional[builtins.str] = None,
    redirect_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    region: typing.Optional[builtins.str] = None,
    ruby_version: typing.Optional[builtins.str] = None,
    sidekiq_files: typing.Optional[builtins.str] = None,
    static_files_path: typing.Optional[builtins.str] = None,
    static_url_prefix: typing.Optional[builtins.str] = None,
    static_webroot: typing.Optional[builtins.str] = None,
    sticky_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    vhosts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RubyVhosts, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__c109dd3db6f094373ca808ffb9cd9daac406ccc56ab7fc0d25fd447b51383324(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__832701dae3a771664ece7c25d8ca68eaefa04c67ec90f1c1135085b0d160f938(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RubyNetworkgroups, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ed63f27e9c1dea6d954e497ac8e152477d854332bc0faf01be41f846248ca4c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RubyVhosts, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23d6552cbc61c9e8a5ef8414d228ae52c7f66531e4bdda9b65909f4a5e2e1014(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__faee2672584a161d92c31d7d22bf2676c9b34a93bfe58162d735811facd3b034(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bde0caf8baa1c216e1267345d826be6c72ad8cd5841c9556cea4a0d1d4f15c7b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b934131ffcfb39e19273c676efd4333d3fba24475a4c7207d2165fc94338f887(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7253f0e3c2317ad162b8dff6f1f69a9942d614c5ef78dec825f40cd822a947d2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b258b56cde2cd11617c90b09674c6435dea15ad9cec9f7a00b3b08d9e926a60a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7dfa05392fd37b28c9661155fc31e214c15bc2c7e468b56951be61cceecf2ef1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f678fad51eafb3bab8a2411a56f6252af5fcaf7cb22c28006113d7411ebd645c(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efcd72aecee8b567e61686c89de54895adbcca54e37a20985935496bccda5a94(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8826818132763c864c4edf9304f452c79a56143d6aacd6c84b93279112205fa8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f184a662fff17e23c625b764bc227b27bdcb7628f28dede51494faa4f72f0b58(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cafd0d8e23f87cfe9c8ac83dd7d0dc679e423866cb43964b5eb871aa77037c64(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c18825ee90d9d3708700040f9f8f81ce5813df1a3604759f60528f7b2020e680(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0738b118edad9fe00edbac76f9f31c44cf922f7fb55f87df1e0cb728278346d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2779f8e1efaeb944e089dd256c30159d54dbe93dd22dffa87a3039fc9b8c1a2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6352690811198c6e1c038efb6f51bdcf32aa9ec5d3303423a89377405cd22151(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d79d6fd3aff360d6415a5d2c4dd957b7aa8a006dc2f05c8f1acb1dcc5e4bc5c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec88f4880a7d36255a0a91cd357d3f85518f47f101c364630842d97bc9a3ad4d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39af4e4ea225733dd03a6331085e50d2b9f0dde01386670c3b2da284426f0559(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdb890bdc8d1782fe7258e53181d6393fd2376ecbcb98177e9cc76e464eeada7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44f55806df519fd46f3adfdbb17b201d0eb0ca48cbe126b49b5b271d17a76370(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e317d1468fcc8ff379c888d6c6fecff40a105c679313ccec75a5a0913299c28(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efeb1a87a2843d8a51f158ea9da05174ca79d3e0cb139ed4b671978f10403268(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__743aeddb227dfce0d97f0ffd9dfbda7685e4ebedcc934d0c0cee94dd6803fff8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d81d50a4c86015044ae24e7a6fada5e8394d285ecd0a9f9ca2df9a42af6cfe32(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7119137b2bcfa0bc1f79876132539e88be380ab3e3d0eaba581e34fd9fc456b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__995f4193cfad05ad2c0190649420b044bec98603d2f59b744553625f3bbe83f1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d1b3464487ec06c654f1124eb3444ae3654577cbeec4f90216ad88baaa97bf8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c53be92c6c2746fd3e324ae0ec8abfcc31355edeccaf9814467f2cce4bb55a0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0a37ede2e791992cc6ee340f1321d682c33481db18540481da49f52d11fd09a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ea27122968680ec8354b0cb9f19048b9a1077097b9e19dc43dd93fc3747cb27(
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
    deployment: typing.Optional[typing.Union[RubyDeployment, typing.Dict[builtins.str, typing.Any]]] = None,
    description: typing.Optional[builtins.str] = None,
    enable_gzip_compression: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_sidekiq: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    exposed_environment: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    gzip_types: typing.Optional[builtins.str] = None,
    hooks: typing.Optional[typing.Union[RubyHooks, typing.Dict[builtins.str, typing.Any]]] = None,
    http_basic_auth: typing.Optional[builtins.str] = None,
    networkgroups: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RubyNetworkgroups, typing.Dict[builtins.str, typing.Any]]]]] = None,
    nginx_proxy_buffers: typing.Optional[builtins.str] = None,
    nginx_proxy_buffer_size: typing.Optional[builtins.str] = None,
    nginx_read_timeout: typing.Optional[jsii.Number] = None,
    rack_env: typing.Optional[builtins.str] = None,
    rackup_server: typing.Optional[builtins.str] = None,
    rails_env: typing.Optional[builtins.str] = None,
    rake_goals: typing.Optional[builtins.str] = None,
    redirect_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    region: typing.Optional[builtins.str] = None,
    ruby_version: typing.Optional[builtins.str] = None,
    sidekiq_files: typing.Optional[builtins.str] = None,
    static_files_path: typing.Optional[builtins.str] = None,
    static_url_prefix: typing.Optional[builtins.str] = None,
    static_webroot: typing.Optional[builtins.str] = None,
    sticky_sessions: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    vhosts: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[RubyVhosts, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9499a3dc6d1488ad26c62097cf20dda8d289e57fddcc8c71abf2a4e1c80519b7(
    *,
    authentication_basic: typing.Optional[builtins.str] = None,
    commit: typing.Optional[builtins.str] = None,
    repository: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5258aaf802b04042f237e2336796231c356fbc628270120aefc3b8d574dcb436(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a73b27447aaa32cc2158fada88f66fb7d3e31de80dcaca3a07c3eb71e2b6212(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b4b60226ac7ae5a82ea0ca9cbe6fb8324e32d26a9d4643b464bb4db623e8d76(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c347855a270387de3539f9e2da104775378199a1526c46edb969cba70466707a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__270f8e4d254f43cbd86a963f62d046921aaabee60a5984e5db1f51b570f83c6b(
    value: typing.Optional[typing.Union[RubyDeployment, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cf1935f52ec04b3161481b3c69016b16a492d9781781c3317038e62096e2859(
    *,
    post_build: typing.Optional[builtins.str] = None,
    pre_build: typing.Optional[builtins.str] = None,
    pre_run: typing.Optional[builtins.str] = None,
    run_failed: typing.Optional[builtins.str] = None,
    run_succeed: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8594c7f0c040c70456cfcf5ed5260b3cffb22b8104adc48ba90d265b2ca96c73(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a73f1a7f8fe21eb0cdd75fe9fbdf30fbfe5790aee07e5e7d9f49be5a6519f15(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61e61be42aba96952ae24d32839230782802fb9a04291f695ec48f5805226372(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07dee12c88ce5e4466ce8dd58676b034731209216d6e7772cd47e3072408f685(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eacbfc0eab071edef83e11992070b33c2ea9645fca2c35c62a54884d9d4df4cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76e825df4a0f8702a12ec77bed086da462ab8cf09612d05fdbc75b81739b1292(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cd533d9bba9ae1823694e272c60a7058316fd4cf7a0f014e0ca5272e35053de(
    value: typing.Optional[typing.Union[RubyHooks, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61756ff60b4999035f50ed5b41736a31fae8de829af62980cadeed0fe59c6ff2(
    *,
    fqdn: builtins.str,
    networkgroup_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cde84e1850858f5e52bd3e24c93d72a5da7b65e4fa3c622f3fab0104670e53a9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ae978b2f3a156124c200d739eb0497a7e112068668aed1e72a0b4047d002c04(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a482df0dd7b35af701c4a8bf314bc8fd16d94d1581dcc66c1fe2ece0ce88243a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__641d4138abd8c5300c3d6243248b733472d3b20a8056f6e832928cf91969d953(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c74bb892e00e97f170039602bdf8c4a7e263c29a624dafff0133003b912083f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47a810df8b7206b6ae7f14a66038b12276b6179bf6ac99a53401accfe614c969(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RubyNetworkgroups]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__760f47b84cd4b448724b1c957fa58ec0b6be3a3a5910cf95cdb15b80529b2805(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__263c859441fd78e0c0255f5066dd13167b04cf39ab11407db16aa57a854a5404(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0fa0dd5d42a9ac4488ef55e02644ee404861ba6564f0d9b7b21609e5d395313(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8100e4710063c69bfd0d840c86dba6515b95b65d6d6e447eb0c962dd1fd9824c(
    value: typing.Optional[typing.Union[RubyNetworkgroups, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__133ce86c56f6c4e74944a61e0b1222b062d1c6d32692b0e0751599aa0c847000(
    *,
    fqdn: builtins.str,
    path_begin: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7499619533bac3581b604247653afb61443fd91e6bae37f844bbf9e664a42188(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efe4302bfd19a8a9e59e7d5ce7eaf492d3dcba744131dabc3a44581819cf086a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e8b2f96d670b57f289f4ca011b9084228c3ebdd5738ac48e3c4028bcc71a651(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c251b1adb9415bb10e2c142e292abf6b88eb03a4292c958affbfd6c9ae00a6a6(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9653d77171fb838f422685d0fc2919685a0f5e1039799d466751348b7e89cfd(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__006c21fd6cde2df8534ec6405d85ad61ff2141d50eb3d1f6ab909b8b4a200794(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[RubyVhosts]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af17642dd92e38994d0ba783dd1155b15dd25483e0a12f92509662d15d947fb3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3c27a5a1cc1c4b1e23275efa2165821266887505f269bbf4a7aa989e08ed1b2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b97da884d531b0ac50bf158b2977eb9c72c2baa39fa29f9f0a5832832ed68569(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e906cd9b15304543997d4ba05b61e911eba7e1a2ed1b6cee93b29dace3bae8b4(
    value: typing.Optional[typing.Union[RubyVhosts, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass
