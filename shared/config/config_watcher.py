import threading
from pathlib import Path

import inotify.adapters
import inotify.constants

from shared.config.config import AppConfig, config, CONFIG_PATH
from shared.logger import logger


class ConfigWatcher:
    def __init__(self, cfg: AppConfig = config):
        self.config_path = CONFIG_PATH
        self.inotify = inotify.adapters.Inotify()
        self.inotify.add_watch(str(self.config_path.parent), mask=inotify.constants.IN_MODIFY)
        self.watch_thread = None
        self.running = False
        self.cfg = cfg

    def _watch(self):
        while self.running:
            for event in self.inotify.event_gen(yield_nones=False):
                (_, type_names, path, filename) = event
                if self.config_path.name == filename:
                    logger.info(f"Config file changed: {filename}")
                    try:
                        self.cfg.__class__.reload_config()
                    except Exception as e:
                        logger.error(f"Error reloading config: {e}")

    def start(self):
        self.running = True
        self.watch_thread = threading.Thread(target=self._watch, daemon=True)
        self.watch_thread.start()

    def stop(self):
        self.running = False
        if self.watch_thread:
            self.watch_thread.join()


watcher = ConfigWatcher()
watcher.start()
