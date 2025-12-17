from shutil import rmtree
import subprocess
from ansible_runner import interface as runner_interface
from .constants import *
from .helpers import *
from .file_builder.playbook_builder import PlaybookBuilder
from .file_builder.docker_compose_builder import DockerComposeBuilder
from .file_builder.nginx_conf_builder import NginxConfBuilder


class Docksible:

    def __init__(self, user, host, action,
            private_data_dir=DEFAULT_PRIVATE_DATA_DIR,
            database_root_password=None, database_username=None,
            database_password=None, database_name=None,
            letsencrypt=False,
            domain=None, email=None,
            test_cert=False,
            ssh_proxy=False,
            sudo_password=None,
            app_image=None,
            app_name=None,
            app_version=DEFAULT_APP_VERSION,
            site_title=DEFAULT_SITE_TITLE,
            admin_username=DEFAULT_ADMIN_USERNAME,
            admin_full_name=DEFAULT_ADMIN_FULL_NAME,
            admin_password=None,
            admin_email=DEFAULT_ADMIN_EMAIL,
            wordpress_locale=DEFAULT_WORDPRESS_LOCALE,
            manual_app_install=False,
            internal_http_port=None,
            phpmyadmin=False,
            extra_env_vars={},
            apparmor_workaround=False,
        ):

        self.private_data_dir = private_data_dir
        try:
            os.makedirs(
                os.path.join(
                    self.private_data_dir,
                    'templates',
                )
            )
        except FileExistsError:
            pass

        self.user = user
        self.host = host

        host_dict = {'ansible_user': self.user}

        if host_is_local(self.host):
            host_dict['ansible_connection'] = 'local'

        self.inventory = {
            'all': {
                'hosts': {
                    self.host: host_dict,
                },
            },
            'ungrouped': {'hosts': {}},
        }

        self.playbook_builder = PlaybookBuilder(
            self.private_data_dir,
            action,
        )
        self.docker_compose_builder = DockerComposeBuilder(
            self.private_data_dir,
            action,
        )
        self.nginx_conf_builder = NginxConfBuilder(
            self.private_data_dir,
            action,
        )
        self.app_image = app_image
        self.app_version = app_version

        self.set_database_root_password(database_root_password)
        self.set_database_username(database_username)
        self.set_database_password(database_password)
        self.set_database_name(database_name)
        self.set_phpmyadmin(phpmyadmin)

        self.domain = domain
        self.email = email
        self.test_cert = test_cert

        self.site_title = site_title
        self.admin_username = admin_username
        self.admin_full_name = admin_full_name
        self.admin_password = admin_password
        self.admin_email = admin_email
        self.wordpress_locale = wordpress_locale

        self.app_name = app_name
        self.set_manual_app_install(manual_app_install)
        self.extra_env_vars = extra_env_vars

        self.sudo_password = sudo_password
        self.apparmor_workaround = apparmor_workaround
        self.extravars = {}

        self.set_action(action)
        self.set_letsencrypt(letsencrypt)
        self.set_ssh_proxy(ssh_proxy)
        self.set_internal_http_port(internal_http_port)


    def set_action(self, action):
        self.action = action

        if action != 'custom-app':
            self.app_image = action

        if action in ['wordpress', 'joomla']:
            self.set_internal_http_port(80)
        elif action in ['redmine']:
            self.set_internal_http_port(3000)

        self.playbook_builder.set_action(self.action)
        self.docker_compose_builder.set_action(self.action)
        self.nginx_conf_builder.set_action(self.action)


    def set_letsencrypt(self, letsencrypt):
        self.letsencrypt = letsencrypt
        self.playbook_builder.set_letsencrypt(letsencrypt)
        self.docker_compose_builder.set_letsencrypt(letsencrypt)
        self.nginx_conf_builder.set_letsencrypt(letsencrypt)


    def set_phpmyadmin(self, phpmyadmin):
        self.phpmyadmin = phpmyadmin
        self.docker_compose_builder.phpmyadmin = phpmyadmin


    def set_ssh_proxy(self, ssh_proxy):
        self.ssh_proxy = ssh_proxy
        self.docker_compose_builder.ssh_proxy = ssh_proxy


    def set_database_root_password(self, database_root_password):
        self.database_root_password = database_root_password
        self.docker_compose_builder.database_root_password = \
                database_root_password


    def set_database_username(self, database_username):
        self.database_username = database_username
        self.docker_compose_builder.database_username = database_username


    def set_database_password(self, database_password):
        self.database_password = database_password
        self.docker_compose_builder.database_password = database_password


    def set_database_name(self, database_name):
        self.database_name = database_name
        self.docker_compose_builder.database_name = database_name


    def set_manual_app_install(self, manual_app_install):
        self.manual_app_install = manual_app_install
        self.docker_compose_builder.manual_app_install = manual_app_install


    def set_extra_env_vars(self, extra_env_vars):
        self.extra_env_vars = extra_env_vars
        self.docker_compose_builder.extra_env_vars = extra_env_vars


    def set_internal_http_port(self, internal_http_port):
        if internal_http_port is None:
            if self.action in ['wordpress', 'joomla']:
                internal_http_port = 80
            elif self.action in ['redmine']:
                internal_http_port = 3000
            else:
                internal_http_port = 8000

        self.internal_http_port = internal_http_port
        self.nginx_conf_builder.internal_http_port = internal_http_port


    def _update_extravars(self):
        if self.action == 'redmine':
            self.internal_http_port = 3000
        elif self.action == 'wordpress':
            self.internal_http_port = 80

        extravars = [
            'docker_compose_volume_dirs',
            'app_version',
            'database_root_password',
            'database_username',
            'database_password',
            'database_name',
            'domain',
            'email',
            'test_cert',
            'ssh_proxy',
            'ansible_sudo_pass',
            'app_image',
            'app_name',
            'site_title',
            'admin_username',
            'admin_full_name',
            'admin_password',
            'admin_email',
            'wordpress_locale',
            'internal_http_port',
            'extra_env_vars',
            'apparmor_workaround',
        ]
        for varname in extravars:
            if varname == 'docker_compose_volume_dirs':
                value = [
                    'db-data',
                    'nginx-data',
                    'app-data',
                ]
                if self.ssh_proxy:
                    value.append('ssh-proxy-data')
                if self.letsencrypt:
                    value.append('certbot-data')

            elif varname == 'test_cert':
                value = self.get_certbot_test_cert_string()

            elif varname == 'domain':
                if not self.domain:
                    value = self.host
                else:
                    value = self.domain

            elif varname == 'ansible_sudo_pass':
                if self.sudo_password:
                    value = self.sudo_password
                else:
                    continue

            else:
                value = getattr(self, varname)

            self.extravars[varname] = value


    def _build_ansible_files(self):
        self.playbook_builder.write()
        self.docker_compose_builder.write()
        self.nginx_conf_builder.write()


    def _install_galaxy_dependencies(self):
        subprocess.run([
            'ansible-galaxy',
            'collection',
            'install',
            'community.docker',
        ])


    def run(self):
        self._update_extravars()
        self._build_ansible_files()
        self._install_galaxy_dependencies()

        runner = runner_interface.run(
            private_data_dir=self.private_data_dir,
            playbook=f'{self.action}.yml',
            inventory=self.inventory,
            extravars=self.extravars,
        )

        self.cleanup_private_data()
        return runner.rc


    def cleanup_private_data(self):
        rmtree(self.private_data_dir)


    def get_certbot_test_cert_string(self):
        return '--test-cert' if self.test_cert else ''
