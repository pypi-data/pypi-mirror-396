from pathlib import Path

import addons_installer

from environ_odoo_config.environ import Environ, _logger


def _post_parse_env(self, curr_env: Environ):
    results = addons_installer.AddonsFinder.parse_env(env_vars=curr_env)
    for result in results:
        path = Path(result.addons_path)
        subs = set(addons_installer.AddonsFinder.parse_submodule([result]))
        self.addons_path.update(map(lambda it: it.addons_path, subs))
        if (path / "EXCLUDE").exists():
            # EXCLUDE not exclude submodule discover
            # Only exclude this module from the addon-path
            _logger.info("Ignore %s with EXCLUDE file", result.addons_path)
            continue
        self.addons_path.add(Path(result.addons_path))
