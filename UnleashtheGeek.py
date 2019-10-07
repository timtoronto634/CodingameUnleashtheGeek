import sys
import math
import random

class Robot(object):
    def __init__(self,row,col,item):
        self.row, self.col = row, col
        self.item = item
        self.orderkind = ""
        self.destrow, self.destcol = -1, -1
        self.request_item = "RADAR"
        self.orderpriority = 10

    def update(self, row, col, item):
        self.row, self.col = row, col
        self.item = item

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
        self.orderpriority = 100

    def request(self, request_item, priority):
        self.orderkind = "REQUEST"
        self.request_item = request_item
        self.orderpriority = priority
    

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

def printorder(robot):
    if robot.orderkind == "REQUEST":
        print(robot.orderkind + " " + robot.request_item)
    else:
        print(robot.orderkind + " " + str(robot.destcol) + " " + str(robot.destrow))

def distance(cur_point, target_point):
    return abs(cur_point[0] - target_point[0]) + abs(cur_point[1] - target_point[1])

def distance(robotrow, robotcol, cellrow, cellcol):
    return abs(robotrow - cellrow) + abs(robotcol - cellcol)

# height: size of the map
ncol, nrow = [int(i) for i in input().split()]
field = [[Cell() for col in range(ncol)] for row in range(nrow)]
myrobots = [Robot(-1,-1,-1) for _ in range(5)]

    # field = [[[-1,-1,-1,-1] for w in range(widths)] for h in range(heights)] # field info. [isinradar, istrap, #ofore, diggedbyme]
    # myrobots = [[[],-1,[-1,-1,-1],-1] for _ in range(5)]  # [[row,col], item, [orderkind, targetrow,targetcol], orderpriority]
    # order = [["",-1,-1] for _ in range(5)] # MOVE row col | DIG row col | REQUEST

# game loop
loop = 0

# first four turn
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
        printorder(myrobots[robot_idx])
    loop += 1

    
    # set order
    for robot:
        if item == 4:
            robot.order = backhome
    # set request radar for only one robot if condition is satisfied
    radar_taken = 0
    if condition:
        for robot:
            if condition:
                radar_taken = 1
                set radar order

