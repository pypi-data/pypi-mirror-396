import json
import os

from concurrent.futures import ThreadPoolExecutor
import requests

from corehttp.runtime.policies import BearerTokenCredentialPolicy

from ._credentials.user_token_credential import UserTokenCredential
from ._credentials.machine_token_credential import MachineTokenCredential

from .exceptions import ProxyStatusError, ProxyNotEnabledError, ProxyNotFoundError, ProxyAuthFailureError, \
    _ERROR_MESSAGE
from ._credentials.config import load_config
from .logging._logger import get_library_logger

logger = get_library_logger()

__all__ = ["SDKSession"]


def _get_proxy_port_from_file():
    port_file = f'{os.path.expanduser("~")}{os.path.sep}.lseg{os.path.sep}VSCode{os.path.sep}.portInUse'
    logger.debug(f'Trying to read proxy port from file:{port_file}')
    if os.path.isfile(port_file):
        logger.info(f"Reading from file:{port_file}")
        with open(port_file) as f:
            port = f.read()
            if port.strip().strip('\n').lower() == 'disabled':
                raise ProxyNotEnabledError(_ERROR_MESSAGE.PROXY_DISABLED.value)
            return int(port)
    else:
        raise Exception(f"Port file({port_file}) is not found")


def get_proxy_status_response(port):
    url = f"http://localhost:{port}/status"
    try:
        response = requests.get(url, timeout=1)  # timeout is 1 second
        return port, response
    except Exception as err:
        logger.warning(f"Get exception:{err} when requesting url :{url}")
        return port, None


def _check_proxy_status(ports_list):
    logger.debug(f'checking if localhost proxy is working with ports[{ports_list}]')
    with ThreadPoolExecutor(max_workers=10) as exe:
        responses = exe.map(get_proxy_status_response, ports_list)
        for port, response in responses:
            try:
                if response is not None:
                    if response.status_code == 200:
                        data = json.loads(response.text)
                        if 'lsegProxyEnabled' in data:
                            if data['lsegProxyEnabled']:
                                return f"http://localhost:{port}"
                            else:
                                raise ProxyNotEnabledError(_ERROR_MESSAGE.PROXY_DISABLED.value)
                        else:
                            logger.error(
                                f"Failed to get status from proxy. lsegProxyEnabled is not in payload, Port: {port} Detail:{data}")
                            raise ProxyStatusError(_ERROR_MESSAGE.INVALID_RESPONSE.value)
                    elif response.status_code == 401:
                        raise ProxyAuthFailureError(_ERROR_MESSAGE.PROXY_UNAUTHORIZED.value)
                    elif response.status_code == 403:
                        raise ProxyAuthFailureError(_ERROR_MESSAGE.PROXY_FORBIDDEN.value)
                    else:
                        logger.error(
                            f"Failed to get status from proxy. Incorrect status code {response.status_code} with port: {port}")
                        raise ProxyStatusError(_ERROR_MESSAGE.INVALID_RESPONSE.value)
            except (ProxyStatusError, ProxyNotEnabledError, ProxyAuthFailureError) as err:
                raise err
            except Exception as err:
                logger.error(
                    f"Failed to get status from proxy. Got exception when parsing response with port {port}: {err}")
                raise ProxyStatusError(_ERROR_MESSAGE.INVALID_RESPONSE.value)
    raise ProxyNotFoundError(_ERROR_MESSAGE.NO_AVALIABLE_PORT.value)


def _get_proxy_info():
    try:
        # add the port from file at first, so we will check it firstly
        port = _get_proxy_port_from_file()
        proxy_url = _check_proxy_status([port])
        logger.info(f"Proxy is found with port configured, proxy url is:{proxy_url}")
        return proxy_url
    except (ProxyStatusError, ProxyNotEnabledError, ProxyAuthFailureError) as err:
        raise err
    except Exception as err:  # No break
        logger.warning(f"Failed to load proxy port from local file, error: {err}")

    # add default ports: 60100 to 60110 inclusive
    ports = range(60100, 60111)
    proxy_url = _check_proxy_status(list(ports))
    logger.info(f"proxy is found, proxy url is:{proxy_url}")
    return proxy_url


from corehttp.runtime.policies import HeadersPolicy

class _SDKHeaderPolicy(HeadersPolicy):
    def on_request(self, request):
        token = SDKSession._token
        if token:
            request.http_request.headers['Authorization'] = f'Bearer {token}'
        super().on_request(request)

class SDKSession:
    _authentication_policy = None
    _headers_policy = None
    _base_url = None
    _username = None
    _user_token_cred = None
    _token = None

    @classmethod
    def reload(cls):
        cls._instance = None

    def __new__(cls, *args, **kwargs):
        if not getattr(cls, '_instance', None):
            cfg = load_config()
            authentication_policy = None
            if cfg.machine_auth and cfg.machine_auth.client_id and cfg.machine_auth.token_endpoint and cfg.machine_auth.client_secret:
                authentication_policy = BearerTokenCredentialPolicy(
                    credential=MachineTokenCredential(
                        client_id=cfg.machine_auth.client_id,
                        client_secret=cfg.machine_auth.client_secret,
                        auth_endpoint=cfg.machine_auth.token_endpoint,
                        scopes=cfg.machine_auth.scopes,
                    ),
                    scopes=cfg.machine_auth.scopes,
                )
            elif cfg.user_auth and cfg.user_auth.client_id and cfg.user_auth.authority and cfg.user_auth.redirect_uri:
                cls._user_token_cred = UserTokenCredential(
                    client_id=cfg.user_auth.client_id,
                    authority=cfg.user_auth.authority,
                    redirect_uri=cfg.user_auth.redirect_uri,
                    scopes=cfg.user_auth.scopes,
                )
                authentication_policy = BearerTokenCredentialPolicy(
                    credential=cls._user_token_cred,
                    scopes=cfg.user_auth.scopes,
                )
            else:
                proxy_disabled = os.getenv("LSEG_ANALYTICS_PROXY_DISABLED", 'false').lower() in ('true', '1')
                if not proxy_disabled:
                    SDKSession._retrieve_proxy_endpoint(cfg)

            headers_policy = _SDKHeaderPolicy()
            if cfg.headers:
                for key, value in cfg.headers.items():
                    headers_policy.add_header(key, value)
            cls._instance = super().__new__(cls)
            cls._instance._authentication_policy = authentication_policy
            cls._instance._headers_policy = headers_policy
            cls._instance._base_url = cfg.base_url
            cls._instance._username = cfg.username

        return cls._instance

    @staticmethod
    def set_token(token: str):
        """
        Sets the authentication token for the SDK session.

        Args:
            token (str): The authentication token to be set for the session.
        """
        SDKSession._token = token

    @staticmethod
    def clean_token():
        """
        Clears the stored authentication token by setting it to None.
        """
        SDKSession._token = None

    @staticmethod
    def _retrieve_proxy_endpoint(cfg):
        if (LSEG_ANALYTICS_PROXY_URL := os.getenv("LSEG_ANALYTICS_PROXY_URL")):
            cfg.base_url = LSEG_ANALYTICS_PROXY_URL
        else:
            cfg.base_url = _get_proxy_info()
