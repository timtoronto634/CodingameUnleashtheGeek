import sys
import math
import random

def debug(strs, *vars):
    print(strs, *vars, file=sys.stderr)

class Robot(object):
    def __init__(self, row, col):
        self.row, self.col = row, col
    
    def update(self, row, col):
        self.row, self.col = row, col

class MyRobot(Robot):
    def __init__(self,row,col,item):
        super().__init__(row, col)
        self.item = item
        self.orderkind = ""
        self.destrow, self.destcol = -1, -1
        self.request_item = "RADAR"
        self.orderpriority = 10

    def update(self, row, col, item):
        self.item = item
        return super().update(row, col)

    def dig(self, row, col, priority):
        self.orderkind = "DIG"
        self.destrow, self.destcol = row, col
        self.orderpriority = priority
    
    def changeDestination(self, row, col, field):
        for r, c in [[0,0], [0, 1],[1,0],[0,-1],[-1,0]]:
            if 0<=row+r<15 and 0<=col+c<30 and not field[row+r][col+c].isdangerous():
                self.destrow = row+r
                self.destcol = col+c
                return

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
    def __init__(self, row, col):
        super().__init__(row, col)
        self.prerow, self.preprerow = -1, -1
        self.precol, self.preprecol = 0, 0
        self.item = False
    
    def update(self, row, col):
        self.prerow, self.preprerow = self.row, self.prerow
        self.precol, self.preprecol = self.col, self.precol
        return super().update(row, col)
    
    def anyalert(self):
        # detect no move
        if self.prerow == self.row and self.precol == self.col:
            if self.col == 0:
                self.item = True
            elif self.item == True:
                # put item
                self.item = False
                return self._dig_places()
        return []

    def _dig_places(self):
        possibility = []
        path_length = abs(self.preprerow - self.row) + abs(self.preprecol - self.col)
        for r, c in [[0,0],[0, 1],[1,0],[0,-1],[-1,0]]:
            if 0<=self.row+r<15 and 0<=self.col+c<30 and abs(self.preprerow - (self.row+r)) + abs(self.preprecol - (self.col+c)) >= path_length:
                possibility.append([self.row+r, self.col+c])
        return possibility
    
class Cell(object):
    def __init__(self):
        self.inRadarRange = False
        self.hasownTrap = False
        self.numofOre = -1 #-1 for unknown
        self.hole = False
        self.diggedbyme = False
        self.wasOre = False

        self.TrapPossibility = False
    
    def foundOre(self):
        self.wasOre = True
        self.diggedbyme = True
    
    def noOre(self):
        self.wasOre = False
        self.numofOre = 0
        self.diggedbyme = True
    
    def hasTrap(self):
        self.hasownTrap = True
        self.diggedbyme = True
        self.wasOre = False
    
    def radardig(self):
        self.numofOre = self.numofOre - 1 if self.numofOre>0 else self.numofOre
        self.hole = True
        self.diggedbyme = True
    
    def rangeRadar(self):
        self.inRadarRange = True
        if self.numofOre == -1:
            self.numofOre = 0
        
    def alert(self):
        if self.hole:
            self.TrapPossibility = True
    
    def isdangerous(self):
        return self.hasownTrap or self.TrapPossibility

