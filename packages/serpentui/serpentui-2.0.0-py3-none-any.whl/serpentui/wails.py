from dataclasses import dataclass
from typing import Callable, List, Optional
from .base import Component
from .ui import Heading, Text, Page
from .app import SerpentApp

@dataclass
class MenuItem:
    """Representa un ítem de menú inspirado en Wails.

    El callback se ejecuta cuando se llama explícitamente a :meth:`trigger`.
    """

    label: str
    action: Optional[Callable] = None
    shortcut: Optional[str] = None

    def trigger(self):
        if callable(self.action):
            return self.action()
        return None


class WailsMenu:
    """Colección sencilla de items de menú para apps de escritorio."""

    def __init__(self, items: Optional[List[MenuItem]] = None):
        self.items: List[MenuItem] = items or []

    def add_item(self, item: MenuItem):
        self.items.append(item)
        return self

    def trigger(self, label: str):
        """Ejecuta el callback del item cuyo label coincide."""

        for item in self.items:
            if item.label == label:
                return item.trigger()
        raise ValueError(f"Menu item not found: {label}")


class WailsDialog:
    """APIs estilo Wails para mostrar diálogos desde Python puro."""

    @staticmethod
    def alert(message: str):
        print(f"[Dialog] {message}")
        return message

    @staticmethod
    def confirm(message: str, default: bool = True) -> bool:
        print(f"[Confirm] {message} -> {default}")
        return default

    @staticmethod
    def prompt(message: str, default: str = "") -> str:
        print(f"[Prompt] {message} -> {default}")
        return default


class WailsNotification:
    """Notificaciones simples estilo Wails."""

    @staticmethod
    def show(title: str, message: str):
        print(f"🔔 {title}: {message}")
        return message


@dataclass
class WailsWindow:
    """Ventana de alto nivel con configuración similar a Wails."""

    title: str = "SerpentUI x Wails"
    width: int = 1280
    height: int = 720
    resizable: bool = True
    background_color: str = "#0B1220"
    start_hidden: bool = False
    frameless: bool = False
    content: Optional[Component] = None

    def set_content(self, component: Component):
        self.content = component
        return self

    def to_serpent_app(self) -> "SerpentApp":
        """Convierte la ventana en una instancia de :class:`SerpentApp`."""

        app = SerpentApp(
            title=self.title,
            width=self.width,
            height=self.height,
            resizable=self.resizable,
        )
        if self.content:
            app.set_root(self.content)
        else:
            fallback = Page(
                Heading("Ventana vacía", level=2),
                Text("Usa set_content() para definir el layout"),
            )
            app.set_root(fallback)
        return app


class WailsApp:
    """App de escritorio compatible con la filosofía de Wails pero 100% Python."""

    def __init__(self, name: str = "SerpentUI Wails App"):
        self.name = name
        self.windows: List[WailsWindow] = []
        self.menus: List[WailsMenu] = []

    def add_window(self, window: WailsWindow):
        self.windows.append(window)
        return self

    def add_menu(self, menu: WailsMenu):
        self.menus.append(menu)
        return self

    def run(self, mode: str = "desktop", **kwargs):
        if not self.windows:
            raise ValueError("Define al menos una ventana con add_window().")

        main_window = self.windows[0]
        app = main_window.to_serpent_app()

        # No modificamos el HTML; mantenemos Python puro y delegamos al runner.
        app.run(mode=mode, **kwargs)
