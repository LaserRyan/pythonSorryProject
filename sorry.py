import graphics as gr#imports graphics
import random#imports random


with open("board.txt","r") as f:#opens board txt to get the sorry board
    boardlines = f.readlines()
    board = [list(line[:-1]) for line in boardlines]
    board[len(board)-1].append('#')


with open('rules.txt', 'r') as f:#opens rules txt to get sorry rules
    lines = f.read()
    
print(lines)


    
slide3Spot = [(1,0),(15,1),(14,15),(0,14),(9,0),(15,9),(6,15),(0,6)]#locations of certain slide spots
 
mydict = {' ': 'green'+str(random.randint(1,4)), '#':'white','>':'blue1','<':'blue1','v':'blue1','^':'blue1','|':'blue3',
          '-':'blue3','o':'blue3','@':'pink','$':'red','%':'purple','&':'orange','H':'black'}#dictionary for the board symbols to graphics
windowsize = 900
border = 50
cell = 50
boardsize = windowsize - border
win = gr.GraphWin('Board', windowsize,windowsize, autoflush=False)#opens drawing window of graphics.py
for row in range(len(board)):
    for col in range(len(board[row])):
        c = gr.Rectangle(gr.Point(border + col * cell, border+row*cell),gr.Point(border+cell+col*cell,border + cell +row*cell ))
        c.draw(win)
        c.setFill(mydict[board[row][col]])

def textQ(question):#this function takes in a question as a string, then using graphics, opens an entry that allows user input to get an answer. returns the user's answer
    quest = gr.Text(gr.Point(450,400),question)
    ask = gr.Entry(gr.Point(450,450),10)
    quest.draw(win)
    ask.draw(win)
    win.getMouse()
    answer = str(ask.getText())
    ask.undraw()
    quest.undraw()
    return answer
p1Name = textQ('Enter Pink Player Name')#gathers players name for the end screen
p2Name = textQ('Enter Red Player Name')
p3Name = textQ('Enter Purple Player Name')
p4Name = textQ('Enter Orange Player Name')


def getBoundPoints(row,col): #parameters of row and colums, then returns the points that bound the oval from graphics
    p1 = gr.Point(col*50 + 50, row*50 + 50)
    p2 = gr.Point(col*50 + 100, row*50 + 100)
    return p1,p2
    
pawnDict = {} #empy pawn dictionary, eventually fills with locations from key of pawn names