class Game(object):
    def __init__(self):
        self.myRadarplacement = []
        self.myTrapplacement = []
        self.shortofRadar = True
        self.rest = None
    
    def putTrap(self, row, col):
        if [row, col] not in self.myTrapplacement:
            self.myTrapplacement.append([row, col])

    def nextplace_to_put_trap(self, trap_place, robot):
        # put trap if diggedbyme==False and hole==True and hasownTrap==False and ore>2
        cur_col = 5
        traprow, trapcol = robot.row, robot.col+1
        for row, col in trap_place:
            if col > cur_col:
                cur_col = col
                traprow, trapcol = row, col
        return traprow, trapcol
    
    def putRadar(self, row, col):
        if [row, col] not in self.myRadarplacement:
            self.myRadarplacement.append([row, col])
            return True
        return False
    
    def nextplace_to_put_radar(self, field, robot):
        lastRadar = max(self.myRadarplacement, key=lambda x: x[1])
        [row, col] = lastRadar
        if row != 7:
            if row == 3 and not field[11][col].inRadarRange:
                return 11, col
            elif row == 11 and not field[3][col].inRadarRange:
                return 3, col
            elif col < 25:
                return 7, col+5


        # second radar
        if len(self.myRadarplacement) == 1:
            leftup, leftdown, rightup, rightdown = 0, 0, 0, 0
            for r in range(-4,1):
                for c in range(-4-r, 1):
                    if 0<=row+r<15 and 0<=col+c<30:
                        leftup += field[row+r][col+c].numofOre
                    else:
                        leftup = 0
                        break
                for c in range(1,5+r):
                    if 0<=row+r<15 and 0<=col+c<30:
                        rightup += field[row+r][col+c].numofOre
            for r in range(0, 5):
                for c in range(-4+r, 1):
                    if 0<=row+r<15 and 0<=col+c<30:
                        leftdown += field[row+r][col+c].numofOre
                for c in range(1,5-r):
                    if 0<=row+r<15 and 0<=col+c<30:
                        rightdown += field[row+r][col+c].numofOre

            if max(leftup, leftdown, rightup, rightdown) < 2: # no clue
                self.rest = [3,col-5,11,col-5]
                if robot.row < 7:
                    return 3, col + 5
                else:
                    return 11, col + 5
            if leftup == max([leftup, leftdown, rightup, rightdown]):
                if not field[row-4][col-5].inRadarRange:
                    self.rest = [11, col-5]
                    return 3, col-5
            leftup = 0
            if leftdown == max([leftup, leftdown, rightup, rightdown]):
                if not field[row+4][col-5].inRadarRange:
                    self.rest = [3, col-5]
                    return 11, col-5
            leftdown = 0
            self.rest = [3,col-5,11,col-5]
            if rightup == max([leftup, leftdown, rightup, rightdown]):
                return 3, col+5
            rightup = 0
            if rightdown == max([leftup, leftdown, rightup, rightdown]):
                return 11, col+5
        
        if row == 7 and col < 25:
            rightup, rightdown = 0, 0
            for c in range(0, 5):
                for r in range(-4+c, 0):
                    rightup += field[row+r][col+c].numofOre
                for r in range(1,5-c):
                    rightdown += field[row+r][col+c].numofOre
            if rightup < rightdown:
                return 11, col+5
            else:
                return 3, col+5

        if self.rest:
            col = self.rest.pop()
            row = self.rest.pop()
            return row, col

        # final option
        nextrow, nextcol = -1, -1
        for r in range(15):
            consistance = 0
            for c in range(30):
                if field[r][c].inRadarRange:
                    consistance = 0
                else:
                    consistance += 1
                if consistance == 7 and (nextcol == -1 or nextcol > c-3):
                    nextrow, nextcol = r, c-3
        if nextcol == -1:
            self.shortofRadar = False
            nextrow, nextcol = robot.row, 1
        return nextrow, nextcol

                
"""
priority:
    100 : request radar and put radar when short
     90 : bring ore back
     80 : dig

     70 : break opponents radar with 0 or 1 move

     50: go to ore place from radar with 1 move
     49: go to ore place from radar with n move (-2n priority)

     35: dig ore place from wasore
     30: go to ore place from wasore with n move (-n+1 priority)

     20: random dig
     10: nothing
"""

def distance(robotrow, robotcol, cellrow, cellcol):
    return abs(robotrow - cellrow) + abs(robotcol - cellcol)

ncol, nrow = [int(i) for i in input().split()]
field = [[Cell() for col in range(ncol)] for row in range(nrow)]
myrobots = [MyRobot(-1,-1,-1) for _ in range(5)]
enemies = [EnemyRobot(-1,-1) for _ in range(5)]

