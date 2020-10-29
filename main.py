import pygame
import json
import numpy as np
import math
import keyboard as kb
import keepAwake
keepAwake.enable()
#constants
DisplayHeight = 720
DisplayWight = 1280
Reward = "Reward"
Finish = "Finish"
Track = "Track"

class Rl:
    def __init__(self,LoadModel,n_states,n_actions,filename="model.txt"):
        self.n_states = n_states
        self.n_actions = n_actions
        self.percentile = 70
        # как быстро обновляется политика в масштабе от 0 до 1
        self.learning_rate = 0.1
        # награда
        self.reward = 0
        # даные полученые в сессии
        self.sessions = []
        self.n_sessions = 10
        # текущая сессия
        self.now_session = 0
        # количество циклов в сессии
        self.num = 300
        # прошедшие цыклы
        self.now_cycle = 0
        # состояния в сессии
        self.states = []
        # действия в сессии
        self.actions = []

        self.filename = filename

        if LoadModel:
            with open( filename, 'r' ) as model:
                load = model.read()
                self.policy = json.loads( load )
                self.policy = np.asarray( self.policy )
        else:
            self.policy = []
            for i in range( self.n_states ):
                self.policy.append( [] )
                for row in range( self.n_actions ):
                    self.policy[i].append( 1 / self.n_actions )
            self.policy = np.asarray( self.policy )
        print(self.policy.tolist())

    def update_policy(self, elite_states, elite_actions ):
        """
        Given old policy and a list of elite states/actions from select_elites,
        return new updated policy where each action probability is proportional to

        policy[s_i,a_i] ~ #[occurences of si and ai in elite states/actions]

        Don't forget to normalize policy to get valid probabilities and handle 0/0 case.
        In case you never visited a state, set probabilities for all actions to 1./n_actions

        :param elite_states: 1D list of states from elite sessions
        :param elite_actions: 1D list of actions from elite sessions

        """

        new_policy = np.zeros( [self.n_states, self.n_actions] )

        # <YOUR CODE: update probabilities for actions given elite states & actions>
        # Don't forget to set 1/n_actions for all actions in unvisited states.
        for s, a in zip( elite_states, elite_actions ):
            new_policy[s, a] += 1

        new_policy += (np.max( new_policy, axis=1, keepdims=True ) == 0) * (1 / self.n_actions)
        num_actions = np.sum( new_policy, axis=1, keepdims=True )
        new_policy /= num_actions
        return new_policy


    def select_elites(self, states_batch, actions_batch, rewards_batch, percentile ):
        """
        Select states and actions from games that have rewards >= percentile
        :param states_batch: list of lists of states, states_batch[session_i][t]
        :param actions_batch: list of lists of actions, actions_batch[session_i][t]
        :param rewards_batch: list of rewards, rewards_batch[session_i]

        :returns: elite_states,elite_actions, both 1D lists of states and respective actions from elite sessions

        Please return elite states and actions in their original order
        [i.e. sorted by session number and timestep within session]

        If you are confused, see examples below. Please don't assume that states are integers
        (they will become different later).
        """

        # reward_threshold = <YOUR CODE: compute minimum reward for elite sessions. Hint: use np.percentile()>
        reward_threshold = np.percentile( rewards_batch, percentile )
        # print(reward_threshold)

        elite_states = []
        elite_actions = []
        for states, actions, reward in zip( states_batch, actions_batch, rewards_batch ):
            if reward < reward_threshold:
                continue

            elite_states.extend( states )
            elite_actions.extend( actions )

        return elite_states, elite_actions

    def update(self,state,reward,endSession):
        #print(self.reward)
        self.now_cycle += 1

        s = state
        rew = reward
        a = np.random.choice( self.n_actions, p=self.policy[s, :] )

        self.states.append(s)
        self.actions.append(a)

        action = a
        self.reward += rew

        if self.now_cycle == self.num or endSession:
            print("session")
            self.now_session += 1
            self.sessions.append( (self.states, self.actions, self.reward) )
            self.now_cycle = 0
            self.states = []
            self.actions = []
            self.reward = 0

        if self.now_session == self.n_sessions:
            #print("end session")

            self.now_session = 0

            states_batch, actions_batch, rewards_batch = zip( *self.sessions )

            elite_states, elite_actions = self.select_elites( states_batch, actions_batch, rewards_batch, self.percentile )

            new_policy = self.update_policy( elite_states, elite_actions )

            self.policy = self.learning_rate * new_policy + (1 - self.learning_rate) * self.policy

            self.sessions = []

            print("update policy")
            with open( self.filename, 'w' ) as model:
                model.write( json.dumps( self.policy.tolist() ) )
        return action

    def learnFromExamples( self,state,action,reward,endSession):
        self.now_cycle += 1

        s = state
        rew = reward
        a = action

        self.states.append( s )
        self.actions.append( a )

        self.reward += rew

        if self.now_cycle == self.num or endSession:
            print( "session" )
            self.now_session += 1
            self.sessions.append( (self.states, self.actions, self.reward) )
            self.now_cycle = 0
            self.states = []
            self.actions = []
            self.reward = 0

        if self.now_session == self.n_sessions:
            # print("end session")

            self.now_session = 0

            states_batch, actions_batch, rewards_batch = zip( *self.sessions )

            elite_states, elite_actions = self.select_elites( states_batch, actions_batch, rewards_batch,
                                                              self.percentile )

            new_policy = self.update_policy( elite_states, elite_actions )

            self.policy = self.learning_rate * new_policy + (1 - self.learning_rate) * self.policy

            # self.sessions = []

            print( "update policy" )
            with open( self.filename, 'w' ) as model:
                model.write( json.dumps( self.policy.tolist() ) )


