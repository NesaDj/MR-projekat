import pygame
import random
import os
import neat
import math

pygame.font.init()

WIN_SIZE = 1000 #definise sirinu i visinu prozora za graficki prikaz
NUMBER_OF_SQUARES = 6  #definise koliko ce polja igra imati
NUMBER_OF_SQUARES_SQUARED = NUMBER_OF_SQUARES**2    #racuna povrsinu mape
SQUARE_SIZE = WIN_SIZE//NUMBER_OF_SQUARES   #racuna koliko je jedno polje u px

BLACK = (255,255,255) #boja pozadine
GREEN = (0,255,0)   #boja zmije
RED = (255,0,0) #boja jabuke

win = pygame.display.set_mode((WIN_SIZE,WIN_SIZE)) #deklarisem prozor
pygame.display.set_caption("Meko Racunarstvo")  #podesavam title na prozoru

class snake_body:   #ova klasa predstavlja jednu tacku tela zmije
    def __init__(self, x, y, moving_side):
        self.x = x
        self.y = y
        self.moving_side = moving_side
  
    def draw_body(self,size):
        pygame.draw.rect(win, GREEN, (self.x * size, self.y * size, size, size))

class Snake:
    def __init__(self,x,y,size): # pravi zmiju od 3 polja
        self.size = size
        self.x = x
        self.y = y
        self.head = snake_body(x,y,'down')
        self.array = []
        self.array.append(self.head)
        self.array.append(snake_body(x,y-1,'down'))
        self.array.append(snake_body(x, y - 2, 'down'))

    def move(self): # pomera zmiju za po jedno polje
        for i in range(len(self.array) - 1, -1, -1):
            if self.array[i].moving_side == 'up':
                self.array[i].y -= 1
            if self.array[i].moving_side == 'down':
                self.array[i].y += 1
            if self.array[i].moving_side == 'left':
                self.array[i].x -= 1
            if self.array[i].moving_side == 'right':
                self.array[i].x += 1

            if i > 0 and self.array[i - 1].moving_side != self.array[i].moving_side:
                self.array[i].moving_side = self.array[i - 1].moving_side

    def draw(self,win): # crta zmiju
        for snake_body in self.array:
            snake_body.draw_body(self.size)

    def increase(self): # povecava zmiju za jedno polje
        if self.array[-1].moving_side == 'up':
            self.array.append(snake_body(self.array[-1].x,self.array[-1].y+1,self.array[-1].moving_side))
        if self.array[-1].moving_side == 'down':
            self.array.append(snake_body(self.array[-1].x,self.array[-1].y-1,self.array[-1].moving_side))
        if self.array[-1].moving_side == 'left':
            self.array.append(snake_body(self.array[-1].x+1,self.array[-1].y,self.array[-1].moving_side))
        if self.array[-1].moving_side == 'right':
            self.array.append(snake_body(self.array[-1].x-1,self.array[-1].y,self.array[-1].moving_side))

    def check_collision(self,num_of_squares): # proverava da li je zmija udarila u nesto
        if self.head.y>num_of_squares-1 or self.head.x > num_of_squares-1 or self.head.x<0 or self.head.y<0:
            return True
        for body in self.array:
            if self.head.x == body.x and self.head.y == body.y and self.head!=body:
                return True
        return False

    def getAngle(self,apple): # racuna ugao izmedju glave i jabuke
        angle = math.atan2((self.head.x-apple.x),(self.head.y-apple.y))
        return angle

    def getSideDistance(self,numSquares): # racuna distance
        distance = [0,0,0,0,0,0,0,0] #up,down,left,right,up-right,up-left,down-right,down-left
        
        bodyInWay = False # racuna distancu iznad glave
        if self.head.moving_side !='down':
            for i in reversed(range(self.head.y)):
                for body in self.array:
                    if body.x == self.head.x and body.y == i:
                        bodyInWay = True
                if not bodyInWay:
                    distance[0]+=1
                else:
                    break
        
        bodyInWay = False # racuna distancu ispod glave
        if self.head.moving_side != 'up':
            for i in range(self.head.y+1,numSquares):
                for body in self.array:
                    if body.x == self.head.x and body.y == i:
                        bodyInWay = True
                if not bodyInWay:
                    distance[1] += 1
                else:
                    break
        
        bodyInWay = False # racuna distancu levo od glave
        if self.head.moving_side != 'right':
            for i in reversed(range(self.head.x)):
                for body in self.array:
                    if body.y == self.head.y and body.x == i:
                        bodyInWay = True
                if not bodyInWay:
                    distance[2]+=1
                else:
                    break
        
        bodyInWay = False # racuna distancu desno od glave
        if self.head.moving_side != 'left':
            for i in range(self.head.x + 1, numSquares):
                for body in self.array:
                    if body.y == self.head.y and body.x == i:
                        bodyInWay = True
                if not bodyInWay:
                    distance[3] += 1
                else:
                    break
        
        distance[4:]=[1,1,1,1]
        for body in self.array: # proverava dijagonale
            #up - left,up-right, down - right, down - left
            if body.x == self.head.x-1 and body.y ==self.head.y-1 or self.head.x -1<0 or self.head.y-1<0:
                distance[4]=0
            if body.x == self.head.x+1 and body.y ==self.head.y-1 or self.head.x+1 >=numSquares or self.head.y-1<0:
                distance[5]=0
            if body.x == self.head.x+1 and body.y ==self.head.y+1 or self.head.x+1 >=numSquares or self.head.y+1>=numSquares:
                distance[6]=0
            if body.x == self.head.x-1 and body.y ==self.head.y+1 or self.head.x-1<0 or self.head.y+1>=numSquares:
                distance[7]=0

        return distance

    def getDistanceFromApple(self,apple): # racuna distancu do jabuke
        return math.sqrt((apple.x-self.x)**2+(apple.y-self.y)**2)