class pawn:#pawn class
    pawnlocs = dict()#dictionary of pawn location

    def __init__(self,player,row,col,p1,p2,name):# initializes a pawn the player that owns it, row and col, its graphical coordinates, and name (color)
        
        self.player = player
        
        self.startp1 = p1
        self.startp2 = p2
        x = p1.getX() % 50
        y = p2.getY() % 50
        self.endp1,_ = getBoundPoints(*list(player.goal)[::-1])
        self.endp1.move(x,y)
        self.endp2 = self.endp1.clone()
        self.endp2.move(25,25)
        
        self.row = row
        self.col = col
        
        self.name = name
        self.oval = gr.Oval(p1,p2)
        self.oval.setFill(self.player.name)
        self.oval.draw(win)
        self.safety = False
    
        
        
    def swap(self,other): #given paramter of current pawn and other pawn, swaps their location, both in pawnlocs dictionary and graphically
        self.row,other.row = other.row,self.row
        self.col,other.col = other.col,self.col
        deltaX = self.oval.getCenter().getX() - other.oval.getCenter().getX()
        deltaY = self.oval.getCenter().getY() - other.oval.getCenter().getY()
        self.oval.move(-deltaX,-deltaY)
        other.oval.move(deltaX,deltaY)
        pawn.pawnlocs[(self.row,self.col)],pawn.pawnlocs[(other.row,other.col)] = self,other
        # pawn.swapLoc(self,other)

    def sorry(self):#if lands on a position with another pawn, bumps that pawn back to start, removes from current active pawns
        if (self.row,self.col) in pawn.pawnlocs:
            pawn.pawnlocs.pop((self.row,self.col))
        self.row,self.col = self.player.startx,self.player.starty
        self.oval.undraw()
        self.oval.p1,self.oval.p2 = self.startp1,self.startp2
        self.oval.draw(win)
        try:#implemented to stop errors. Supposed to remove pawn from active pawns
            self.player.activepawns.remove(self)
        except ValueError:
            print('Something Went Wrong')

    def moveHoriz(self,sign):#given a sign, moves the pawn that many steps forwards or backwards(sign determines forward or backwards movement)
        if sign == '+':
            self.oval.move(50,0)
            gr.update(60)

        else:
            self.oval.move(-50,0)
            gr.update(60)

    def moveVert(self,sign):# given a sign, moves the pawn that many steps up or down(sign determines forward or backwards movement)
        if sign == '+':
            self.oval.move(0,-50)
            gr.update(60)
        
        else:
            self.oval.move(0,50)
            gr.update(60)

    def moving(self,step):         
        '''#given a sign, gives commands to moveVert or Move Horiz to graphically move the pawn. also updates the location in the pawnloc dict | also if at end of move, checks if currently on a slide square'''
        cords = self.player.getmove(self.row,self.col,step)
        
        if cords[-1] != self.player.goal and cords[-1] in pawn.pawnlocs and pawn.pawnlocs[cords[-1]].player == self.player:
            return None # cannot complete move
        for i in range(len(cords)-1):
            p1,p2 = cords[i],cords[i+1]
            if p1[0] < p2[0]:
                pawn.moveHoriz(self,'+')
            elif p1[0] > p2[0]:
                pawn.moveHoriz(self,'-')
            elif p1[1] < p2[1]:
                pawn.moveVert(self,'-')
            else:
                pawn.moveVert(self,'+')
       
       
        pawn.pawnlocs.pop((self.row,self.col))
        self.row,self.col = cords[-1]
        if (self.row,self.col) in pawn.pawnlocs:
            pawn.pawnlocs[(self.row,self.col)].sorry()
        
        pawn.pawnlocs[(self.row,self.col)] = self
        if 0 < self.row < 15 and 0 < self.col < 15:
            self.safety = True
        if (self.row,self.col) == self.player.goal:
            try:#error keeps persisting when trying to remove pawn from active pawn list. put this so code still runs. don't know how to fix
                self.player.activepawns.remove(self)
            except ValueError:
                print('Something Went Wrong')
            self.player.goalpawns.append(self)
            self.oval.undraw()
            self.oval.p1,self.oval.p2 = self.endp1,self.endp2
            self.oval.draw(win)
        self.slide(cords[-1])

        
    def setPawnLoc(self,row,col):
        '''Set pawns location'''
        
        self.row,self.col = row,col
        if (self.row,self.col) in pawn.pawnlocs:
            pawn.pawnlocs[(self.row,self.col)].sorry()
        
        pawn.pawnlocs[(self.row,self.col)] = self
        self.oval.undraw()
        self.oval.p1,self.oval.p2 = getBoundPoints(self.col,self.row)
        self.oval.draw(win)
  

    def slide(self,cord):
        '''checks the current cords of a pawn, then slides if pawn resides on a slide square'''
        if (cord) in slide3Spot:
            self.moving(3)
        

    
    
    def sPawn(self):
        '''spawns the pawn on the graphic board'''
        
        self.oval.undraw()
        self.oval.p1,self.oval.p2 = getBoundPoints(self.col,self.row)
        self.oval.draw(win)
        pawn.pawnlocs[(self.row,self.col)] = self


        



    
    


    



    


        

        

