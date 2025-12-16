from aheadworks_core.api.composer_manager import ComposerManager
from aheadworks_composer_manager.model.package import Package

def load_required_modules(package: Package):
    modules_to_require = dict()
    for full_module_name in package.get_require():
        modules_to_require[full_module_name] = ""
    ComposerManager.require_magento_modules(modules_to_require)
