r'''
# CDKTF prebuilt bindings for CleverCloud/clevercloud provider version 1.7.1

This repo builds and publishes the [Terraform clevercloud provider](https://registry.terraform.io/providers/CleverCloud/clevercloud/1.7.1/docs) bindings for [CDK for Terraform](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@clevercloud/provider-clevercloud](https://www.npmjs.com/package/@clevercloud/provider-clevercloud).

`npm install @clevercloud/provider-clevercloud`

### PyPI

The PyPI package is available at [https://pypi.org/project/clevercloud-cdktf-provider-clevercloud](https://pypi.org/project/clevercloud-cdktf-provider-clevercloud).

`pipenv install clevercloud-cdktf-provider-clevercloud`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/CleverCloud.Cdktf.Providers.Clevercloud](https://www.nuget.org/packages/CleverCloud.Cdktf.Providers.Clevercloud).

`dotnet add package CleverCloud.Cdktf.Providers.Clevercloud`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.clevercloud/cdktf-provider-clevercloud](https://mvnrepository.com/artifact/com.clevercloud/cdktf-provider-clevercloud).

```
<dependency>
    <groupId>com.clevercloud</groupId>
    <artifactId>cdktf-provider-clevercloud</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

### Go

The go package is generated into the [`github.com/clevercloud/cdktf-provider-clevercloud-go`](https://github.com/clevercloud/cdktf-provider-clevercloud-go) package.

`go get github.com/clevercloud/cdktf-provider-clevercloud-go/clevercloud/<version>`

Where `<version>` is the version of the prebuilt provider you would like to use e.g. `v11`. The full module name can be found
within the [go.mod](https://github.com/clevercloud/cdktf-provider-clevercloud-go/blob/main/clevercloud/go.mod#L1) file.

## Docs

Find auto-generated docs for this provider here:

* [Typescript](./docs/API.typescript.md)
* [Python](./docs/API.python.md)
* [Java](./docs/API.java.md)
* [C#](./docs/API.csharp.md)
* [Go](./docs/API.go.md)

You can also visit a hosted version of the documentation on [constructs.dev](https://constructs.dev/packages/@cdktf/provider-clevercloud).

## Versioning

This project is explicitly not tracking the Terraform clevercloud provider version 1:1. In fact, it always tracks `latest` of `~> 1.7.1` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by [generating the provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [CDK for Terraform](https://cdk.tf)
* [Terraform clevercloud provider](https://registry.terraform.io/providers/CleverCloud/clevercloud/1.7.1)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped.

## Features / Issues / Bugs

Please report bugs and issues to the [CDK for Terraform](https://cdk.tf) project:

* [Create bug report](https://cdk.tf/bug)
* [Create feature request](https://cdk.tf/feature)

## Contributing

### Projen

This is mostly based on [Projen](https://github.com/projen/projen), which takes care of generating the entire repository.

### cdktf-provider-project based on Projen

There's a custom [project builder](https://github.com/cdktf/cdktf-provider-project) which encapsulate the common settings for all `cdktf` prebuilt providers.

### Provider Version

The provider version can be adjusted in [./.projenrc.js](./.projenrc.js).

### Repository Management

The repository is managed by [CDKTF Repository Manager](https://github.com/cdktf/cdktf-repository-manager/).
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

__all__ = [
    "addon",
    "cellar",
    "cellar_bucket",
    "configprovider",
    "data_clevercloud_default_loadbalancer",
    "docker",
    "dotnet",
    "drain_datadog",
    "drain_elasticsearch",
    "drain_http",
    "drain_newrelic",
    "drain_ovh",
    "drain_syslog_tcp",
    "drain_syslog_udp",
    "elasticsearch",
    "frankenphp",
    "fsbucket",
    "go",
    "java_war",
    "keycloak",
    "materia_kv",
    "matomo",
    "metabase",
    "mongodb",
    "mysql",
    "networkgroup",
    "nodejs",
    "otoroshi",
    "php",
    "play2",
    "postgresql",
    "provider",
    "pulsar",
    "python",
    "redis",
    "ruby",
    "rust",
    "scala",
    "static_resource",
    "v",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import addon
from . import cellar
from . import cellar_bucket
from . import configprovider
from . import data_clevercloud_default_loadbalancer
from . import docker
from . import dotnet
from . import drain_datadog
from . import drain_elasticsearch
from . import drain_http
from . import drain_newrelic
from . import drain_ovh
from . import drain_syslog_tcp
from . import drain_syslog_udp
from . import elasticsearch
from . import frankenphp
from . import fsbucket
from . import go
from . import java_war
from . import keycloak
from . import materia_kv
from . import matomo
from . import metabase
from . import mongodb
from . import mysql
from . import networkgroup
from . import nodejs
from . import otoroshi
from . import php
from . import play2
from . import postgresql
from . import provider
from . import pulsar
from . import python
from . import redis
from . import ruby
from . import rust
from . import scala
from . import static_resource
from . import v
