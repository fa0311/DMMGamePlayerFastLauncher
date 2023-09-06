from pathlib import Path

import i18n
from lib.DGPSessionV2 import DgpSessionV2, DMMAlreadyRunningException


class DgpSessionWrap(DgpSessionV2):
    @staticmethod
    def read_cookies(path: Path) -> DgpSessionV2:
        try:
            return DgpSessionV2.read_cookies(path)
        except DMMAlreadyRunningException as e:
            raise DMMAlreadyRunningException(i18n.t("app.lib.dmm_already_running")) from e
