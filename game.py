#!/usr/bin/env python3
# game.py
from game_objects import *
import time
from tkinter import Tk, Frame, Canvas, ALL, NW, Button
from pyglet import media
from random import randrange

__author__ = 'Seth Tinglof'
__version__ = '1.0'

MINIMUM_FRAME_LENGTH = 1 / 60
GAME_WIDTH = 1280
GAME_HEIGHT = 720

CENTER_X = GAME_WIDTH // 2
CENTER_Y = GAME_HEIGHT // 2

DELAY_BETWEEN_PLAYER_SHOTS = .5
DELAY_BETWEEN_ENEMY_SHOTS = 2.5
TIME_UNTIL_BULLETS_ARE_DELETED = 2

TIME_BETWEEN_ENEMY_SPAWNS = 6
MAX_ENEMIES = 5

PLAYER_DRAG = .97
ENEMY_DRAG = .95


class Game:
    """
    Logic and game loop for Planes game.
    """
    def __init__(self):
        """
        Creates a new Game object.
        :return: None
        """
        self.playing = True
        self.player = Player(0, 0)
        self.enemies = []
        self.bullets = []
        self.enemies_killed = 0    # count of enemies killed.
        self.current_time = time.time()
        self.last_time = self.current_time - MINIMUM_FRAME_LENGTH
        self.track_number = randrange(3)
        self.next_song_time = 0
        self.song = None
        self.music_player = None
        ###################################
        # Booleans control player actions #
        # Toggled by user's key presses   #
        ###################################
        self.turn_counter_clockwise = False
        self.turn_clockwise = False
        self.accelerate = False
        self.shoot = False

        self.last_player_shot_time = -DELAY_BETWEEN_PLAYER_SHOTS
        self.last_enemy_spawn_time = self.current_time

    def game_loop(self, current_time):
        """
        The main game loop.  Each time it is run, the game progresses one frame.
        :param current_time: The current time as a float in seconds.
        :return: None
        """
        self.last_time = self.current_time
        self.current_time = current_time
        self.player_move()
        self.enemy_move()

        # Bullets must be moved last so that all other hit boxes are set first
        self.move_bullets()

        self.music_check()

    def player_move(self):
        """
        Moves the player for one frame.
        :return: None
        """
        if self.turn_counter_clockwise:
            self.player.angle += PLAYER_TURN_ANGLE
            self.player.rotate_player()
        if self.turn_clockwise:
            self.player.angle -= PLAYER_TURN_ANGLE
            self.player.rotate_player()
        if self.accelerate:
            self.player.speed_up()
        if self.shoot and self.current_time - self.last_player_shot_time >= DELAY_BETWEEN_PLAYER_SHOTS:
            self.last_player_shot_time = self.current_time
            self.player_shoot()
            media.load("bullet.wav").play()
        self.player.drag(PLAYER_DRAG)
        self.player.move(self.current_time - self.last_time)
        self.player.gravity()
        self.player.set_hit_box()

    def move_bullets(self):
        """
        Moves the bullets for one frame.
        :return: None
        """
        for bullet in self.bullets:
            if self.current_time - bullet.creation_time >= TIME_UNTIL_BULLETS_ARE_DELETED:
                self.bullets.remove(bullet)
            bullet.move(self.current_time - self.last_time)
            bullet.set_hit_box()
            if not bullet.team and bullet.collision_test(self.player):
                self.music_player.pause()
                media.load("player_death.wav").play()
                self.playing = False
            for enemy in self.enemies:
                if bullet.team and bullet.collision_test(enemy):
                    self.enemies.remove(enemy)
                    self.enemies_killed += 1
                    media.load("enemy_death.wav").play()

    def enemy_move(self):
        """
        Moves the enemies for one frame.
        :return: None
        """
        if self.current_time - self.last_enemy_spawn_time >= TIME_BETWEEN_ENEMY_SPAWNS\
                and len(self.enemies) <= MAX_ENEMIES:
            self.last_enemy_spawn_time = self.current_time
            self.enemies.append(create_enemy_semi_random_position(self.player.x_pos, self.player.y_pos))
        for enemy in self.enemies:
            enemy.chase_player(self.player.x_pos, self.player.y_pos)
            enemy.drag(ENEMY_DRAG)
            enemy.rotate_enemy()
            enemy.move(self.current_time - self.last_time)
            enemy.set_hit_box()
            if self.current_time - enemy.last_shot_time >= DELAY_BETWEEN_ENEMY_SHOTS:
                enemy.last_shot_time = self.current_time
                self.enemy_shoot(enemy)
                media.load("bullet.wav").play()

    def player_shoot(self):
        """
        The player shoots a bullet.
        :return: None
        """
        self.bullets.append(Bullet(self.player.x_pos, self.player.y_pos,
                                   self.player.x_velocity, self.player.y_velocity,
                                   self.player.angle, self.current_time, True))

    def enemy_shoot(self, enemy):
        """
        An enemy shoots a bullet.
        :param enemy: The enemy that is firing.
        :return: None
        """
        self.bullets.append(Bullet(enemy.x_pos, enemy.y_pos,
                                   enemy.x_velocity, enemy.y_velocity,
                                   enemy.angle, self.current_time, False))

    def music_check(self):
        if self.current_time > self.next_song_time:
            self.track_number += 1
            self.play_song()

    def play_song(self):
        if self.track_number > 2:
            self.track_number = 1
        if self.track_number == 1:
            self.song = media.load("track_one.wav")
            self.music_player = self.song.play()
            self.next_song_time = self.current_time + 82
        elif self.track_number == 2:
            self.song = media.load("track_two.wav")
            self.music_player = self.song.play()
            self.next_song_time = self.current_time + 95


