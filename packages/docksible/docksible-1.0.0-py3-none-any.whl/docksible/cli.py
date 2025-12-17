import argparse
from . import __version__
from .constants import *
from .arg_validator import ArgValidator
from .docksible import Docksible


def main():

    print(DOCKSIBLE_BANNER)

    parser = argparse.ArgumentParser(
        prog='docksible'
    )

    parser.add_argument('user_at_host', nargs='?',
        help="""
        user and host where you want to \
        install your app. example: user@example.com, root@192.168.0.2, etc.
        If running locally, you can omit the user and simply pass in
        localhost, 127.0.0.1, etc.
        """
        )
    parser.add_argument('action', nargs='?', choices=SUPPORTED_ACTIONS)

    parser.add_argument('--app-version', '-v', default=DEFAULT_APP_VERSION)
    parser.add_argument('--ask-remote-sudo', action='store_true')
    parser.add_argument('--insecure-cli-password', action='store_true')
    parser.add_argument('--remote-sudo-password')
    parser.add_argument('--database-root-password')
    parser.add_argument('--database-username')
    parser.add_argument('--database-password')
    parser.add_argument('--database-name')
    parser.add_argument('--database-table-prefix', default=DEFAULT_DATABASE_TABLE_PREFIX)
    parser.add_argument('--letsencrypt', '-l', action='store_true')
    parser.add_argument('--domain', '-d')
    parser.add_argument('--email',  '-e')
    parser.add_argument('--test-cert', '-t', action='store_true')
    parser.add_argument('--ssh-proxy', action='store_true',
        help="""
        Pass this flag to include a lightweight SSH proxy container
        in your Docker network, so you can port forward hidden services
        such as the database.
        """
    )
    parser.add_argument('--app-image',
        help="""
        Required for the 'custom-app' action, it should be the publicly
        available Docker image of your app, something like
        'docker-hub-user/example-app:latest'
        """
    )
    parser.add_argument('--app-name')

    parser.add_argument('--site-title')
    parser.add_argument('--admin-username')
    parser.add_argument('--admin-full-name')
    parser.add_argument('--admin-password')
    parser.add_argument('--admin-email')
    parser.add_argument('--wordpress-locale')

    parser.add_argument('--internal-http-port')
    parser.add_argument('--phpmyadmin', action='store_true',
        help="""
        Set this flag to include a phpmyadmin container in your app's
        Docker network. It won't be exposed, so you will still have to proxy
        the connection through an SSH tunnel.
        Omit this flag, if you don't need phpmyadmin to connect to your
        app's database.
        """
    )
    parser.add_argument('--manual-app-install', action='store_true',
        help="""
        Set this flag if, for example, you don't want WP-CLI to install your
        site, but you want to perform the "Famous 5 Minute WordPress Install"
        manually. Applies to other apps that have an equivalent to this.
        """
    )
    parser.add_argument('--extra-env-vars',
        help="""
        Comma separated key value pairs, to provide any environment variables
        that your app may require. For a custom app, you'll most likely need
        these to configure the database, because the environment variable names
        that the app expects are arbitrary.
        """
    )
    parser.add_argument('--apparmor-workaround', action='store_true')
    parser.add_argument('--private-data-dir', default=DEFAULT_PRIVATE_DATA_DIR)
    parser.add_argument('--version', '-V', action='version', version=__version__)

    args = parser.parse_args()

    validator = ArgValidator(args)
    if validator.validate_args() != 0:
        print("FATAL! Bad args. Run 'docksible --help' for usage help.")
        return 1

    args = validator.get_validated_args()

    docksible = Docksible(
        user=args.user,
        host=args.host,
        action=args.action,
        private_data_dir=args.private_data_dir,
        letsencrypt=args.letsencrypt,
        domain=args.domain,
        email=args.email,
        test_cert=args.test_cert,
        app_version=args.app_version,
        database_root_password=args.database_root_password,
        database_username=args.database_username,
        database_password=args.database_password,
        database_name=args.database_name,
        sudo_password=args.remote_sudo_password,
        site_title=args.site_title,
        admin_username=args.admin_username,
        admin_full_name=args.admin_full_name,
        admin_password=args.admin_password,
        admin_email=args.admin_email,
        wordpress_locale=args.wordpress_locale,
        ssh_proxy=args.ssh_proxy,
        app_image=args.app_image,
        app_name=args.app_name,
        internal_http_port=args.internal_http_port,
        phpmyadmin=args.phpmyadmin,
        manual_app_install=args.manual_app_install,
        extra_env_vars=args.extra_env_vars,
        apparmor_workaround=args.apparmor_workaround,
    )

    return docksible.run()


if __name__ == "__main__":
    main()
