from typing import Dict, List, Optional
from .base import Component

# ============================================================================
# BUILDER PATTERN PARA CREAR UIS MÁS FÁCIL
# ============================================================================

class UIBuilder:
    """Builder para crear UIs de forma más intuitiva"""
    
    def __init__(self):
        self.components = []
    
    def add(self, component):
        """Agregar un componente"""
        self.components.append(component)
        return self
    
    def build(self):
        """Construir la UI"""
        return Container(children=self.components)


# ============================================================================
# NEXTUI COMPONENTS (Simplificados con valores por defecto)
# ============================================================================

class Button(Component):
    def __init__(self, text: str = "", **props):
        props.setdefault('color', 'primary')
        props.setdefault('variant', 'solid')
        props.setdefault('size', 'md')
        super().__init__(**props)
        if text:
            self.children = [text]
    
    def component_name(self) -> str:
        return "Button"


class Input(Component):
    def __init__(self, **props):
        props.setdefault('type', 'text')
        super().__init__(**props)
    
    def component_name(self) -> str:
        return "Input"


class Card(Component):
    def __init__(self, children=None, **props):
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "Card"


class CardHeader(Component):
    def __init__(self, children=None, **props):
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "CardHeader"


class CardBody(Component):
    def __init__(self, children=None, **props):
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "CardBody"


class CardFooter(Component):
    def __init__(self, children=None, **props):
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "CardFooter"


class Modal(Component):
    def __init__(self, children=None, **props):
        props.setdefault('isOpen', False)
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "Modal"


class ModalContent(Component):
    def __init__(self, children=None, **props):
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "ModalContent"


class ModalHeader(Component):
    def __init__(self, children=None, **props):
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "ModalHeader"


class ModalBody(Component):
    def __init__(self, children=None, **props):
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "ModalBody"


class ModalFooter(Component):
    def __init__(self, children=None, **props):
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "ModalFooter"


class Table(Component):
    def __init__(self, columns: List[Dict] = None, rows: List[Dict] = None, **props):
        super().__init__(columns=columns or [], rows=rows or [], **props)
    
    def component_name(self) -> str:
        return "Table"


class Navbar(Component):
    def __init__(self, children=None, **props):
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "Navbar"


class NavbarBrand(Component):
    def __init__(self, children=None, **props):
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "NavbarBrand"


class NavbarContent(Component):
    def __init__(self, children=None, **props):
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "NavbarContent"


class NavbarItem(Component):
    def __init__(self, children=None, **props):
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "NavbarItem"


class Dropdown(Component):
    def __init__(self, children=None, **props):
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "Dropdown"


class DropdownTrigger(Component):
    def __init__(self, children=None, **props):
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "DropdownTrigger"


class DropdownMenu(Component):
    def __init__(self, children=None, **props):
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "DropdownMenu"


class DropdownItem(Component):
    def __init__(self, children=None, **props):
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "DropdownItem"


class Avatar(Component):
    def __init__(self, **props):
        props.setdefault('size', 'md')
        super().__init__(**props)
    
    def component_name(self) -> str:
        return "Avatar"


class Chip(Component):
    def __init__(self, children=None, **props):
        props.setdefault('color', 'default')
        props.setdefault('variant', 'solid')
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "Chip"


class Progress(Component):
    def __init__(self, **props):
        props.setdefault('value', 0)
        props.setdefault('color', 'primary')
        super().__init__(**props)
    
    def component_name(self) -> str:
        return "Progress"


class Spinner(Component):
    def __init__(self, **props):
        props.setdefault('color', 'primary')
        props.setdefault('size', 'md')
        super().__init__(**props)
    
    def component_name(self) -> str:
        return "Spinner"


class Switch(Component):
    def __init__(self, **props):
        props.setdefault('isSelected', False)
        super().__init__(**props)
    
    def component_name(self) -> str:
        return "Switch"


class Tabs(Component):
    def __init__(self, children=None, **props):
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "Tabs"


class Tab(Component):
    def __init__(self, children=None, **props):
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "Tab"


class Tooltip(Component):
    def __init__(self, children=None, **props):
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "Tooltip"


class Divider(Component):
    def __init__(self, **props):
        super().__init__(**props)
    
    def component_name(self) -> str:
        return "Divider"


class Spacer(Component):
    def __init__(self, **props):
        props.setdefault('x', 0)
        props.setdefault('y', 0)
        super().__init__(**props)
    
    def component_name(self) -> str:
        return "Spacer"


class Terminal(Component):
    def __init__(self, **props):
        props.setdefault('title', 'Terminal')
        props.setdefault('height', '400px')
        props.setdefault('theme', 'dark')
        super().__init__(**props)
    
    def component_name(self) -> str:
        return "Terminal"


class Container(Component):
    def __init__(self, children=None, **props):
        props.setdefault('maxWidth', 'lg')
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "Container"


class Grid(Component):
    def __init__(self, children=None, **props):
        props.setdefault('cols', 12)
        props.setdefault('gap', 4)
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "Grid"


class GridItem(Component):
    def __init__(self, children=None, **props):
        props.setdefault('colSpan', 1)
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "GridItem"


class Flex(Component):
    def __init__(self, children=None, **props):
        props.setdefault('direction', 'row')
        props.setdefault('gap', 4)
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "Flex"


class Box(Component):
    def __init__(self, children=None, **props):
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "Box"


class Div(Component):
    def __init__(self, children=None, **props):
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "div"


class Text(Component):
    def __init__(self, content: str = "", **props):
        super().__init__(children=[content], **props)
    
    def component_name(self) -> str:
        return "p"


class Heading(Component):
    def __init__(self, content: str = "", level: int = 1, **props):
        super().__init__(children=[content], **props)
        self.level = level
    
    def component_name(self) -> str:
        return f"h{self.level}"


class Link(Component):
    def __init__(self, children=None, **props):
        props.setdefault('href', '#')
        super().__init__(children=children or [], **props)
    
    def component_name(self) -> str:
        return "a"


class Image(Component):
    def __init__(self, **props):
        props.setdefault('alt', '')
        super().__init__(**props)
    
    def component_name(self) -> str:
        return "img"


# ============================================================================
# FUNCIONES HELPER PARA CREAR UIS MÁS RÁPIDO
# ============================================================================

def Row(*children, **props):
    """Crear una fila horizontal fácilmente"""
    props['direction'] = 'row'
    return Flex(children=list(children), **props)


def Column(*children, **props):
    """Crear una columna vertical fácilmente"""
    props['direction'] = 'column'
    return Flex(children=list(children), **props)


def Page(*children, **props):
    """Crear una página completa fácilmente"""
    return Container(children=list(children), **props)