class Window:
    """
    Creates a tkinter window to display the planes game.
    """
    def __init__(self):
        """
        Creates a new window.
        :return: None
        """
        self.root = Tk()
        self.root.title("Planes!")
        self.frame = Frame(self.root, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
        self.frame.pack()
        self.root.resizable(False, False)
        self.canvas = Canvas(self.frame, width=SCREEN_WIDTH, height=SCREEN_HEIGHT, bg="#%02x%02x%02x" % (0, 135, 211))
        self.start_canvas = Canvas(self.frame, width=SCREEN_WIDTH, height=SCREEN_HEIGHT - 100)
        self.score_canvas = Canvas(self.frame, width=SCREEN_WIDTH, height=SCREEN_HEIGHT - SCREEN_HEIGHT // 8)
        self.root.after(0, self.instruction_screen)
        self.root.mainloop()

    def instruction_screen(self):
        """
        Displays the instructions to play the game.
        :return: None
        """
        self.start_canvas.pack()
        self.start_canvas.create_image(0, 0, image=get_title_image(), anchor=NW)
        self.start_canvas.update()
        button = Button(self.frame, text='continue')

        def button_hit():
            """
            Actions for when the player hits the 'continue' button.
            """
            self.start_canvas.pack_forget()
            button.pack_forget()
            self.start_game()

        button.configure(command=button_hit)
        button.pack()

    def start_game(self):
        """
        Starts a new game and runs the main game loop.
        :return: None
        """
        self.canvas.pack()
        self.game = Game()
        self.background = Background()
        self.player = self.game.player
        self.enemies = self.game.enemies
        self.bullets = self.game.bullets
        self.score = 0
        self.window_loop()

    def score_screen(self):
        """
        Displays the final score/game over screen with the plays kill count.
        :return: None
        """
        self.score_canvas.pack()
        self.score_canvas.create_text(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5, text="Game Over", font=("Calibri", 50))
        self.score_canvas.create_text(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                      text="You destroyed " + str(self.score) + " enemy planes.",
                                      font=("Calibri", 36))
        quit_button = Button(self.frame, text="Quit", command=quit)
        quit_button.pack(side='bottom')
        play_again_button = Button(self.frame, text="Play Again")

        def play_again():
            """
            Actions for when the player hits the 'play again' button.
            """
            play_again_button.pack_forget()
            quit_button.pack_forget()
            self.score_canvas.delete(ALL)
            self.score_canvas.pack_forget()
            self.start_game()
        play_again_button.configure(command=play_again)
        play_again_button.pack()

    def window_loop(self):
        """
        The main loop that runs after the window is created. Progresses and displays the game.
        :return:
        """
        self.setup_keybindings()
        current_time = time.time()
        next_time = current_time
        ##################
        # Main Game Loop #
        ##################
        while self.game.playing:
            current_time = time.time()
            if next_time - current_time > 0:
                time.sleep(next_time - current_time)
            next_time = current_time + MINIMUM_FRAME_LENGTH
            self.game.game_loop(current_time)
            self.update_canvas()
        #######################
        # Main Game Loop Ends #
        #######################
        self.score = self.game.enemies_killed
        self.canvas.pack_forget()
        self.score_screen()

    def setup_keybindings(self):
        """
        creates keybindings for the game.
        :return: None
        """
        self.root.bind("<KeyPress>", self.key_pressed)
        self.root.bind("<KeyRelease>", self.key_released)

    def key_pressed(self, event):
        """
        Actions for when a key is pressed.
        :param event: Key pressed event.
        :return: None
        """
        if event.keysym == "z":
            self.game.accelerate = True
        elif event.keysym == "Left":
            self.game.turn_counter_clockwise = True
        elif event.keysym == "Right":
            self.game.turn_clockwise = True
        elif event.keysym == 'x':
            self.game.shoot = True

    def key_released(self, event):
        """
        Action for when a key is released.
        :param event: Key released event.
        :return: None
        """
        if event.keysym == "z":
            self.game.accelerate = False
        elif event.keysym == "Left":
            self.game.turn_counter_clockwise = False
        elif event.keysym == "Right":
            self.game.turn_clockwise = False
        elif event.keysym == 'x':
            self.game.shoot = False

    def update_canvas(self):
        """
        Updates the images displayed on the canvas.
        :return: None
        """
        self.canvas.delete(ALL)
        self.display_clouds()
        self.canvas.create_image(CENTER_X, CENTER_Y, image=self.player.get_image())
        self.display_enemies()
        self.display_bullets()
        self.canvas.update()

    def display_clouds(self):
        """
        Displays the cloud images on the canvas.
        :return: None
        """
        clouds = self.background.get_cloud_positions(self.player.x_pos, self.player.y_pos)
        for cloud in clouds:
            self.canvas.create_image(cloud[0], cloud[1], image=self.background.get_image(), anchor=NW)

    def display_enemies(self):
        """
        Displays the enemy images on the canvas.
        :return: None
        """
        for enemy in self.enemies:
            self.canvas.create_image(enemy.x_pos - self.player.x_pos + CENTER_X,
                                     enemy.y_pos - self.player.y_pos + CENTER_Y,
                                     image=enemy.get_image())

    def display_bullets(self):
        """
        Displays the bullet images on the canvas.
        :return: None
        """
        for bullet in self.bullets:
            self.canvas.create_image(bullet.x_pos - self.player.x_pos + CENTER_X,
                                     bullet.y_pos - self.player.y_pos + CENTER_Y,
                                     image=bullet.get_image())
