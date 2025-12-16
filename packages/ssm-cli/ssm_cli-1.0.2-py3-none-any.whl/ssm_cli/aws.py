import boto3
import botocore
import contextlib
from ssm_cli.cli_args import ARGS

class AWSError(Exception):
    """ A generic exception for any AWS errors """
    pass

class AWSAuthError(AWSError):
    """ A generic exception for any AWS authentication errors """
    pass

class AWSAccessDeniedError(AWSError):
    """ An exception for when the AWS credentials do not have the required permissions """
    pass

_session_cache = []
_client_cache = {}

@contextlib.contextmanager
def aws_session(use_cache=True):
    """ A context manager for creating a boto3 session with caching built in """
    try:
        if len(_session_cache) > 0 and use_cache:
            yield _session_cache[0]
            return
        
        session = boto3.Session(profile_name=ARGS.global_args.profile)
        if session.region_name is None:
            raise AWSAuthError(f"AWS config missing region for profile {session.profile_name}")
        
        _session_cache.append(session)
        yield session
    except botocore.exceptions.ProfileNotFound as e:
        raise AWSAuthError(f"profile invalid") from e
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ExpiredTokenException':
            raise AWSAuthError(f"AWS credentials expired") from e
        elif e.response['Error']['Code'] == "AccessDeniedException":
            raise AWSAccessDeniedError(f"AWS credentials do not have the required permissions") from e
        raise e

@contextlib.contextmanager
def aws_client(service_name, use_cache=True):
    """ A context manager for creating a boto3 client with caching built in """
    with aws_session(use_cache) as session:
        if service_name in _client_cache and use_cache:
            yield _client_cache[service_name]
            return
        
        client = session.client(service_name)
        _client_cache[service_name] = client
        yield client
