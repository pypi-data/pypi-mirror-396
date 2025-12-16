import uuid
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union

class Component(ABC):
    """Base class for all SerpentUI components"""
    
    def __init__(self, **props):
        self.props = props
        self.children = props.pop('children', [])
        self.id = props.get('id', f"serpent_{uuid.uuid4().hex[:8]}")
        self._class = props.pop('className', props.pop('class_name', ''))
        if self._class:
            self.props['className'] = self._class
    
    @abstractmethod
    def component_name(self) -> str:
        """Return the React component name"""
        pass
    
    def to_dict(self) -> Dict:
        """Convert component to dictionary for React rendering"""
        children = self.children if isinstance(self.children, list) else [self.children]
        return {
            'type': self.component_name(),
            'props': {**self.props, 'id': self.id},
            'children': [
                child.to_dict() if isinstance(child, Component) else str(child)
                for child in children
            ]
        }
