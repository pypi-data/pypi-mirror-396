from .docksible_file_builder import DocksibleFileBuilder


class PlaybookBuilder(DocksibleFileBuilder):

    def __init__(self, private_data_dir, action, letsencrypt=False):

        super().__init__(
            private_data_dir,
            'base-playbook.yml',
            action,
            letsencrypt,
        )

        self._playbook_dict = self.base_template[0]

        self.set_action(action)
        self.set_letsencrypt(letsencrypt)


    def set_action(self, action):
        self.action = action
        self.playbook_filename = f'{action}.yml'


    def write(self, filepath=[]):
        if self.action != 'setup-docker-compose':
            self._playbook_dict['tasks'].extend(
                self.get_additional_template('playbook-run-tasks.yml')
            )

        if self.letsencrypt:
            self._playbook_dict['tasks'].extend(
                self.get_additional_template('letsencrypt-tasks.yml')
            )
        filepath = [self.playbook_filename]
        super().write(filepath)
