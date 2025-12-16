"""
SerpentUI - Modern Python UI Framework with React + NextUI
"""

__version__ = "2.0.0"

from .base import Component
from .app import SerpentApp, quick_app
from .ui import (
    UIBuilder, Button, Input, Card, CardHeader, CardBody, CardFooter,
    Modal, ModalContent, ModalHeader, ModalBody, ModalFooter,
    Table, Navbar, NavbarBrand, NavbarContent, NavbarItem,
    Dropdown, DropdownTrigger, DropdownMenu, DropdownItem,
    Avatar, Chip, Progress, Spinner, Switch, Tabs, Tab,
    Tooltip, Divider, Spacer, Terminal, Container, Grid,
    GridItem, Flex, Box, Div, Text, Heading, Link, Image,
    Row, Column, Page
)
from .utils import ui_component
from .wails import (
    MenuItem, WailsMenu, WailsDialog, WailsNotification,
    WailsWindow, WailsApp
)
