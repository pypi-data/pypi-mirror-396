import os
import crossplane
from docksible.constants import *
from .docksible_file_builder import DocksibleFileBuilder


class NginxConfBuilder(DocksibleFileBuilder):

    def __init__(self, private_data_dir, action, letsencrypt=False,
                internal_http_port=None):
        self.private_data_dir = private_data_dir

        self.base_template = crossplane.parse(
                os.path.join(TEMPLATES_DIR, 'base-nginx.conf.j2'))

        self._init_nginx_conf()

        self.internal_http_port = internal_http_port

        self.set_letsencrypt(letsencrypt)
        self.set_action(action)


    def _init_nginx_conf(self):
        # TODO: Is there a better way?
        self.nginx_conf = self.base_template['config'][0]['parsed'][0]['block']
        self._server_block = self.nginx_conf[0]['block']


    def set_action(self, action):
        self.action = action

        if action in ['setup-docker-compose', 'nginx']:
            self._init_nginx_conf()
            return

        # TODO: Quick fix shortly before release...
        # In the future, solve this in a better way.
        if self.internal_http_port is None:
            if action in ['wordpress', 'joomla']:
                self.internal_http_port = 80
            elif action in ['redmine']:
                self.internal_http_port = 3000
            else:
                self.internal_http_port = 8000

        root_location_block = [
            {
                'directive': 'proxy_pass',
                'args': ['http://docksible_app:{}'.format(self.internal_http_port)],
            },
            {
                'directive': 'proxy_set_header',
                'args': ['Host', '$host'],
            },
            {
                'directive': 'proxy_set_header',
                'args': ['X-Real-IP', '$remote_addr'],
            },
        ]
        if self.letsencrypt:
            root_location_block.append({
                'directive': 'proxy_set_header',
                'args': ['X-Forwarded-Proto', '$scheme'],
            })

        self._set_root_location_block(root_location_block)


    def set_letsencrypt(self, letsencrypt):
        if letsencrypt:
            self._set_root_location_block([
                {
                    'directive': 'proxy_pass',
                    'args': ['http://docksible_app:{}'.format(self.internal_http_port)],
                },
                {
                    'directive': 'proxy_set_header',
                    'args': ['Host', '$host'],
                },
                {
                    'directive': 'proxy_set_header',
                    'args': ['X-Real-IP', '$remote_addr'],
                },
                {
                    'directive': 'proxy_set_header',
                    'args': ['X-Forwarded-Proto', '$scheme'],
                },
            ])
            self.base_ssl_template = crossplane.parse(
                    os.path.join(TEMPLATES_DIR, 'nginx-ssl.conf.j2'))
            self.nginx_ssl_conf = self.base_ssl_template[
                    'config'][0]['parsed'][0]['block']
        return super().set_letsencrypt(letsencrypt)


    def _set_root_location_block(self, root_location_block):
        found_it = False
        for conf_dict in self._server_block:
            if conf_dict['directive'] == 'location' \
                    and conf_dict['args'] == ['/']:
                conf_dict['block'] = root_location_block
                found_it = True
        if not found_it:
            raise RuntimeError('Found no root location block in nginx_conf')


    def write(self, filepath=['templates', 'nginx.conf.j2']):
        if self.action == 'wordpress':
            self._server_block.append({
                'directive': 'location',
                'args': ['/xmlrpc.php'],
                'block': [
                    {'directive': 'deny', 'args': ['all']},
                    {'directive': 'access_log', 'args': ['off']},
                ],
            })

        with open(
            os.path.join(
                self.private_data_dir,
                *filepath
            ), 'w'
        ) as fh:
            fh.write(
                crossplane.build(
                    self.nginx_conf
                )
            )

        if self.letsencrypt:
            with open(
                os.path.join(
                    self.private_data_dir,
                    'templates',
                    'nginx-ssl.conf.j2',
                ), 'w'
            ) as fh:
                fh.write(
                    crossplane.build(
                        self.nginx_ssl_conf
                    )
                )
