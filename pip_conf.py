import argparse
import os
import urllib.parse


def write_pip_conf(username, token, url):
    """
    Since pypi does not support credentials, artifactory uses the credentials in the
    url to authenticate a user.  This config sets the extra-index-url to artifactory.
    This means pip will pull from pypi first and then try artifactory.
    :param url: The url of the Pypi the hosts the packages you want
    :param username: The artifactory user name.  This can include spaces
    :param token: Token from artifactory used for authentication
    :return:
    """
    pip_file = os.environ.get('PIP_CONFIG_FILE')
    if not pip_file:
        raise KeyError("Environment Variable 'PIP_CONFIG_FILE' not set")
    username = urllib.parse.quote(username)
    custom_url = f'https://{username}:{token}@{url}'
    with open(pip_file, 'w') as f:
        conf_lines = [
            '[global]\n',
            f'extra-index-url = {custom_url}'
        ]
        f.writelines(conf_lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Configure pip Pypi')
    parser.add_argument('username', type=str, help='The quoted username for your credentials')
    parser.add_argument('token', type=str, help='The token to authentication your credentials')
    parser.add_argument(
        '--url',
        type=str,
        help='The base url for your custom Pypi',
        default='cyrusbio.jfrog.io/cyrusbio/api/pypi/pypi/simple',
    )
    args = parser.parse_args()
    write_pip_conf(args.username, args.token, args.url)
