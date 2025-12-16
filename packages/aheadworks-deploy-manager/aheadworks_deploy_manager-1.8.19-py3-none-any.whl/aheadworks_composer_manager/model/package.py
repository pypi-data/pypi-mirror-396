class Package:
    def __init__(self, composer: dict):
        self.composer = composer

    def get_composer(self) -> dict:
        return self.composer

    def get_name(self) -> str:
        """ full_module_name - 'aheadworks/module-name'
        """

        return self.composer['name']

    def set_name(self, new_name: str):
        self.composer['name'] = new_name

        return self.composer['name']
    
    def get_short_name(self) -> str:
        """ module_name - 'module-name'
        """

        return self._to_short(self.composer['name'])
    
    def get_composer_package_filename(self) -> str:
        """ name of the release artifact 
        """

        short_name = self.get_short_name()
        version = self.composer['version']
        return f"{short_name}-{version}.zip"

    def get_bitbucket_artifact_filename(self) -> str:
        """ name of the intermediate build result
        """

        short_name = self.get_short_name()
        return f"{short_name}.zip"

    def get_version(self) -> str:
        return self.composer['version']

    def get_require(self) -> dict:
        if not 'require' in self.composer:
            return {}
        return self.composer['require']

    def require_iterator(self, loader_func, base_path):
        require_dict = self.get_require()
        for package_name, version_constraint in require_dict.items():
            package_path = f"{base_path}/{package_name}"
            composer_data = loader_func(package_name, package_path)
            print(f"Composer data loaded from {package_path}")
            print(composer_data)
            yield Package(composer_data)

    def get_suggests(self) -> dict:
        if not 'suggests' in self.composer:
            return {}
        return self.composer['suggests']


    def _to_short(self, name: str) -> str:
        return name.split('/')[1]
