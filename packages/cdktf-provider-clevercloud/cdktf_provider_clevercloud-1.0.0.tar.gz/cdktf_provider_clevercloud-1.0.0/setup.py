import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdktf-provider-clevercloud",
    "version": "1.0.0",
    "description": "Prebuilt clevercloud Provider for Terraform CDK (cdktf)",
    "license": "MPL-2.0",
    "url": "https://github.com/clevercloud/cdktf-provider-clevercloud.git",
    "long_description_content_type": "text/markdown",
    "author": "HashiCorp",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/clevercloud/cdktf-provider-clevercloud.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "clevercloud_cdktf_provider_clevercloud",
        "clevercloud_cdktf_provider_clevercloud._jsii",
        "clevercloud_cdktf_provider_clevercloud.addon",
        "clevercloud_cdktf_provider_clevercloud.cellar",
        "clevercloud_cdktf_provider_clevercloud.cellar_bucket",
        "clevercloud_cdktf_provider_clevercloud.configprovider",
        "clevercloud_cdktf_provider_clevercloud.data_clevercloud_default_loadbalancer",
        "clevercloud_cdktf_provider_clevercloud.docker",
        "clevercloud_cdktf_provider_clevercloud.dotnet",
        "clevercloud_cdktf_provider_clevercloud.drain_datadog",
        "clevercloud_cdktf_provider_clevercloud.drain_elasticsearch",
        "clevercloud_cdktf_provider_clevercloud.drain_http",
        "clevercloud_cdktf_provider_clevercloud.drain_newrelic",
        "clevercloud_cdktf_provider_clevercloud.drain_ovh",
        "clevercloud_cdktf_provider_clevercloud.drain_syslog_tcp",
        "clevercloud_cdktf_provider_clevercloud.drain_syslog_udp",
        "clevercloud_cdktf_provider_clevercloud.elasticsearch",
        "clevercloud_cdktf_provider_clevercloud.frankenphp",
        "clevercloud_cdktf_provider_clevercloud.fsbucket",
        "clevercloud_cdktf_provider_clevercloud.go",
        "clevercloud_cdktf_provider_clevercloud.java_war",
        "clevercloud_cdktf_provider_clevercloud.keycloak",
        "clevercloud_cdktf_provider_clevercloud.materia_kv",
        "clevercloud_cdktf_provider_clevercloud.matomo",
        "clevercloud_cdktf_provider_clevercloud.metabase",
        "clevercloud_cdktf_provider_clevercloud.mongodb",
        "clevercloud_cdktf_provider_clevercloud.mysql",
        "clevercloud_cdktf_provider_clevercloud.networkgroup",
        "clevercloud_cdktf_provider_clevercloud.nodejs",
        "clevercloud_cdktf_provider_clevercloud.otoroshi",
        "clevercloud_cdktf_provider_clevercloud.php",
        "clevercloud_cdktf_provider_clevercloud.play2",
        "clevercloud_cdktf_provider_clevercloud.postgresql",
        "clevercloud_cdktf_provider_clevercloud.provider",
        "clevercloud_cdktf_provider_clevercloud.pulsar",
        "clevercloud_cdktf_provider_clevercloud.python",
        "clevercloud_cdktf_provider_clevercloud.redis",
        "clevercloud_cdktf_provider_clevercloud.ruby",
        "clevercloud_cdktf_provider_clevercloud.rust",
        "clevercloud_cdktf_provider_clevercloud.scala",
        "clevercloud_cdktf_provider_clevercloud.static_resource",
        "clevercloud_cdktf_provider_clevercloud.v"
    ],
    "package_data": {
        "clevercloud_cdktf_provider_clevercloud._jsii": [
            "cdktf-bindings@1.0.0.jsii.tgz"
        ],
        "clevercloud_cdktf_provider_clevercloud": [
            "py.typed"
        ]
    },
    "python_requires": "~=3.9",
    "install_requires": [
        "cdktf>=0.21.0, <0.22.0",
        "constructs>=10.4.2, <11.0.0",
        "jsii>=1.120.0, <2.0.0",
        "publication>=0.0.3",
        "typeguard==2.13.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ],
    "scripts": []
}
"""
)

with open("README.md", encoding="utf8") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
