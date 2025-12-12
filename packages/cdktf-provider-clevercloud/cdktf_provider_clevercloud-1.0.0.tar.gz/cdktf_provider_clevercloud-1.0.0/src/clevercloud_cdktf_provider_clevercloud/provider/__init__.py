r'''
# `provider`

Refer to the Terraform Registry for docs: [`clevercloud`](https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs).
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


class ClevercloudProvider(
    _cdktf_9a9027ec.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@clevercloud/cdktf-bindings.provider.ClevercloudProvider",
):
    '''Represents a {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs clevercloud}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        alias: typing.Optional[builtins.str] = None,
        consumer_key: typing.Optional[builtins.str] = None,
        consumer_secret: typing.Optional[builtins.str] = None,
        disable_networkgroups: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        endpoint: typing.Optional[builtins.str] = None,
        organisation: typing.Optional[builtins.str] = None,
        secret: typing.Optional[builtins.str] = None,
        token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs clevercloud} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#alias ClevercloudProvider#alias}
        :param consumer_key: Clever Cloud OAuth1 consumer key. Allows using a dedicated OAuth consumer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#consumer_key ClevercloudProvider#consumer_key}
        :param consumer_secret: CleverCloud OAuth1 consumer secret. Allows using a dedicated OAuth consumer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#consumer_secret ClevercloudProvider#consumer_secret}
        :param disable_networkgroups: Disable netorkgroups features. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#disable_networkgroups ClevercloudProvider#disable_networkgroups}
        :param endpoint: Clever Cloud API endpoint, default to https://api.clever-cloud.com. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#endpoint ClevercloudProvider#endpoint}
        :param organisation: Clever Cloud organisation, can be either orga_xxx, or user_xxx for personal spaces. This parameter can also be provided via CC_ORGANISATION environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#organisation ClevercloudProvider#organisation}
        :param secret: Clever Cloud OAuth1 secret, can be took from clever-tools after login. This parameter can also be provided via CC_OAUTH_SECRET environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#secret ClevercloudProvider#secret}
        :param token: Clever Cloud OAuth1 token, can be took from clever-tools after login. This parameter can also be provided via CC_OAUTH_TOKEN environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#token ClevercloudProvider#token}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2446b9292b9da39255bba755abf1e8d1f2c3cd971147b95175badf7fdeb70a3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = ClevercloudProviderConfig(
            alias=alias,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            disable_networkgroups=disable_networkgroups,
            endpoint=endpoint,
            organisation=organisation,
            secret=secret,
            token=token,
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
        '''Generates CDKTF code for importing a ClevercloudProvider resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the ClevercloudProvider to import.
        :param import_from_id: The id of the existing ClevercloudProvider that should be imported. Refer to the {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the ClevercloudProvider to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8fcb30b5ff8efc6ca309fbc9e4a48fbc0049c873d5ba237e05b0fc5bd5793226)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetConsumerKey")
    def reset_consumer_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConsumerKey", []))

    @jsii.member(jsii_name="resetConsumerSecret")
    def reset_consumer_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConsumerSecret", []))

    @jsii.member(jsii_name="resetDisableNetworkgroups")
    def reset_disable_networkgroups(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableNetworkgroups", []))

    @jsii.member(jsii_name="resetEndpoint")
    def reset_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpoint", []))

    @jsii.member(jsii_name="resetOrganisation")
    def reset_organisation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganisation", []))

    @jsii.member(jsii_name="resetSecret")
    def reset_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecret", []))

    @jsii.member(jsii_name="resetToken")
    def reset_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetToken", []))

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
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property
    @jsii.member(jsii_name="consumerKeyInput")
    def consumer_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "consumerKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="consumerSecretInput")
    def consumer_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "consumerSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="disableNetworkgroupsInput")
    def disable_networkgroups_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableNetworkgroupsInput"))

    @builtins.property
    @jsii.member(jsii_name="endpointInput")
    def endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpointInput"))

    @builtins.property
    @jsii.member(jsii_name="organisationInput")
    def organisation_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organisationInput"))

    @builtins.property
    @jsii.member(jsii_name="secretInput")
    def secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenInput")
    def token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenInput"))

    @builtins.property
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__271f059a12dfc58475661498544eee825f4d31a543082b43d940834a0b74d841)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="consumerKey")
    def consumer_key(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "consumerKey"))

    @consumer_key.setter
    def consumer_key(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__755c821c9e08c949776c4e4cb5595938f3aea1035d47d6942c4a52d3260afa52)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "consumerKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="consumerSecret")
    def consumer_secret(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "consumerSecret"))

    @consumer_secret.setter
    def consumer_secret(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cda6531711aede38ea2a94bf51214235f5f69495f1b8520d2eb776ddadfd49d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "consumerSecret", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableNetworkgroups")
    def disable_networkgroups(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableNetworkgroups"))

    @disable_networkgroups.setter
    def disable_networkgroups(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f5c3b36ce235a89b3ac15c9cbbe8a4a7eada81f9569f61f9f83ba27f1b981a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableNetworkgroups", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endpoint")
    def endpoint(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "endpoint"))

    @endpoint.setter
    def endpoint(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b39bac74456b9060dca1328bb21b284e0aec67235914351e1ba6e1d1c5811fdf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endpoint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="organisation")
    def organisation(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organisation"))

    @organisation.setter
    def organisation(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b6480374c5bb72916a95e76a03be16fb5f8cd2fc7251e123ef02fa6da78498a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "organisation", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secret")
    def secret(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secret"))

    @secret.setter
    def secret(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ed5586772bd180f65cd7cc6e3f6b78638f48324093322c9b6d8cfa241886af5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secret", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="token")
    def token(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "token"))

    @token.setter
    def token(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0d431e4ef7cbe162d47d98cd0f55efa3e79255ffd784a250bb03f8928d57ebb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "token", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@clevercloud/cdktf-bindings.provider.ClevercloudProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "alias": "alias",
        "consumer_key": "consumerKey",
        "consumer_secret": "consumerSecret",
        "disable_networkgroups": "disableNetworkgroups",
        "endpoint": "endpoint",
        "organisation": "organisation",
        "secret": "secret",
        "token": "token",
    },
)
class ClevercloudProviderConfig:
    def __init__(
        self,
        *,
        alias: typing.Optional[builtins.str] = None,
        consumer_key: typing.Optional[builtins.str] = None,
        consumer_secret: typing.Optional[builtins.str] = None,
        disable_networkgroups: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        endpoint: typing.Optional[builtins.str] = None,
        organisation: typing.Optional[builtins.str] = None,
        secret: typing.Optional[builtins.str] = None,
        token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#alias ClevercloudProvider#alias}
        :param consumer_key: Clever Cloud OAuth1 consumer key. Allows using a dedicated OAuth consumer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#consumer_key ClevercloudProvider#consumer_key}
        :param consumer_secret: CleverCloud OAuth1 consumer secret. Allows using a dedicated OAuth consumer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#consumer_secret ClevercloudProvider#consumer_secret}
        :param disable_networkgroups: Disable netorkgroups features. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#disable_networkgroups ClevercloudProvider#disable_networkgroups}
        :param endpoint: Clever Cloud API endpoint, default to https://api.clever-cloud.com. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#endpoint ClevercloudProvider#endpoint}
        :param organisation: Clever Cloud organisation, can be either orga_xxx, or user_xxx for personal spaces. This parameter can also be provided via CC_ORGANISATION environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#organisation ClevercloudProvider#organisation}
        :param secret: Clever Cloud OAuth1 secret, can be took from clever-tools after login. This parameter can also be provided via CC_OAUTH_SECRET environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#secret ClevercloudProvider#secret}
        :param token: Clever Cloud OAuth1 token, can be took from clever-tools after login. This parameter can also be provided via CC_OAUTH_TOKEN environment variable. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#token ClevercloudProvider#token}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88a6e8afe8e33046addb4222c5959f42e9f677b7d020b4f046bcbd468f784354)
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument consumer_key", value=consumer_key, expected_type=type_hints["consumer_key"])
            check_type(argname="argument consumer_secret", value=consumer_secret, expected_type=type_hints["consumer_secret"])
            check_type(argname="argument disable_networkgroups", value=disable_networkgroups, expected_type=type_hints["disable_networkgroups"])
            check_type(argname="argument endpoint", value=endpoint, expected_type=type_hints["endpoint"])
            check_type(argname="argument organisation", value=organisation, expected_type=type_hints["organisation"])
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias
        if consumer_key is not None:
            self._values["consumer_key"] = consumer_key
        if consumer_secret is not None:
            self._values["consumer_secret"] = consumer_secret
        if disable_networkgroups is not None:
            self._values["disable_networkgroups"] = disable_networkgroups
        if endpoint is not None:
            self._values["endpoint"] = endpoint
        if organisation is not None:
            self._values["organisation"] = organisation
        if secret is not None:
            self._values["secret"] = secret
        if token is not None:
            self._values["token"] = token

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#alias ClevercloudProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def consumer_key(self) -> typing.Optional[builtins.str]:
        '''Clever Cloud OAuth1 consumer key. Allows using a dedicated OAuth consumer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#consumer_key ClevercloudProvider#consumer_key}
        '''
        result = self._values.get("consumer_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def consumer_secret(self) -> typing.Optional[builtins.str]:
        '''CleverCloud OAuth1 consumer secret. Allows using a dedicated OAuth consumer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#consumer_secret ClevercloudProvider#consumer_secret}
        '''
        result = self._values.get("consumer_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_networkgroups(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Disable netorkgroups features.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#disable_networkgroups ClevercloudProvider#disable_networkgroups}
        '''
        result = self._values.get("disable_networkgroups")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def endpoint(self) -> typing.Optional[builtins.str]:
        '''Clever Cloud API endpoint, default to https://api.clever-cloud.com.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#endpoint ClevercloudProvider#endpoint}
        '''
        result = self._values.get("endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organisation(self) -> typing.Optional[builtins.str]:
        '''Clever Cloud organisation, can be either orga_xxx, or user_xxx for personal spaces.

        This parameter can also be provided via CC_ORGANISATION environment variable.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#organisation ClevercloudProvider#organisation}
        '''
        result = self._values.get("organisation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret(self) -> typing.Optional[builtins.str]:
        '''Clever Cloud OAuth1 secret, can be took from clever-tools after login.

        This parameter can also be provided via CC_OAUTH_SECRET environment variable.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#secret ClevercloudProvider#secret}
        '''
        result = self._values.get("secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''Clever Cloud OAuth1 token, can be took from clever-tools after login.

        This parameter can also be provided via CC_OAUTH_TOKEN environment variable.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/clevercloud/clevercloud/1.7.1/docs#token ClevercloudProvider#token}
        '''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClevercloudProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "ClevercloudProvider",
    "ClevercloudProviderConfig",
]

publication.publish()

def _typecheckingstub__f2446b9292b9da39255bba755abf1e8d1f2c3cd971147b95175badf7fdeb70a3(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    alias: typing.Optional[builtins.str] = None,
    consumer_key: typing.Optional[builtins.str] = None,
    consumer_secret: typing.Optional[builtins.str] = None,
    disable_networkgroups: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    endpoint: typing.Optional[builtins.str] = None,
    organisation: typing.Optional[builtins.str] = None,
    secret: typing.Optional[builtins.str] = None,
    token: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fcb30b5ff8efc6ca309fbc9e4a48fbc0049c873d5ba237e05b0fc5bd5793226(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__271f059a12dfc58475661498544eee825f4d31a543082b43d940834a0b74d841(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__755c821c9e08c949776c4e4cb5595938f3aea1035d47d6942c4a52d3260afa52(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cda6531711aede38ea2a94bf51214235f5f69495f1b8520d2eb776ddadfd49d(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f5c3b36ce235a89b3ac15c9cbbe8a4a7eada81f9569f61f9f83ba27f1b981a0(
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b39bac74456b9060dca1328bb21b284e0aec67235914351e1ba6e1d1c5811fdf(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b6480374c5bb72916a95e76a03be16fb5f8cd2fc7251e123ef02fa6da78498a(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ed5586772bd180f65cd7cc6e3f6b78638f48324093322c9b6d8cfa241886af5(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0d431e4ef7cbe162d47d98cd0f55efa3e79255ffd784a250bb03f8928d57ebb(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88a6e8afe8e33046addb4222c5959f42e9f677b7d020b4f046bcbd468f784354(
    *,
    alias: typing.Optional[builtins.str] = None,
    consumer_key: typing.Optional[builtins.str] = None,
    consumer_secret: typing.Optional[builtins.str] = None,
    disable_networkgroups: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    endpoint: typing.Optional[builtins.str] = None,
    organisation: typing.Optional[builtins.str] = None,
    secret: typing.Optional[builtins.str] = None,
    token: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
