import pygame
import math
import sys
import random
import time
import sqlite3
import tkinter as tk
from tkinter import messagebox

#
# Initialize Pygame
pygame.init()

db = sqlite3.connect("leaderboard.db")
dbc = db.cursor()
dbc.execute("create table if not exists leaderboard1 (player str, wins int, kills int)")
dbc.execute("create table if not exists accounts1 (username str, password str)")

def create_table():
    conn = sqlite3.connect("accounts.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
                        username TEXT PRIMARY KEY,
                        password TEXT)''')
    conn.commit()
    conn.close()

def register():
    global dbc
    def register_user():
        global dbc
        username = entry_new_user.get()
        password = entry_new_pass.get()
        if username and password:
            conn = sqlite3.connect("accounts.db")
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO accounts (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                messagebox.showinfo("Success", "Account created successfully!")
                register_window.destroy()
                dbc.execute("insert into leaderboard1 (player, kills, wins) values (?, ?, ?)", (username, 0, 0))
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Username already exists!")
            conn.close()
        else:
            messagebox.showerror("Error", "Fields cannot be empty!")

    register_window = tk.Toplevel()
    register_window.title("Register")
    tk.Label(register_window, text="Set Username:").pack()
    entry_new_user = tk.Entry(register_window)
    entry_new_user.pack()
    tk.Label(register_window, text="Set Password:").pack()
    entry_new_pass = tk.Entry(register_window, show="*")
    entry_new_pass.pack()
    tk.Button(register_window, text="Register", command=register_user).pack()

username_var = ""
password_var = ""
def login_popup():
    def login():
        global username_var, password_var
        username = entry_user.get()
        password = entry_pass.get()
        conn = sqlite3.connect("accounts.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM accounts WHERE username=? AND password=?", (username, password))
        result = cursor.fetchone()
        conn.close()
        if result:
            username_var, password_var = username, password
            messagebox.showinfo("Success", "Login successful!")
            login_window.destroy()
        else:
            messagebox.showerror("Error", "Invalid credentials!")

    login_window = tk.Tk()
    login_window.title("Login")

    tk.Label(login_window, text="Username:").pack()
    entry_user = tk.Entry(login_window)
    entry_user.pack()

    tk.Label(login_window, text="Password:").pack()
    entry_pass = tk.Entry(login_window, show="*")
    entry_pass.pack()

    tk.Button(login_window, text="Login", command=login).pack()
    tk.Button(login_window, text="Create Account", command=register).pack()

    login_window.mainloop()

create_table()

# Screen dimensions
WIDTH, HEIGHT = 1280, 720
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ENEMIES")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PLATFORM_COLOR = (150, 75, 0)
GRAY = (200, 200, 200)
CONFETTI_COLORS = [RED, BLUE, GREEN, (255, 165, 0)]

# Font settings
HEALTH_FONT = pygame.font.SysFont('trebuchems', 50)
WINNER_FONT = pygame.font.SysFont('comicsans', 100)
MENU_FONT = pygame.font.SysFont('impact', 50)
OPTION_FONT = pygame.font.SysFont('microsoftjhenghei', 30)
NAME_FONT = pygame.font.SysFont('trebuchems', 20)
INPUT_FONT = pygame.font.SysFont('microsoftjhenghei', 40)
SCORE_FONT = pygame.font.SysFont('microsoftjhenghei', 40)

# Player settings
PLAYER_WIDTH, PLAYER_HEIGHT = 30, 30
PLAYER_VEL = 5
DASH_VEL = 100  # Dash distance in pixels
DASH_COOLDOWN = 180  # Cooldown time in frames (3 seconds at 60 FPS)
BULLET_WIDTH, BULLET_HEIGHT = 7, 7
MAX_BULLETS = 5
GRAVITY = 0.5
JUMP_VEL = 12
MAX_HEALTH = 1000
CROSSHAIR_LENGTH = 30

# Platform settings
PLATFORMS = [
    pygame.Rect(100, 500, 300, 20),
    pygame.Rect(400, 400, 200, 20),
    pygame.Rect(250, 300, 300, 20),
    pygame.Rect(100, 200, 150, 20),
    pygame.Rect(600, 100, 200, 20),
    pygame.Rect(600, 200, 200, 20),
    pygame.Rect(600, 400, 200, 20),
    pygame.Rect(450, 600, 200, 20),
    pygame.Rect(250, 50, 200, 20)
]

# Gun settings
PRIMARIES = {
    "pistol": {"fire_rate": 10, "reload_time": 130, "ammo_capacity": 10, "bullet_speed": 15, "damage": 100},
    "rifle": {"fire_rate": 10, "reload_time": 160, "ammo_capacity": 100, "bullet_speed": 20, "damage": 25},
    "sniper": {"fire_rate": 150, "reload_time": 100, "ammo_capacity": 4, "bullet_speed": 25, "damage": 756},
    "machine gun": {"fire_rate": 1, "reload_time": 1000, "ammo_capacity": 500, "bullet_speed": 15, "damage": 5},
    "shotgun": {"fire_rate": 50, "reload_time": 80, "ammo_capacity": 1, "bullet_speed": 18, "damage": 100},

}


SECONDARIES = {
    "revolver": {"fire_rate": 60, "reload_time": 130, "ammo_capacity": 6, "bullet_speed": 15, "damage": 250},
    "uzi": {"fire_rate": 5, "reload_time": 160, "ammo_capacity": 50, "bullet_speed": 20, "damage": 30},
    "handgun": {"fire_rate": 150, "reload_time": 100, "ammo_capacity": 4, "bullet_speed": 25, "damage": 756},
}

MELEES = {
    "sword1": {"fire_rate": 100, "reload_time": 130, "ammo_capacity": 6, "bullet_speed": 1, "damage": 250},
    "sword2": {"fire_rate": 1, "reload_time": 1, "ammo_capacity": 1, "bullet_speed": 10, "damage": 1},
    "sword3": {"fire_rate": 150, "reload_time": 100, "ammo_capacity": 4, "bullet_speed": 1, "damage": 756},
}

UTILITIES = {
    "error 4041": {"fire_rate": 1, "reload_time": 1, "ammo_capacity": 1289739, "bullet_speed": 0, "damage": 1},
    "medkit": {"fire_rate": 100, "reload_time": 1000, "ammo_capacity": 1, "bullet_speed": 0, "damage": 9999},
}

GUNS = {
    "pistol": {"fire_rate": 10, "reload_time": 130, "ammo_capacity": 10, "bullet_speed": 15, "damage": 100},
    "rifle": {"fire_rate": 3, "reload_time": 160, "ammo_capacity": 100, "bullet_speed": 20, "damage": 20},
    "sniper": {"fire_rate": 150, "reload_time": 100, "ammo_capacity": 4, "bullet_speed": 25, "damage": 756},
    "machine gun": {"fire_rate": 1, "reload_time": 1000, "ammo_capacity": 500, "bullet_speed": 15, "damage": 5},
    "shotgun": {"fire_rate": 50, "reload_time": 80, "ammo_capacity": 1, "bullet_speed": 18, "damage": 100},
    "revolver": {"fire_rate": 60, "reload_time": 130, "ammo_capacity": 6, "bullet_speed": 15, "damage": 250},
    "uzi": {"fire_rate": 5, "reload_time": 160, "ammo_capacity": 50, "bullet_speed": 20, "damage": 30},
    "handgun": {"fire_rate": 30, "reload_time": 100, "ammo_capacity": 4, "bullet_speed": 25, "damage": 75},
    "sword1": {"fire_rate": 100, "reload_time": 130, "ammo_capacity": 6, "bullet_speed": 1, "damage": 250},
    "sword2": {"fire_rate": 5, "reload_time": 160, "ammo_capacity": 50, "bullet_speed": 1, "damage": 50},
    "sword3": {"fire_rate": 150, "reload_time": 100, "ammo_capacity": 4, "bullet_speed": 1, "damage": 756},
    "error 4041": {"fire_rate": 1, "reload_time": 1, "ammo_capacity": 1289739, "bullet_speed": 0, "damage": 5},
    "medkit": {"fire_rate": 100, "reload_time": 1000, "ammo_capacity": 1, "bullet_speed": 0, "damage": 999},
}

# Bullet class


class Bullet:
    def __init__(self, x, y, vel_x, vel_y, color, player):
        self.rect = pygame.Rect(x, y, BULLET_WIDTH, BULLET_HEIGHT)
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.color = color
        self.player = player

    def move(self):
        if not self.player.gun == "sniper":
            self.vel_y += 0.1  # Gravity effect
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect)


    # Dash Trail class


class DashTrail:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.alpha = 255  # Start fully opaque

    def update(self):
        self.alpha -= 5  # Decrease alpha for fading
        if self.alpha < 0:
            self.alpha = 0  # Clamp to 0


    # Player class


class Player:
    def __init__(self, x, y, color, name, gun):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.color = color
        self.name = name
        self.health = MAX_HEALTH
        self.bullets = []
        self.y_vel = 0
        self.is_jumping = False
        self.on_ground = False
        self.aim_direction = (1, 0)  # Default aiming right
        self.fire_rate_counter = 0
        self.reload_counter = 0
        self.selected_gun = 0
        self.guns_list = gun
        self.gun = gun[self.selected_gun]
        self.ammo = GUNS[self.gun]["ammo_capacity"]
        self.dash_cooldown = 0  # Cooldown for dashing
        self.dash_trails = []  # List to hold the dash trails
        self.cooldowns = {
            "1": 0,
            "2": 0,
            "3": 0,
            "4": 0
        }

    def switch_weapons(self):
        # blah blah blah code
        self.gun = self.guns_list[self.selected_gun]

    def change_cooldowns(self):
        pass
        # WHYME

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, win):
        # Draw the dash trails
        for trail in self.dash_trails:
            surface = pygame.Surface((self.width, self.height))
            surface.set_alpha(trail.alpha)  # Set the transparency
            surface.fill(self.color)  # Fill with player's color
            win.blit(surface, (trail.x, trail.y))  # Draw the trail
        pygame.draw.rect(win, self.color, self.rect)
        for bullet in self.bullets:
            bullet.draw(win)
        self.draw_crosshair(win)
        self.draw_reload_bar(win)
        self.draw_dash_cooldown_bar(win)
        name_text = NAME_FONT.render(self.name, 1, BLACK)
        win.blit(name_text, (self.x + self.width // 2 - name_text.get_width() // 2, self.y - 45))

    def draw_crosshair(self, win):
        # Calculate the crosshair endpoint based on direction
        if self.gun == "sniper":
            crosshair_x = self.x + self.width // 2 + 1000 * self.aim_direction[0]
            crosshair_y = self.y + self.height // 2 + 1000 * self.aim_direction[1]
            pygame.draw.line(win, RED, (self.x + self.width // 2, self.y + self.height // 2),
                             (crosshair_x, crosshair_y),
                             1)
            crosshair_x = self.x + self.width // 2 + CROSSHAIR_LENGTH * self.aim_direction[0]
            crosshair_y = self.y + self.height // 2 + CROSSHAIR_LENGTH * self.aim_direction[1]
            pygame.draw.line(win, BLACK, (self.x + self.width // 2, self.y + self.height // 2),
                             (crosshair_x, crosshair_y),
                             2)
        else:
            crosshair_x = self.x + self.width // 2 + CROSSHAIR_LENGTH * self.aim_direction[0]
            crosshair_y = self.y + self.height // 2 + CROSSHAIR_LENGTH * self.aim_direction[1]
        # Draw crosshair lines
            pygame.draw.line(win, BLACK, (self.x + self.width // 2, self.y + self.height // 2), (crosshair_x, crosshair_y),
                         2)

    def draw_reload_bar(self, win):
        a = list(self.guns_list)
        self.reload_counter = self.cooldowns[str(a.index(self.gun) + 1)]
        if self.reload_counter > 0:
            reload_bar_width = 60  # Width of the reload bar
            reload_bar_height = 10  # Height of the reload bar
            reload_progress = (self.reload_counter / GUNS[self.gun]["reload_time"]) * reload_bar_width
            reload_bar_x = self.x + (self.width // 2) - (reload_bar_width // 2)
            reload_bar_y = self.y - reload_bar_height - 5  # 5 pixels above the player
            # Draw the empty reload bar
            pygame.draw.rect(win, BLACK, (reload_bar_x, reload_bar_y, reload_bar_width, reload_bar_height))
            # Draw the filled part of the reload bar
            pygame.draw.rect(win, GREEN, (reload_bar_x, reload_bar_y, reload_progress, reload_bar_height))

    def draw_dash_cooldown_bar(self, win):
        if self.dash_cooldown > 0:
            cooldown_bar_width = 60  # Width of the cooldown bar
            cooldown_bar_height = 10  # Height of the cooldown bar
            cooldown_progress = (self.dash_cooldown / DASH_COOLDOWN) * cooldown_bar_width
            cooldown_bar_x = self.x + (self.width // 2) - (cooldown_bar_width // 2)
            cooldown_bar_y = self.y - cooldown_bar_height - 20  # 20 pixels above the player
            # Draw the empty cooldown bar
            pygame.draw.rect(win, BLACK, (cooldown_bar_x, cooldown_bar_y, cooldown_bar_width, cooldown_bar_height))
            # Draw the filled part of the cooldown bar in blue
            pygame.draw.rect(win, BLUE, (cooldown_bar_x, cooldown_bar_y, cooldown_progress, cooldown_bar_height))

    def dash(self):
        if self.dash_cooldown == 0:  # Only dash if cooldown is over
            self.x += DASH_VEL * self.aim_direction[0]  # Move along x-axis based on aim direction
            self.y += DASH_VEL * self.aim_direction[1]  # Move along y-axis based on aim direction
            self.dash_trails.append(DashTrail(self.x, self.y))  # Add a new dash trail
            self.dash_cooldown = DASH_COOLDOWN  # Reset cooldown

    def move(self, keys, left, right, up, aim_up, aim_down):
        if keys[left] and self.x - PLAYER_VEL > 0:  # Move left
            self.x -= PLAYER_VEL
            self.aim_direction = (-1, self.aim_direction[1])
        if keys[right] and self.x + PLAYER_VEL + self.width < WIDTH:  # Move right
            self.x += PLAYER_VEL
            self.aim_direction = (1, self.aim_direction[1])
        if keys[up] and not self.is_jumping and self.on_ground:  # Jump
            self.y_vel = -JUMP_VEL
            self.is_jumping = True
            self.on_ground = False

        # Handle dash
        if keys[pygame.K_LSHIFT] and self.color == RED:  # Player 1 dashes
            self.dash()
        if keys[pygame.K_o] and self.color == BLUE:  # Player 2 dashes
            self.dash()

        if keys[aim_up]:
            angle = math.atan2(self.aim_direction[1], self.aim_direction[0])
            if self.gun == "sniper":
                angle -= 0.01
            else:
                angle -= 0.05
            self.aim_direction = (math.cos(angle), math.sin(angle))
        elif keys[aim_down]:
            angle = math.atan2(self.aim_direction[1], self.aim_direction[0])
            if self.gun == "sniper":
                angle += 0.01
            else:
                angle += 0.05
            self.aim_direction = (math.cos(angle), math.sin(angle))

        self.y += self.y_vel
        self.y_vel += GRAVITY

        # Check for collision with platforms
        self.on_ground = False
        for platform in PLATFORMS:
            if self.y + self.height <= platform.y and self.y + self.height + self.y_vel >= platform.y and \
                    self.x + self.width > platform.x and self.x < platform.x + platform.width:
                self.y = platform.y - self.height
                self.y_vel = 0
                self.is_jumping = False
                self.on_ground = True

        if self.y + self.height >= HEIGHT:
            self.y = HEIGHT - self.height
            self.y_vel = 0
            self.is_jumping = False
            self.on_ground = True

    def move_bullets(self, opponent):
        for bullet in self.bullets[:]:  # Iterate over a copy of the list
            if not self.gun == "error 404":
                bullet.move()  # Move the bullet
            # Check for collision with the opponent
            if bullet.rect.colliderect(opponent.rect):
                opponent.health -= GUNS[self.gun]["damage"]  # Damage the opponent
                self.bullets.remove(bullet)  # Remove the bullet after hitting
            # Remove bullets that go off-screen
            elif (bullet.rect.x < 0 or bullet.rect.x > WIDTH or bullet.rect.y < 0 or bullet.rect.y > HEIGHT):
                self.bullets.remove(bullet)

    def update_dash_trails(self):
        for trail in self.dash_trails:
            trail.update()
        self.dash_trails = [trail for trail in self.dash_trails if trail.alpha > 0]

    def shoot(self):
        if self.fire_rate_counter == 0 and self.ammo > 0:
            bullet_vel_x = GUNS[self.gun]["bullet_speed"] * self.aim_direction[0]
            bullet_vel_y = GUNS[self.gun]["bullet_speed"] * self.aim_direction[1]
            if self.gun == "medkit":
                bullet_count = 1  # Number of bullets to fire
                spread_angle = 0.1  # Spread angle in radians
                for i in range(bullet_count):
                    angle_offset = spread_angle * (i - (bullet_count - 1) / 2)  # Spread bullets
                    bullet_vel_x_spread = bullet_vel_x * math.cos(angle_offset) - bullet_vel_y * math.sin(angle_offset)
                    bullet_vel_y_spread = bullet_vel_x * math.sin(angle_offset) + bullet_vel_y * math.cos(angle_offset)
                    if self.color == RED:
                        bullet = Bullet(self.x + self.width, self.y + self.height // 2 - BULLET_HEIGHT // 2,
                                        bullet_vel_x_spread, bullet_vel_y_spread, RED, self)
                    else:
                        bullet = Bullet(self.x, self.y + self.height // 2 - BULLET_HEIGHT // 2, bullet_vel_x_spread,
                                        bullet_vel_y_spread, BLUE, self)
                    self.bullets.append(bullet)
                    if self.health < 250:
                        self.health += 750
                    else:
                        self.health = 1000
            elif self.gun == "shotgun":
                bullet_count = 5  # Number of bullets to fire
                spread_angle = 0.1  # Spread angle in radians
                for i in range(bullet_count):
                    angle_offset = spread_angle * (i - (bullet_count - 1) / 2)  # Spread bullets
                    bullet_vel_x_spread = bullet_vel_x * math.cos(angle_offset) - bullet_vel_y * math.sin(angle_offset)
                    bullet_vel_y_spread = bullet_vel_x * math.sin(angle_offset) + bullet_vel_y * math.cos(angle_offset)
                    if self.color == RED:
                        bullet = Bullet(self.x + self.width, self.y + self.height // 2 - BULLET_HEIGHT // 2,
                                        bullet_vel_x_spread, bullet_vel_y_spread, RED, self)
                    else:
                        bullet = Bullet(self.x, self.y + self.height // 2 - BULLET_HEIGHT // 2, bullet_vel_x_spread,
                                        bullet_vel_y_spread, BLUE, self)
                    self.bullets.append(bullet)
            else:
                if self.color == RED:
                    bullet = Bullet(self.x + self.width, self.y + self.height // 2 - BULLET_HEIGHT // 2, bullet_vel_x,
                                    bullet_vel_y, RED, self)
                else:
                    bullet = Bullet(self.x, self.y + self.height // 2 - BULLET_HEIGHT // 2, bullet_vel_x, bullet_vel_y,
                                    BLUE, self)
                self.bullets.append(bullet)
            self.ammo -= 1
            self.fire_rate_counter = GUNS[self.gun]["fire_rate"]
            if self.ammo == 0:
                a = list(self.guns_list)
                self.cooldowns[str(a.index(self.gun)+1)] = GUNS[self.gun]["reload_time"]
                print(self.cooldowns)

    def update_fire_rate(self):
        a = list(self.guns_list)
        if self.fire_rate_counter > 0:
            self.fire_rate_counter -= 1
        for i in self.cooldowns:
            self.cooldowns[i] -= 1 if self.cooldowns[i] > 0 else 0
        print(self.cooldowns)
        if self.cooldowns[str(a.index(self.gun)+1)] < 1:
            self.ammo = GUNS[self.gun]["ammo_capacity"]

    def update_cooldowns(self):
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1

    def reset(self):
        self.x = self.start_x
        self.y = self.start_y
        self.health = MAX_HEALTH
        self.bullets = []
        self.y_vel = 0
        self.is_jumping = False
        self.on_ground = False
        self.aim_direction = (1, 0)
        self.fire_rate_counter = 0
        for i in self.cooldowns:
            self.cooldowns[i] = 0
        self.ammo = GUNS[self.gun]["ammo_capacity"]
        self.dash_cooldown = 0


    # Draw health bars, players, and platforms


def draw_window(player1, player2, player1_wins, player2_wins):
    win.fill(WHITE)
    # Draw health bars
    health_bar_width = 200
    health_bar_height = 20
    health_bar_padding = 10
    # Player 1 health bar
    pygame.draw.rect(win, RED, (
        health_bar_padding, health_bar_padding, (player1.health / MAX_HEALTH) * health_bar_width, health_bar_height))
    pygame.draw.rect(win, BLACK, (health_bar_padding, health_bar_padding, health_bar_width, health_bar_height), 2)
    # Player 2 health bar
    pygame.draw.rect(win, BLUE, (
        WIDTH - health_bar_width - health_bar_padding, health_bar_padding,
        (player2.health / MAX_HEALTH) * health_bar_width,
        health_bar_height))
    pygame.draw.rect(win, BLACK, (
        WIDTH - health_bar_width - health_bar_padding, health_bar_padding, health_bar_width, health_bar_height), 2)
    # Draw platforms
    for platform in PLATFORMS:
        pygame.draw.rect(win, PLATFORM_COLOR, platform)
    # Draw players
    player1.draw(win)
    player2.draw(win)
    # Draw score
    score_text = SCORE_FONT.render(f"{player1_wins} - {player2_wins}", 1, BLACK)
    win.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 10))
    pygame.display.update()


    # Handle bullet movement and collision


def handle_bullets(player1, player2):
    player1.move_bullets(player2)
    player2.move_bullets(player1)


    # Display winner text and run animation


def draw_winner(text):
    for _ in range(100):  # Number of frames for animation
        win.fill(WHITE)
        draw_text = WINNER_FONT.render(text, 1, BLACK)
        win.blit(draw_text, (WIDTH // 2 - draw_text.get_width() // 2, HEIGHT // 2 - draw_text.get_height() // 2))
        # Draw confetti
        for _ in range(50):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            pygame.draw.circle(win, random.choice(CONFETTI_COLORS), (x, y), 5)
        pygame.display.update()
        pygame.time.delay(50)


    # Display start menu

def fetch_leaderboard():
    conn = sqlite3.connect("leaderboard.db")
    cursor = conn.cursor()
    cursor.execute("SELECT player, kills, wins FROM leaderboard1 ORDER BY wins DESC, kills DESC LIMIT 5")
    data = cursor.fetchall()
    conn.close()
    return data

MENU_FONT = pygame.font.Font(None, 48)
OPTION_FONT = pygame.font.Font(None, 32)
LEADERBOARD_FONT = pygame.font.Font(None, 24)

def draw_start_menu():
    win.fill(BLACK)

    # Title
    title_text = MENU_FONT.render(" - E N E M I E S - ", True, WHITE)
    win.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

    # Instructions
    instructions = [
        "Press ENTER to Start Game",
        "Press ESC to Quit"
    ]
    for i, instruction in enumerate(instructions):
        text = OPTION_FONT.render(instruction, True, WHITE)
        win.blit(text, (WIDTH // 2 - text.get_width() // 2, 150 + i * 50))

    # Draw Leaderboard
    leaderboard_data = fetch_leaderboard()
    leaderboard_title = LEADERBOARD_FONT.render("Leaderboard (Top 5)", True, WHITE)
    win.blit(leaderboard_title, (WIDTH // 2 - leaderboard_title.get_width() // 2, 280))

    y_offset = 310
    for rank, (username, kills, wins) in enumerate(leaderboard_data, start=1):
        entry_text = LEADERBOARD_FONT.render(f"{rank}. {username} - Kills: {kills}, Wins: {wins}", True, WHITE)
        win.blit(entry_text, (WIDTH // 2 - entry_text.get_width() // 2, y_offset))
        y_offset += 25

    pygame.display.update()



def draw_text_input(prompt, input_text):
    win.fill(WHITE)
    prompt_text = INPUT_FONT.render(prompt, 1, BLACK)
    input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)
    win.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 - 100))
    pygame.draw.rect(win, BLACK, input_box, 2)
    input_surface = INPUT_FONT.render(input_text, 1, BLACK)
    win.blit(input_surface, (input_box.x + 5, input_box.y + 5))
    pygame.display.update()


def draw_gun_selection(num):
    win.fill(WHITE)
    if num == 1:
        title_text = INPUT_FONT.render("Select Primary for Player", 1, BLACK)
    elif num == 2:
        title_text = INPUT_FONT.render("Select Secondary for Player", 1, BLACK)
    elif num == 3:
        title_text = INPUT_FONT.render("Select Melee for Player (work in progress)", 1, BLACK)
    else:
        title_text = INPUT_FONT.render("Select Utility for Player", 1, BLACK)
    win.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
    button_width, button_height = 200, 50
    buttons = []
    if num == 1:
        for i, gun in enumerate(PRIMARIES.keys()):
            button_rect = pygame.Rect(WIDTH // 2 - button_width // 2, 150 + i * (button_height + 10), button_width + 50,
                                      button_height)
            buttons.append((button_rect, gun))
            pygame.draw.rect(win, GRAY, button_rect)
            gun_text = INPUT_FONT.render(gun.capitalize(), 1, BLACK)
            win.blit(gun_text, (button_rect.x + button_rect.width // 2 - gun_text.get_width() // 2,
                                button_rect.y + button_rect.height // 2 - gun_text.get_height() // 2))
    elif num == 2:
        for i, gun in enumerate(SECONDARIES.keys()):
            button_rect = pygame.Rect(WIDTH // 2 - button_width // 2, 150 + i * (button_height + 10), button_width + 50,
                                      button_height)
            buttons.append((button_rect, gun))
            pygame.draw.rect(win, GRAY, button_rect)
            gun_text = INPUT_FONT.render(gun.capitalize(), 1, BLACK)
            win.blit(gun_text, (button_rect.x + button_rect.width // 2 - gun_text.get_width() // 2,
                                button_rect.y + button_rect.height // 2 - gun_text.get_height() // 2))
    elif num == 3:
        for i, gun in enumerate(MELEES.keys()):
            button_rect = pygame.Rect(WIDTH // 2 - button_width // 2, 150 + i * (button_height + 10), button_width + 50,
                                      button_height)
            buttons.append((button_rect, gun))
            pygame.draw.rect(win, GRAY, button_rect)
            gun_text = INPUT_FONT.render(gun.capitalize(), 1, BLACK)
            win.blit(gun_text, (button_rect.x + button_rect.width // 2 - gun_text.get_width() // 2,
                                button_rect.y + button_rect.height // 2 - gun_text.get_height() // 2))
    else:
        for i, gun in enumerate(UTILITIES.keys()):
            button_rect = pygame.Rect(WIDTH // 2 - button_width // 2, 150 + i * (button_height + 10), button_width + 50,
                                      button_height)
            buttons.append((button_rect, gun))
            pygame.draw.rect(win, GRAY, button_rect)
            gun_text = INPUT_FONT.render(gun.capitalize(), 1, BLACK)
            win.blit(gun_text, (button_rect.x + button_rect.width // 2 - gun_text.get_width() // 2,
                                button_rect.y + button_rect.height // 2 - gun_text.get_height() // 2))
    pygame.display.update()
    return buttons


def get_player_info(player_num):
    name = ""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode
        draw_text_input(f"Enter name for Player {player_num}:", name)


def get_player_gun(player_num, num):
    while True:
        buttons = draw_gun_selection(num)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for button_rect, gun in buttons:
                    if button_rect.collidepoint(mouse_pos):
                        return gun


def get_first_to():
    first_to = ""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return int(first_to)
                elif event.key == pygame.K_BACKSPACE:
                    first_to = first_to[:-1]
                elif event.unicode.isdigit():
                    first_to += event.unicode
        draw_text_input("Enter 'First to' win condition:", first_to)


def draw_intermission(seconds):
    for i in range(seconds, 0, -1):
        win.fill(WHITE)
        intermission_text = MENU_FONT.render(f"Next round starts in {i}", 1, BLACK)
        win.blit(intermission_text,
                 (WIDTH // 2 - intermission_text.get_width() // 2, HEIGHT // 2 - intermission_text.get_height() // 2))
        pygame.display.update()
        time.sleep(1)


    # Main function


def main():
    global username_var, dbc
    run = True
    clock = pygame.time.Clock()
    # Start menu loop
    while run:
        draw_start_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    run = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    # Get player info
    login_popup()
    name1 = username_var
    gun1 = []
    for i in range(1, 5):
        gun1.append(get_player_gun(1, i))
    print(gun1)
    name2 = get_player_info(2)
    gun2 = []
    for i in range(1, 5):
        gun2.append(get_player_gun(2, i))
    print(gun2)

    player1 = Player(100, HEIGHT // 2, RED, name1, gun1)
    player2 = Player(WIDTH - 150, HEIGHT // 2, BLUE, name2, gun2)

    first_to = get_first_to()
    player1_wins = 0
    player2_wins = 0
    draw_intermission(3)  # Initial intermission

    run = True
    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        player1.move(keys, pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_e, pygame.K_q)
        player2.move(keys, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_p, pygame.K_l)

        # Shooting
        if keys[pygame.K_SPACE]:
            player1.shoot()
        if keys[pygame.K_RETURN]:
            player2.shoot()
        if keys[pygame.K_1]:
            player1.selected_gun = 0
            player1.switch_weapons()
        if keys[pygame.K_2]:
            player1.selected_gun = 1
            player1.switch_weapons()
        if keys[pygame.K_3]:
            player1.selected_gun = 2
            player1.switch_weapons()
        if keys[pygame.K_4]:
            player1.selected_gun = 3
            player1.switch_weapons()
        if keys[pygame.K_7]:
            player2.selected_gun = 0
            player2.switch_weapons()
        if keys[pygame.K_8]:
            player2.selected_gun = 1
            player2.switch_weapons()
        if keys[pygame.K_9]:
            player2.selected_gun = 2
            player2.switch_weapons()
        if keys[pygame.K_0]:
            player2.selected_gun = 3
            player2.switch_weapons()


        player1.update_fire_rate()
        player2.update_fire_rate()

        # Update cooldowns
        player1.update_cooldowns()
        player2.update_cooldowns()

        handle_bullets(player1, player2)

        winner_text = ""
        if player1.health <= 0 and not player2_wins == first_to:
            player2_wins += 1
            player1.reset()
            player2.reset()
            draw_intermission(5)
        if player2_wins == first_to:
            winner_text = f"{player2.name} Wins the Game!"
            draw_winner(winner_text)
            break

        if player2.health <= 0 and not player1_wins == first_to:
            player1_wins += 1
            player1.reset()
            player2.reset()
            draw_intermission(5)
        if player1_wins == first_to:

            winner_text = f"{player1.name} Wins the Game!"
            draw_winner(winner_text)
            break

        draw_window(player1, player2, player1_wins, player2_wins)

    pygame.quit()


if __name__ == "__main__":
    main()

