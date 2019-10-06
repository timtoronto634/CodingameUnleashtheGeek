import sys
import math
import random

def distance(cur_point, target_point):
    return abs(cur_point[0] - target_point[0]) + abs(cur_point[1] - target_point[1])

# height: size of the map
widths, heights = [int(i) for i in input().split()]
field = [[[-1,-1,-1,-1] for w in range(widths)] for h in range(heights)] # field info. [isinradar, istrap, #ofore, diggedbyme]
myrobots = [[[],-1,[-1,-1,-1],-1] for _ in range(5)]  # [[row,col], item, [orderkind, targetrow,targetcol], orderpriority]
order = [["",-1,-1] for _ in range(5)] # MOVE row col | DIG row col | REQUEST
# game loop
loop = 0

# first four turn
for initial in range(4):
    my_score, opponent_score = [int(i) for i in input().split()]

    for height in range(heights):
        inputs = input().split()
        for width in range(widths):
            # ore: amount of ore or "?" if unknown
            # hole: 1 if cell has a hole
            num_of_ore = inputs[2*width]
            ishole = int(inputs[2*width+1])

            # update field
            field[height][width][2] = '?' if num_of_ore == '?' else int(num_of_ore)
            #field[height][width][3] = 0 if num_of_ore == '0' else field[height][width][3]  # undigged:-1, was empty:0, ore found in the past:1
        
    entity_count, radar_cooldown, trap_cooldown = [int(i) for i in input().split()]
    for i in range(entity_count):
        # id: unique id of the entity
        # type: 0 for your robot, 1 for other robot, 2 for radar, 3 for trap
        # y: position of the entity
        # item: if this entity is a robot, the item it is carrying (-1 for NONE, 2 for RADAR, 3 for TRAP, 4 for ORE)
        id, type, col, row, item = [int(j) for j in input().split()]

        if type == 0:
            id %= 5
            myrobots[id][0] = [row, col]
            myrobots[id][1] = item

            # detect digging ore
            if item == 4 and order[id][0] == "DIG":
                field[order[id][1]][order[id][2]][3] = 1
            # digged but empty
            elif order[id][0] == "DIG" and distance(myrobots[id][0], [order[id][1],order[id][2]]) < 2:
                field[order[id][1]][order[id][2]][3] = 0
        
    if loop == 0:
        for i in range(5):
            order[i][0] = "MOVE" # "MOVE row col"
            order[i][1], order[i][2] = myrobots[i][0][0], 4
        order[2] = ["REQUEST", "RADAR", -1]
    elif loop == 1:
        for i in range(5):
            if myrobots[i][1] == 2:
                order[i][0] = "MOVE"
                order[i][1], order[i][2] = 4, 5
            else:
                order[i][0] = "DIG" # dig right
                order[i][1], order[i][2] = myrobots[i][0][0], 5
    elif loop == 2:
        for i in range(5):
            if myrobots[i][1] == 2:
                order[i][0] = "DIG"
                order[i][1], order[i][2] = 4, 5
            elif myrobots[i][1] == 4:
                order[i][0] = "MOVE"
                order[i][1], order[i][2] = myrobots[i][0][0], 0
                myrobots[i][3] = 90
            else:
                order[i][0] = "MOVE"
                order[i][1], order[i][2] = myrobots[i][0][0], myrobots[i][0][1]+2
    elif loop == 3:
        for i in range(5):
            if myrobots[i][1] == 2:
                order[i][0] = "DIG"
                order[i][1], order[i][2] = 4, 5
                myrobots[i][3] = 10
            elif myrobots[i][1] == 4:
                order[i][0] = "MOVE"
                order[i][1], order[i][2] = myrobots[i][0][0], 0
                myrobots[i][3] = 90
            elif myrobots[i][0][1] < 4:
                order[i][0] = "MOVE"
                order[i][1], order[i][2] = myrobots[i][0][0]+1, myrobots[i][0][1]+3
                myrobots[i][3] = 10
            else:
                order[i][0] = "DIG"
                order[i][1], order[i][2] = myrobots[i][0][0], myrobots[i][0][1]+1
                myrobots[i][3] = 10
    
    #print order
    for i in range(5):
        if order[i][0] == "REQUEST":
            print(order[i][0] + " " + order[i][1])
        else:
            print(order[i][0] + " " + str(order[i][2]) + " " + str(order[i][1]))
    loop += 1

radar_put_place = [[10,8],[1,11],[8,2],[6,13],[10,18],[3,19], [7,23]]
previous_radar_num = 0
while True:
    # my_score: Amount of ore delivered
    my_score, opponent_score = [int(i) for i in input().split()]
    ore_this_turn = []
    for height in range(heights):
        inputs = input().split()
        for width in range(widths):
            # ore: amount of ore or "?" if unknown
            # hole: 1 if cell has a hole
            num_of_ore = inputs[2*width]
            ishole = int(inputs[2*width+1])

            # update field
            if num_of_ore == '?':
                continue

            field[height][width][2] = int(num_of_ore)
            # field[height][width][3] = 0 if num_of_ore == '0' else field[height][width][3]  # undigged:-1, was empty:0, ore found in the past:1

            if field[height][width][2] > 0:  #and field[height][width][1]==-1
                ore_this_turn.append([[height, width],int(num_of_ore)])
        
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