#-------------------------------------------------------------------------------------------------------------------------------------
# game start
game = Game()
turn = 0
# first four turn
for initial in range(4):
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
                if item == 4:
                    field[robot.destrow][robot.destcol].foundOre()
                else:
                    field[robot.destrow][robot.destcol].noOre()
        
        elif type == 1:
            id %= 5
            robot = enemies[id]
            robot.update(row, col)
        
        elif type == 2:
            isnew = game.putRadar(row, col)
            if isnew:
                for i in range(-4,5):
                    for j in range(-4+abs(i), 5-abs(i)):
                        if 0<=row+i<15 and 0<=col+j<30:
                            field[row+i][col+j].rangeRadar()

    if turn == 0:
        nearest_dist, nearest_robot_idx = 7, 0
        for robot_idx in range(5):
            robot = myrobots[robot_idx]
            robot.move(robot.row + (2 * (robot.row < 7) - 1), 3, 10)
            if abs(7 - robot.row) < nearest_dist:
                nearest_dist = abs(7-robot.row)
                nearest_robot_idx = robot_idx
        myrobots[nearest_robot_idx].request("RADAR", 90)
    elif turn == 1:
        for robot_idx in range(5):
            robot = myrobots[robot_idx]
            if robot.item ==2:
                robot.move(7, max(0, 4 - abs(7-robot.row)), 90)
            elif robot.item == 4:
                robot.home()
            else:
                robot.dig(robot.row, robot.col+1, 10)

    elif turn == 2:
        for robot_idx in range(5):
            robot = myrobots[robot_idx]
            if robot.item ==2:
                robot.move(7, robot.col + max(0, 4 - abs(7-robot.row)), 90)
            elif robot.item==4:
                robot.home()
            else:
                robot.move(robot.row + (2 * (robot.row < 7) - 1), robot.col+3, 10)
    elif turn == 3:
        for robot_idx in range(5):
            robot = myrobots[robot_idx]
            if robot.item == 2:
                robot.dig(robot.row, robot.col+1, 90)
            elif robot.item==4:
                robot.home()
            else:
                robot.dig(robot.row, robot.col+1,50)

    #print order
    for robot_idx in range(5):
        myrobots[robot_idx].printorder()
    turn += 1

