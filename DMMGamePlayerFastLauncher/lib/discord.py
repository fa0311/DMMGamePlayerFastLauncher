import logging
import time

import i18n
from pypresence import Presence
from static.config import DiscordConfig


def start_rich_presence(pid: int, id: str, title: str):
    try:
        RPC = Presence(DiscordConfig.CLIENT_ID)
        RPC.connect()
        RPC.update(
            name=title,
            state=i18n.t("app.title"),
            pid=pid,
            start=int(time.time()),
            large_image=f"https://media.games.dmm.com/freegame/client/{id}/200.gif",
        )
    except Exception as e:
        logging.error(f"Failed to start rich presence: {e}")
