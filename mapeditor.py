import pygame
import keyboard as kb
import json

pygame.init()
screen = pygame.display.set_mode((1280,720))
screen.fill((0, 0, 0))
pygame.display.set_caption("Racing")
clock = pygame.time.Clock()


Map = [[],[]]

Rewards = []

filename = "map3.txt"
with open(filename,"r") as f:
    data = json.loads(f.read())

Map = data["Map"].copy()
Rewards = data["Rewards"].copy()
BCount = False

Count = len(Rewards)

RewardMode = False
Line2Mode = False

while True:
    screen.fill((0, 0, 0))
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            print("saving...")
            data = { "Map": Map, "Rewards": Rewards }
            file = json.dumps( data )
            with open( filename, "w" ) as f:
                f.write( file )
            print("save")
            print("exit")
            exit()
        if i.type == pygame.MOUSEBUTTONDOWN:
            if i.button == 1:
                if not RewardMode:
                    if not Line2Mode:
                        Map[0].append([i.pos[0],i.pos[1]])
                    else:
                        Map[1].append([i.pos[0],i.pos[1]])
                    pygame.draw.circle(screen, (255,0,0), i.pos, 3)
                else:

                    if not BCount:
                        Rewards.append([i.pos[0],i.pos[1]])
                        BCount = True
                    else:
                        Rewards[Count].append(i.pos[0])
                        Rewards[Count].append(i.pos[1])
                        Count+=1
                        BCount = False



    if kb.is_pressed("q"):
        Line2Mode = True
    if kb.is_pressed("r"):
        RewardMode = True
    if kb.is_pressed("esc"):
        Map = [[],[]]
        Rewards = []
        RewardMode = False
        Line2Mode = False
        BCount = False
    if kb.is_pressed("s"):
        print( "saving..." )
        data = { "Map": Map, "Rewards": Rewards }
        file = json.dumps( data )
        with open( filename, "w" ) as f:
            f.write( file )
        print( "save" )
    if len(Map) > 1:
        #print(var)
        for row in Map:
            for i in range( len( row ) ):
                try:
                    pygame.draw.line( screen, (255, 0, 0), (row[i][0],row[i][1]), (row[i+1][0],row[i+1][1]) )
                except IndexError:
                    pass
                    #pygame.draw.line( screen, (255, 0, 0), (row[i][0],row[i][1]),(row[0][0],row[0][1]))
        for row in Rewards:
            try:
                pygame.draw.line( screen, (0, 255, 0), (row[0], row[1]), (row[2], row[3]) )
            except:
                pass


    pygame.display.update()
    clock.tick(20)