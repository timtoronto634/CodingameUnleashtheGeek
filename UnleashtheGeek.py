import sys
import math
import random

# Deliver more ore to hq (left side of the map) than your opponent. Use radars to find ore but beware of traps!

def defaultorder(x, y, visited):
    xnext = x
    ynext = y
    while not (0 < xnext < 29 and 0 < ynext < 14) and [xnext, ynext] in visited:
        dx = random.randint(-4,4)
        xnext  = x + dx if 0 < x+dx < 29 else x-dx
        dy = random.randint(-4, 4)
        ynext  = y + dy if 0 < y+dy < 14 else y-dy

    return "DIG {} {}".format(xnext, ynext)

def dig(x,y,visited):
    if [x,y] not in visited:
        return "DIG {} {}".format(x, y)
    else:
        return defaultorder(x,y,visited)

def whichorder(order):
    L = order.split()
    if len(L) == 2:
        return "R",-1,-1 # request
    else:
        return L[0][0], int(L[1]), int(L[2])

# height: size of the map
width, height = [int(i) for i in input().split()]
turn = 0
order = ["" for _ in range(5)]
trap = True
radar = True
radar_place, trap_place = 5, 5
visited = []
busy = [0,0,0,0,0]
# game loop
while True:
    # my_score: Amount of ore delivered
    my_score, opponent_score = [int(i) for i in input().split()]
    orehole = []
    for i in range(height):
        inputs = input().split()
        for j in range(width):
            # ore: amount of ore or "?" if unknown
            # hole: 1 if cell has a hole
            ore = inputs[2*j]
            hole = int(inputs[2*j+1])
            if ore != '?' and int(ore) > 0 and [j,i] not in visited:
                orehole.append([j, i])
                print("ore", ore, "xy:", j, i, file=sys.stderr)
    #orehole.sort(key=lambda x: x[1],reverse=True)
    # entity_count: number of entities visible to you
    # radar_cooldown: turns left until a new radar can be requested
    # trap_cooldown: turns left until a new trap can be requested
    entity_count, radar_cooldown, trap_cooldown = [int(i) for i in input().split()]
    if not radar_cooldown: radar =True
    if not trap_cooldown: trap = True
    
    for i in range(entity_count):
        # id: unique id of the entity
        # type: 0 for your robot, 1 for other robot, 2 for radar, 3 for trap
        # y: position of the entity
        # item: if this entity is a robot, the item it is carrying (-1 for NONE, 2 for RADAR, 3 for TRAP, 4 for ORE)
        id, type, x, y, item = [int(j) for j in input().split()]
        # my robot 
        if type==0:
            id %= 5
            if item == 4:
                order[id] = "MOVE 0 {}".format(y)
                busy[id] = 1

            elif x == 0 and item == -1 and radar:
                order[id] = "REQUEST RADAR"
                radar = False
            elif order[id] == "":
                order[id] = defaultorder(x,y,visited)
                visited.append([whichorder(order[id])[1],whichorder(order[id])[2]])
            elif x==0 and item == 2:
                order[id] = dig(radar_place, y,visited)
                radar_place += 2
                busy[id] = 0
    
            elif item == -1:
                order_kind, targetx, targety = whichorder(order[id])
                if order_kind == "R":
                    continue
                # still not digged yet
                elif x-1 <= targetx <= x+1 and y-1 <= targety <= y+1 and busy[id]:
                    busy[id] = 0
                # already finished digging
                elif x-1 <= targetx <= x+1 and y-1 <= targety <= y+1 and radar:
                    order[id] = "REQUEST RADAR"
                    radar = False
                # no item and already finished digging and there is order
                elif x-1 <= targetx <= x+1 and y-1 <= targety <= y+1 and orehole:
                    digx, digy = orehole.pop(random.randint(0,len(orehole)-1))
                    print("radar info catched!!",digx,digy, file=sys.stderr)
                    order[id] = dig(digx,digy,visited)
                    busy[id] = 1

                elif x-1 <= targetx <= x+1 and y-1 <= targety <= y+1:
                    order[id] = defaultorder(x,y,visited)
                    visited.append([x, y])
                    busy[id] = 1
            else:
                print("else...", file=sys.stderr)
        
                
    for i in range(5):

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)

        # WAIT|MOVE x y|DIG x y|REQUEST item
        print(order[i])
            
    turn += 1
    if radar_place > 29:
        radar_place = random.randint(2,29)