class Line:
    def __init__(self,start = (0,0),end = (0,0)):
        self.start = start
        self.end = end

class BoxCollision:
    def __init__(self,width,height,source,Map,RewardMap):
        self.width = width
        self.height = height
        self.scr = source
        self.lines = [Line(),Line(),Line(),Line()]
        self.isIntersection = False
        self.isGetReward = False
        self.Map = Map
        self.RewardMap = RewardMap

    def update( self,pos,angle):
        angleR = angle * math.pi / 180
        cosA = math.cos( angleR )
        sinA = math.sin( angleR )

        dwx = self.width / 2 * cosA
        dwy = -self.width / 2 * sinA

        dhx = self.height / 2 * sinA
        dhy = self.height / 2 * cosA

        fl = ( pos[0] + dwx + dhx, pos[1] + dwy + dhy )
        fr = ( pos[0] + dwx - dhx, pos[1] + dwy - dhy )
        rl = ( pos[0] - dwx + dhx, pos[1] - dwy + dhy )
        rr = ( pos[0] - dwx - dhx, pos[1] - dwy - dhy )

        self.lines[0] = Line(rl, fl)
        self.lines[1] = Line(fl, fr)
        self.lines[2] = Line(fr, rr)
        self.lines[3] = Line(rr, rl)

        for l in self.lines:
            for line in self.Map:
                success, x, y = line_intersection([l.start, l.end], [line.start, line.end])
                if success:
                    return Track
        isBreak = False
        for l in self.lines:
            if isBreak:
                break
            for line in self.RewardMap:
                success, x, y = line_intersection([l.start, l.end], [line.start, line.end])
                self.isIntersection = True
                if success:
                    if not self.isGetReward:
                        self.isGetReward = True
                        #print("reward")
                        return Reward
                    else:
                        isBreak = True
                        break
                else:
                    self.isIntersection = False


        if not self.isIntersection:
            self.isGetReward = False

        for row in self.lines:
            pygame.draw.line(self.scr,(255,0,0),row.start,row.end)
        return None



