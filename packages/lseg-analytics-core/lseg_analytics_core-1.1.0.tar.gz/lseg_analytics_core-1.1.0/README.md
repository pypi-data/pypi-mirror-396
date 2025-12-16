# LSEG Analytics SDK Auth for Python

The LSEG Analytics SDK Auth for Python provides SDK client information for Analytics SDK.

## Getting Started

```shell
$ pip install lseg-analytics-core
```


## Usage Examples

An example to use SDKClient.

```python
from lseg_analytics.core.sdk_session import SDKSession

base_url = SDKSession._base_url
username = SDKSession._username
headers_policy = SDKSession._headers_policy
authentication_policy = SDKSession._authentication_policy
```

