from dataclasses import dataclass
from typing import Annotated

from epublib.xml_element import XMLAttribute, XMLElement


@dataclass(kw_only=True)
class WithProperties(XMLElement):
    """Mixin for XMLElements with a properties attribute."""

    properties: Annotated[list[str] | None, XMLAttribute()] = None

    def add_property(self, prop: str) -> None:
        """
        Add a property to this item, if not already present.

        Args:
            prop: The property to add.
        """
        if self.properties is None:
            self.properties = []
        if prop not in self.properties:
            self.properties.append(prop)

        self.update_tag("properties", self.properties)

    def has_property(self, prop: str) -> bool:
        """
        Returns whether this item has the given property.

        Args:
            prop: The property to check for.
        """
        if self.properties is None:
            return False
        return prop in self.properties

    def remove_property(self, prop: str) -> None:
        """
        Remove the given property from this item, if present.

        Args:
            prop: The property to remove.
        """
        if self.properties is None:
            return
        try:
            self.properties.remove(prop)
        except ValueError:
            pass

        if not self.properties:
            self.properties = None

        self.update_tag("properties", self.properties)
