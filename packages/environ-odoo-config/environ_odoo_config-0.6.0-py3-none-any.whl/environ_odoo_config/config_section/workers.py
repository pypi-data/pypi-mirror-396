from environ_odoo_config.config_section.api import (
    OdooConfigGroup,
    SimpleKey,
)


class ConfigConverterWorkers(OdooConfigGroup):
    _opt_group = "POSIX Worker Configuration"
    worker_http: int = SimpleKey("WORKER_HTTP", cli="--workers", ini_dest="workers")
    worker_cron: int = SimpleKey(
        "WORKER_CRON",
        cli="--max-cron-threads",
        info="Maximum number of threads processing concurrently cron jobs (default 2).",
        ini_dest="max_cron_threads",
    )

    @property
    def cron(self) -> int:
        return self.worker_cron

    @property
    def total(self) -> int:
        return self.worker_http + self.worker_cron
