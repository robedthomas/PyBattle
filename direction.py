""" Contains the Direction class.
"""
from enum import Enum


class Direction(Enum):
    """ A cardinal direction.
    """
    north = 0
    east = 1
    south = 2
    west = 3

    def get_right(self):
        """ Returns the Direction to the right (clockwise) of this one.
        """
        if self is Direction.north:
            return Direction.east
        if self is Direction.east:
            return Direction.south
        if self is Direction.south:
            return Direction.west
        if self is Direction.west:
            return Direction.north

    def get_left(self):
        """ Returns the Direction to the left (counter-clockwise) of this one.
        """
        if self is Direction.north:
            return Direction.west
        if self is Direction.east:
            return Direction.north
        if self is Direction.south:
            return Direction.east
        if self is Direction.west:
            return Direction.south

    def get_behind(self):
        """ Returns the Direction behind this one.
        """
        if self is Direction.north:
            return Direction.south
        if self is Direction.east:
            return Direction.west
        if self is Direction.south:
            return Direction.north
        if self is Direction.west:
            return Direction.east

    def get_from_relative(self, relative_direction):
        """ Returns the Direction in the given relative direction from this one.
        """
        if relative_direction is RelativeDirection.front:
            return self
        if relative_direction is RelativeDirection.right:
            return self.get_right()
        if relative_direction is RelativeDirection.back:
            return self.get_behind()
        if relative_direction is RelativeDirection.left:
            return self.get_left()


class RelativeDirection(Enum):
    """ A direction relative to a unit.
    """
    front = 0
    right = 1
    back = 2
    left = 3

    @staticmethod
    def direction_from(from_this, to_this):
        """ Determines the relative direction from something facing one
            absolute direction to something facing another absolute direction.

            Positional arguments:
            from_this -- Direction of the object running into the second object
            to_this -- Direction of the second object
        """
        if from_this is to_this:
            return RelativeDirection.back
        if from_this.get_behind() is to_this:
            return RelativeDirection.front
        if from_this.get_left() is to_this:
            return RelativeDirection.left
        if from_this.get_right() is to_this:
            return RelativeDirection.right
