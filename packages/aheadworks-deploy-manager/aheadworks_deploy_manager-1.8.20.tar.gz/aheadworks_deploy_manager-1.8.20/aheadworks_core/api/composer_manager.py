import os
import json

class ComposerManager:
    @staticmethod
    def init_extra_repos():
        # COMPOSER_REPOSITORIES -- variable in module repo settings
        extraRepositories = os.environ.get('COMPOSER_REPOSITORIES', "")
        if not extraRepositories:
            print('COMPOSER_REPOSITORIES variable is empty or unset. This is ok if you need no external composer repositories.')
        else:
            try:
                composer = json.loads(extraRepositories)
                for item in composer:
                    os.system(f"composer config -g repositories.{item['name']} {item['type']} {item['url']}")
            except:
                print(f'COMPOSER_REPOSITORIES variable contains invalid JSON:{extraRepositories}')

    @staticmethod
    def require_magento_module(module_name, module_version = None):
        old_cwd = os.getcwd()
        if module_version is not None:
            os.system(f"cd /var/www/html && composer require {module_name}:{module_version}")
        else:
            os.system(f"cd /var/www/html && composer require {module_name}")
        os.system(f"cd {old_cwd}")

    @staticmethod
    def require_magento_modules(modules: dict):
        if len(modules)==0:
            return

        all_modules = ""
        for module_name, module_version in modules.items():
            if module_version != "":
              all_modules = f"{all_modules} {module_name}:{module_version}"
            else:
              all_modules = f"{all_modules} {module_name}"

        ComposerManager.require_magento_module(all_modules)