class player: #player class
    def __init__(self,name,startx,starty): 
        '''takes in the name, starting coordinates. given name, creates a movemap for the pawns by the player to follow around the board. this way it implements the safety zones as a unique entrance'''
        self.name = name
        self.pawns = []
        self.activepawns = []
        self.goalpawns = []
        stx,sty = startx,starty
        if startx == 0:
            stx += 1
        elif startx == 15:
            stx -= 1
        elif starty == 0:
            sty += 1
        else:
            sty -= 1
        
        base = [(i,0) for i in range(16)] + [(15,i) for i in range(1,16)] + [(i,15) for i in range(14,-1,-1)] + [(0,i) for i in range(14,0,-1)]
        idx = base.index((startx,starty))
        movemap = base[idx-1:] + base[:idx-1]
        if idx <= 4:
            movemap = base[-2:] + base[:idx-1] + movemap
        else:
            movemap = base[idx-6:idx-1] + movemap
        # safety zone area that's unique
        if starty == 0:
            movemap += [(2,i) for i in range(1,7)] # pink
        elif startx == 15:
            movemap += [(i,2) for i in range(14,8,-1)] # red
        elif starty == 15:
            movemap += [(13,i) for i in range(14,8,-1)] # purple
        elif startx == 0:
            movemap += [(i,13) for i in range(1,7)] # orange
        #
        self.goal = movemap[-1]
        self.movemap = movemap 
        
        p1,p2 = getBoundPoints(sty,stx)
        for i in range(2):
            for j in range(2):
                pawnp1 = p1.clone()
                pawnp2 = p2.clone()
                if i == 0:
                    pawnp2.move(0,-25)
                else:
                    pawnp1.move(0,25)
                if j == 0:
                    pawnp2.move(-25,0)
                else:
                    pawnp1.move(25,0)

                self.pawns.append(pawn(self,startx,starty,pawnp1,pawnp2,self.name))
        self.startx = startx
        self.starty = starty
        
    def checkGoal(self): 
        '''checks if all pawns have entered the goal zone. If so, returns variables to be used in main.'''
        if len(self.goalpawns) ==4:
            gameOn = False
            winner = str(self.name)

            return [gameOn,winner]
        else:
            return [True,True]
        
     
    def getActiveList(self): 
        '''returns list of active pawns for testing purposes'''
        return self.activepawns
    

    def getmove(self,c,r,move):
        '''checks ahead on the movemap of a pawn, to find if any obstructions prevent it from moving i.e a pawn of its own color'''
        index = self.movemap.index((c,r),5)
        
        if move > 0:
            return self.movemap[index:index+move+1]
        return self.movemap[index:index+move-1:-1]# returns c,r of potential move
    
    def checksPawnZone(self):
        '''checks if spawn zone is available (not occupied by same color)'''
        if (self.startx,self.starty) in pawn.pawnlocs:
            if pawn.pawnlocs[(self.startx,self.starty)].player == self:
                return False
            

        return True
        
    def checksPawnZoneDel(self):
        '''checks if spawn zone is available, also bumps out any different colored pawn that is currently inhabiting the spot'''
        
        if (self.startx,self.starty) in pawn.pawnlocs:
            if pawn.pawnlocs[(self.startx,self.starty)].player == self:
                return False
            
            if pawn.pawnlocs[(self.startx,self.starty)].player != self:
                pawn.pawnlocs[(self.startx,self.starty)].sorry()
        return True
    def sPawn(self):
        '''spawns a pawn (after checking requirements to spawn)'''
        # check location if obstructed
        if not self.checksPawnZoneDel():
            textt('Spawn Zone Obstructed')
        elif not self.checkSPawn():
            textt('No More Pawns Left to Spawn')
        else:
            # newpawn = pawn(self,self.startx,self.starty,(self.name)+str(len(self.pawns)+1))
            for i in range(4):
                if self.pawns[i] not in self.activepawns and self.pawns[i] not in self.goalpawns:
                    self.activepawns.append(self.pawns[i])
                    #print(f'spawned {self.name}')
                    self.pawns[i].sPawn()
                    return
                    
                    
        


    def checkSPawn(self): 
        '''checks if any pawns are left to spawn. returns false if not'''
        return len(self.activepawns) + len(self.goalpawns) < 4
    
    
    def pbToPoint(self,isself):
        '''returns list of locations of possible to pick pawns (used to implement when choosing pawns)'''
       
        cords = list(pawn.pawnlocs.keys())
      
        pointList = []
        for i in range(len(cords)):
            if (pawn.pawnlocs[cords[i]].player == self) == isself:
                if not isself and pawn.pawnlocs[cords[i]].safety:
                    continue
                pointList.append((cords[i],gr.Point(50+50*cords[i][0],50+50*cords[i][1])))
        
        return pointList

    def choosePawn(self,isself):
        '''given parameter of isself, checks if user clicked on list of possible pawns. returns the pawn that gets chosen.'''
        myList=player.pbToPoint(self,isself)
        within = False
        mypawn = None #filler
        if len(myList) == 0:
            return None
        while within == False:
            click = win.getMouse()
            for i in range(len(myList)):
                testRect = gr.Rectangle(myList[i][1],gr.Point(myList[i][1].getX()+50,myList[i][1].getY()+50))
                if withinRect(click,testRect):
                    within =True
                    mypawn = pawn.pawnlocs[myList[i][0]]
            
        return mypawn
        

    def chosenPawn(self,isself=True): 
        '''prompts user to pick a pawn, then returns the pawn that gets chosen'''
        if isself:
            textt(f'Please Select a {self.name} pawn')
        else:
            textt('Please select another player\'s pawn')
        if player.choosePawn is None:
            return None 
        return player.choosePawn(self,isself)
        
  

    def drawOne(self): 
        '''what happends when you draw a one'''
        textt('You Drew a One')

        
        if player.checksPawnZone(self):

            decision = buttonchoice(['Start','Move 1'])
            if decision == 'Move 1':
                if len(self.activepawns) ==1:
                    pawn.moving(self.activepawns[0],1)
                else:
                    chosen = player.chosenPawn(self)
                    pawn.moving(chosen,1)
            else:
                player.sPawn(self)

        else:
            if len(self.activepawns) ==1:
                    pawn.moving(self.activepawns[0],1)
            else:
                chosen = player.chosenPawn(self)
                pawn.moving(chosen,1)

    def drawTwo(self):#what happends when you draw a two
        textt('You Drew a Two')
        
        if player.checksPawnZone(self):

            decision = buttonchoice(['Start','Move 2'])
            if decision == 'Move 2':
                if len(self.activepawns) ==1:
                    pawn.moving(self.activepawns[0],2)
                else:
                    chosen = player.chosenPawn(self)
                    pawn.moving(chosen,2)
            else:
                player.sPawn(self)

        else:
            if len(self.activepawns) ==1:
                    pawn.moving(self.activepawns[0],2)
            else:
                chosen = player.chosenPawn(self)
                pawn.moving(chosen,2)
        textt('You get to Draw Again')
        player.drawCard(self)

    def drawThree(self):#what happends when you draw a three
        textt('You Drew a Three')
        if len(self.activepawns) ==1:
            pawn.moving(self.activepawns[0],3)
        else:
            chosen = player.chosenPawn(self)
            pawn.moving(chosen,3)
    
    def drawFour(self):
        textt('You Drew a Four')
        if len(self.activepawns) ==1:
            pawn.moving(self.activepawns[0],-4)
        else:

            chosen = player.chosenPawn(self)
            pawn.moving(chosen,-4)

    def drawFive(self):#what happends when you draw a four
        textt('You Drew a Five')
        if len(self.activepawns) ==1:
            pawn.moving(self.activepawns[0],5)
        else:

            chosen = player.chosenPawn(self)
            pawn.moving(chosen,5)

    def drawSeven(self):#what happends when you draw a five
        textt('You Drew a Seven')
        if len(self.activepawns) >1:
            
            chosen = player.chosenPawn(self)
            firstPawn = int(textQ('This pawn can move up to 7, type the amount you want this pawn to move'))
            while firstPawn > 7:
                textt('Input a number Seven or less')
                firstPawn = int(textQ('This pawn can move up to 7, type the amount you want this pawn to move')) 

            pawn.moving(chosen,firstPawn)

            if firstPawn != 7:
                secondPawn = 7-firstPawn
                textt('Choose the pawn you want to split with')
                
                chosen2 = player.chosenPawn(self)
                while chosen2 == chosen:
                    textt('Choose the pawn you want to split with')
                    chosen2 = player.chosenPawn(self)
                pawn.moving(chosen2,secondPawn)
        else:
            
            pawn.moving(self.activepawns[0],7)

    def drawEight(self): #what happends when you draw an eight
        textt('You Drew an Eight')
        if len(self.activepawns) ==1:
            pawn.moving(self.activepawns[0],8)
        else:

            chosen = player.chosenPawn(self)
            pawn.moving(chosen,8)

    def drawTen(self):#what happends when you draw a ten
        textt('You Drew a Ten')
        decision = buttonchoice(['Move 10','Move -1'])
       
        # chosen = player.chosenPawn(self)
        if decision == 'Move 10':
            if len(self.activepawns) ==1:
                pawn.moving(self.activepawns[0],10)
            else:
             chosen = player.chosenPawn(self)
             pawn.moving(chosen,10)
        else:
            if len(self.activepawns) ==1:
                pawn.moving(self.activepawns[0],-1)
            else:
                chosen = player.chosenPawn(self)
                pawn.moving(chosen,-1)
        
    def drawEleven(self):#what happends when you draw a eleven
        textt('You Drew an Eleven')
        decision = buttonchoice(['Move 11', 'Swap'])
        #chosen = player.chosenPawn(self)
        if decision == 'Move 11':
            if len(self.activepawns) ==1:
                pawn.moving(self.activepawns[0],11)
            else:
                chosen = player.chosenPawn(self)
                pawn.moving(chosen,11)
        else:
                if len(self.activepawns) ==1:
                    chosen = self.activepawns[0]
                else:
                    chosen = player.chosenPawn(self)
                other = player.chosenPawn(self,False)  #NO CLUE IF THIS WORKS
                pawn.swap(chosen,other)

    def drawTwelve(self):#what happends when you draw a twelve
        textt('You Drew a Twelve')
        if len(self.activepawns) ==1:
            pawn.moving(self.activepawns[0],12)
        else:

            chosen = player.chosenPawn(self)
            pawn.moving(chosen,12)
    
    def drawSorry(self):#what happends when you draw a sorry
        textt('You Drew a Sorry')
        mypawn = None #temp var
        for i in range(4):
            if self.pawns[i] not in self.activepawns and self.pawns[i] not in self.goalpawns:
                mypawn = self.pawns[i]
                self.activepawns.append(self.pawns[i])

                break
            
        if mypawn is None:
            textt(f"{self.name} has no available pawns, turn is forfeited")
        else:
            if self.chosenPawn(False) is None:
                textt('No available pawns, turn is forfeited')
                return
            otherpawn = self.chosenPawn(False)
            mypawn.setPawnLoc(otherpawn.row,otherpawn.col)


            




    def drawCard(self): #draws a card, using a dictionairy that returns value of a key. key is generated through random chance
        ranval = random.randint(1,11)
        if ranval != 11 and len(self.activepawns) == 0:
            self.sPawn()
        
        textt(f'{self.name} turn: Click to Draw')
        drawDict[ranval](self)
        # else:
        #     textt('No possible move, turn forfeited')

    




    #dictionary for drawing cards
