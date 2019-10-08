import sys
import math
import random

from collections import deque

def debug(strs, *vars):
    print(strs, *vars, file=sys.stderr)

class Robot(object):
    def __init__(self, row, col, item):
        self.row, self.col = row, col
        self.item = item
    
    def update(self, row, col, item):
        self.row, self.col = row, col
        self.item = item

class MyRobot(Robot):
    def __init__(self,row,col,item):
        super().__init__(row, col, item)
        self.orderkind = ""
        self.destrow, self.destcol = -1, -1
        self.request_item = "RADAR"
        self.orderpriority = 10

    def update(self, row, col, item):
        return super().update(row, col, item)

    def dig(self, row, col, priority):
        self.orderkind = "DIG"
        self.destrow, self.destcol = row, col
        self.orderpriority = priority
        if abs(self.row - self.destrow) + abs(self.col - self.destcol) > 1: raise ValueError("cant dig. too far")
    
    def move(self,row,col, priority):
        self.orderkind = "MOVE"
        self.destrow, self.destcol = row, col
        self.orderpriority = priority
    
    def home(self):
        self.orderkind = "MOVE"
        self.destrow, self.destcol = self.row, 0
        self.orderpriority = 90

    def request(self, request_item, priority):
        self.orderkind = "REQUEST"
        self.request_item = request_item
        self.orderpriority = priority

    def printorder(self):
        if self.orderkind == "REQUEST":
            print(self.orderkind + " " + self.request_item)
        else:
            print(self.orderkind + " " + str(self.destcol) + " " + str(self.destrow))

class EnemyRobot(Robot):
    def __init__(self, row, col, item):
        super().__init__(row, col, item)
        self.prerow = -1
        self.precol = -1
        self.preitem = -1
    
    def update(self, row, col, item):
        self.prerow = self.row
        self.precol = self.col
        self.preitem = self.item
        return super().update(row, col, item)

    def status(self):
        if self.item != self.preitem:
            if self.preitem == 2:
                return 2
            elif self.preitem == 3:
                return 3
            elif self.item == 4:
                return 4
        return 0
    
class Cell(object):
    def __init__(self):
        self.inRadarRange = False
        self.hasownTrap = False
        self.numofOre = -1 #-1 for unknown
        self.hole = False
        self.diggedbyme = False
        self.wasOre = False

        # vague info estimated opponent move
        self.RadarPossibility = 0
        self.TrapPossibility = 0
        self.OrePossibility = 0

"""
priority:
    100 : request radar and put radar when short
     90 : bring ore back
     80 : dig

     70 : break opponents radar with 0 or 1 move

     50: go to ore place from radar with 1 move
     40: go to ore place from radar with n move (-n+1 priority)

     35: dig ore place from wasore
     30: go to ore place from wasore with n move (-n+1 priority)

     20: random dig
     10: nothing

enemy status:
    0: no need to worry
    2: just put radar
    3: just put trap
    4: just got ore
"""

def distance(robotrow, robotcol, cellrow, cellcol):
    return abs(robotrow - cellrow) + abs(robotcol - cellcol)

def nextplace_to_put_radar(tempi):
    temp = [[10,8],[1,11],[8,2],[6,13],[10,18],[3,19], [7,23]]
    if tempi >= len(temp):
        return [random.randint(4,10), random.randint(25,29)]
    return temp[tempi]

# height: size of the map
ncol, nrow = [int(i) for i in input().split()]
field = [[Cell() for col in range(ncol)] for row in range(nrow)]
myrobots = [MyRobot(-1,-1,-1) for _ in range(5)]
enemies = [EnemyRobot(-1,-1,-1) for _ in range(5)]

    # field = [[[-1,-1,-1,-1] for w in range(widths)] for h in range(heights)] # field info. [isinradar, istrap, #ofore, diggedbyme]
    # myrobots = [[[],-1,[-1,-1,-1],-1] for _ in range(5)]  # [[row,col], item, [orderkind, targetrow,targetcol], orderpriority]
    # order = [["",-1,-1] for _ in range(5)] # MOVE row col | DIG row col | REQUEST

# game loop
loop = 0

# first three turn
for initial in range(3):
    my_score, opponent_score = [int(i) for i in input().split()]

    for row in range(nrow):
        inputs = input().split()
        for col in range(ncol):
            # ore: amount of ore or "?" if unknown
            # hole: 1 if cell has a hole
            num_of_ore = inputs[2*col]
            ishole = int(inputs[2*col+1])

            # update
            if num_of_ore != '?':
                field[row][col].numofOre = int(num_of_ore)
            field[row][col].hole = bool(ishole)
        
    entity_count, radar_cooldown, trap_cooldown = [int(i) for i in input().split()]
    for i in range(entity_count):
        # id: unique id of the entity
        # type: 0 for your robot, 1 for other robot, 2 for radar, 3 for trap
        # y: position of the entity
        # item: if this entity is a robot, the item it is carrying (-1 for NONE, 2 for RADAR, 3 for TRAP, 4 for ORE)
        id, type, col, row, item = [int(j) for j in input().split()]

        if type == 0:
            id %= 5
            robot = myrobots[id]
            robot.update(row, col, item)

            if robot.orderkind == "DIG":
                field[robot.destrow][robot.destcol].diggedbyme = True
                if item == 4:
                    field[robot.destrow][robot.destcol].wasOre = True
        
        elif type == 1:
            id %= 5
            robot = enemies[id]
            robot.update(row, col, item)


    if loop == 0:
        nearest_dist, nearest_robot_idx = 5, 0
        for robot_idx in range(5):
            robot = myrobots[robot_idx]
            print("raobot_idx, row, col, nearest_dist ", robot_idx, robot.row, robot.col, nearest_dist, file=sys.stderr)
            robot.move(robot.row, robot.col+4, 10)
            if abs(4 - robot.row) < nearest_dist:
                nearest_dist = abs(4-robot.row)
                nearest_robot_idx = robot_idx
        myrobots[nearest_robot_idx].request("RADAR", 90)
    elif loop == 1:
        for robot_idx in range(5):
            robot = myrobots[robot_idx]
            if robot.item ==2:
                robot.move(robot.row, robot.col+4, 90)
            else:
                robot.dig(robot.row, robot.col+1, 10)

    elif loop == 2:
        for robot_idx in range(5):
            robot = myrobots[robot_idx]
            if robot.item ==2:
                robot.dig(robot.row, robot.col+1, 90)
            elif robot.item == 4:
                robot.home()
            else:
                # if anyone found ore, try to go there
                robot.dig(robot.row, robot.col-1, 10)

    #print order
    for robot_idx in range(5):
        myrobots[robot_idx].printorder()
    loop += 1

