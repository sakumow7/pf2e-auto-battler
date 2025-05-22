from typing import Tuple
from src.constants.game_constants import GRID_SIZE

class GridPosition:
    """
    Represents a position on the game grid.
    Handles grid-based positioning and calculations for movement and distance.
    
    Attributes:
        x: X coordinate on the grid
        y: Y coordinate on the grid
    """
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        if not isinstance(other, GridPosition):
            return False
        return self.x == other.x and self.y == other.y
    
    def distance_to(self, other: 'GridPosition') -> int:
        """Calculate grid distance (in squares) to another position"""
        return max(abs(self.x - other.x), abs(self.y - other.y))
    
    def get_pixel_pos(self) -> Tuple[int, int]:
        """Convert grid position to pixel coordinates"""
        return (self.x * GRID_SIZE, self.y * GRID_SIZE)
    
    def get_rect(self):
        """Get pygame rect for this position"""
        x, y = self.get_pixel_pos()
        return (x, y, GRID_SIZE, GRID_SIZE) 