class Car(pygame.sprite.Sprite):
    def __init__( self ,x,y,Map,RewardMap,source,learningFromExamplesMode = False):
        pygame.sprite.Sprite.__init__( self )
        self.gas = False
        self.brake = False
        self.left = False
        self.right = False
        self.speed = 0
        self.angle = 0
        self.spawnAngle = self.angle
        self.maxSpeed = 7
        self.minSpeed = -1
        self.scr = source
        self.x,self.y = x,y
        self.spawnx,self.spawny = x,y

        self.Map = Map
        self.original_img = pygame.image.load("sprites\\black_viper.png").convert_alpha()
        self.original_img = pygame.transform.scale(self.original_img, (int(214*0.2), int(100*0.2)))
        self.img = self.original_img
        self.visionsLines = [Line(),Line(),Line(),Line(),Line()]
        self.collision = BoxCollision(self.img.get_width(),self.img.get_height(),self.scr,Map,RewardMap)
        self.endSession = False
        self.RlModel = Rl(True,1125,6,"model.txt")
        self.Attempts = 1
        self.learningFromExamplesMode = learningFromExamplesMode

    def rotate(self,img,angle ):
        img2 = pygame.transform.rotate(img, int( angle ) )
        return img2

    def render(self):
        #pygame.draw.rect(scr,(255,0,0),self.imgRect,2)
        self.scr.blit(self.img, (self.x - self.img.get_width()/2, self.y - self.img.get_height()/2))

    def line( self,angle,dis=300):
        x = self.x + dis * math.cos((-self.angle + angle) * math.pi / 180 )
        y = self.y + dis * math.sin((-self.angle + angle) * math.pi / 180 )
        pygame.draw.line(screen,(255,0,0),(self.x, self.y),(x,y))
        return x,y

    def movement(self,action=-1 ):
        if action == 0:
            self.gas = True
            self.brake = False
            self.right = False
            self.left = False
        elif action == 1:
            self.brake = True
            self.gas = False
            self.right = False
            self.left = False
        elif action == 2:
            self.gas = True
            self.right = True
            self.left = False
            self.brake = False
        elif action == 3:
            self.gas = True
            self.right = False
            self.left = True
            self.brake = False
        elif action == 4:
            self.gas = False
            self.right = True
            self.left = False
            self.brake = True
        elif action == 5:
            self.gas = False
            self.right = False
            self.left = True
            self.brake = True


        if self.gas:
            if self.speed < self.maxSpeed:
                self.speed+=1
            if self.right:
                self.angle -= 4
            if self.left:
                self.angle += 4

        elif self.brake:
            if self.speed > self.minSpeed:
                self.speed-=0.5
            if self.right:
                self.angle += 4
            if self.left:
                self.angle -= 4
        else:
            if self.speed > 0:
                self.speed-=0.5
            elif self.speed < 0:
                self.speed +=0.5


        self.x += self.speed * math.cos(-self.angle * math.pi / 180 )
        self.y += self.speed * math.sin(-self.angle * math.pi / 180 )
        #self.imgRect.x = self.x
        #self.imgRect.y = self.y

    def vision( self ):
        start = (self.x, self.y)
        visionDepth = 300
        self.visionsLines[0] = Line(start,self.line( 0, visionDepth ))
        self.visionsLines[1] = Line(start,self.line( 30, visionDepth ))
        self.visionsLines[2] = Line(start,self.line( -30, visionDepth ))
        self.visionsLines[3] = Line(start, self.line(80, visionDepth ))
        self.visionsLines[4] = Line(start, self.line(-80, visionDepth ))

        state = 0
        for index,vl in enumerate(self.visionsLines):
            minLength = visionDepth
            for line in self.Map:
                success,x,y = line_intersection([vl.start,vl.end],[line.start,line.end])
                if success:
                    minLength = min( minLength, math.hypot( x - self.x, y - self.y ) )
                    #print(success)
                if success:
                    if 0 < x < DisplayWight and 0 < y < DisplayHeight:
                        pygame.draw.circle(screen,(0,255,0),(round(x),round(y)),3)



            lineStateCount = 5 if index < 3 else 3
            lineState = min( lineStateCount-1, math.floor( math.log2( max( 0.1, minLength / 20 ) ) ) )
            state = state * lineStateCount + lineState

        return state


    def update(self,gas,brake,right,left):
        self.img = self.rotate(self.original_img,self.angle)
        self.gas = gas
        self.brake = brake
        self.right = right
        self.left = left

        font = pygame.font.Font( None, 40)
        text = font.render( f"Попытка: {self.Attempts}" , 1, (200, 200, 200) )
        self.scr.blit(text,(50,50))

        reward = 0
        overlapEvent = self.collision.update((self.x,self.y),self.angle)
        if overlapEvent == Reward:
            reward += 1
        elif overlapEvent == Track:
            reward -= 10
        reward -= 0.0001
        #print(reward)
        state = self.vision()
        action = self.RlModel.update(state,reward,self.endSession)
        self.movement(action)

        if overlapEvent == Track:
            self.x,self.y = self.spawnx,self.spawny
            self.speed = 0
            self.angle = self.spawnAngle
            self.Attempts +=1
            self.endSession = True
            #print("end session")
        else:
            self.endSession = False


def control():
    gas,brake,right,left = False,False,False,False
    e = pygame.event.poll()
    if kb.is_pressed("up"):
        gas = True
    if kb.is_pressed("right"):
        right = True
    if kb.is_pressed("left"):
        left = True
    if kb.is_pressed("down"):
        brake = True
    if e.type == pygame.QUIT:
        exit(0)
    return gas,brake,right,left

def line_intersection(line1, line2):
    k1 = ( line1[1][0] - line1[0][0], line1[1][1] - line1[0][1] )
    k2 = ( line2[1][0] - line2[0][0], line2[1][1] - line2[0][1] )

    rd = ( line2[0][0] - line1[0][0], line2[0][1] - line1[0][1] )

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    def in_range(n, d):
        if abs(d) < abs(n):
            return False
        if d > 0:
            return n >= 0
        else:
            return n <= 0

    div = det( k2, k1 )
    n1 = det( k2, rd )
    if not in_range(n1, div):
        return False, 0, 0

    n2 = det( k1, rd )
    if not in_range(n2, div):
        return False, 0, 0

    t = n2 / div
    return True, line2[0][0] + t * k2[0], line2[0][1] + t * k2[1]


pygame.init()
screen = pygame.display.set_mode((DisplayWight,DisplayHeight))
screen.fill((135, 206, 250))
pygame.display.set_caption("Racing")
clock = pygame.time.Clock()
Map = []
Rewards = []
with open("map2.txt","r") as f:
    file = f.read()
    data = json.loads(file)
print(data)
for row in data["Map"]:
    for i in range( len( row ) ):
        try:
            Map.append(Line(row[i],row[i+1]))
        except IndexError:
            Map.append(Line(row[i],row[0]))

for row in data["Rewards"]:
    try:
        Rewards.append(Line((int(row[0]),int(row[1])),(int(row[2]),int(row[3]))))
    except IndexError:
        pass

car = Car(520,670,Map,Rewards,screen)

while True:
    pygame.display.set_caption(str(int(round(clock.get_fps()))))
    control()
    screen.fill( (0, 0, 0) )
    for row in Map:
        pygame.draw.line(screen,(100,100,100),row.start,row.end)
    for row in Rewards:
        pygame.draw.line(screen,(0,255,0),row.start,row.end)
    g,b,r,l = control()
    car.update(g,b,r,l)
    car.render()
    pygame.display.flip()
    clock.tick(60)
