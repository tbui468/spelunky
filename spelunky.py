#review: the Player class
#review: added a goal, and split entities into separate scenes
#review: also used a dictionary to store level data
#goal: have game switch from scene to scene when player touches goal using custom events

print("this is a small change")

import pygame

pygame.init()
window = pygame.display.set_mode((500, 400))
clock = pygame.time.Clock()

NEXT_LEVEL = pygame.USEREVENT + 1
#MY_EVENT2 = pygame.USEREVENT + 2
#MY_OTHER_EVENT = pygame.USEREVENT + 3

class Animation():
    def __init__(self, files): #["hero1.png", "hero2.png"]
        self.frames = 0
        self.idx = 0
        self.images = []
        for file in files:
            image = pygame.image.load(file)
            image = pygame.transform.scale(image, (25, 25))
            self.images.append(image)

    def get_sprite(self, surface):
        self.frames += 1
        #surface.blit(self.images[self.idx], self.rect)
        if self.frames % 10 == 0: #this is true every 10 frames
            self.idx += 1
            if self.idx >= len(self.images):
                self.idx = 0

        return self.images[self.idx]

class Entity():
    def __init__(self, x, y, w, h, anchored, can_collide):
        self.rect = pygame.Rect(x, y, w, h)
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 0.5
        self.anchored = anchored
        self.can_collide = can_collide

    def update(self, entities, events):
        if not self.anchored:
            self.velocity_y += self.gravity
            self.rect.y += self.velocity_y

    def draw(self, surface):
        pygame.draw.rect(surface, (200, 255, 0), self.rect)

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 25, 25, False, True)
        self.respawn = (x, y)

        self.idle_animation = Animation(["hero_idle_1.png", "hero_idle_2.png"])

    def draw(self, surface):
        image = self.idle_animation.get_sprite(surface)
        surface.blit(image, self.rect)

    def on_ground(self, entities):
        self.rect.y += 1

        for e in entities:
            if e == self or not e.can_collide:
                continue
            if self.rect.colliderect(e.rect): 
                self.rect.y -= 1
                return True
        
        self.rect.y -= 1
        return False

    def update(self, entities, events):
        super().update(entities, events)

        #vertical undo logic
        undo = 1
        if self.velocity_y > 0:
            undo = -1

        for e in entities:
            if e == self or not e.can_collide:
                continue
            
            while self.rect.colliderect(e.rect):
                self.rect.y += undo
                self.velocity_y = 0

        #horizontal movement
        #left movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            self.rect.x -= 2
            for e in entities:
                if e == self or not e.can_collide:
                    continue
                
                while self.rect.colliderect(e.rect):
                    self.rect.x += 1

        #right movement            
        if keys[pygame.K_d]:
            self.rect.x += 2
            for e in entities:
                if e == self or not e.can_collide:
                    continue
                
                while self.rect.colliderect(e.rect):
                    self.rect.x -= 1

        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE and self.on_ground(entities):
                self.velocity_y = -10

        if self.rect.y > 400:
            self.rect.x = self.respawn[0]
            self.rect.y = self.respawn[1]
            self.velocity_y = 0

class Goal(Entity):
    def __init__(self, x, y, next_level, spawn_coords):
        super().__init__(x, y, 25, 25, True, False)
        self.next_level = next_level
        self.spawn_coords = spawn_coords

        self.animation = Animation(["anim0.png", "anim1.png", "anim2.png", "anim3.png"])

    def draw(self, surface):
        image = self.animation.get_sprite(surface)
        surface.blit(image, self.rect)
    
    def update(self, entities, events):
        if self.rect.colliderect(entities[0].rect):
            event = pygame.event.Event(NEXT_LEVEL, next_level=self.next_level, spawn_coords=self.spawn_coords)
            pygame.event.post(event)

            #reset player
            player = entities[0]   
            player.rect.x = player.respawn[0]
            player.rect.y = player.respawn[1]

class Wall(Entity):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, True, True)


class Scene():
    def __init__(self, entities):
        self.entities = entities
        self.image = pygame.image.load("space.jpg")
        self.image = pygame.transform.scale(self.image, (500, 400))

    def update(self, events):
        for e in self.entities:
            e.update(self.entities, events)

    def draw(self, surface):
        #window.fill((200, 200, 255)) 
        surface.blit(self.image, (0, 0))
        for e in self.entities:
            e.draw(window)


data = {"1": [Player(100, 100), Wall(0, 300, 600, 25), Goal(450, 200, "2", (50, 200))],
        "2": [Player(100, 100), Wall(0, 300, 600, 25), 
                Goal(0, 200, "1", (350, 200)), Goal(450, 200, "3", (50, 200))],
        "3": [Player(100, 100), Wall(0, 300, 600, 25), Goal(0, 200, "2", (400, 200))],
       }

scene = Scene(data["1"])
run = True
while run:
    events = pygame.event.get()
    for e in events:
        if e.type == pygame.QUIT:
            run = False
        if e.type == NEXT_LEVEL:
            scene = Scene(data[e.next_level])
            player = scene.entities[0]
            player.rect.x = e.spawn_coords[0]
            player.rect.y = e.spawn_coords[1]
            player.respawn = e.spawn_coords

    #update
    scene.update(events)
   
    #drawing 
    scene.draw(window)
    
    pygame.display.update() 
    clock.tick(60)