radar_put_place = [[10,8],[1,11],[8,2],[6,13],[10,18],[3,19], [7,23]]
previous_radar_num = 0
while True:
    # my_score: Amount of ore delivered
    my_score, opponent_score = [int(i) for i in input().split()]
    ore_this_turn = []
    for height in range(nrow):
        inputs = input().split()
        for col in range(ncol):
            # ore: amount of ore or "?" if unknown
            # hole: 1 if cell has a hole
            num_of_ore = inputs[2*col]
            ishole = int(inputs[2*col+1])

            # update field
            if num_of_ore == '?':
                continue

            field[height][width][2] = int(num_of_ore)
            # field[height][width][3] = 0 if num_of_ore == '0' else field[height][width][3]  # undigged:-1, was empty:0, ore found in the past:1

            if field[height][col][2] > 0:  #and field[height][col][1]==-1
                ore_this_turn.append([[height, col],int(num_of_ore)])
        
    # entity_count: number of entities visible to you
    # radar_cooldown: turns left until a new radar can be requested
    # trap_cooldown: turns left until a new trap can be requested
    ore_this_turn.sort(key=lambda x:x[0][1])
    print("all ore", ore_this_turn, file=sys.stderr)
    entity_count, radar_cooldown, trap_cooldown = [int(i) for i in input().split()]
    radar_taken, radar_num = 0, 0
    for i in range(entity_count):
        # id: unique id of the entity
        # type: 0 for your robot, 1 for other robot, 2 for radar, 3 for trap
        # y: position of the entity
        # item: if this entity is a robot, the item it is carrying (-1 for NONE, 2 for RADAR, 3 for TRAP, 4 for ORE)
        id, type, col, row, item = [int(j) for j in input().split()]

        if type==2:
            radar_num += 1
        elif type == 0:
            id %= 5
            myrobots[id][0] = [row, col]
            myrobots[id][1] = item

            # back home
            if item == 4:
                if order[id][0] == "DIG": # detect digging ore
                    field[order[id][1]][order[id][2]][3] = 1
                if radar_cooldown == 0 and not radar_taken and (previous_radar_num < 7 or len(ore_this_turn) < 5):
                    order[id][0], order[id][1], order[id][2] = "REQUEST", "RADAR", -1
                    myrobots[id][3] = 100
                    radar_taken = 1
                else:
                    order[id][0], order[id][1], order[id][2] = "MOVE", myrobots[id][0][0], 0
                    myrobots[id][3] = 90
                continue

            # digged but empty
            elif order[id][0] == "DIG" and distance(myrobots[id][0], [order[id][1],order[id][2]]) < 2 and item==-1:
                #field[order[id][1]][order[id][2]][3] = 0
                myrobots[id][3] = 10
            
            # just got radar
            if item == 2 and order[id][0] == "REQUEST":
                if radar_put_place:
                    targetrow, targetcol = radar_put_place.pop(0)
                else:
                    targetrow, targetcol = random.randint(5, 10), random.randint(10, 24)
                # for c in range(5,25): # find place to put
                #     if field[row][c-4][0] == -1 and field[row][c+4][0] == -1:
                #         if field[max(0, row-4)][c][0] == -1 and field[min(14,row+4)][c][0] == -1:
                #             targetrow, targetcol = row, c
                #             break
                #         targetrow, targetcol = row, c
                order[id][0], order[id][1], order[id][2] = "DIG",targetrow, targetcol
                myrobots[id][3] = 100
            
            # reset priority after finished going home
            if item == -1 and myrobots[id][3] < 99:
                myrobots[id][3] = 10

            # robots with nothing to do
            if myrobots[id][3] < 79:
                for ore_index in range(len(ore_this_turn)):
                    point, ore = ore_this_turn[ore_index]
                    dist = distance([row,col], point)
                    if dist < 2 and ore>0: # dig there
                        #print("distance must be under2", dist, file=sys.stderr)
                        order[id][0], order[id][1], order[id][2] = "DIG", point[0], point[1] 
                        myrobots[id][3] = 80
                        ore_this_turn[ore_index][1] -= 1
                        break
                    elif dist < 5 and myrobots[id][3] < 49 and ore>0:
                        order[id][0], order[id][1], order[id][2] = "MOVE", point[0], point[1]
                        myrobots[id][3] = 50
                    elif dist < 8 and myrobots[id][3] < 39:
                        order[id][0], order[id][1], order[id][2] = "MOVE", point[0], point[1]
                        myrobots[id][3] = 40
                    elif myrobots[id][3] < 39:
                        #print("distance must be over 7", dist, file=sys.stderr)
                        order[id][0], order[id][1], order[id][2] = "MOVE", point[0], point[1]
                        myrobots[id][3] = 30
                if not ore_this_turn:
                    if order[id][0] == 'MOVE':
                        order[id][0], order[id][1], order[id][2] = "DIG", myrobots[id][0][0], myrobots[id][0][1] + 1
                    elif order[id][0] == 'DIG':
                        order[id][0], order[id][1], order[id][2] = "MOVE", myrobots[id][0][0], myrobots[id][0][1] + 4

    previous_radar_num = radar_num
    # take radar
    nearest_robot, nearest_distance, nearest_priority = -1, 30, 49
    if radar_cooldown < 4 and radar_num < 6:
        for robot_idx in range(5):
            if myrobots[robot_idx][3] > 89:
                break
            turn_needed = myrobots[robot_idx][0][1] // 4 + 1 # move + request
            if nearest_distance > myrobots[robot_idx][0][1] and myrobots[robot_idx][3] <= nearest_priority:
                nearest_distance = myrobots[robot_idx][0][1] // 4 * 4
                nearest_robot = robot_idx
                nearest_priority = myrobots[robot_idx][3]
        else:
            if radar_cooldown - myrobots[robot_idx][0][1] // 4 + 1 < 1: # rest 1 turn at most
                order[nearest_robot][0], order[nearest_robot][1], order[nearest_robot][2] = "REQUEST", "RADAR", -1 
                myrobots[nearest_robot][3] = 100


            

    # To debug: print("robots", file=sys.stderr)
    print("rowcol, item, o, priority", myrobots, file=sys.stderr)
    #print order
    for i in range(5):
        if order[i][0] == "REQUEST":
            print(order[i][0] + " " + order[i][1])
        else:
            print(order[i][0] + " " + str(order[i][2]) + " " + str(order[i][1]))

    loop += 1