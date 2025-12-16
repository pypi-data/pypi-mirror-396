"""Common helpers for flow layout."""

from abc import ABC, abstractmethod
from ibm_watsonx_data_integration.services.datastage.models.flow.dag import Node


class BoundingBox(ABC):
    """A bounding box for the flow layout."""

    def __init__(self, *, width: float = 0, height: float = 0, x: float = 0, y: float = 0) -> None:
        # POSITIONING IS ALWAYS RELATIVE TO PARENT
        """Initializes a bounding box."""
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.x_velocity = 0.0
        self.y_velocity = 0.0
        self.x_force = 0.0
        self.y_force = 0.0

    @abstractmethod
    def update_absolute_positions(self, parent_x: float, parent_y: float) -> None:
        """Update absolute positions."""
        pass

    def center_x(self) -> float:
        """Calculate center x."""
        return self.x + self.width / 2

    def center_y(self) -> float:
        """Calculate center y."""
        return self.y + self.height / 2

    def y_boundary_distance(self, other: "BoundingBox") -> float:
        """Calculate y boundary distance."""
        return min(
            abs(self.y - (other.y + other.height)),
            abs(other.y - (self.y + self.height)),
        )

    def get_x_from_center(self, center_x: float) -> float:
        """Get x from center x."""
        return center_x - self.width / 2

    def get_y_from_center(self, center_y: float) -> float:
        """Get y from center y."""
        return center_y - self.height / 2

    def add_force(self, x_force: float, y_force: float) -> None:
        """Add force."""
        self.x_force += x_force
        self.y_force += y_force

    def apply_forces(self) -> None:
        """Apply forces."""
        self.x_velocity += self.__clamp_magnitude(self.x_force, 60)
        self.y_velocity += self.__clamp_magnitude(self.y_force, 60)
        self.x_velocity *= 0.5
        self.y_velocity *= 0.5
        self.x_force = 0
        self.y_force = 0
        self.x += self.x_velocity
        self.y += self.y_velocity

    @staticmethod
    def __clamp_magnitude(val: float, magnitude: float) -> float:
        """Clamp magnitude."""
        if val > 0:
            return min(val, magnitude)
        return max(val, -magnitude)


class NodeBoundingBox(BoundingBox):
    """A node bounding box."""

    def __init__(self, node: Node, width: float = 0, height: float = 0) -> None:
        """Initializes a node bounding box."""
        super().__init__(width=width, height=height)
        self.node = node

    def update_absolute_positions(self, parent_x: float, parent_y: float) -> None:
        """Updates the absolute positions of node bounding box based on parent x and y."""
        self.node.metadata["x"] = round(parent_x + self.x)
        self.node.metadata["y"] = round(parent_y + self.y)
        self.node.metadata["width"] = round(self.width)
        self.node.metadata["height"] = round(self.height)


class GroupBoundingBox(BoundingBox):
    """A group bounding box."""

    def __init__(self, *, width: float = 0, height: float = 0, x: float = 0, y: float = 0) -> None:
        """Initializes a group bounding box."""
        super().__init__(width=width, height=height, x=x, y=y)
        self.children: list[BoundingBox] = []

    def center_within(self, other: BoundingBox) -> None:
        """Centers within a bounding box."""
        self.x = other.center_x() - self.width / 2
        self.y = other.center_y() - self.height / 2

    def update_absolute_positions(self, parent_x: float, parent_y: float) -> None:
        """Updates the absolute positions of group bounding box based on parent x and y."""
        for child in self.children:
            child.update_absolute_positions(parent_x + self.x, parent_y + self.y)

    def arrange_children_vertically(self, spacing: float = 0) -> None:
        """Arrange children vertically with the specified spacing."""
        y = self.y
        for child in self.children:
            child.y = y
            y += child.height + spacing
        self.height = y - self.y

    def arrange_children_horizontally(self, spacing: float = 0) -> None:
        """Arrange children horizontally with the specified spacing."""
        x = self.x
        for child in self.children:
            child.x = x
            x += child.width + spacing
        self.width = x - self.x

    def round(self) -> None:
        """Rounds the x, y, width, and height."""
        self.x = round(self.x)
        self.y = round(self.y)
        self.width = round(self.width)
        self.height = round(self.height)
