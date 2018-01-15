#!/usr/bin/env python3
# physics.py
import math

__author__ = 'Seth Tinglof'
__version__ = '1.0'


class Entity:
    """
    Entities are objects that have a position and an image and can move.  They are meant to be displayed.
    Entity is not meant to be instantiated.
    """
    def __init__(self, x_pos, y_pos):
        """
        Create a new Entity object with an x position and a y position.  The Entity's initial hit box
        is set to the point (0, 0).
        :param x_pos: horizontal coordinate of Entity.
        :param y_pos: vertical coordinate of Entity.
        :return: self
        """
        self.x_pos = x_pos
        self.y_pos = y_pos

        self.x_hit_max = 0
        self.x_hit_min = 0
        self.y_hit_max = 0
        self.y_hit_min = 0

    def get_image(self):
        """
        Gets the image for this entity.  Must be overriden in a subclass to be used.
        :return: Image for this entity.
        """
        return

    def move(self):
        """
        Performs default move action for this entity.  Must be overriden in a subclass to be used.
        :return: None
        """
        return

    def collision_test(self, entity):
        """
        Tests if this and another entity have collided based on their hit boxes.
        :param entity: The other entity that is being tested for a collision.
        :return: True if self collided with entity, else false.
        """
        if self.x_hit_min <= entity.x_hit_max\
                and self.x_hit_max >= entity.x_hit_min\
                and self.y_hit_min <= entity.y_hit_max\
                and self.y_hit_max >= entity.y_hit_min:
            return True
        else:
            return False


class TrueCoordinates(Entity):
    """
    TrueCoordinates extends Entity because it is meant to be displayed with a position.  TrueCoordinates store
    position in a float that can be turned back into an integer for precise movement.  TrueCoordinates is not meant
    to be instantiated.
    """
    def __init__(self, x_pos, y_pos):
        """
        Create a new TrueCoordinates object with an x position and a y position.
        :param x_pos: horizontal coordinate of TrueCoordinates.
        :param y_pos: vertical coordinate of TrueCoordinates.
        :return: self
        """
        Entity.__init__(self, x_pos, y_pos)
        self.true_x_pos = x_pos
        self.true_y_pos = y_pos

    def set_integer_position(self):
        """
        Sets the integer display position of the TrueCoordinates object based on the objects float coordinates.
        :return: None
        """
        self.x_pos = int(self.true_x_pos)
        self.y_pos = int(self.true_y_pos)

    def shift_position(self, x_shift, y_shift):
        """
        Shifts the floating point and integer coordinates of the TrueCoordinates object based from its current position.
        The shift is based on a grid where Y increases in the vertical direction and X increases in the right direction.
        :param x_shift: Amount the x position is shifted in the positive x direction.
        :param y_shift: Amount the y position is shifted in the positive y direction.
        :return: None
        """
        self.true_x_pos += x_shift
        self.true_y_pos -= y_shift     # Subtraction because movement is in first quadrant of an X, Y Coordinate plane.
        self.set_integer_position()


class Flying(TrueCoordinates):
    """
    Flying objects can undergo acceleration and are affected by gravity and a drag.  This extends TrueCoordinates in
    order to save a precises position when moving at non-integer speeds and at angles.  Flying is not meant to be
    instantiated and should be extended.
    """
    GRAVITY_CONSTANT = .15             # Value determines the acceleration due to gravity of all flying objects

    def __init__(self, x_pos, y_pos):
        """
        Creates a new Flying object with a horizontal and vertical position.
        :param x_pos: horizontal position of Flying
        :param y_pos: vertical position of Flying
        :return: self
        """
        TrueCoordinates.__init__(self, x_pos, y_pos)
        self.x_velocity = 0
        self.y_velocity = 0

    def accelerate(self, magnitude, angle):
        """
        Accelerates Flying object in the direction specified with the magnitude specified.
        :param magnitude: magnitude of acceleration or the speed increase in direction of the passed angle.
        :param angle: angle of acceleration.
        :return: None
        """
        self.x_velocity += magnitude * math.cos(angle)
        self.y_velocity += magnitude * math.sin(angle)

    def move(self, frame_length):
        """
        moves the Flying object according to its current velocity.
        :return: None
        """
        self.shift_position(self.x_velocity * frame_length * 60, self.y_velocity * frame_length * 60)

    def drag(self, drag_coefficient):
        """
        Causes the Flying to slow down; amount that the Flying slows down is proportional to the speed it is moving.
        :param drag_coefficient: number from 0 to 1, the lower the drag coefficient the larger the drag is.
        :return: None
        """
        self.x_velocity *= drag_coefficient
        self.y_velocity *= drag_coefficient

    def gravity(self):
        """
        Causes the Flying to accelerate downwards, all Flyings undergo the same acceleration due to gravity.
        :return: None
        """
        self.y_velocity -= self.GRAVITY_CONSTANT

    def get_angle(self):
        """
        Gets the angle that this Flying is currently moving.
        :return: The angle that the player is currently moving.
        """
        math.atan2(self.y_velocity, self.x_velocity)
