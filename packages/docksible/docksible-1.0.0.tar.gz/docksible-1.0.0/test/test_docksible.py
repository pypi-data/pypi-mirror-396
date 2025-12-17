import os
import unittest
from getpass import getpass, getuser
import yaml
from docksible.docksible import Docksible
from docksible.constants import TEMPLATES_DIR
from docksible.helpers import *


class TestDocksible(unittest.TestCase):

    def setUp(self):
        try:
            tmp_remote = os.environ['DOCKSIBLE_REMOTE'].split('@')
            user = tmp_remote[0]
            host = tmp_remote[1]
        except IndexError:
            user = getuser()
            host = 'localhost'
        except KeyError:
            exit("Please set environment variable 'DOCKSIBLE_REMOTE'!")

        self.docksible = Docksible(
            user=user,
            host=host,
            action='setup-docker-compose',
            private_data_dir=os.path.join(
                'test',
                'tmp-private-data',
            ),
            database_root_password='rootpassword',
            database_username='db-username',
            database_password='password',
            database_name='test_db',
            test_cert=True
        )

        if host_is_local(host) or host_is_private(host):
            if user != 'root':
                self.docksible.sudo_password = getpass(
                    'Please enter sudo password for test host: '
                )
        else:
            self.docksible.domain = host
            # 'user@example.com' will be rejected by Let's Encrypt,
            # but 'me@me.me' seems OK...
            # And Docksible fails silently... we could maybe
            # improve that as well...
            #self.docksible.email = 'user@example.com'
            self.docksible.email = 'me@me.me'


    def must_set_letsencrypt(self):
        return not host_is_local(self.docksible.host) \
            and not host_is_private(self.docksible.host)


    def test_docker_compose(self):
        self.docksible.set_letsencrypt(False)
        self._do_test_run()


    def test_nginx(self):
        # TODO: Set letsencrypt to True, and make minimal Nginx
        # work with SSL too?
        self.docksible.set_letsencrypt(False)
        self.docksible.set_action('nginx')
        self._do_test_run()


    def test_wordpress(self):
        self.docksible.set_database_name('wordpress')
        self.docksible.site_title = 'My WordPress Site'
        self.docksible.admin_username = 'admin'
        self.docksible.admin_password = 'password'
        self.docksible.admin_email = 'me@me.me'
        self.docksible.wordpress_locale = 'en_US'

        self.docksible.set_action('wordpress')
        self.docksible.set_letsencrypt(self.must_set_letsencrypt())
        self._do_test_run()


    def test_joomla(self):
        self.docksible.set_database_name('joomla')
        self.docksible.site_title = 'My Joomla Site'
        self.docksible.admin_username = 'admin'
        self.docksible.admin_full_name = 'Joomla administrator'
        self.docksible.admin_password = 'passwordpassword'
        self.docksible.admin_email = 'me@me.me'

        self.docksible.set_action('joomla')
        self.docksible.set_letsencrypt(self.must_set_letsencrypt())
        self._do_test_run()


    def test_redmine(self):
        self.docksible.set_database_name('redmine')
        self.docksible.set_action('redmine')
        self.docksible.set_letsencrypt(self.must_set_letsencrypt())
        self._do_test_run()


    def test_ssh_proxy(self):
        self.docksible.set_ssh_proxy(True)
        self.docksible.set_database_name('redmine')
        self.docksible.set_action('redmine')
        self._do_test_run()


    def test_custom_app(self):
        self.docksible.set_action('custom-app')
        self.docksible.set_database_name('smartestate')
        self.docksible.app_name = 'smartestate'
        self.docksible.app_image = 'belalibrahim/smartestate'
        self.docksible.set_extra_env_vars({
            'DEBUG': 0,
            'ALLOWED_HOSTS': self.docksible.host,
            'DATABASE_ENGINE': 'django.db.backends.mysql',
            'DATABASE_HOST': 'docksible_db',
            'DATABASE_NAME': self.docksible.database_name,
            'DATABASE_USER': self.docksible.database_username,
            'DATABASE_PASSWORD': self.docksible.database_password,
        })
        # Not necessary, because it's the default value.
        # But in any case, it should work with and without.
        #self.docksible.set_internal_http_port(8000)
        self._do_test_run()


    def test_phpmyadmin(self):
        self.docksible.set_database_name('redmine')
        self.docksible.set_action('redmine')
        self.docksible.set_phpmyadmin(True)
        self._do_test_run()


    def test_playbook_builder(self):
        with open(
            os.path.join(
                TEMPLATES_DIR,
                'base-playbook.yml',
            ), 'r'
        ) as fh:
            expected_playbook_ls = yaml.safe_load(fh)

        self.docksible.set_action('setup-docker-compose')
        self.docksible._build_ansible_files()
        with open(
            os.path.join(
                self.docksible.private_data_dir,
                self.docksible.playbook_builder.playbook_filename
            ), 'r'
        ) as fh:
            written_yaml = yaml.safe_load(fh)

        self.docksible.cleanup_private_data()
        self.assertListEqual(expected_playbook_ls, written_yaml)


    def test_docker_compose_builder(self):
        with open(
            os.path.join(
                TEMPLATES_DIR,
                'base-docker-compose.yml.j2',
            ), 'r'
        ) as fh:
            expected_docker_compose = yaml.safe_load(fh)

        self.docksible.set_action('nginx')
        self.docksible._build_ansible_files()
        with open(
            os.path.join(
                self.docksible.private_data_dir,
                'templates',
                'docker-compose.yml.j2',
            ), 'r'
        ) as fh:
            written_yaml = yaml.safe_load(fh)

        self.docksible.cleanup_private_data()
        self.assertDictEqual(expected_docker_compose, written_yaml)


    def test_nginx_conf_builder(self):

        self.docksible.set_action('nginx')
        self.docksible._build_ansible_files()

        expected = os.path.join('test', 'expected-nginx.conf')
        actual = os.path.join(self.docksible.private_data_dir, 'templates', 'nginx.conf.j2')

        with open(expected, 'r', encoding='utf-8') as f1, open(actual, 'r', encoding='utf-8') as f2:
            self.docksible.cleanup_private_data()
            assert f1.read().strip().replace('\r\n', '\n') == f2.read().strip().replace('\r\n', '\n')


    def _do_test_run(self):
        self.assertEqual(self.docksible.run(), 0)
