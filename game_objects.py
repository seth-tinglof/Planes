#!/usr/bin/env python3
# game_objects.py
from physics import *
from PIL import Image, ImageTk
from math import degrees, pi, atan2, sin, cos
from random import randrange

__author__ = 'Seth Tinglof'
__version__ = '1.0'

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

TITLE_IMAGE = Image.open("Instructions.png")

PLAYER_IMAGE = Image.open("player_plane.png")
PLAYER_SPEED = .5
PLAYER_TURN_ANGLE = pi / 60

ENEMY_IMAGE = Image.open("enemy_plane.png")
ENEMY_SPEED = .4

BULLET_IMAGE = Image.open("bullet.png")
BULLET_SPEED = 8

CLOUD_IMAGE = Image.open("cloud.png")

# Method removed, but kept in-case it is needed later.
# def rotate_pil(image, angle):
#     angle = degrees(angle)
#     start_size = image.size
#     image_string = image.convert('RGBA')
#     rotated_image_string = image_string.rotate(angle, expand=0).resize(start_size)
#     rotated_image = Image.new('RGBA', start_size, (255, 255, 255, 0))
#     rotated_image.paste(rotated_image_string, (0, 0), rotated_image_string)
#     return rotated_image


def rotate_pil(image, angle):
    """
    Rotates a PIL image object.
    :param image: PIL image to be rotated.
    :param angle: Angle of rotations counter-clockwise in radians.
    :return: New rotated PIL image.
    """
    return image.rotate(degrees(angle))


def get_title_image():
    global tk_title_image
    tk_title_image = ImageTk.PhotoImage(TITLE_IMAGE)
    return tk_title_image


def two_tuple_subtraction(t_one, t_two):
    """
    Subtracts the corresponding values of one 2-tuple from another 2-tuple.
    :param t_one: Tuple with size two with starting values.
    :param t_two: Tuple with size two with values that will be subtracted from t-one.
    :return: Tuple with size two that contains the difference between each of the values in the param tuples.
    """
    return t_one[0] - t_two[0], t_one[1] - t_two[1]


class Player(Flying):
    """
    The player's plane in the game.  The player has a position and has a velocity.  The player also has a tkinter
    compatible image for its plane.
    """
    def __init__(self, x_pos, y_pos):
        """
        Creates a new player object with starting coordinates.
        :param x_pos: The player's starting X coordinate.
        :param y_pos: The player's starting Y coordinate.
        :return: self
        """
        Flying.__init__(self, x_pos, y_pos)
        self.image = PLAYER_IMAGE
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.angle = 0

    def get_image(self):
        """
        Creates the player's tkinter compatible image.
        :return: A tkinter compatible image for the player.
        """
        self.tk_image = ImageTk.PhotoImage(self.image)
        return self.tk_image

    def rotate_player(self):
        """
        Rotates the player's image to match the player's current angle.
        :return: None
        """
        self.image = rotate_pil(PLAYER_IMAGE, self.angle)

    def speed_up(self):
        """
        Accelerates the player in the direction that it is facing.
        :return: None
        """
        self.accelerate(PLAYER_SPEED, self.angle)

    def set_hit_box(self):
        """
        Sets the hit box based on current position.
        :return: None
        """
        self.x_hit_max = self.x_pos + 10
        self.x_hit_min = self.x_pos - 10
        self.y_hit_max = self.y_pos + 10
        self.y_hit_min = self.y_pos - 10


class Background:
    """
    Sky background to the game, used to calculate the placement of the clouds surrounding the player and returns the
    image for those clouds.
    """

    #######################################################################
    # Tuples with positions of cloud when the player is at position (0,0) #
    #######################################################################
    CLOUD_ONE = (0, 0)
    CLOUD_TWO = (SCREEN_WIDTH + 300, 0)
    CLOUD_THREE = (SCREEN_WIDTH + 300, SCREEN_HEIGHT + 300)
    CLOUD_FOUR = (0, SCREEN_HEIGHT + 300)

    def __init__(self):
        """
        Creates a new background object.
        :return: self
        """
        self.image = CLOUD_IMAGE
        self.image_tk = ImageTk.PhotoImage(self.image)

    def get_image(self):
        """
        :return: A tkinter compatible image for the cloud.
        """
        return self.image_tk

    def get_cloud_positions(self, player_x, player_y):
        """
        Calculates where the clouds should be drawn on the background and returns the four positions as a tuple
        size four with a tuple size two in each index, each of which contain and X coordinate and a Y coordinate.
        :param player_x: The player's current X coordinate position.
        :param player_y: The player's current Y coordinate position.
        :return: A 4-tuple of 2-tuples containing the positions that the clouds should be displayed at.
        """
        player_x %= SCREEN_WIDTH + 300
        player_y %= SCREEN_HEIGHT + 300
        if player_x < 0:
            player_x += SCREEN_WIDTH + 300
        if player_y < 0:
            player_y += SCREEN_HEIGHT + 300
        player_pos = (player_x, player_y)
        return (two_tuple_subtraction(self.CLOUD_ONE, player_pos),
                two_tuple_subtraction(self.CLOUD_TWO, player_pos),
                two_tuple_subtraction(self.CLOUD_THREE, player_pos),
                two_tuple_subtraction(self.CLOUD_FOUR, player_pos))