tempi = 0 # temporal for radar put place
while True:
    # my_score: Amount of ore delivered
    my_score, opponent_score = [int(i) for i in input().split()]
    ore_this_turn = []
    for row in range(nrow):
        inputs = input().split()
        for col in range(ncol):
            # ore: amount of ore or "?" if unknown
            # hole: 1 if cell has a hole
            num_of_ore = inputs[2*col]
            ishole = int(inputs[2*col+1])

            # update field
            if num_of_ore != '?':
                field[row][col].numofOre = int(num_of_ore)
            field[row][col].hole = bool(ishole)
        
    # entity_count: number of entities visible to you
    # radar_cooldown: turns left until a new radar can be requested
    # trap_cooldown: turns left until a new trap can be requested
    entity_count, radar_cooldown, trap_cooldown = [int(i) for i in input().split()]
    radar_taken, radar_num = 0, 0
    for i in range(entity_count):
        # id: unique id of the entity
        # type: 0 for your robot, 1 for other robot, 2 for radar, 3 for trap
        # y: position of the entity
        # item: if this entity is a robot, the item it is carrying (-1 for NONE, 2 for RADAR, 3 for TRAP, 4 for ORE)
        id, type, col, row, item = [int(j) for j in input().split()]

        if type == 2:
            radar_num += 1
        elif type == 0:
            id %= 5
            robot = myrobots[id]
            robot.update(row, col, item)

            if robot.orderkind == "DIG":
                field[robot.destrow][robot.destcol].diggedbyme = True
                if item == 4:
                    field[robot.destrow][robot.destcol].wasOre = True
                else:
                    field[robot.destrow][robot.destcol].numofOre = 0
        
        elif type == 1:
            id %= 5
            robot = enemies[id]
            robot.update(row, col, item)
    
    radar_says_ore, was_ore = [], []
    for row in range(nrow):
        for col in range(ncol):
            cell = field[row][col]
            if cell.numofOre > 0:
                radar_says_ore.append([row,col])
            elif cell.numofOre == -1 and cell.wasOre:
                was_ore.append([row,col])

    radar_incharge = False
    # put order
    for robot_idx in range(5):
        robot = myrobots[robot_idx]
        if robot.item == 4:
            robot.home()
        elif robot.item == 2:
            if robot.orderkind == 'REQUEST':
                radarrow, radarcol = nextplace_to_put_radar(tempi)
                tempi+=1
                robot.move(radarrow, radarcol, 100)
            if distance(robot.row, robot.col, robot.destrow, robot.destcol) < 2:
                robot.dig(robot.destrow, robot.destcol, 100)
        elif robot.item == -1:
            robot.orderpriority = 10
            if robot.col == 0 and radar_cooldown < 2 and (radar_num < 6 or len(radar_says_ore) < 6) and not radar_incharge: # when short of radar
                robot.request("RADAR", 100)
                radar_incharge = True
            else:
                for candidate_idx in range(len(radar_says_ore)):
                    row, col = radar_says_ore[candidate_idx]
                    dist = distance(robot.row, robot.col, row, col)
                    if dist < 2 and field[row][col].numofOre > 0:
                        robot.dig(row,col, 80)
                        field[row][col].numofOre -= 1
                        if field[row][col].numofOre == 0: radar_says_ore.remove([row,col])
                        break
                    elif robot.orderpriority < 40 - ( dist // 4):
                        robot.move(row, col, 40-(dist//4))


            # nothing to do
            if robot.orderpriority == 10:
                for candidate_idx in range(len(was_ore)):
                    row, col = was_ore[candidate_idx]
                    dist = distance(robot.row, robot.col, row, col)
                    if dist < 2 and field[row][col].numofOre != 0:
                        robot.dig(row,col, 35)
                        break
                    elif robot.orderpriority < 30 - ( dist // 4):
                        robot.move(row, col, 30-(dist//4))
                if robot.orderpriority == 10: # really nothing to do
                    for r, c in [[0, 1],[1,0],[0,-1],[-1,0],[0,0]]:
                        if 0<=robot.row+r<15 and 0<=robot.col+c<30 and field[robot.row+r][robot.col+c].numofOre != 0:
                            robot.dig(robot.row+r, robot.col+c, 20)
                            break
                    else:
                        robot.move(14,29, 11)

    #print order
    for robot_idx in range(5):
        myrobots[robot_idx].printorder()
    loop += 1