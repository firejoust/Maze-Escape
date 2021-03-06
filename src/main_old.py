import pygame
import math
from pygame.locals import *
from classes.world import terrain, polygon
from classes.geometry import vec2, line, PI
from classes.entities import boundingbox, entity, player
from classes.interface import canvas, colourDistanceMultiplier

pygame.init()
dimensions = vec2(1280, 720)
map_dimensions = vec2(50, 50)
window = pygame.display.set_mode(dimensions.display()) # Initialise window
minimap = canvas(vec2(10, 10), dimensions, dimensions.divide(4, 4))
camera = canvas(vec2(0, 0), dimensions, dimensions)

'''
    Create the environment
'''

world = terrain(map_dimensions, dimensions)
world.setSquare(vec2(5, 4), polygon(boundingbox(5)))
world.setSquare(vec2(20, 20), polygon(boundingbox(10)))
print(world.getSquare(vec2(5, 4)))

walls = [
    line(vec2(0, 0), vec2(0, 300)),
    line(vec2(0, 300), vec2(300, 300)),
    line(vec2(300, 300), vec2(300, 0)),
    line(vec2(300, 0), vec2(0, 0)),
]

'''
    Create the player
'''
player1 = player(vec2(100, 100), boundingbox(10))
entities = [
    player1
]
    
'''
    Update loop
'''
while True:
    '''
        Retrieve queued input events
    '''
    for event in pygame.event.get(): # Retreive all queued events. Must be ran to display a window
        pass

    '''
        Retrieve keystrokes
    '''
    key = pygame.key.get_pressed()
    if key[pygame.K_a] or key[pygame.K_d] or key[pygame.K_w] or key[pygame.K_s]:
        velocity = vec2(0, 0)

        if key[pygame.K_a]:
            velocity.x -= 0.02
        if key[pygame.K_d]:
            velocity.x += 0.02
        if key[pygame.K_w]:
            velocity.y -= 0.02
        if key[pygame.K_s]:
            velocity.y += 0.02

        # Gets a new vector based on difference between the player's yaw and applied velocity. Required for directional movement, and PI/2 there to offset 90 degrees
        relative_velocity = velocity.relative(player1.yaw.subtract(math.atan2(velocity.y, velocity.x) + PI/2)) 
        player1.velocity = player1.velocity.add(relative_velocity.x, relative_velocity.y)

    if key[pygame.K_LEFT]:
        player1.yaw = player1.yaw.add(PI/180)
    if key[pygame.K_RIGHT]:
        player1.yaw = player1.yaw.subtract(PI/180)

    '''

    '''
    rays = list(reversed(player1.retrieveRays(400, 60)))

    # todo: triangles connecting each column.
    # perhaps columns uncovering a texture?

    for i in range(len(rays)):
        raycast = rays[i]
        closest_point = None
        #pygame.draw.line(window, (255, 255, 128), minimap.relative(raycast.start, dimensions).display(), minimap.relative(raycast.finish, dimensions).display(), width=math.ceil(minimap.ratio(dimensions).length() * 1))

        '''
        for x in range(world.dimensions.x):
            for y in range(world.dimensions.y):
                square = world.getSquare(vec2(x, y))

                if square is None or square.occupation is None:
                    continue

                for boundary in square.occupation.display:
                    intercept = boundary.relative(dimensions, map_dimensions).intercept(raycast)

                    if intercept is None:
                        continue

                    pygame.draw.circle(window, (255, 255, 0), minimap.relative(intercept, dimensions).display(), minimap.ratio(dimensions).length() * 4)
                    if closest_point is None:
                        closest_point = intercept
                    elif player1.position.distance(intercept) < player1.position.distance(closest_point):
                        closest_point = intercept

            '''

        '''
            Checks walls
        '''

        for wall in walls:
            intercept = wall.intercept(raycast)

            if not intercept is None:
                pygame.draw.circle(window, (255, 255, 0), minimap.relative(intercept, dimensions).display(), minimap.ratio(dimensions).length() * 4)
                if closest_point is None:
                    closest_point = intercept
                elif player1.position.distance(intercept) < player1.position.distance(closest_point):
                    closest_point = intercept

        if not closest_point is None:
            distance = player1.position.distance(closest_point)
            bar_dimensions = vec2((dimensions.x * (1/len(rays))+1), dimensions.y * (10/distance))
            position = vec2(dimensions.x * (i/len(rays)), (dimensions.y / 2) -  bar_dimensions.y/2)
            rect = pygame.Rect(position.x, position.y, bar_dimensions.x, bar_dimensions.y)
            colour = 255 * colourDistanceMultiplier(distance, 20)
            pygame.draw.rect(window, (colour, colour, colour), rect)

    '''
        Check world
    '''

    '''
    for x in range(world.dimensions.x):
        for y in range(world.dimensions.y):
            square = world.getSquare(vec2(x, y))

            if not square is None:
                occupation = square.occupation
                
                if not occupation.display is None:
                    for boundary in occupation.display:
                      intercept = boundary.intercept()
    '''


    '''
        Display minimap
    '''

    rect = pygame.Rect(minimap.position.x, minimap.position.y, minimap.display_dimensions.x, minimap.display_dimensions.y)
    pygame.draw.rect(window, (10, 10, 10), rect)

    for wall in walls:
        colour = (255, 255, 255) # white
        start = minimap.relative(wall.start, dimensions).display()
        finish = minimap.relative(wall.finish, dimensions).display()
        width = math.ceil(minimap.ratio(dimensions).length() * 5)
        pygame.draw.line(window, colour, start, finish, width=width)

    for entity in entities:
        entity.tick()
        
    pygame.draw.circle(window, (255, 255, 60), minimap.relative(player1.position, dimensions).display(), minimap.ratio(dimensions).length() * player1.boundingbox.radius) # draw the player

    pygame.display.update() # Update the window displayed
    window.fill((0, 0, 0))