drawDict={1:player.drawOne, 2:player.drawTwo,3:player.drawThree,4:player.drawFour,5:player.drawFive,6:player.drawSeven,7:player.drawEight,8:player.drawTen,9:player.drawEleven,10:player.drawTwelve,11:player.drawSorry}
    






def withinRect(point,rect):
    '''checks if point given is within a test rectangle (used for checking if the player clicked on a pawn)'''
    x = point.getX()
    y = point.getY()
    return (rect.getP1().getX() <= x <= rect.getP2().getX()) and (rect.getP1().getY() <= y <= rect.getP2().getY())

def buttonchoice(answers): 
    '''prompts the user with two buttons, the parameter is a list of two answers to a question. returns the value of the answer the user chose'''
    center = gr.Point(450,450)
    b1p1 = center.clone()
    b1p1.move(-175,-25)
    b1p2 = center.clone()
    b1p2.move(-25,25)
    button1 = gr.Rectangle(b1p1,b1p2)
    button1.setFill("White")
    b2p1 = center.clone()
    b2p1.move(25,-25)
    b2p2 = center.clone()
    b2p2.move(175,25)
    button2 = gr.Rectangle(b2p1,b2p2)
    button2.setFill("White")
    button1.draw(win)
    button2.draw(win)
    text1 = gr.Text(gr.Point(350,450),answers[0])
    text2 = gr.Text(gr.Point(550,450),answers[1])
    text1.draw(win)
    text2.draw(win)
    
    click = win.getMouse()
    while not withinRect(click,button1) and not withinRect(click,button2):
        
        click = win.getMouse()
    button1.undraw()
    button2.undraw()    
    text1.undraw()
    text2.undraw()
    
    if withinRect(click,button1):
        return answers[0]
    return answers[1]