class Apple:
    def __init__(self,x,y,size,num_of_squares,snake): # definise jabuku
        self.x = x
        self.y = y
        self.size = size
        self.num_of_squares =num_of_squares
        self.snake = snake

    def draw(self,win): # crta jabuku
        if len(self.snake.array) < self.num_of_squares ** 2:
            pygame.draw.rect(win, RED, (self.x * self.size, self.y * self.size, self.size, self.size))

    def generate(self): # generise jabuku
        if len(self.snake.array) < self.num_of_squares**2:
            self.x = random.randint(0, self.num_of_squares-1)
            self.y = random.randint(0, self.num_of_squares-1)

            for body in self.snake.array:
                if self.x == body.x and self.y == body.y:
                    self.generate()

def draw_window(snake,distance,apple,gen): # crta igru
    win.fill(BLACK)
    snake.draw(win)
    apple.draw(win)
    pygame.display.update()

def moving_side_to_int(side): # pretvara string u int
    if side == 'up':
        return 0
    if side == 'down':
        return 1
    if side == 'left':
        return 2
    if side == 'right':
        return 3

def set_move(y, snake): # bira potez
    m=-math.inf
    side = snake.head.moving_side

    if y[0]>m and snake.head.moving_side!='down':
        side = 'up'
        m = y[0]
    if y[1]>m and snake.head.moving_side!='up':
        side = 'down'
        m=y[1]
    if y[2]>m and snake.head.moving_side!='right':
        side = 'left'
        m=y[2]
    if y[3]>m and snake.head.moving_side!='left':
        side = 'right'
        m=y[3]

    snake.head.moving_side = side

gen = 0 # broj generacija
max_score = 0 # maksimalan skor
score_gen = 0 # maksimalan skor jedne generacije
draw_win = False # da li crta igru
normal_speed = False # da li je igra ubrzana

def run_genomes(genomes, config):  # ova petlja se odvija za sve generaciju
    global gen,max_score,draw_win,normal_speed,score_gen
    print("Generations:",gen," Max-Score:",max_score," Score:",score_gen)

    gen+=1
    score_gen=0

    for id, genome in genomes: # ova petlja se odvija za svaku generaciju
        num_of_moves = 0
        net =  neat.nn.FeedForwardNetwork.create(genome,config)
        genome.fitness = 0
        score = 0

        snake = Snake(NUMBER_OF_SQUARES//2, NUMBER_OF_SQUARES//2, SQUARE_SIZE)
        apple = Apple(0, 0, SQUARE_SIZE, NUMBER_OF_SQUARES,snake)
        apple.generate()

        run = True
        while run: # ova petlja se odvija za svaku jedinku

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()
                    quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        draw_win = not draw_win
                        normal_speed = not normal_speed
            
            snake.move()
            num_of_moves += 1

            if snake.check_collision(NUMBER_OF_SQUARES):
                genome.fitness -= 6
                run = False

            if num_of_moves>NUMBER_OF_SQUARES_SQUARED:
                genome.fitness -= 6
                run = False

            if snake.head.x == apple.x and snake.head.y == apple.y:
                genome.fitness += 6
                score+=1
                snake.increase()
                apple.generate()
                num_of_moves = 0

            if score == NUMBER_OF_SQUARES_SQUARED-3:
                genome.fitness+=10
                break

            if score>score_gen:
                score_gen = score
            if score> max_score:
                max_score = score

        
            distance = snake.getSideDistance(NUMBER_OF_SQUARES) # prikuplja podatke
            angle = snake.getAngle(apple)
            dist_from_apple = snake.getDistanceFromApple(apple)
            

            output = net.activate((snake.head.x,snake.head.y,moving_side_to_int(snake.head.moving_side), # bira potez
                                   distance[0],distance[1],distance[2],distance[3],
                                   distance[4],distance[5],distance[6],distance[7],
                                   angle,dist_from_apple,apple.x,apple.y))

            set_move(output,snake) # igra potez

            if draw_win: # proverava da li treba da crta
                draw_window(snake,distance,apple,gen)
            
            if normal_speed: # proverava da li igra tece normalnom brzinom
                pygame.time.delay(100)
    
def run(config_path):
    config  = neat.config.Config(neat.DefaultGenome,neat.DefaultReproduction,neat.DefaultSpeciesSet, neat.DefaultStagnation,config_path)

    population = neat.Population(config)
    population.run(run_genomes,100000000)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir,"config.txt")
    run(config_path)