# ----------------------------------------------------------------------------------------------------------------------------------------------
while True:
    my_score, opponent_score = [int(i) for i in input().split()]
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
    for i in range(entity_count):
        # id: unique id of the entity
        # type: 0 for your robot, 1 for other robot, 2 for radar, 3 for trap
        # x y: position of the entity
        # item: if this entity is a robot, the item it is carrying (-1 for NONE, 2 for RADAR, 3 for TRAP, 4 for ORE)
        id, type, col, row, item = [int(j) for j in input().split()]

        if type == 0:
            id %= 5
            robot = myrobots[id]
            robot.update(row, col, item)

            if robot.orderkind == "DIG":
                if item == 4:
                    field[robot.destrow][robot.destcol].foundOre()
                else:
                    field[robot.destrow][robot.destcol].noOre()

        elif type == 1:
            id %= 5
            robot = enemies[id]
            robot.update(row, col)

        elif type == 2:
            isnew = game.putRadar(row, col)
            if isnew:
                for i in range(-4,5):
                    for j in range(-4+abs(i), 5-abs(i)):
                        if 0<=row+i<15 and 0<=col+j<30:
                            field[row+i][col+j].rangeRadar()

        elif type == 3:
            game.putTrap(row, col)

    # detect trap
    for enemy_idx in range(5):
        enemy_robot = enemies[enemy_idx]
        alert = enemy_robot.anyalert()
        if alert != []:
            for r,c in alert:
                field[r][c].alert()

    # for each cell
    ore_place, trap_place, was_ore, near_was_ore = [], [], [], []
    for row in range(nrow):
        for col in range(ncol):
            cell = field[row][col]
            if cell.numofOre > 0 and cell.hasownTrap==False:
                if not cell.TrapPossibility:
                    ore_place.append([row, col])
                if cell.numofOre>1 and cell.diggedbyme==False and cell.hole==True and not cell.TrapPossibility:
                    trap_place.append([row,col])
            elif cell.numofOre == -1 and cell.wasOre:
                if not cell.hasownTrap and not cell.TrapPossibility:
                    was_ore.append([row,col])
                for r, c in [[0, 1],[1,0],[0,-1],[-1,0]]:
                    if 0<=row+r<15 and 0<=col+c<30 and field[row][col].numofOre == -1 and field[row][col].TrapPossibility==False and field[row][col].hasownTrap==False:
                        near_was_ore.append([row+r, col+c])

    radar_incharge, trap_incharge = False, False
    # put order
    for robot_idx in range(5):
        robot = myrobots[robot_idx]
        if robot.item == 4:
            robot.home()
        elif robot.item == 2:
            if robot.orderkind == 'REQUEST':
                radarrow, radarcol = game.nextplace_to_put_radar(field, robot)
                robot.move(radarrow, radarcol, 100)
            if field[robot.destrow][robot.destcol].inRadarRange:
                radarrow, radarcol = game.nextplace_to_put_radar(field, robot)
                robot.move(radarrow, radarcol, 100)
            if distance(robot.row, robot.col, robot.destrow, robot.destcol) < 2:
                if field[robot.destrow][robot.destcol].isdangerous():
                    robot.changeDestination(robot.row, robot.col, field)
                else:
                    robot.dig(robot.destrow, robot.destcol, 100)
        elif robot.item == 3:
            if robot.orderkind == 'REQUEST':
                traprow, trapcol = game.nextplace_to_put_trap(trap_place, robot)
                if distance(robot.row, robot.col, traprow, trapcol) < 2:
                    robot.dig(traprow, trapcol, 80)
                else:
                    robot.move(traprow, trapcol, 80)
            if field[robot.destrow][robot.destcol].numofOre < 2 or field[robot.destrow][robot.destcol].hasownTrap:
                traprow, trapcol = game.nextplace_to_put_trap(trap_place, robot)
                robot.move(traprow, trapcol, 80)
            if distance(robot.row, robot.col, robot.destrow, robot.destcol) < 2:
                robot.dig(robot.destrow, robot.destcol, 80)
                field[robot.destrow][robot.destcol].hasTrap()
        elif robot.item == -1:
            robot.orderpriority = 10
            # when short of radar
            if robot.col == 0 and radar_cooldown < 2 and game.shortofRadar and not radar_incharge and len(ore_place)<10:
                robot.request("RADAR", 100)
                radar_incharge = True
            # when need trap
            elif robot.col == 0 and len(trap_place) > 4 and trap_cooldown == 0 and turn > 40 and not trap_incharge:
                robot.request("TRAP", 80)
                trap_incharge = True
            else:
                for candidate_idx in range(len(ore_place)):
                    row, col = ore_place[candidate_idx]
                    dist = distance(robot.row, robot.col, row, col)
                    if dist < 2 and field[row][col].numofOre > 0 and not field[row][col].isdangerous():
                        robot.dig(row,col, 80)
                        field[row][col].radardig()
                        if field[row][col].numofOre == 0:
                            ore_place.remove([row, col])
                        break
                    elif robot.orderpriority < 50 - dist // 4 * 2 or (robot.orderpriority == 50 - dist // 4 * 2 and col < robot.destcol):
                        robot.move(row, col - 1, 50 - dist // 4 * 2)

            # when nothing to do
            if robot.orderpriority == 10: # was ore
                for candidate_idx in range(len(was_ore)):
                    row, col = was_ore[candidate_idx]
                    dist = distance(robot.row, robot.col, row, col)
                    if dist < 2 and field[row][col].numofOre != 0 and not field[row][col].isdangerous():
                        robot.dig(row,col, 35)
                        was_ore.remove([row,col])
                        break
                    elif robot.orderpriority < 30 - ( dist // 4):
                        robot.move(row, col-1, 30-(dist//4))
                if robot.orderpriority == 10: # near was ore
                    for candidate_idx in range(len(near_was_ore)):
                        row, col = near_was_ore[candidate_idx]
                        dist = distance(robot.row, robot.col, row, col)
                        if dist < 2 and field[row][col].numofOre != 0 and not field[row][col].isdangerous():
                            robot.dig(row,col, 30)
                            near_was_ore.remove([row,col])
                            break
                        elif robot.orderpriority < 30 - ( dist // 4):
                            robot.move(row, col-1, 30-(dist//4))
                if robot.orderpriority == 10: # really nothing to do
                    for r, c in [[0, 1],[1,0],[0,-1],[-1,0],[0,0]]:
                        if 0<=robot.row+r<15 and 0<=robot.col+c<30 and field[robot.row+r][robot.col+c].numofOre != 0 and not field[row][col].isdangerous():
                            robot.dig(robot.row+r, robot.col+c, 20)
                            break
                    else:
                        robot.move(14,29, 11)

    # adjust order
    for robot_idx in range(5):
        robot = myrobots[robot_idx]
        if robot.orderpriority > 80: continue
        collision = 0
        for other_idx in range(5):
            if robot_idx == other_idx: continue
            other = myrobots[other_idx]
            if robot.destrow == other.destrow and robot.destcol==other.destcol:
                collision += 1
        if field[robot.destrow][robot.destcol].numofOre <= collision and robot.orderpriority <= other.orderpriority:
            originalrow, originalcol = robot.destrow, robot.destcol
            for candidate_idx in range(len(ore_place)):
                row, col = ore_place[candidate_idx]
                if row == originalrow and col == originalcol: continue
                dist = distance(robot.row, robot.col, row, col)
                if dist < 2 and field[row][col].numofOre > 0 and field[row][col].hasownTrap==False and field[row][col].TrapPossibility==False:
                    robot.dig(row,col, 80)
                    field[row][col].radardig()
                    if field[row][col].numofOre == 0:
                        ore_place.remove([row, col])
                    break
                elif robot.orderpriority < 50 - dist // 4 * 2 or (robot.orderpriority == 50 - dist // 4 * 2 and col < robot.destcol):
                    robot.move(row, col - 1, 50 - dist // 4 * 2)
    
    #print order
    for robot_idx in range(5):
        myrobots[robot_idx].printorder()
    
    if turn >190 and len(ore_place) < 2:
        break
    turn += 1

# ----------------------------------------------------------------------------------------------------------------------------------------------
debug("==========================================")
while True:
    # my_score: Amount of ore delivered
    my_score, opponent_score = [int(i) for i in input().split()]
    for row in range(nrow):
        inputs = input().split()
        for col in range(ncol):
            num_of_ore = inputs[2*col]
            ishole = int(inputs[2*col+1])

            # update field
            if num_of_ore != '?':
                field[row][col].numofOre = int(num_of_ore)
            field[row][col].hole = bool(ishole)

    entity_count, radar_cooldown, trap_cooldown = [int(i) for i in input().split()]
    for i in range(entity_count):
        # id: unique id of the entity
        # type: 0 for your robot, 1 for other robot, 2 for radar, 3 for trap
        # x y: position of the entity
        # item: if this entity is a robot, the item it is carrying (-1 for NONE, 2 for RADAR, 3 for TRAP, 4 for ORE)
        id, type, col, row, item = [int(j) for j in input().split()]

        if type == 0:
            id %= 5
            robot = myrobots[id]
            robot.update(row, col, item)

            if robot.orderkind == "DIG":
                if item == 4:
                    field[robot.destrow][robot.destcol].foundOre()
                else:
                    field[robot.destrow][robot.destcol].noOre()
        elif type == 3:
            game.putTrap(row, col)
        elif type == 1:
            id %= 5
            robot = enemies[id]
            robot.update(row, col)

    # for each cell
    ore_place, was_ore, near_was_ore = [], [], []
    trap_place = []
    for row in range(nrow):
        for col in range(ncol):
            cell = field[row][col]
            if cell.numofOre > 0 and cell.hasownTrap==False:
                ore_place.append([row, col])
            elif cell.numofOre == -1 and cell.wasOre:
                if not cell.hasownTrap:
                    was_ore.append([row,col])
                for r, c in [[0, 1],[1,0],[0,-1],[-1,0]]:
                    if 0<=row+r<15 and 0<=col+c<30 and field[row][col].numofOre == -1 and field[row][col].hasownTrap==False:
                        near_was_ore.append([row+r, col+c])

    radar_incharge, trap_incharge = False, False
    # put order
    for robot_idx in range(5):
        robot = myrobots[robot_idx]
        if robot.item == 4:
            robot.home()
        elif robot.item == 2:
            if robot.orderkind == 'REQUEST':
                radarrow, radarcol = game.nextplace_to_put_radar(field, robot)
                robot.move(radarrow, radarcol, 100)
            if field[robot.destrow][robot.destcol].inRadarRange:
                radarrow, radarcol = game.nextplace_to_put_radar(field, robot)
                robot.move(radarrow, radarcol, 100)
            if distance(robot.row, robot.col, robot.destrow, robot.destcol) < 2:
                if field[robot.destrow][robot.destcol].hasownTrap==True:
                    robot.changeDestination(robot.row, robot.col, field)
                else:
                    robot.dig(robot.destrow, robot.destcol, 100)
        elif robot.item == -1:
            robot.orderpriority = 10
            for candidate_idx in range(len(ore_place)):
                row, col = ore_place[candidate_idx]
                dist = distance(robot.row, robot.col, row, col)
                if dist < 2 and field[row][col].numofOre > 0 and field[row][col].hasownTrap==False and field[row][col].TrapPossibility==False:
                    robot.dig(row,col, 80)
                    field[row][col].radardig()
                    if field[row][col].numofOre == 0:
                        ore_place.remove([row, col])
                    break
                elif robot.orderpriority < 50 - dist // 4 * 2 or (robot.orderpriority == 50 - dist // 4 * 2 and col < robot.destcol):
                    robot.move(row, col - 1, 50 - dist // 4 * 2)


            # nothing to do
            if robot.orderpriority == 10:
                for candidate_idx in range(len(was_ore)):
                    row, col = was_ore[candidate_idx]
                    dist = distance(robot.row, robot.col, row, col)
                    if dist < 2 and field[row][col].numofOre != 0 and field[row][col].hasownTrap==False:
                        robot.dig(row,col, 35)
                        was_ore.remove([row,col])
                        break
                    elif robot.orderpriority < 30 - ( dist // 4):
                        robot.move(row, col-1, 30-(dist//4))
                if robot.orderpriority == 10: # really nothing to do
                    for candidate_idx in range(len(near_was_ore)):
                        row, col = near_was_ore[candidate_idx]
                        dist = distance(robot.row, robot.col, row, col)
                        if dist < 2 and field[row][col].numofOre != 0 and field[row][col].hasownTrap==False:
                            robot.dig(row,col, 30)
                            near_was_ore.remove([row,col])
                            break
                        elif robot.orderpriority < 30 - ( dist // 4):
                            robot.move(row, col-1, 30-(dist//4))
                if robot.orderpriority == 10: # really nothing to do
                    for r, c in [[0, 1],[1,0],[0,-1],[-1,0],[0,0]]:
                        if 0<=robot.row+r<15 and 0<=robot.col+c<30 and field[robot.row+r][robot.col+c].numofOre != 0 and field[row][col].hasownTrap==False:
                            robot.dig(robot.row+r, robot.col+c, 20)
                            break
                    else:
                        robot.move(14,29, 11)
    #print order
    for robot_idx in range(5):
        myrobots[robot_idx].printorder()