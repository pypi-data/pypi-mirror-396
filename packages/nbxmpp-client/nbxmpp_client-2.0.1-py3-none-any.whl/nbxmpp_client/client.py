from typing import Any
from typing import cast

import json
import logging
import os
import sys
import time
from enum import IntEnum
from pathlib import Path

import nbxmpp
from gi.repository import Adw
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import GtkSource
from nbxmpp.client import Client
from nbxmpp.const import ConnectionProtocol
from nbxmpp.const import ConnectionType
from nbxmpp.const import Mode
from nbxmpp.const import StreamError
from nbxmpp.http import HTTPSession
from nbxmpp.protocol import JID
from nbxmpp.structs import ProxyData
from nbxmpp.structs import StanzaHandler

from .util import at_the_end
from .util import scroll_to_end

logging.basicConfig(
    format="%(levelname)-9s: %(message)s", level="INFO", datefmt="%H:%M:%S"
)


class ProxyType(IntEnum):
    SOCKS5 = 0


class TestClient(Adw.ApplicationWindow):
    def __init__(self, application: Adw.Application) -> None:
        Adw.ApplicationWindow.__init__(
            self, title="Test Client for nbxmpp", application=application
        )
        self.set_default_size(1200, -1)

        self._build_gui()

        self._client = None
        self._create_paths()
        self._load_config()

    def _build_gui(self) -> None:
        toggle_pane_button = Gtk.ToggleButton()
        toggle_pane_button.set_icon_name("sidebar-show-symbolic")
        header_bar = Adw.HeaderBar()
        header_bar.pack_start(toggle_pane_button)

        self._xmpp_address = Adw.EntryRow(title="XMPP Address")
        self._password = Adw.PasswordEntryRow(title="Password")

        save_button = Gtk.Button.new_from_icon_name("document-save-symbolic")
        save_button.set_tooltip_text("Save all settings")
        save_button.connect("clicked", self._on_save_clicked)

        credentials_group = Adw.PreferencesGroup(title="Account Credentials")
        credentials_group.set_header_suffix(save_button)
        credentials_group.add(self._xmpp_address)
        credentials_group.add(self._password)

        type_model = Gtk.StringList.new(["SOCKS5"])
        self._proxy_type = Adw.ComboRow(title="Type")
        self._proxy_type.set_model(type_model)
        self._proxy_host = Adw.EntryRow(title="Host/IP")
        self._proxy_port = Adw.EntryRow(title="Port")
        self._proxy_username = Adw.EntryRow(title="Username")
        self._proxy_password = Adw.PasswordEntryRow(title="Password")

        proxy_expander = Adw.ExpanderRow(title="Proxy Settings")
        proxy_expander.add_row(self._proxy_type)
        proxy_expander.add_row(self._proxy_host)
        proxy_expander.add_row(self._proxy_port)
        proxy_expander.add_row(self._proxy_username)
        proxy_expander.add_row(self._proxy_password)

        proxy_group = Adw.PreferencesGroup(title="Proxy")
        proxy_group.add(proxy_expander)

        self._con_direct_tls = Gtk.Switch(valign=Gtk.Align.CENTER)
        con_direct_tls = Adw.ActionRow(title="DIRECT TLS")
        con_direct_tls.add_suffix(self._con_direct_tls)
        con_direct_tls.set_activatable_widget(self._con_direct_tls)

        self._con_start_tls = Gtk.Switch(valign=Gtk.Align.CENTER)
        con_start_tls = Adw.ActionRow(title="START TLS")
        con_start_tls.add_suffix(self._con_start_tls)
        con_start_tls.set_activatable_widget(self._con_start_tls)

        self._con_plain = Gtk.Switch(valign=Gtk.Align.CENTER)
        con_plain = Adw.ActionRow(title="PLAIN")
        con_plain.add_suffix(self._con_plain)
        con_plain.set_activatable_widget(self._con_plain)

        connection_type_group = Adw.PreferencesGroup(title="Connection Type")
        connection_type_group.add(con_direct_tls)
        connection_type_group.add(con_start_tls)
        connection_type_group.add(con_plain)

        self._con_tcp = Gtk.Switch(valign=Gtk.Align.CENTER)
        con_tcp = Adw.ActionRow(title="TCP")
        con_tcp.add_suffix(self._con_tcp)
        con_tcp.set_activatable_widget(self._con_tcp)

        self._con_websocket = Gtk.Switch(valign=Gtk.Align.CENTER)
        con_websocket = Adw.ActionRow(title="WEBSOCKET")
        con_websocket.add_suffix(self._con_websocket)
        con_websocket.set_activatable_widget(self._con_websocket)

        connection_protocol_group = Adw.PreferencesGroup(title="Connection Protocol")
        connection_protocol_group.add(con_tcp)
        connection_protocol_group.add(con_websocket)

        mode_model = Gtk.StringList.new(["Client", "Login", "Register", "Anonymous"])
        self._con_mode = Adw.ComboRow(title="Mode")
        self._con_mode.set_model(mode_model)

        connection_mode_group = Adw.PreferencesGroup(title="Connection Mode")
        connection_mode_group.add(self._con_mode)

        pref_page = Adw.PreferencesPage()
        pref_page.set_hexpand_set(True)
        pref_page.add(credentials_group)
        pref_page.add(proxy_group)
        pref_page.add(connection_type_group)
        pref_page.add(connection_protocol_group)
        pref_page.add(connection_mode_group)

        connect_button = Gtk.Button(label="Connect")
        connect_button.connect("clicked", self._on_connect_clicked)
        connect_button.get_style_context().add_class("suggested-action")
        disconnect_button = Gtk.Button(label="Disconnect")
        disconnect_button.connect("clicked", self._on_disconnect_clicked)
        disconnect_button.get_style_context().add_class("destructive-action")
        reconnect_button = Gtk.Button(label="Reconnect")
        reconnect_button.connect("clicked", self._on_reconnect_clicked)
        clear_button = Gtk.Button(label="Clear")
        clear_button.set_tooltip_text("Clear XML output window")
        clear_button.connect("clicked", self._on_clear_clicked)

        button_box = Gtk.Box(
            spacing=12,
            halign=Gtk.Align.CENTER,
            margin_start=24,
            margin_end=24,
            margin_bottom=24,
        )
        button_box.append(connect_button)
        button_box.append(disconnect_button)
        button_box.append(reconnect_button)
        button_box.append(clear_button)

        left_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        left_box.append(pref_page)
        left_box.append(button_box)

        self._xml_view = GtkSource.View()
        self._xml_view.set_editable(False)
        self._xml_view.set_monospace(True)
        self._xml_view.set_top_margin(6)
        self._xml_view.set_bottom_margin(6)
        self._xml_view.set_left_margin(6)
        self._xml_view.set_right_margin(6)
        tags = [
            "incoming",
            "outgoing",
        ]
        buffer_ = self._xml_view.get_buffer()
        for tag_name in tags:
            buffer_.create_tag(tag_name)

        source_manager = GtkSource.LanguageManager.get_default()
        lang = source_manager.get_language("xml")
        self._xml_view.get_buffer().set_language(lang)

        style_scheme_manager = GtkSource.StyleSchemeManager.get_default()
        dark = style_scheme_manager.get_scheme("solarized-dark")
        self._xml_view.get_buffer().set_style_scheme(dark)

        self._scrolled_win = Gtk.ScrolledWindow()
        self._scrolled_win.set_hexpand(True)
        self._scrolled_win.set_min_content_width(600)
        self._scrolled_win.set_child(self._xml_view)

        flap = Adw.Flap()
        flap.bind_property(
            "reveal-flap",
            toggle_pane_button,
            "active",
            GObject.BindingFlags.SYNC_CREATE | GObject.BindingFlags.BIDIRECTIONAL,
        )
        flap.set_separator(Gtk.Separator())
        flap.set_flap(left_box)
        flap.set_content(self._scrolled_win)

        self._toast_overlay = Adw.ToastOverlay()
        self._toast_overlay.set_child(flap)

        window_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        window_box.append(header_bar)
        window_box.append(self._toast_overlay)

        self.set_content(window_box)

    def _create_client(self) -> None:
        self._client = Client(log_context="TEST")
        self._client.set_domain(self.address.domain)
        self._client.set_username(self.address.localpart)
        self._client.set_resource("test")
        self._client.set_http_session(HTTPSession())

        proxy_host = self._proxy_host.get_text()
        if proxy_host:
            proxy_port = int(self._proxy_port.get_text())
            proxy_host = f"{proxy_host}:{proxy_port}"
            selected_proxy_type = cast(
                Gtk.StringObject, self._proxy_type.get_selected_item()
            )
            proxy = ProxyData(
                selected_proxy_type.get_string().lower(),
                proxy_host,
                self._proxy_username.get_text() or None,
                self._proxy_password.get_text() or None,
            )
            self._client.set_proxy(proxy)

        selected_con_mode = cast(Gtk.StringObject, self._con_mode.get_selected_item())
        con_mode = selected_con_mode.get_string()
        if con_mode == "Login":
            self._client.set_mode(Mode.LOGIN_TEST)
        elif con_mode == "Client":
            self._client.set_mode(Mode.CLIENT)
        elif con_mode == "Register":
            self._client.set_mode(Mode.REGISTER)
        elif con_mode == "Anonymous":
            self._client.set_mode(Mode.ANONYMOUS_TEST)
        else:
            raise ValueError("No mode selected")

        self._client.set_connection_types(self._get_connection_types())
        self._client.set_protocols(self._get_connection_protocols())

        self._client.set_password(self.password)

        self._client.subscribe("resume-failed", self._on_signal)
        self._client.subscribe("resume-successful", self._on_signal)
        self._client.subscribe("disconnected", self._on_signal)
        self._client.subscribe("connection-lost", self._on_signal)
        self._client.subscribe("connection-failed", self._on_signal)
        self._client.subscribe("connected", self._on_connected)

        self._client.subscribe("stanza-sent", self._on_stanza_sent)
        self._client.subscribe("stanza-received", self._on_stanza_received)

        self._client.register_handler(StanzaHandler("message", self._on_message))

    @property
    def password(self) -> str:
        return self._password.get_text()

    @property
    def address(self) -> JID:
        return JID.from_string(self._xmpp_address.get_text())

    def _on_signal(
        self, _client: Client, signal_name: str, *args: Any, **kwargs: Any
    ) -> None:
        logging.info("%s, Error: %s", signal_name, self._client.get_error())
        if signal_name == "disconnected":
            if self._client.get_error() is None:
                return
            domain, _error, _text = self._client.get_error()
            if domain == StreamError.BAD_CERTIFICATE:
                self._client.set_ignore_tls_errors(True)
                self._client.connect()

    def _on_connected(self, _client: Client, _signal_name: str) -> None:
        self.send_presence()

    def _on_message(self, _stream, stanza, _properties):
        logging.info("Message received")
        logging.info(stanza.getBody())

    def _on_stanza_sent(self, _stream, _signal_name, stanza):
        self._print_stanza(stanza, "outgoing")

    def _on_stanza_received(self, _stream, _signal_name, stanza):
        self._print_stanza(stanza, "incoming")

    def _print_stanza(self, stanza, direction: str) -> None:

        if isinstance(stanza, bytes):
            stanza = str(stanza)
        if not isinstance(stanza, str):
            stanza = stanza.__str__(fancy=True)

        is_at_the_end = at_the_end(self._scrolled_win)

        buffer_ = self._xml_view.get_buffer()
        end_iter = buffer_.get_end_iter()

        stanza = "<!-- {direction} {time} -->\n{stanza}\n\n".format(
            direction=direction.capitalize(), time=time.strftime("%c"), stanza=stanza
        )
        buffer_.insert_with_tags_by_name(end_iter, stanza, direction)

        if is_at_the_end:
            GLib.idle_add(scroll_to_end, self._scrolled_win)

    def _on_connect_clicked(self, _button: Gtk.Button) -> None:
        if self._client is not None:
            self._client.destroy()

        self._create_client()

        self._client.connect()

    def _on_disconnect_clicked(self, _button: Gtk.Button) -> None:
        if self._client is not None:
            self._client.disconnect()

    def _on_clear_clicked(self, _button: Gtk.Button) -> None:
        self._xml_view.get_buffer().set_text("")

    def _on_reconnect_clicked(self, _button: Gtk.Button) -> None:
        # TODO
        self._toast_overlay.add_toast(Adw.Toast.new("Not implemented"))

    def _get_connection_types(self) -> list[ConnectionType]:
        types: list[ConnectionType] = []
        if self._con_direct_tls.get_active():
            types.append(ConnectionType.DIRECT_TLS)
        if self._con_start_tls.get_active():
            types.append(ConnectionType.START_TLS)
        if self._con_plain.get_active():
            types.append(ConnectionType.PLAIN)
        return types

    def _get_connection_protocols(self) -> list[ConnectionProtocol]:
        protocols: list[ConnectionProtocol] = []
        if self._con_tcp.get_active():
            protocols.append(ConnectionProtocol.TCP)
        if self._con_websocket.get_active():
            protocols.append(ConnectionProtocol.WEBSOCKET)
        return protocols

    def _on_save_clicked(self, _button: Gtk.Button) -> None:
        data: dict[str, str | bool] = {}
        data["jid"] = self._xmpp_address.get_text()
        data["password"] = self._password.get_text()
        selected_proxy = cast(Gtk.StringObject, self._proxy_type.get_selected_item())
        data["proxy_type"] = selected_proxy.get_string()
        data["proxy_host"] = self._proxy_host.get_text()
        data["proxy_port"] = self._proxy_port.get_text()
        data["proxy_username"] = self._proxy_username.get_text()
        data["proxy_password"] = self._proxy_password.get_text()

        data["directtls"] = self._con_direct_tls.get_active()
        data["starttls"] = self._con_start_tls.get_active()
        data["plain"] = self._con_plain.get_active()
        data["tcp"] = self._con_tcp.get_active()
        data["websocket"] = self._con_websocket.get_active()

        path = self._get_config_dir() / "config"
        with path.open("w") as fp:
            json.dump(data, fp)

        self._toast_overlay.add_toast(Adw.Toast.new("Settings saved"))

    def _load_config(self) -> None:
        path = self._get_config_dir() / "config"
        if not path.exists():
            return

        with path.open("r") as fp:
            data = json.load(fp)

        self._xmpp_address.set_text(data.get("jid", ""))
        self._password.set_text(data.get("password", ""))

        stored_type = data.get("proxy_type", "SOCKS5")
        self._proxy_type.set_selected(ProxyType[stored_type].value)
        self._proxy_host.set_text(data.get("proxy_host", ""))
        self._proxy_port.set_text(data.get("proxy_port", ""))
        self._proxy_username.set_text(data.get("proxy_username", ""))
        self._proxy_password.set_text(data.get("proxy_password", ""))

        self._con_direct_tls.set_active(data.get("directtls", False))
        self._con_start_tls.set_active(data.get("starttls", False))
        self._con_plain.set_active(data.get("plain", False))
        self._con_tcp.set_active(data.get("tcp", False))
        self._con_websocket.set_active(data.get("websocket", False))

    @staticmethod
    def _get_config_dir() -> Path:
        if sys.platform == "win32":
            return Path(os.path.join(os.environ["appdata"], "nbxmpp"))

        expand = os.path.expanduser
        base = os.getenv("XDG_CONFIG_HOME")
        if base is None or base[0] != "/":
            base = expand("~/.config")
        return Path(os.path.join(base, "nbxmpp"))

    def _create_paths(self) -> None:
        path_ = self._get_config_dir()
        if not path_.exists():
            for parent_path in reversed(path_.parents):
                # Create all parent folders
                # don't use mkdir(parent=True), as it ignores `mode`
                # when creating the parents
                if not parent_path.exists():
                    logging.info("creating %s directory", parent_path)
                    parent_path.mkdir(mode=0o700)
            logging.info("creating %s directory", path_)
            path_.mkdir(mode=0o700)

    def send_presence(self) -> None:
        presence = nbxmpp.Presence()
        self._client.send_stanza(presence)
