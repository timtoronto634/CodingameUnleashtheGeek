"""

Amadeusium is a rare and valuable crystal ore which is only found on inhospitable planets. As one of two competing mining companies, you must control the robots on-site to unearth as much ore as you can.

Deliver more Amadeusium than your opponent!
 	Rules
Both players control a team of several robots. The teams start out at the same points on the map, at the headquarters. The robots can use radars from the headquarters to detect and mine Amadeusium veins. They may also trap certain areas of the map with EMP traps. These can be triggered by robots which are then rendered inoperable.


The map


The game is played on a grid 30 cells wide by 15 cells high. The coordinates x=0, y=0 corresponds to the top left cell.

The first column of cells is considered to be part of the headquarters. This is where Amadeusium ore must be returned to once mined and where objects are requested.

The cells that contain Amadeusium ore are called vein cells. Veins are not visible to the players unless they are within the range of the player's radar. There are no vein cells in the headquarters.

Robots can drill a hole on any cell (except the headquarters'). Holes are visible to both players and do not impede movement.


Robots


Each robot can hold 1 item in its inventory.

A robot may:

REQUEST an item from the headquarters.
MOVE towards a given cell.
DIG on a cell. This will, in order:
Create a hole on this cell if there isn't one already.
Bury any item the robot is holding into the hole.
If digging on a vein cell and ore was not buried on step 2, place one unit of ore into the robot's inventory.
WAIT to do nothing.
Details:

Robots may only dig on the cell they occupy or neighbouring cells. Cells have 4 neighbours: up, left, right, and down.
Robots on any cell part of the headquarters will automatically deliver any ore it is holding.
Robots can occupy the same cell.
Robots cannot leave the grid.
Robots' inventories are not visible to the opponent.
Items


Amadeusium Ore is considered an item and should be delivered to the headquarters to score 1 point.

At the headquarters, robots may request one of two possible items: a RADAR or a TRAP.

If an item is taken from the headquarters, that item will no longer be available for the robots of the same team for 5 turns.

A trap buried inside a hole will go off if any robot uses the DIG command on the cell it is buried in. The EMP pulse destroys any robots on the cell or on the 4 neighbouring cells. Any other trap caught in the pulse will also go off, causing a chain reaction.

A radar buried inside a hole will grant the ability to see the amount of buried ore in veins within a range of 4 cells, for the team which buried it. If an opponent robot uses the DIG on the cell the radar is buried in, the radar is destroyed.


Action order for one turn

If DIG commands would trigger Traps, they go off.
The other DIG commands are resolved.
REQUEST commands are resolved.
Request timers are decremented.
MOVE and WAIT commands are resolved.
Ore is delivered to the headquarters.
Victory Conditions
After 200 rounds, your team has delivered the most Amadeusium ore.
You have delivered more ore than your opponent and they have no more active robots.
Defeat Conditions
Your program does not provide one valid command per robot in time, including destroyed robots.
 	Technical Details
Robots can insert ore into a cell, the cell becomes a vein.
Each robot, radar and trap has a unique id.
Receiving an item from the headquarters will destroy any item a robot may already be holding.
When several robots of the same team request an item, robots with no item will be given priority for the request.
Traps have no effect on buried radars and ore.
If a robot holding an item is destroyed, the item is lost.
You can check out the source code of this game on this GitHub repo.

 	Game Input
Initialization Input
Line 1: two integers width and height for the size of the map. The leftmost row are cells with access to the headquarters.
Input for One Game Turn
First line: Two integers:
myScore for the amount of ore you delivered to the elevator.
enemyScore for the amount ore your opponent delivered to the elevator.
Next height lines: each line has width * 2 variables: ore and hole.
ore is:
? character if this cell is not within range of a radar you control.
A positive integer otherwise, for the amount of ore this cell contains.
hole is:
1 if this cell has a hole on it.
0 otherwise.


Next line: Four integers
entityCount for the amount of robots, radars and traps currently visible to you.
radarCooldown for the number of turns until a new RADAR can be requested.
trapCooldown for the number of turns until a new TRAP can be requested.
Next entityCount lines: 5 integers to describe each entity
id: entity's unique id.
type:
0: one of your robots
1: one of your opponent's robots
2: one of your buried radars
3: one of your buried traps
x & y: the entity's position.
If this entity is a destroyed robot, x y will equal -1 -1
item: if this entity is a robot, the item this robot is carrying:
-1for nothing
2for a radar
3for a trap
4for a unit of Amadeusium ore
Output
5 lines, one for each robot, in the same order in which they were given, containing one of the following actions:
WAIT: the robot does nothing.
MOVE x y: the robot moves 4 cells towards the given cell.
DIG x y: the robot attempts to bury the item it is carrying in the target cell, retrieve ore from the cell, or both. If the cell is not adjacent, the robot will execute a MOVE command towards the target instead.
REQUEST followed by RADAR or TRAP: the robot attempts to take an item from the headquarters. If the robot is not on a headquarters cell, the robot will execute the MOVE 0 y command instead, where y is the ordinate of the robot.
You may append text to a command to have it displayed in the viewer above your robot.

Examples:
MOVE 8 4
WAIT nothing to do...
You must provide a command to all robots each turn, even if they are destroyed. Destroyed robots will ignore the command.
Constraints
Response time per turn ≤ 50ms
Response time for the first turn ≤ 1000ms
"""


import sys
import math
import random

# Deliver more ore to hq (left side of the map) than your opponent. Use radars to find ore but beware of traps!

def defaultorder(x, y, visited):
    xnext = x
    ynext = y
    while not (0 < xnext < 29 and 0 < ynext < 14) and [xnext, ynext] not in visited:
        dx = random.randint(-4,4)
        xnext  = x + dx if 0 < x+dx < 29 else x-dx
        dy = random.randint(-4, 4)
        ynext  = y + dy if 0 < y+dy < 14 else y-dy
    visited.append([xnext, ynext])
    return "DIG {} {}".format(xnext, ynext)

def dig(x,y,visited):
    if [x,y] not in visited:
        visited.append([x,y])
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
            if ore != '?' and int(ore) > 0 and not hole:
                orehole.append([j, i])
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
            elif x == 0 and item == -1 and trap:
                order[id] = "REQUEST TRAP"
                trap = False
            elif order[id] == "":
                order[id] = defaultorder(x,y,visited)
            elif x==0 and item == 2:
                order[id] = dig(radar_place, y,visited)
                radar_place += 2
                busy[id] = 0
            elif x==0 and item == 3:
                order[id] = "DIG {} {}".format(trap_place, y)
                visited.append([trap_place, y])
                busy[id] = 0
                trap_place += 2
    
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
                    busy[id] = 1
            else:
                print("else...", file=sys.stderr)
        
        # if trap found, try not to dig there
        if type == 3:
            visited.append([x,y])
                
    for i in range(5):

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)

        # WAIT|MOVE x y|DIG x y|REQUEST item
        print(order[i])
            
    turn += 1
    radar_place = min(radar_place % 30, 5)
    trap_place = min(trap_place % 30, 5)
    