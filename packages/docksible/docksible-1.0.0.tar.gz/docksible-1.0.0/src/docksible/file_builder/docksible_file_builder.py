import os
import yaml
from docksible.constants import TEMPLATES_DIR


class DocksibleFileBuilder:

    def __init__(self, private_data_dir, base_template_filename, action,
                 letsencrypt=False):

        self.private_data_dir = private_data_dir

        with open(
            os.path.join(
                TEMPLATES_DIR,
                base_template_filename
            ), 'r'
        ) as fh:
            self.base_template = yaml.safe_load(fh)


    def set_action(self, action):
        self.action = action


    def set_letsencrypt(self, letsencrypt):
        self.letsencrypt = letsencrypt


    def get_additional_template(self, filename):
        result = None
        with open(
            os.path.join(
                TEMPLATES_DIR,
                filename
            ), 'r'
        ) as fh:
            result = yaml.safe_load(fh)

        return result


    def write(self, filepath):
        with open(
            os.path.join(self.private_data_dir, *filepath), 'w'
        ) as fh:
            yaml.dump(self.base_template, fh)
