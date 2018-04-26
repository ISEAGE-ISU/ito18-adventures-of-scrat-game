# pygame = Python game library
import pygame
from pygame.locals import *
from pygame.compat import geterror

# python packages
import os, sys, random, time

# other python files related to this game
import settings, backend


# globally initialize pygame for use in multiple functions
pygame.init()

main_dir = os.path.split(os.path.abspath(__file__))[0]
images_dir = os.path.join(main_dir, 'images')


# load an image for the game given the filename
def load_image_tile(name):
    fullname = os.path.join(images_dir, name)
    try:
        # load image with transparency
        image = pygame.image.load(fullname).convert_alpha()

        # resize image to tile size
        image = pygame.transform.scale(image, (settings.tile_size, settings.tile_size))
    except pygame.error:
        print ('Cannot load image:', fullname)
        raise SystemExit(str(geterror()))
    return image, image.get_rect()


# The player's character - Scrat the squirrel!
class Scrat(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image_tile('player.png')
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.speed = 20
        self.state = "still"
        self.reinit()
        self.rotate_dir = "up"
        self.original_img = self.image

    def reinit(self):
        self.state = "still"
        self.movepos = [0, 0]

    def update(self):
        newpos = self.rect.move(self.movepos)
        if self.area.contains(newpos):
            self.rect = newpos
        pygame.event.pump()

    def moveup(self):
        self.movepos[1] = self.movepos[1] - self.speed
        self.state = "moveup"
        if self.rotate_dir != "up":
            self.image = self.rotateScrat("up")

    def movedown(self):
        self.movepos[1] = self.movepos[1] + self.speed
        self.state = "movedown"
        if self.rotate_dir != "down":
            self.image = self.rotateScrat("down")

    def moveleft(self):
        self.movepos[0] = self.movepos[0] - self.speed
        self.state = "moveleft"
        if self.rotate_dir != "left":
            self.image = self.rotateScrat("left")

    def moveright(self):
        self.movepos[0] = self.movepos[0] + self.speed
        self.state = "moveright"
        if self.rotate_dir != "right":
            self.image = self.rotateScrat("right")

    # check to see if anything has collided with Scrat (like fire)
    def checkCollision(self, sprite1, sprite2):
        col = pygame.sprite.collide_rect(sprite1, sprite2)
        
        # boolean return value indicating status of collision
        return col

    # turn Scrat's image based on his current direction ingame
    def rotateScrat(self, direction):
        scrat = 0
        if direction == "up":
            scrat = pygame.transform.rotate(self.original_img, 0)
        elif direction == "down":
            scrat = pygame.transform.rotate(self.original_img, 180)
        elif direction == "left":
            scrat = pygame.transform.rotate(self.original_img, 90)
        elif direction == "right":
            scrat = pygame.transform.rotate(self.original_img, -90)

        self.rotate_dir = direction
        return scrat


# Fires that Scrat must put out by walking over them
class Fire(pygame.sprite.Sprite):
    def __init__(self, curr_time):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image_tile('fire.png')
        self.rect.topleft = [0, 0]
        self.creation_time = curr_time
        self.time_alive = 0
        self.reinit(curr_time)

    # put the fire in a new random location and update the time values
    def reinit(self, curr_time):
        randX = random.randrange(0, settings.disp_width - settings.tile_size)
        randY = random.randrange(0, settings.disp_height - settings.tile_size)
        self.rect.topleft = [randX, randY]
        self.creation_time = curr_time
        self.time_alive = 0

    def update(self, t):
        self.time_alive = t - self.creation_time


# A login menu to ensure the user is valid and has paid for the game.
# See backend.py for more code related to the authentication.
def login(background, screen, clock, authenticated):
    font = pygame.font.Font(None, 50)

    # show mouse icon
    pygame.mouse.set_visible(1)

    # we need two inputs boxes - one for username, one for password
    text_title = font.render('Welcome to The Adventures of Scrat', True, settings.txt_color)
    text_caption = font.render('Please fill out the fields and hit "Enter" to login.', True, settings.txt_color)
    textpos_title = text_title.get_rect(centerx=background.get_width() / 2)
    textpos_caption = text_caption.get_rect(centerx=background.get_width() / 2, centery=100)
    background.blit(text_title, textpos_title)
    background.blit(text_caption, textpos_caption)

    # USERNAME INPUT AREA
    text_user = font.render('Enter username in box below', True, (0, 0, 255))
    textpos = text_user.get_rect(centerx=background.get_width() / 2, centery = 180)
    background.blit(text_user, textpos)
    username_rect = pygame.Rect(50, 200, 440, 50)
    username_rect.centerx = screen.get_width() / 2
    # END USERNAME INPUT AREA

    # PASSWORD INPUT AREA
    text_pass = font.render('Enter password in box below', True, (0, 0, 255))
    textpos = text_user.get_rect(centerx=background.get_width() / 2, centery = 310)
    background.blit(text_pass, textpos)
    password_rect = pygame.Rect(screen.get_width() / 2 - 300, 340, 440, 50)
    password_rect.centerx = screen.get_width() / 2
    # END PASSWORD INPUT AREA

    color_active = pygame.Color('dodgerblue2')
    color_inactive = pygame.Color('lightskyblue3')
    color_user = color_inactive
    color_pass = color_inactive
    user_active = False
    pass_active = False
    text = ''
    done = False

    # input strings from the player
    user_text = ''
    pass_text = ''

    while not done:
        clock.tick(settings.fps)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == MOUSEBUTTONDOWN:
                if username_rect.collidepoint(event.pos):
                    user_active = True
                    pass_active = False
                elif password_rect.collidepoint(event.pos):
                    pass_active = True
                    user_active = False
                else:
                    user_active = False
                    pass_active = False
                color_user = color_active if user_active else color_inactive
                color_pass = color_active if pass_active else color_inactive
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    # submit the login to billing/drm and check to see if it is valid
                    login_success, purchased = backend.authenticate(user_text, pass_text)
                    
                    if login_success and purchased:
                        return True, user_text
                    else:
                        # reset the username and password fields
                        user_text = ''
                        pass_text = ''
                        
                        failed_login(login_success, clock, background, screen)
                        return False, ''
                        
                if user_active:
                    if event.key == K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        if len(user_text) < 20:
                            user_text += event.unicode
                        else:
                            # don't allow anymore to be added to username, 20 chars max
                            user_text = user_text
                if pass_active:
                    if event.key == K_BACKSPACE:
                        pass_text = pass_text[:-1]
                    else:
                        if len(pass_text) < 20:
                            pass_text += event.unicode
                        else:
                            # don't allow anymore to be added to password, 20 chars max
                            pass_text = pass_text

        screen.blit(background, (0,0))
        txt_user_surface = font.render(user_text, True, color_user)
        txt_pass_surface = font.render(pass_text, True, color_pass)
        screen.blit(txt_user_surface, (username_rect.x+5, username_rect.y+5))
        screen.blit(txt_pass_surface, (password_rect.x+5, password_rect.y+5))
        pygame.draw.rect(screen, color_user, username_rect, 2)
        pygame.draw.rect(screen, color_pass, password_rect, 2)
        pygame.display.flip()


def failed_login(auth, clock, background, screen):
    if auth == False:
        text_title = pygame.font.Font(None, 50).render('Login failed. Press Enter to login again', True, settings.txt_color)
        textpos = text_title.get_rect(centerx=background.get_width() / 2, centery = 100)
        
    else:
        # if auth passed we can assume game is not purchased
        text_title = pygame.font.Font(None, 40).render('You have not paid for the game. Visit our webpage and pay. Press Enter to continue.', True, settings.txt_color)
        
    textpos = text_title.get_rect(centerx=background.get_width() / 2, centery = 100)
    background.fill(settings.bg_color)
    screen.blit(background, (0, 0))
    
    while 1:
        # limit framerate or "frames per second"
        clock.tick(settings.fps)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            elif event.type == KEYDOWN: # player pressed a key indicating a move
                if event.key == K_RETURN:
                    return

            # update the screen
            screen.blit(text_title, textpos)
            pygame.display.flip()


def main_menu(background, screen, clock):
    font = pygame.font.Font(None, 100)
    text_title = font.render('Welcome to The Adventures of Scrat', True, settings.txt_color)
    text_cap1 = font.render('To begin the game, press W', True, settings.txt_color)
    text_capbot = font.render('Press L to open the Leaderboard', True, settings.txt_color)
    text_cap2 = pygame.font.Font(None, 40).render('Move Scrat with WASD. Put out fires. Game over if a fire lasts for more than 6 seconds', 1, settings.txt_color)
    
    textpos_title = text_title.get_rect(centerx=background.get_width() / 2)
    textpos_cap1 = text_cap1.get_rect(centerx=background.get_width() / 2, centery=200)
    textpos_cap2 = text_cap2.get_rect(centerx=background.get_width() / 2, centery=300)
    textpos_capbot = text_capbot.get_rect(centerx=background.get_width() / 2, centery=600)
    background.fill(settings.bg_color)
    screen.blit(background, (0, 0))
    
    while 1:
        clock.tick(settings.fps)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == KEYDOWN:
                if event.key == K_w:
                    return
                if event.key == K_l:
                    backend.open_leaderboard()

        background.blit(text_title, textpos_title)
        background.blit(text_cap1, textpos_cap1)
        background.blit(text_cap2, textpos_cap2)
        background.blit(text_capbot, textpos_capbot)
        screen.blit(background, (0, 0))
        pygame.display.flip()


def game(background, screen, clock, time_begin):
    # initialize the player
    player = Scrat()
    player_sprite = pygame.sprite.GroupSingle(player)

    # initialize fires
    t = time.time()
    fire1 = Fire(t)
    fire2 = Fire(t)
    fire3 = Fire(t)
    fire4 = Fire(t)
    fire5 = Fire(t)
    fire6 = Fire(t)

    fire_active = pygame.sprite.Group(fire1) # fires alive on the screen
    fire_dormant = pygame.sprite.Group(fire2, fire3, fire4, fire5, fire6) # fires waiting to be sprung
    num_fires = 1

    # hide mouse icon
    pygame.mouse.set_visible(0)

    # clear the background
    background.fill((255, 214, 145))
    screen.blit(background, (0, 0))

    while 1:
        clock.tick(settings.fps)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            elif event.type == KEYDOWN: # player pressed a key indicating a move
                if event.key == K_w:
                    player.moveup()
                if event.key == K_s:
                    player.movedown()
                if event.key == K_a:
                    player.moveleft()
                if event.key == K_d:
                    player.moveright()
            elif event.type == KEYUP: # player depressed key, stop moving
                if event.key == K_w or event.key == K_s or event.key == K_a or event.key == K_d:
                    player.movepos = [0, 0]
                    player.state = "still"

        # update the screen
        screen.blit(background, (0,0))
        player_sprite.update()
        player_sprite.draw(screen)
        fire_active.draw(screen)

        # update the time alive for all living fires
        fire_active.update(time.time())

        # force a refresh of the screen
        pygame.display.flip()

        active_fires = fire_active.sprites() # a list of all active fires
        dormant_fires = fire_dormant.sprites() # a list of all dormant fires

        # if scrat collides with fire, reinitialize it to another location
        for fire in active_fires:
            if player.checkCollision(player, fire):
                fire_active.remove(fire) # remove from active and...
                fire_dormant.add(fire)   # ... add it to dormant

        # the number of fires that should be active at next clock cycle
        # the number works out to be a new, additional fire active every 10 seconds
        # at 11 seconds, 2 fires exist. at 30 seconds, 4 fires exist.
        time_elapsed = time.time() - time_begin
        num_fires = time_elapsed / 10

        while len(active_fires) < num_fires:
            if len(dormant_fires) > 0:
                new_fire = dormant_fires[0]

            fire_active.add(new_fire)
            new_fire.reinit(time.time())
            fire_dormant.remove(new_fire)
            active_fires = fire_active.sprites()
            dormant_fires = fire_dormant.sprites()

        for fire in active_fires:
            if fire.time_alive > 6:
                # game over, a fire has been burning too long
                message = "A fire has been burning too long"
                score = str(round(time.time() - time_begin))
                return score, message


def game_over(clock, background, screen, message, score, time_now, is_high_score):
    font = pygame.font.Font(None, 50)
    text_title = font.render('Game Over! ' + message, 1, (255, 0, 0))
    text_caption = font.render('Press Enter to start a new game', 1, (255, 0, 0))
    text_score = font.render('Score: ' + score + ' seconds', 1, (255, 0, 0))
    textpos_title = text_title.get_rect(centerx=background.get_width() / 2)
    textpos_caption = text_caption.get_rect(centerx=background.get_width() / 2, centery=200)
    textpos_score = text_score.get_rect(centerx=background.get_width() / 2, centery=400)
    
    text_high_score = font.render("Congrats! You've hit a new high score!", True, (12, 225, 0))
    textpos_hs = text_high_score.get_rect(centerx=background.get_width() / 2, centery=600)
    

    while 1:
        clock.tick(settings.fps)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN:
                    return

        if is_high_score:
            background.blit(text_high_score, textpos_hs)
        background.blit(text_title, textpos_title)
        background.blit(text_caption, textpos_caption)
        background.blit(text_score, textpos_score)
        screen.blit(background, (0, 0))
        pygame.display.flip()


def main():
    # boolean - True if user logged in, False otherwise
    authenticated = False

    # set caption at top of the game window
    pygame.display.set_caption(settings.caption)

    # set screen to size in settings
    screen = pygame.display.set_mode((settings.disp_width, settings.disp_height))

    # set the background color of the game window
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(settings.bg_color)
    screen.blit(background, (0,0))
    pygame.display.flip()

    clock = pygame.time.Clock()

    if not authenticated:
        # main menu of the game
        authenticated, user = login(background, screen, clock, authenticated)

    # if the user is logged in, take them to the main menu
    # where they can begin the game
    while 1:
        if authenticated:
            main_menu(background, screen, clock)
            score, message = game(background, screen, clock, time.time())
            is_high_score = backend.send_score(user, score)
            game_over(clock, background, screen, message, score, time.time(), is_high_score)
        else:
            authenticated = login(background, screen, clock, authenticated)

if __name__ == '__main__':
    main()