class Enemy(Flying):
    """
    The Enemy's plane in the game.  The Enemy has a position and has a velocity and chases the player.
    Enemy also also has a tkinter compatible image for its plane.
    """
    def __init__(self, x_pos, y_pos):
        """
        Creates a new Enemy object.
        :param x_pos: Starting X coordinate of the Enemy.
        :param y_pos: Starting Y coordinate of the Enemy.
        :return: self
        """
        Flying.__init__(self, x_pos, y_pos)
        self.image = ENEMY_IMAGE
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.angle = 0                 # Angle in radians.
        self.last_shot_time = 0        # The last time at which this enemy shot.

    def chase_player(self, player_x, player_y):
        """
        Accelerates the Enemy in the direction of the player.
        :param player_x: The player's current X coordinate.
        :param player_y: The player's current Y coordinate
        :return: None
        """
        self.angle = atan2(self.y_pos - player_y, player_x - self.x_pos)
        self.accelerate(.4, self.angle)

    def rotate_enemy(self):
        """
        Rotates the enemy's image to match its current angle.
        :return: None
        """
        self.image = rotate_pil(ENEMY_IMAGE, self.angle)

    def get_image(self):
        """
        Creates a tkinter compatible image for this enemy.
        :return: A tkinter compatible image of the enemy.
        """
        self.tk_image = ImageTk.PhotoImage(self.image)
        return self.tk_image

    def set_hit_box(self):
        """
        Sets the hit box based on current position.
        :return: None
        """
        self.x_hit_max = self.x_pos + 10
        self.x_hit_min = self.x_pos - 10
        self.y_hit_max = self.y_pos + 10
        self.y_hit_min = self.y_pos - 10


def create_enemy_semi_random_position(player_x, player_y):
    """
    Creates a new enemy object with a semi-random position near but not too near the player.
    :param player_x: The player's current X coordinate position.
    :param player_y: The player's current Y coordinate position.
    :return:
    """
    distance = randrange(750, 1000)
    angle = randrange(0, 360) / 180 * pi
    return Enemy(int(player_x + distance * cos(angle)), int(player_y + distance * sin(angle)))


class Bullet(Flying):
    """
    A bullet that either the player or the enemy can fire at the other.  Has an angle, a velocity, and a
    tkinter compatible image.
    """
    def __init__(self, x_pos, y_pos, starting_x_velocity, starting_y_velocity, angle, time, team):
        """
        A new Bullet object.
        :param x_pos: Bullet's starting X coordinate.
        :param y_pos: Bullet's starting Y coordinate.
        :param starting_x_velocity: The initial X velocity of the bullet.
        :param starting_y_velocity: The initial Y velocity of the bullet.
        :param angle: The angle that the bullet is fired at.
        :param time: The time that the bullet is created at.
        :param team: True if the player fired the bullet, False if the enemy fired it.
        :return: self
        """
        Flying.__init__(self, x_pos, y_pos)
        self.image = rotate_pil(BULLET_IMAGE, angle)
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.creation_time = time
        self.x_velocity = BULLET_SPEED * cos(angle) + starting_x_velocity
        self.y_velocity = BULLET_SPEED * sin(angle) + starting_y_velocity
        self.team = team

    def get_image(self):
        """
        :return: A tkinter compatible image for the bullet.
        """
        return self.tk_image

    def set_hit_box(self):
        """
        Sets the hit box based on current position.
        :return: None
        """
        self.x_hit_max = self.x_pos + 8
        self.x_hit_min = self.x_pos - 8
        self.y_hit_max = self.y_pos + 8
        self.y_hit_min = self.y_pos - 8