def textt(textt): #
    '''puts a text on the screen for the player/s to read. click to make it go away'''
    texttt = gr.Text(gr.Point(450,350),textt)
    texttt.draw(win)
    win.getMouse()
    texttt.undraw()


#main()
gameOn = True
winner = ''

pinkPlayer = player('pink',4,0)
redPlayer = player('red',15,4)
purplePlayer = player('purple',11,15)
orangePlayer = player('orange',0,11)

playerDict= {0:pinkPlayer,1:redPlayer,2:purplePlayer,3:orangePlayer}

win.getMouse()
i = 0

while gameOn:
    
    trueTurn = i % 4
    i+= 1
    player.drawCard(playerDict[trueTurn])
    
    #print(len(player.getActiveList(playerDict[trueTurn])))
    if not player.checkGoal(playerDict[trueTurn])[0]:
        gameOn = player.checkGoal(playerDict[trueTurn])[0]
        winner = player.checkGoal(playerDict[trueTurn])[1]
    

textt('Game Over')
if winner == 'pink':
    textt(f'{p1Name} WINS')
elif winner == 'red':
    textt(f'{p2Name} WINS')
elif winner == 'purple':
    textt(f'{p3Name} WINS')
else:
    textt(f'{p4Name} WINS')





win.getMouse()
win.close()

