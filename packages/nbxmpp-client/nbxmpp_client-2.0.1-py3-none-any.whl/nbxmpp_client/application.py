from gi.repository import Adw
from gi.repository import GLib

from .client import TestClient


class App(Adw.Application):
    def __init__(self) -> None:
        Adw.Application.__init__(self, application_id="org.nbxmpp.Client")
        GLib.set_prgname("org.nbxmpp.Client")

        self._window: TestClient | None = None
        self.connect("activate", self._on_activate)

    def _on_activate(self, app: Adw.Application) -> None:
        self.window = TestClient(application=app)
        self.window.present()

    def _on_close(self, window: TestClient) -> None:
        self.quit()
