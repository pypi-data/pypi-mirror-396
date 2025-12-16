import signal
import sys
from types import FrameType

from .application import App


def run() -> None:
    application = App()

    def sigint_cb(num: int, stack: FrameType | None) -> None:
        print(" SIGINT/SIGTERM received")  # noqa: T201
        application.quit()

    # ^C exits the application normally
    signal.signal(signal.SIGINT, sigint_cb)
    signal.signal(signal.SIGTERM, sigint_cb)
    if sys.platform != "win32":
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)

    application.run(sys.argv)
