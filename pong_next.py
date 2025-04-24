import pygame
pygame.init()
#Variables
# ball
Ball_color=(0,0,126)
Ball_x_pos, Ball_y_pos=0,0
Ball_x_vel,Ball_y_vel=2,2
Ball_radius=10
#bat
Bat_color=(0,0,0)
Bat_x_pos,Bat_y_pos=400,575
Bat_width,Bat_height=150,25
Bat_stroke=10
bat_speed=25

# class definations:

class Brick:
    def __init__(self,color:(int,int,int),x:int,y:int,wdh:int,hgt,border:int):
        self.color=color
        self.x=x
        self.y=y
        self.wdh=wdh
        self.hgt=hgt
        self.border=border
    def collision_brick(self,Ball):
        # Check if the ball is within the brick’s bounding box



        if (Ball.y-Ball_radius<=self.y+self.hgt) and (Ball.y+Ball_radius>=self.y):
            if(Ball.x+Ball.radius>=self.x) and (Ball.x<=self.x+self.wdh):
                Ball.y_vel=-1*Ball.y_vel
                return True
            #check for side collision
            if (Ball.x>=self.x) and (Ball.x<=self.x+self.wdh):
                Ball.x_vel=-1*Ball.x_vel
                return True
            else :
                return False
    def draw(self,surface):
        pygame.draw.rect(surface,self.color,(self.x,self.y,self.wdh,self.hgt),self.border)
                


class Ball:
    def __init__(self,color: (int ,int, int),x:int,y:int,x_vel,y_vel,radius:int) -> None:  #def __init__(self,color: (int ,int, int),position:(int,int),radius:int) -> None:
        self.color=color
        self.x=x
        self.y=y
        self.x_vel=x_vel
        self.y_vel=y_vel
        self.radius=radius
    def move(self):
        self.x=self.x+self.x_vel
        self.y=self.y+self.y_vel
    
    

    def draw(self,surface) :
        pygame.draw.circle(surface, self.color, (self.x,self.y), self.radius)

    #Funtions for ball bouncing and collision detection   
    def bounce(self):
            Over_font=pygame.font.Font(None,100)
            if self.x>WIDTH:
                self.x_vel= -1*self.x_vel
            if self.x<0:
                self.x_vel= -1*self.x_vel
            if self.y>HEIGHT:
                #adding gameover screen
                screen.fill((126,0,0))
                score_text2=Over_font.render(f"GAME OVER",True,(0,0,0))
                screen.blit(score_text2,(200,300))
                pygame.display.update()
                pygame.time.delay(5000) # wait for 5 sec
                #reset corridinate
                self.x=0
                self.y=0
                return True
            if self.y<0:
                self.y_vel=-1*self.y_vel
            return False
    

class Bat:
    def __init__(self,color: (int,int,int),x_bat:int, y_bat:int,wdt:int,hgt:int,border:int,speed : int ):
        self.color=color
        self.x_bat=x_bat
        self.y_bat=y_bat
        self.wdt=wdt
        self.hgt=hgt
        self.border=border
        self.speed=speed
    def move(self):  #(self,direction):
         #paddle control
        keys=pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.x_bat=self.x_bat+self.speed
        if keys[pygame.K_LEFT]:
            self.x_bat=self.x_bat-self.speed
        #add maximum range of paddle movement
        if self.x_bat<0:
            self.x_bat=0
        if self.x_bat>WIDTH-Bat_width:
            self.x_bat=WIDTH-Bat_width
    def collision(self,Ball):
        if (Ball.y+Ball.radius>=HEIGHT-self.hgt) and (Ball.y+Ball.radius<=HEIGHT):
            if(Ball.x>=self.x_bat) and (Ball.x<=self.x_bat+self.wdt): #just match the x corrdinate of ball wtbat when ball crosses the at level
                Ball.y_vel= -1*Ball.y_vel 
                return True
            else:
                return False

        

    def draw(self,surface):
        pygame.draw.rect(surface,self.color,(self.x_bat,self.y_bat,self.wdt,self.hgt),self.border)

class gameManager():
    def __init__(self):
        self.score=0
        
    def updateScore(self,Collision,Collsion_brick,Bounce):
        if Collision==True:
             self.score=self.score+1
        elif Collsion_brick==True:
            self.score=self.score+5
        #score zero
        elif Bounce:
                self.score=0
                
        

#Defining game screen
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Game by johnson")
clock = pygame.time.Clock() 

# creating game object
newBall = Ball(Ball_color, Ball_x_pos, Ball_y_pos, Ball_x_vel, Ball_y_vel, Ball_radius)
newBat=Bat(Bat_color,Bat_x_pos,Bat_y_pos,Bat_width,Bat_height,bat_speed,Bat_stroke)
newBrick=Brick((0,0,0),300,300,100,50,5)
new_gameManager=gameManager()


running = True


#Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    screen.fill((0,126,0))  # 1) clear background
    newBall.move() 
    newBat.move()  
    
    bounce=newBall.bounce() #we need to update alaway to fetch the score
    collision=newBat.collision(newBall)
    collison_brick=newBrick.collision_brick(newBall)
    newBrick.draw(screen) 

    newBall.draw(screen)
    newBat.draw(screen)
    new_gameManager.updateScore(collision,collison_brick,bounce)
    font=pygame.font.Font(None,36)
    score_text=font.render(f"score: {new_gameManager.score}",True,(255,255,255))
    screen.blit(score_text,(10,10))
    pygame.display.update()       # 4) flip buffers
    clock.tick(120)


    
pygame.quit()
