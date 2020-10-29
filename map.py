import json
import pygame
pygame.init()
screen = pygame.display.set_mode((1280,720))
screen.fill((0, 0, 0))
pygame.display.set_caption("Racing")
clock = pygame.time.Clock()
with open("map.txt","r") as f:
    file = f.read()
    data = json.dumps(file)
    Map = json.loads(file)
print(Map[0])
while True:
    for row in Map:
        for i in range( len( row ) ):
            try:
                pygame.draw.line( screen, (255, 0, 0), (row[i][0],row[i][1]), (row[i+1][0],row[i+1][1]) )
            except:
                pygame.draw.line( screen, (255, 0, 0), (row[i][0],row[i][1]),(row[0][0],row[0][1]))
    pygame.display.update()
