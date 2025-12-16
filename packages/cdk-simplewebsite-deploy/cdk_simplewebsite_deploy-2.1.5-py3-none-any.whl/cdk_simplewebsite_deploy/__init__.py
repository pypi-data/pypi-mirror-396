r'''
[![License](https://img.shields.io/badge/License-Apache%202.0-yellowgreen.svg)](https://opensource.org/licenses/Apache-2.0)
![Build](https://github.com/SnapPetal/cdk-simplewebsite-deploy/workflows/build/badge.svg)
![Release](https://github.com/SnapPetal/cdk-simplewebsite-deploy/workflows/release/badge.svg?branch=main)

# cdk-simplewebsite-deploy

This is an AWS CDK Construct to simplify deploying a single-page website using either S3 buckets or CloudFront distributions with enhanced security, performance, and monitoring capabilities.

## Installation and Usage

### [CreateBasicSite](https://github.com/snappetal/cdk-simplewebsite-deploy/blob/main/API.md#cdk-cloudfront-deploy-createbasicsite)

#### Creates a simple website using S3 buckets with a domain hosted in Route 53.

##### Typescript

```console
yarn add cdk-simplewebsite-deploy
```

```python
import * as cdk from 'aws-cdk-lib';
import { CreateBasicSite } from 'cdk-simplewebsite-deploy';
import { Construct } from 'constructs';

export class PipelineStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new CreateBasicSite(this, 'test-website', {
      websiteFolder: './src/build',
      indexDoc: 'index.html',
      hostedZone: 'example.com',
    });
  }
}
```

##### C#

```console
dotnet add package ThonBecker.CDK.SimpleWebsiteDeploy
```

```cs
using Amazon.CDK;
using ThonBecker.CDK.SimpleWebsiteDeploy;

namespace SimpleWebsiteDeploy
{
    public class PipelineStack : Stack
    {
        internal PipelineStack(Construct scope, string id, IStackProps props = null) : base(scope, id, props)
        {
            new CreateBasicSite(scope, "test-website", new BasicSiteConfiguration()
            {
                WebsiteFolder = "./src/build",
                IndexDoc = "index.html",
                HostedZone = "example.com",
            });
        }
    }
}
```

##### Java

```xml
<dependency>
	<groupId>com.thonbecker.simplewebsitedeploy</groupId>
	<artifactId>cdk-simplewebsite-deploy</artifactId>
	<version>0.4.2</version>
</dependency>
```

```java
package com.myorg;

import software.amazon.awscdk.core.Construct;
import software.amazon.awscdk.core.Stack;
import software.amazon.awscdk.core.StackProps;
import com.thonbecker.simplewebsitedeploy.CreateBasicSite;

public class MyProjectStack extends Stack {
    public MyProjectStack(final Construct scope, final String id) {
        this(scope, id, null);
    }

    public MyProjectStack(final Construct scope, final String id, final StackProps props) {
        super(scope, id, props);

        CreateBasicSite.Builder.create(this, "test-website")
        		.websiteFolder("./src/build")
        		.indexDoc("index.html")
        		.hostedZone("example.com");
    }
}
```

##### Python

```console
pip install cdk-simplewebsite-deploy
```

```python
from aws_cdk import Stack
from cdk_simplewebsite_deploy import CreateBasicSite
from constructs import Construct

class MyProjectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        CreateBasicSite(self, 'test-website', website_folder='./src/build',
                        index_doc='index.html',
                        hosted_zone='example.com')
```

### [CreateCloudfrontSite](https://github.com/snappetal/cdk-simplewebsite-deploy/blob/main/API.md#cdk-cloudfront-deploy-createcloudfrontsite)

#### Creates a simple website using a CloudFront distribution with a domain hosted in Route 53.

##### Typescript

```console
yarn add cdk-simplewebsite-deploy
```

```python
import * as cdk from 'aws-cdk-lib';
import { CreateCloudfrontSite } from 'cdk-simplewebsite-deploy';
import { Construct } from 'constructs';

export class PipelineStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new CreateCloudfrontSite(this, 'test-website', {
      websiteFolder: './src/dist',
      indexDoc: 'index.html',
      hostedZone: 'example.com',
      subDomain: 'www.example.com',
    });
  }
}
```

##### C#

```console
dotnet add package ThonBecker.CDK.SimpleWebsiteDeploy
```

```cs
using Amazon.CDK;
using ThonBecker.CDK.SimpleWebsiteDeploy;

namespace SimpleWebsiteDeploy
{
    public class PipelineStack : Stack
    {
        internal PipelineStack(Construct scope, string id, IStackProps props = null) : base(scope, id, props)
        {
            new CreateCloudfrontSite(scope, "test-website", new CloudfrontSiteConfiguration()
            {
                WebsiteFolder = "./src/build",
                IndexDoc = "index.html",
                HostedZone = "example.com",
                SubDomain = "www.example.com",
            });
        }
    }
}
```

##### Java

```xml
<dependency>
	<groupId>com.thonbecker.simplewebsitedeploy</groupId>
	<artifactId>cdk-simplewebsite-deploy</artifactId>
	<version>0.4.2</version>
</dependency>
```

```java
package com.myorg;

import software.amazon.awscdk.core.Construct;
import software.amazon.awscdk.core.Stack;
import software.amazon.awscdk.core.StackProps;
import com.thonbecker.simplewebsitedeploy.CreateCloudfrontSite;

public class MyProjectStack extends Stack {
    public MyProjectStack(final Construct scope, final String id) {
        this(scope, id, null);
    }

    public MyProjectStack(final Construct scope, final String id, final StackProps props) {
        super(scope, id, props);

        CreateCloudfrontSite.Builder.create(this, "test-website")
        		.websiteFolder("./src/build")
        		.indexDoc("index.html")
        		.hostedZone("example.com")
        		.subDomain("www.example.com");
    }
}
```

##### Python

```console
pip install cdk-simplewebsite-deploy
```

```python
from aws_cdk import core
from cdk_simplewebsite_deploy import CreateCloudfrontSite


class MyProjectStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        CreateCloudfrontSite(self, 'test-website', website_folder='./src/build',
                             index_doc='index.html',
                             hosted_zone='example.com',
                             sub_domain='www.example.com')
```

## 🚀 Enhanced Features

The `CreateCloudfrontSite` construct now includes several optional advanced features for improved security, performance, and monitoring:

### Security Headers

Enable comprehensive security headers including HSTS, X-Frame-Options, Content-Type-Options, and XSS protection:

```python
new CreateCloudfrontSite(this, 'secure-website', {
  websiteFolder: './src/dist',
  indexDoc: 'index.html',
  hostedZone: 'example.com',
  enableSecurityHeaders: true, // 🔒 Adds security headers
});
```

### IPv6 Support

Enable IPv6 connectivity with AAAA records:

```python
new CreateCloudfrontSite(this, 'ipv6-website', {
  websiteFolder: './src/dist',
  indexDoc: 'index.html',
  hostedZone: 'example.com',
  enableIpv6: true, // 🌐 Adds AAAA records for IPv6
});
```

### Access Logging

Enable CloudFront access logging for analytics and monitoring:

```python
new CreateCloudfrontSite(this, 'logged-website', {
  websiteFolder: './src/dist',
  indexDoc: 'index.html',
  hostedZone: 'example.com',
  enableLogging: true, // 📊 Enables access logging
  // logsBucket: myCustomBucket, // Optional: use existing bucket
});
```

### WAF Integration

Integrate with AWS WAF for enhanced security:

```python
new CreateCloudfrontSite(this, 'waf-protected-website', {
  websiteFolder: './src/dist',
  indexDoc: 'index.html',
  hostedZone: 'example.com',
  webAclId: 'arn:aws:wafv2:us-east-1:123456789012:global/webacl/my-web-acl/12345678-1234-1234-1234-123456789012', // 🛡️ WAF protection
});
```

### Custom Cache Behaviors

Add custom cache behaviors for different content types:

```python
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';

new CreateCloudfrontSite(this, 'optimized-website', {
  websiteFolder: './src/dist',
  indexDoc: 'index.html',
  hostedZone: 'example.com',
  additionalBehaviors: {
    '/api/*': {
      origin: myApiOrigin,
      allowedMethods: cloudfront.AllowedMethods.ALLOW_ALL,
      cachePolicy: cloudfront.CachePolicy.CACHING_DISABLED,
    },
    '/static/*': {
      cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED_FOR_UNCOMPRESSED_OBJECTS,
    },
  }, // ⚡ Custom caching strategies
});
```

### Custom Error Responses

Define custom error handling:

```python
new CreateCloudfrontSite(this, 'custom-errors-website', {
  websiteFolder: './src/dist',
  indexDoc: 'index.html',
  hostedZone: 'example.com',
  customErrorResponses: [
    {
      httpStatus: 404,
      responseHttpStatus: 200,
      responsePagePath: '/index.html', // SPA routing
    },
    {
      httpStatus: 403,
      responseHttpStatus: 200,
      responsePagePath: '/index.html',
    },
  ], // 🎯 Custom error handling
});
```

### Complete Example with All Features

```python
import * as cdk from 'aws-cdk-lib';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import { CreateCloudfrontSite } from 'cdk-simplewebsite-deploy';
import { Construct } from 'constructs';

export class AdvancedWebsiteStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new CreateCloudfrontSite(this, 'advanced-website', {
      websiteFolder: './dist',
      indexDoc: 'index.html',
      errorDoc: 'error.html',
      hostedZone: 'example.com',
      subDomain: 'www.example.com',

      // Performance & Security
      priceClass: cloudfront.PriceClass.PRICE_CLASS_ALL,
      enableSecurityHeaders: true,
      enableIpv6: true,

      // Monitoring & Protection
      enableLogging: true,
      webAclId: 'arn:aws:wafv2:us-east-1:123456789012:global/webacl/my-web-acl/12345678-1234-1234-1234-123456789012',

      // Custom Behaviors
      additionalBehaviors: {
        '/api/*': {
          allowedMethods: cloudfront.AllowedMethods.ALLOW_ALL,
          cachePolicy: cloudfront.CachePolicy.CACHING_DISABLED,
        },
      },

      // SPA Error Handling
      customErrorResponses: [
        {
          httpStatus: 404,
          responseHttpStatus: 200,
          responsePagePath: '/index.html',
        },
      ],
    });
  }
}
```

## 🎯 Key Benefits

### 🔒 **Enhanced Security**

* **Security Headers**: Automatic HSTS, X-Frame-Options, Content-Type-Options, and XSS protection
* **WAF Integration**: Support for AWS WAF Web ACLs for advanced threat protection
* **Origin Access Control**: Modern S3 bucket protection (replaces deprecated OAI)

### ⚡ **Optimized Performance**

* **Smart Caching**: Optimized cache policies for better performance
* **HTTP/2 & HTTP/3**: Latest protocol support for faster loading
* **Global Edge Locations**: Configurable price classes for worldwide distribution
* **IPv6 Support**: Dual-stack networking for better connectivity

### 📊 **Comprehensive Monitoring**

* **Access Logging**: CloudFront access logs for analytics
* **Custom Error Handling**: Flexible error response configuration
* **SPA Support**: Built-in single-page application routing support

### 🚀 **Developer Experience**

* **Backward Compatible**: All existing configurations continue to work
* **Type Safe**: Full TypeScript support with comprehensive interfaces
* **CDK v2 Ready**: Built for the latest AWS CDK version
* **Multi-Language**: Support for TypeScript, Python, Java, and C#

## License

Distributed under the [Apache-2.0](./LICENSE) license.
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

import aws_cdk.aws_cloudfront as _aws_cdk_aws_cloudfront_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="cdk-simplewebsite-deploy.BasicSiteConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "hosted_zone": "hostedZone",
        "index_doc": "indexDoc",
        "website_folder": "websiteFolder",
        "error_doc": "errorDoc",
    },
)
class BasicSiteConfiguration:
    def __init__(
        self,
        *,
        hosted_zone: builtins.str,
        index_doc: builtins.str,
        website_folder: builtins.str,
        error_doc: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param hosted_zone: Hosted Zone used to create the DNS record for the website.
        :param index_doc: The index document of the website.
        :param website_folder: Local path to the website folder you want to deploy on S3.
        :param error_doc: The error document of the website. Default: - No error document.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55e1d457f7f88b408ecc128e65052c3c69d68b852e2406239079c5f4b76a672d)
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
            check_type(argname="argument index_doc", value=index_doc, expected_type=type_hints["index_doc"])
            check_type(argname="argument website_folder", value=website_folder, expected_type=type_hints["website_folder"])
            check_type(argname="argument error_doc", value=error_doc, expected_type=type_hints["error_doc"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "hosted_zone": hosted_zone,
            "index_doc": index_doc,
            "website_folder": website_folder,
        }
        if error_doc is not None:
            self._values["error_doc"] = error_doc

    @builtins.property
    def hosted_zone(self) -> builtins.str:
        '''Hosted Zone used to create the DNS record for the website.'''
        result = self._values.get("hosted_zone")
        assert result is not None, "Required property 'hosted_zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def index_doc(self) -> builtins.str:
        '''The index document of the website.'''
        result = self._values.get("index_doc")
        assert result is not None, "Required property 'index_doc' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def website_folder(self) -> builtins.str:
        '''Local path to the website folder you want to deploy on S3.'''
        result = self._values.get("website_folder")
        assert result is not None, "Required property 'website_folder' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def error_doc(self) -> typing.Optional[builtins.str]:
        '''The error document of the website.

        :default: - No error document.
        '''
        result = self._values.get("error_doc")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BasicSiteConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk-simplewebsite-deploy.CloudfrontSiteConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "hosted_zone": "hostedZone",
        "index_doc": "indexDoc",
        "website_folder": "websiteFolder",
        "additional_behaviors": "additionalBehaviors",
        "custom_error_responses": "customErrorResponses",
        "domain": "domain",
        "enable_ipv6": "enableIpv6",
        "enable_logging": "enableLogging",
        "enable_security_headers": "enableSecurityHeaders",
        "error_doc": "errorDoc",
        "logs_bucket": "logsBucket",
        "price_class": "priceClass",
        "sub_domain": "subDomain",
        "web_acl_id": "webAclId",
    },
)
class CloudfrontSiteConfiguration:
    def __init__(
        self,
        *,
        hosted_zone: builtins.str,
        index_doc: builtins.str,
        website_folder: builtins.str,
        additional_behaviors: typing.Optional[typing.Mapping[builtins.str, typing.Union["_aws_cdk_aws_cloudfront_ceddda9d.BehaviorOptions", typing.Dict[builtins.str, typing.Any]]]] = None,
        custom_error_responses: typing.Optional[typing.Sequence[typing.Union["_aws_cdk_aws_cloudfront_ceddda9d.ErrorResponse", typing.Dict[builtins.str, typing.Any]]]] = None,
        domain: typing.Optional[builtins.str] = None,
        enable_ipv6: typing.Optional[builtins.bool] = None,
        enable_logging: typing.Optional[builtins.bool] = None,
        enable_security_headers: typing.Optional[builtins.bool] = None,
        error_doc: typing.Optional[builtins.str] = None,
        logs_bucket: typing.Optional["_aws_cdk_aws_s3_ceddda9d.IBucket"] = None,
        price_class: typing.Optional["_aws_cdk_aws_cloudfront_ceddda9d.PriceClass"] = None,
        sub_domain: typing.Optional[builtins.str] = None,
        web_acl_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param hosted_zone: Hosted Zone used to create the DNS record for the website.
        :param index_doc: The index document of the website.
        :param website_folder: Local path to the website folder you want to deploy on S3.
        :param additional_behaviors: Optional cache behaviors for different path patterns. Default: - No additional cache behaviors.
        :param custom_error_responses: Custom error responses for different HTTP status codes. Default: - Default error responses based on errorDoc setting.
        :param domain: Used to deploy a Cloudfront site with a single domain. e.g. sample.example.com If you include a value for both domain and subDomain, an error will be thrown. Default: - no value
        :param enable_ipv6: Enable IPv6 support with AAAA records. Default: false - No IPv6 support.
        :param enable_logging: Enable CloudFront access logging. Default: false - No access logging.
        :param enable_security_headers: Enable response headers policy for security headers. Default: false - No security headers policy applied.
        :param error_doc: The error document of the website. Default: - No error document.
        :param logs_bucket: S3 bucket for CloudFront access logs. If not provided and logging is enabled, a new bucket will be created. Default: - New bucket created if logging is enabled.
        :param price_class: The price class determines how many edge locations CloudFront will use for your distribution. Default: PriceClass.PRICE_CLASS_100.
        :param sub_domain: The subdomain name you want to deploy. e.g. www.example.com If you include a value for both domain and subDomain, an error will be thrown. Default: - no value
        :param web_acl_id: Optional WAF Web ACL ARN for enhanced security. Default: - No WAF integration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e850e19fcfb3492790ff3ec407df63abfa515b2415ed714c8499dc3239a822f)
            check_type(argname="argument hosted_zone", value=hosted_zone, expected_type=type_hints["hosted_zone"])
            check_type(argname="argument index_doc", value=index_doc, expected_type=type_hints["index_doc"])
            check_type(argname="argument website_folder", value=website_folder, expected_type=type_hints["website_folder"])
            check_type(argname="argument additional_behaviors", value=additional_behaviors, expected_type=type_hints["additional_behaviors"])
            check_type(argname="argument custom_error_responses", value=custom_error_responses, expected_type=type_hints["custom_error_responses"])
            check_type(argname="argument domain", value=domain, expected_type=type_hints["domain"])
            check_type(argname="argument enable_ipv6", value=enable_ipv6, expected_type=type_hints["enable_ipv6"])
            check_type(argname="argument enable_logging", value=enable_logging, expected_type=type_hints["enable_logging"])
            check_type(argname="argument enable_security_headers", value=enable_security_headers, expected_type=type_hints["enable_security_headers"])
            check_type(argname="argument error_doc", value=error_doc, expected_type=type_hints["error_doc"])
            check_type(argname="argument logs_bucket", value=logs_bucket, expected_type=type_hints["logs_bucket"])
            check_type(argname="argument price_class", value=price_class, expected_type=type_hints["price_class"])
            check_type(argname="argument sub_domain", value=sub_domain, expected_type=type_hints["sub_domain"])
            check_type(argname="argument web_acl_id", value=web_acl_id, expected_type=type_hints["web_acl_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "hosted_zone": hosted_zone,
            "index_doc": index_doc,
            "website_folder": website_folder,
        }
        if additional_behaviors is not None:
            self._values["additional_behaviors"] = additional_behaviors
        if custom_error_responses is not None:
            self._values["custom_error_responses"] = custom_error_responses
        if domain is not None:
            self._values["domain"] = domain
        if enable_ipv6 is not None:
            self._values["enable_ipv6"] = enable_ipv6
        if enable_logging is not None:
            self._values["enable_logging"] = enable_logging
        if enable_security_headers is not None:
            self._values["enable_security_headers"] = enable_security_headers
        if error_doc is not None:
            self._values["error_doc"] = error_doc
        if logs_bucket is not None:
            self._values["logs_bucket"] = logs_bucket
        if price_class is not None:
            self._values["price_class"] = price_class
        if sub_domain is not None:
            self._values["sub_domain"] = sub_domain
        if web_acl_id is not None:
            self._values["web_acl_id"] = web_acl_id

    @builtins.property
    def hosted_zone(self) -> builtins.str:
        '''Hosted Zone used to create the DNS record for the website.'''
        result = self._values.get("hosted_zone")
        assert result is not None, "Required property 'hosted_zone' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def index_doc(self) -> builtins.str:
        '''The index document of the website.'''
        result = self._values.get("index_doc")
        assert result is not None, "Required property 'index_doc' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def website_folder(self) -> builtins.str:
        '''Local path to the website folder you want to deploy on S3.'''
        result = self._values.get("website_folder")
        assert result is not None, "Required property 'website_folder' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def additional_behaviors(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, "_aws_cdk_aws_cloudfront_ceddda9d.BehaviorOptions"]]:
        '''Optional cache behaviors for different path patterns.

        :default: - No additional cache behaviors.
        '''
        result = self._values.get("additional_behaviors")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, "_aws_cdk_aws_cloudfront_ceddda9d.BehaviorOptions"]], result)

    @builtins.property
    def custom_error_responses(
        self,
    ) -> typing.Optional[typing.List["_aws_cdk_aws_cloudfront_ceddda9d.ErrorResponse"]]:
        '''Custom error responses for different HTTP status codes.

        :default: - Default error responses based on errorDoc setting.
        '''
        result = self._values.get("custom_error_responses")
        return typing.cast(typing.Optional[typing.List["_aws_cdk_aws_cloudfront_ceddda9d.ErrorResponse"]], result)

    @builtins.property
    def domain(self) -> typing.Optional[builtins.str]:
        '''Used to deploy a Cloudfront site with a single domain.

        e.g. sample.example.com
        If you include a value for both domain and subDomain,
        an error will be thrown.

        :default: - no value
        '''
        result = self._values.get("domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_ipv6(self) -> typing.Optional[builtins.bool]:
        '''Enable IPv6 support with AAAA records.

        :default: false - No IPv6 support.
        '''
        result = self._values.get("enable_ipv6")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_logging(self) -> typing.Optional[builtins.bool]:
        '''Enable CloudFront access logging.

        :default: false - No access logging.
        '''
        result = self._values.get("enable_logging")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_security_headers(self) -> typing.Optional[builtins.bool]:
        '''Enable response headers policy for security headers.

        :default: false - No security headers policy applied.
        '''
        result = self._values.get("enable_security_headers")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def error_doc(self) -> typing.Optional[builtins.str]:
        '''The error document of the website.

        :default: - No error document.
        '''
        result = self._values.get("error_doc")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logs_bucket(self) -> typing.Optional["_aws_cdk_aws_s3_ceddda9d.IBucket"]:
        '''S3 bucket for CloudFront access logs.

        If not provided and logging is enabled, a new bucket will be created.

        :default: - New bucket created if logging is enabled.
        '''
        result = self._values.get("logs_bucket")
        return typing.cast(typing.Optional["_aws_cdk_aws_s3_ceddda9d.IBucket"], result)

    @builtins.property
    def price_class(
        self,
    ) -> typing.Optional["_aws_cdk_aws_cloudfront_ceddda9d.PriceClass"]:
        '''The price class determines how many edge locations CloudFront will use for your distribution.

        :default: PriceClass.PRICE_CLASS_100.

        :see: https://aws.amazon.com/cloudfront/pricing/.
        '''
        result = self._values.get("price_class")
        return typing.cast(typing.Optional["_aws_cdk_aws_cloudfront_ceddda9d.PriceClass"], result)

    @builtins.property
    def sub_domain(self) -> typing.Optional[builtins.str]:
        '''The subdomain name you want to deploy.

        e.g. www.example.com
        If you include a value for both domain and subDomain,
        an error will be thrown.

        :default: - no value
        '''
        result = self._values.get("sub_domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def web_acl_id(self) -> typing.Optional[builtins.str]:
        '''Optional WAF Web ACL ARN for enhanced security.

        :default: - No WAF integration.
        '''
        result = self._values.get("web_acl_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudfrontSiteConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CreateBasicSite(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-simplewebsite-deploy.CreateBasicSite",
):
    def __init__(
        self,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        hosted_zone: builtins.str,
        index_doc: builtins.str,
        website_folder: builtins.str,
        error_doc: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param hosted_zone: Hosted Zone used to create the DNS record for the website.
        :param index_doc: The index document of the website.
        :param website_folder: Local path to the website folder you want to deploy on S3.
        :param error_doc: The error document of the website. Default: - No error document.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b1cd29a96c6c8b996276e29a8e2730cf2a3c15a5c12e1c5bc0e23986cb136f7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = BasicSiteConfiguration(
            hosted_zone=hosted_zone,
            index_doc=index_doc,
            website_folder=website_folder,
            error_doc=error_doc,
        )

        jsii.create(self.__class__, self, [scope, id, props])


class CreateCloudfrontSite(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-simplewebsite-deploy.CreateCloudfrontSite",
):
    def __init__(
        self,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        hosted_zone: builtins.str,
        index_doc: builtins.str,
        website_folder: builtins.str,
        additional_behaviors: typing.Optional[typing.Mapping[builtins.str, typing.Union["_aws_cdk_aws_cloudfront_ceddda9d.BehaviorOptions", typing.Dict[builtins.str, typing.Any]]]] = None,
        custom_error_responses: typing.Optional[typing.Sequence[typing.Union["_aws_cdk_aws_cloudfront_ceddda9d.ErrorResponse", typing.Dict[builtins.str, typing.Any]]]] = None,
        domain: typing.Optional[builtins.str] = None,
        enable_ipv6: typing.Optional[builtins.bool] = None,
        enable_logging: typing.Optional[builtins.bool] = None,
        enable_security_headers: typing.Optional[builtins.bool] = None,
        error_doc: typing.Optional[builtins.str] = None,
        logs_bucket: typing.Optional["_aws_cdk_aws_s3_ceddda9d.IBucket"] = None,
        price_class: typing.Optional["_aws_cdk_aws_cloudfront_ceddda9d.PriceClass"] = None,
        sub_domain: typing.Optional[builtins.str] = None,
        web_acl_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param hosted_zone: Hosted Zone used to create the DNS record for the website.
        :param index_doc: The index document of the website.
        :param website_folder: Local path to the website folder you want to deploy on S3.
        :param additional_behaviors: Optional cache behaviors for different path patterns. Default: - No additional cache behaviors.
        :param custom_error_responses: Custom error responses for different HTTP status codes. Default: - Default error responses based on errorDoc setting.
        :param domain: Used to deploy a Cloudfront site with a single domain. e.g. sample.example.com If you include a value for both domain and subDomain, an error will be thrown. Default: - no value
        :param enable_ipv6: Enable IPv6 support with AAAA records. Default: false - No IPv6 support.
        :param enable_logging: Enable CloudFront access logging. Default: false - No access logging.
        :param enable_security_headers: Enable response headers policy for security headers. Default: false - No security headers policy applied.
        :param error_doc: The error document of the website. Default: - No error document.
        :param logs_bucket: S3 bucket for CloudFront access logs. If not provided and logging is enabled, a new bucket will be created. Default: - New bucket created if logging is enabled.
        :param price_class: The price class determines how many edge locations CloudFront will use for your distribution. Default: PriceClass.PRICE_CLASS_100.
        :param sub_domain: The subdomain name you want to deploy. e.g. www.example.com If you include a value for both domain and subDomain, an error will be thrown. Default: - no value
        :param web_acl_id: Optional WAF Web ACL ARN for enhanced security. Default: - No WAF integration.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35939f41a1cbd87bd7b3fa20b126e3c79332b77b538ed266f3ea73f154b3c68a)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CloudfrontSiteConfiguration(
            hosted_zone=hosted_zone,
            index_doc=index_doc,
            website_folder=website_folder,
            additional_behaviors=additional_behaviors,
            custom_error_responses=custom_error_responses,
            domain=domain,
            enable_ipv6=enable_ipv6,
            enable_logging=enable_logging,
            enable_security_headers=enable_security_headers,
            error_doc=error_doc,
            logs_bucket=logs_bucket,
            price_class=price_class,
            sub_domain=sub_domain,
            web_acl_id=web_acl_id,
        )

        jsii.create(self.__class__, self, [scope, id, props])


__all__ = [
    "BasicSiteConfiguration",
    "CloudfrontSiteConfiguration",
    "CreateBasicSite",
    "CreateCloudfrontSite",
]

publication.publish()

def _typecheckingstub__55e1d457f7f88b408ecc128e65052c3c69d68b852e2406239079c5f4b76a672d(
    *,
    hosted_zone: builtins.str,
    index_doc: builtins.str,
    website_folder: builtins.str,
    error_doc: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e850e19fcfb3492790ff3ec407df63abfa515b2415ed714c8499dc3239a822f(
    *,
    hosted_zone: builtins.str,
    index_doc: builtins.str,
    website_folder: builtins.str,
    additional_behaviors: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.BehaviorOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    custom_error_responses: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.ErrorResponse, typing.Dict[builtins.str, typing.Any]]]] = None,
    domain: typing.Optional[builtins.str] = None,
    enable_ipv6: typing.Optional[builtins.bool] = None,
    enable_logging: typing.Optional[builtins.bool] = None,
    enable_security_headers: typing.Optional[builtins.bool] = None,
    error_doc: typing.Optional[builtins.str] = None,
    logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    price_class: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.PriceClass] = None,
    sub_domain: typing.Optional[builtins.str] = None,
    web_acl_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b1cd29a96c6c8b996276e29a8e2730cf2a3c15a5c12e1c5bc0e23986cb136f7(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    hosted_zone: builtins.str,
    index_doc: builtins.str,
    website_folder: builtins.str,
    error_doc: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35939f41a1cbd87bd7b3fa20b126e3c79332b77b538ed266f3ea73f154b3c68a(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    hosted_zone: builtins.str,
    index_doc: builtins.str,
    website_folder: builtins.str,
    additional_behaviors: typing.Optional[typing.Mapping[builtins.str, typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.BehaviorOptions, typing.Dict[builtins.str, typing.Any]]]] = None,
    custom_error_responses: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_cloudfront_ceddda9d.ErrorResponse, typing.Dict[builtins.str, typing.Any]]]] = None,
    domain: typing.Optional[builtins.str] = None,
    enable_ipv6: typing.Optional[builtins.bool] = None,
    enable_logging: typing.Optional[builtins.bool] = None,
    enable_security_headers: typing.Optional[builtins.bool] = None,
    error_doc: typing.Optional[builtins.str] = None,
    logs_bucket: typing.Optional[_aws_cdk_aws_s3_ceddda9d.IBucket] = None,
    price_class: typing.Optional[_aws_cdk_aws_cloudfront_ceddda9d.PriceClass] = None,
    sub_domain: typing.Optional[builtins.str] = None,
    web_acl_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
