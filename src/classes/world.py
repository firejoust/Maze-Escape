from dataclasses import dataclass
from typing import Optional, List, Callable, Tuple
from classes.geometry import vec2, line
import math
import random

'''
    Global
'''

FRICTION = 1.5
CARDINAL = [[1, 0],[0, 1],[-1, 0],[0, -1]]
DIAGONAL = [[1, 1],[-1, 1],[-1, -1],[1, -1]]
REVERSE = {
    'NORTH': 'SOUTH',
    'EAST': 'WEST',
    'SOUTH': 'NORTH',
    'WEST': 'EAST',
}

'''
    Get adjacent coordinates
'''
def adjacentCorner(position: vec2, radius_x: int, radius_y: int) -> List[vec2]:
    coordinates = []
    for x in range(1, abs(radius_x)):
        coordinates.append(vec2(position.x + math.copysign(x, radius_x), position.y + radius_y))

        if x == abs(radius_x) - 1:
            for y in range(1, abs(radius_y)):
                coordinates.append(vec2(position.x + radius_x, position.y + math.copysign(y, radius_y)))
    return coordinates

def adjacentDirectional(position: vec2, radius: int) -> List[vec2]:
    coordinates = []

    for i in range(4):
        cardinal_coordinate = vec2(position.x + (CARDINAL[i][0] * radius), position.y + (CARDINAL[i][1] * radius))
        diagonal_coordinate = vec2(position.x + (DIAGONAL[i][0] * radius), position.y + (DIAGONAL[i][1] * radius))
        miscellaneous_coordinates = adjacentCorner(position, DIAGONAL[i][0] * radius, DIAGONAL[i][1] * radius)
        miscellaneous_coordinates.extend([cardinal_coordinate, diagonal_coordinate])
        coordinates.extend(miscellaneous_coordinates)
    
    return coordinates

'''
    Maze generation
'''
# Items:
# - Time extension
# 
def generateMaze(reference, item_frequency):
    assert len(reference) > 3, f'grid x axis needs to be larger than 3, got {len(reference)}'
    assert len(reference[0]) > 3, f'grid y axis needs to be larger than 3, got {len(reference[0])}' # We can do this as coordinates are regular
    assert len(reference) % 2 != 0 and len(reference[0]) % 2 != 0, 'Grid needs to be an odd value.'

    grid = [[y for y in x] for x in reference]
    dimensions = vec2(len(grid), len(grid[0]))

    start = vec2(1, 1) # offset from wall
    finish = vec2(dimensions.x - 1, dimensions.y - 1) # coordinates start at 0, offset from wall

    # Clear a hole for the start and finish of the maze
    #grid[start.x-1][start.y].occupation = None
    grid[finish.x][finish.y-1].occupation = polygon('finish', boundingbox(0.1), (255, 255, 0))

    current_position = None
    cache = [start]

    # still have valid places to move
    while len(cache) > 0:
        current_position = cache[len(cache) - 1]
        directional = []
        
        for direction in CARDINAL:
            query = vec2(current_position.x + (direction[0] * 2), current_position.y + (direction[1] * 2)) # 2 spaces in each direction
            difference = vec2(dimensions.x - (query.x + 1), dimensions.y - (query.y + 1))

            # determine if space hasn't been taken yet and is inside the grid
            inside = (difference.x > 0 and difference.y > 0) and (difference.x < dimensions.x and difference.y < dimensions.y)

            if inside and not grid[query.x][query.y].occupation is None and grid[query.x][query.y].occupation.type == 'wall':
                directional.append(query)

        valid = None
        # select a random direction
        if len(directional) > 0:
            valid = directional[int(random.randint(0, len(directional)-1))]

        if not valid is None:

            # Remove every square from current position to new position
            difference = vec2(valid.x - current_position.x, valid.y - current_position.y)
            difference.floor()
            if difference.x == 0:
                for y in range(0, difference.y, int(math.copysign(1, difference.y))):
                    query = vec2(current_position.x, current_position.y + y)
                    query.floor()
                    grid[query.x][query.y].occupation = None
                    if random.randint(1, 100) <= item_frequency:
                        grid[query.x][query.y].occupation = polygon('time', boundingbox(0.1), (0, 100, 100))

            elif difference.y == 0:
                for x in range(0, difference.x, int(math.copysign(1, difference.x))):
                    query = vec2(current_position.x + x, current_position.y)
                    query.floor()
                    grid[query.x][query.y].occupation = None
                    if random.randint(1, 100) <= item_frequency:
                        grid[query.x][query.y].occupation = polygon('time', boundingbox(0.1), (0, 100, 100))

            else:
                raise RuntimeError('Offset either non cardinal or same as starting position.')

            grid[valid.x][valid.y].occupation = None
            cache.append(valid)
            continue

        # No valid directions left; remove last element from cache and backtrack
        cache.pop()

    return grid

'''
    Objects, collision, etc
'''

@dataclass
class boundingbox:
    radius: int
    boundaries = None

    def __post_init__(self):
        self.boundaries = {
            'NORTH': line(vec2(self.radius, self.radius), vec2(-self.radius, self.radius)),
            'SOUTH': line(vec2(-self.radius, self.radius), vec2(-self.radius, -self.radius)),
            'EAST': line(vec2(-self.radius, -self.radius), vec2(self.radius, -self.radius)),
            'WEST': line(vec2(self.radius, -self.radius), vec2(self.radius, self.radius)),
        }            


@dataclass
class polygon:
    type: str
    boundingbox: boundingbox
    colour: Tuple[int, int, int]

'''
    Coordinate occupation
'''
@dataclass
class square:
    position: vec2
    occupation: Optional[polygon] = None

    def setOccupation(self, occupation: object):
        self.occupation = occupation

@dataclass
class terrain:
    dimensions: vec2
    grid: List[List[square]] = None

    '''
        Define grid for own coordinates
    '''
    def generate(self):
        self.grid = []
        # fill in x axis
        for x in range(self.dimensions.x):
            self.grid.append([])
            # fill in y axis
            for y in range(self.dimensions.y):
                position = vec2(x, y)
                self.grid[x].append(square(position))
    
    def fill(self):
        for x in range(self.dimensions.x):
            for y in range(self.dimensions.y):
                self.getSquare(vec2(x, y)).setOccupation(polygon('wall', boundingbox(0.5), (255, 255, 255)))

    '''
        Retrieves a square from a defined terrain. Returns None if coordinate doesn't exist
    '''
    def getSquare(self, position: vec2) -> square:
        try:
            assert position.x >= 0 and position.y >= 0
            return self.grid[position.x][position.y]
        except (IndexError, AssertionError):
            return None

    def getAdjacentSquares(self, position: vec2, radius: int) -> List[square]:
        coordinates = []
        for iterator in range(radius):
            coordinates.extend(adjacentDirectional(position, iterator + 1))

        squares = []
        for offset in coordinates:
            try: # simply push if no error
                square = self.getSquare(vec2(math.floor(offset.x), math.floor(offset.y)))
                squares.append(square)
            except:
                pass
        
        return squares
            
    def __post_init__(self):
        self.generate()
