import pygame
from pygame.locals import *
import random
from collections import defaultdict
import os
import math
from abc import ABC, abstractmethod
from random import choice

class GUI(object): # initializing board/graphical elements/piece information
    def __init__(self):
        self.width = 1010
        self.boardWidth = 640 
        self.boardHeight = 640
        self.height = 640
        self.cellRadius = 32
        self.cellSize = self.boardHeight/10
        self.gameRun = False
        self.gameOver = False
        self.black = (0, 0, 0)
        self.playMode = False
        self.randomSetup = False
        self.quit = False
        self.help = False
        self.returnPhase = None
        self.modern, self.classic = False, False
        self.gameDisplay = pygame.display.set_mode((self.width, self.height))
        self.board = pygame.image.load('StrategoBoard.png')
        # board image from: https://adam.younglogic.com/2018/10/imagining-go-with-alternate-boards/
        self.titleImage = pygame.image.load("StrategoTitleImage.png")
        # title screen image from https://www.ultraboardgames.com/stratego/game-rules.php
        #################################################
        # all modern piece images from: http://www.stratego.com/en/play/stratego-rules/
        self.spy = pygame.image.load('spyPiece.png')
        self.bomb = pygame.image.load('bombPiece.png')
        self.flag = pygame.image.load('flagPiece.png')
        self.scout = pygame.image.load('scoutPiece.png')
        self.three = pygame.image.load('threePiece.png')
        self.four = pygame.image.load('fourPiece.png')
        self.five = pygame.image.load('fivePiece.png')
        self.six = pygame.image.load('sixPiece.png')
        self.seven = pygame.image.load('sevenPiece.png')
        self.eight = pygame.image.load('eightPiece.png')
        self.nine = pygame.image.load('ninePiece.png')
        self.ten = pygame.image.load('tenPiece.png')
        ###################################################
        # all classic piece images from https://www.ultraboardgames.com/stratego/game-rules.php
        self.classicSpy = pygame.image.load('blueSpy.png')
        self.classicBomb = pygame.image.load('bomb.png')
        self.classicFlag = pygame.image.load('flag.png')
        self.classicScout = pygame.image.load('scout.png')
        self.classicThree = pygame.image.load('three.png')
        self.classicFour = pygame.image.load('four.png')
        self.classicFive = pygame.image.load('five.png')
        self.classicSix = pygame.image.load('six.png')
        self.classicSeven = pygame.image.load('seven.png')
        self.classicEight = pygame.image.load('eight.png')
        self.classicNine = pygame.image.load('nine.png')
        self.classicTen = pygame.image.load('ten.png')
        self.red = pygame.image.load('redPieceHiding.png')
        # self.red (redPieceHiding.png) from: https://www.myabandonware.com/media/screenshots/s/stratego-3y0/stratego_1.png
        self.styleBackground = pygame.image.load('StyleBackground.png')
        # background image from: https://pixels.com/featured/llanowar-reborn-philip-straub.html?product=poster
        self.pieces = self.getPieceList()
        self.boardData = [ ([None] * 10) for row in range(10) ]
        self.setPieces = dict()
        self.illegalMoves = self.getObstaclePos()
        self.pieceData = self.getPieceData()
        self.classicPieceData = self.getClassicPieceData()
        self.rankData = self.getRankData()
        self.gamePhase = 0
        self.turn = 'blue'
        self.twoPlayer = False
        self.displayingEnemyPiece = None
        self.mouseX = 0
        self.mouseY = 0
        self.ready = False
        self.mouseClicked = False
        self.selectedPiece = None
        self.clock = pygame.time.Clock() 
        self.win = False
        self.lose = False 
        self.AIMode = None
        self.mcts_ai = None
        self.tree = None
        self.capturedPieces = []
        self.capturedPieceSet = set()
        self.aiMoveSet = set()  
        self.pieceImageDict = {"Ten": self.ten, "Nine": self.nine, 'Eight': self.eight, "Seven": self.seven, 
        "Six": self.six, "Five": self.five, "Four": self.four, "Three": self.three, "Scout": self.scout, 
        "Spy": self.spy, "Bomb": self.bomb, "Flag": self.flag}
        self.classicPieceImageDict = {"Ten": self.classicTen, "Nine": self.classicNine, 'Eight': self.classicEight, "Seven": self.classicSeven, 
        "Six": self.classicSix, "Five": self.classicFive, "Four": self.classicFour, "Three": self.classicThree, "Scout": self.classicScout, 
        "Spy": self.classicSpy, "Bomb": self.classicBomb, "Flag": self.classicFlag}       
        self.initializeBoard()
    
    def getPieceData(self): # number of each piece
        return {self.ten: [1, 'Ten'], self.nine: [1, 'Nine'], self.eight: [2, 'Eight'], self.seven: [3, 'Seven'], 
        self.six: [4, 'Six'], self.five: [4, 'Five'], self.four: [4, 'Four'], self.three: [5, 'Three'], 
        self.scout: [8, 'Scout'], self.spy: [1, 'Spy'], self.bomb: [6, 'Bomb'], self.flag: [1, 'Flag']}

    def getClassicPieceData(self): # number of each piece
        return {self.classicTen: [1, 'Ten'], self.classicNine: [1, 'Nine'], self.classicEight: [2, 'Eight'], self.classicSeven: [3, 'Seven'], 
        self.classicSix: [4, 'Six'], self.classicFive: [4, 'Five'], self.classicFour: [4, 'Four'], self.classicThree: [5, 'Three'], 
        self.classicScout: [8, 'Scout'], self.classicSpy: [1, 'Spy'], self.classicBomb: [6, 'Bomb'], self.classicFlag: [1, 'Flag']}

    def getRankData(self): # rank of each 
        return {"Ten": 10, "Nine": 9, 'Eight': 8, "Seven": 7, 
        "Six": 6, "Five": 5, "Four": 4, "Three": 3, "Scout": 2, 
        "Spy": 1, "Bomb": 0, "Flag": "F"}

    def loadTitleScreen(self): 
        self.gameDisplay.fill(self.black)
        pygame.mixer.music.load('StartMusic.ogg')
        # startMusic from: https://www.free-stock-music.com/peritune-world-op.html
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
        x, y = 2*self.cellSize, 0
        self.gameDisplay.blit(self.titleImage, (x, y))
        font = pygame.font.Font('Shade.ttf', 20)
        # Shade font from: https://www.myfonts.com/fonts/intellecta/antiqua-shaded/?refby=urbanfonts
        buttonText = font.render('Begin', True, (0,0,0))
        button = pygame.Rect(self.width/2 - self.cellSize, self.height-2*self.cellSize, 2*self.cellSize, self.cellSize)
        if self.quit == True:
            quitText = font.render('Restart', True, (0, 0, 0))
            quitButton = pygame.Rect(self.width/2 - 3*self.cellSize, self.height-2*self.cellSize, 2*self.cellSize, self.cellSize)
            buttonText = font.render('Continue', True, (0, 0, 0))
            button = pygame.Rect(self.width/2 + .5*self.cellSize, self.height-2*self.cellSize, 2*self.cellSize, self.cellSize)
            if self.mouseClicked and quitButton.collidepoint((self.mouseX, self.mouseY)):
                print('Restart')
                self.__init__()
            elif self.mouseClicked and button.collidepoint((self.mouseX, self.mouseY)):
                print('Continue')
                self.gameDisplay.fill((255,255,255))
                self.gamePhase = 5
            elif quitButton.collidepoint((self.mouseX, self.mouseY)):
                pygame.draw.rect(self.gameDisplay, (218,165,32), quitButton)
                pygame.draw.rect(self.gameDisplay, (204,0,0), button)
            elif button.collidepoint((self.mouseX, self.mouseY)):
                pygame.draw.rect(self.gameDisplay, (218,165,32), button)
                pygame.draw.rect(self.gameDisplay, (204,0,0), quitButton)
            else:
                pygame.draw.rect(self.gameDisplay, (204,0,0), button)
                pygame.draw.rect(self.gameDisplay, (204,0,0), quitButton)
            self.gameDisplay.blit(buttonText, (self.width/2 + .75*self.cellSize, self.height-1.7*self.cellSize))
            self.gameDisplay.blit(quitText, (self.width/2 - 2.5*self.cellSize, self.height-1.7*self.cellSize))
        else:
            if self.mouseClicked and button.collidepoint((self.mouseX, self.mouseY)):
                self.newPhase()
            elif button.collidepoint((self.mouseX, self.mouseY)):
                pygame.draw.rect(self.gameDisplay, (218,165,32), button)
            else:
                pygame.draw.rect(self.gameDisplay, (204, 0, 0), button)
            self.gameDisplay.blit(buttonText, (self.width/2-.5*self.cellSize, self.height-1.7*self.cellSize))
        pygame.display.update()
        self.clock.tick(60)

    def getTupleRep(self, boardData):
        dataTuple = ()
        for row in range (10):
            for col in range (10):
                dataTuple += (boardData[row][col],)
        return dataTuple

    def newPhase(self): # switch game phase
        self.gamePhase += 1
        print(f'Game Phase : {self.gamePhase}')
    
    def loadInstructionScreen(self): # written rules from https://github.com/Therizno/STRATEGO-with-Pygame
        x, y = self.width/2-self.cellSize, self.cellSize
        font = pygame.font.Font('Livingst.ttf', 46)
        # livingst font from https://www.urbanfonts.com/fonts/Livingstone.font
        title = font.render('Rules', True, (0,0,0))
        font2 = pygame.font.Font('Deutsch.ttf', 20)
        # Deutsche font from: https://www.myfonts.com/fonts/alterlittera/deutsche-schrift/?refby=urbanfonts
        self.gameDisplay.blit(title, (x, y))
        file = open("rules.csv", "r")
        y = self.height/4
        for line in file:
            ruleTextSurfaceObj = font2.render(line.rstrip(), True, self.black)
            rulesRect = ruleTextSurfaceObj.get_rect()
            rulesRect.center = (self.width/2, y)
            self.gameDisplay.blit(ruleTextSurfaceObj, rulesRect)
            y += 25
        file.close()
        font = pygame.font.Font('Shade.ttf', 20)
        # Shade font from: https://www.myfonts.com/fonts/intellecta/antiqua-shaded/?refby=urbanfonts
        if self.help == True:
            returnText = font.render('Return', True, (0,0,0))
            returnButton = pygame.Rect(.5*self.cellSize, self.height-self.cellSize, 2*self.cellSize, 0.8*self.cellSize) 
            if self.mouseClicked and returnButton.collidepoint((self.mouseX, self.mouseY)):
                self.gameDisplay.fill((255,255,255))
                self.gamePhase = self.returnPhase
                self.help = None
            elif returnButton.collidepoint((self.mouseX, self.mouseY)):
                pygame.draw.rect(self.gameDisplay, (218,165,32), returnButton)
            else:
                pygame.draw.rect(self.gameDisplay, (204, 0, 0), returnButton)
            self.gameDisplay.blit(returnText, (self.cellSize, self.height-.8*self.cellSize))  
        else:
            buttonText = font.render('Continue', True, (0,0,0))
            button = pygame.Rect(self.width - 2.5*self.cellSize, self.height-self.cellSize, 2*self.cellSize, 0.8*self.cellSize)
            if self.mouseClicked and button.collidepoint((self.mouseX, self.mouseY)):
                self.newPhase()
            elif button.collidepoint((self.mouseX, self.mouseY)):
                pygame.draw.rect(self.gameDisplay, (218,165,32), button)
            else:
                pygame.draw.rect(self.gameDisplay, (204, 0, 0), button)
            self.gameDisplay.blit(buttonText, (self.width - 2.3*self.cellSize, self.height-.8*self.cellSize))
        pygame.display.update()
    
    def loadGameModeSelection(self):
        self.gameDisplay.blit(self.styleBackground, (0, 0))
        x, y = self.boardWidth/2 - self.cellSize, self.boardHeight/3
        font = pygame.font.Font('Livingst.ttf', 60)
        # livingst font from: https://www.urbanfonts.com/fonts/Livingstone.font
        font2 = pygame.font.Font('Shade.ttf', 20)
        # Shade font from: https://www.myfonts.com/fonts/intellecta/antiqua-shaded/?refby=urbanfonts
        title = font.render('Select Game Mode', True, self.black)
        self.gameDisplay.blit(title, (x, y))
        defensiveText = font2.render('Defensive AI', True, (0,0,0))
        defensiveButton = pygame.Rect(self.width/2 - 6*self.cellSize, self.height-2*self.cellSize, 2.3*self.cellSize, 0.8*self.cellSize)
        strategicText = font2.render('Strategic AI', True, (0,0,0))
        strategicButton = pygame.Rect(self.width/2 - self.cellSize, self.height-2*self.cellSize, 2.3*self.cellSize, .8*self.cellSize)
        aggressiveText = font2.render('Aggressive AI', True, (0,0,0))
        aggressiveButton = pygame.Rect(self.width/2 + 4*self.cellSize, self.height-2*self.cellSize, 2.3*self.cellSize, .8*self.cellSize)
        if self.mouseClicked and defensiveButton.collidepoint((self.mouseX, self.mouseY)):
            self.AIMode = 'defensive'
            self.newPhase()
        elif self.mouseClicked and strategicButton.collidepoint((self.mouseX, self.mouseY)):
            self.AIMode = 'strategic'
            self.newPhase()
        elif self.mouseClicked and aggressiveButton.collidepoint((self.mouseX, self.mouseY)):
            self.AIMode = 'aggressive'
            self.newPhase()
        elif defensiveButton.collidepoint((self.mouseX, self.mouseY)):
            pygame.draw.rect(self.gameDisplay, (218,165,32), defensiveButton)
            pygame.draw.rect(self.gameDisplay, (255, 255, 255), strategicButton)
            pygame.draw.rect(self.gameDisplay, (255, 255, 255), aggressiveButton)
        elif strategicButton.collidepoint((self.mouseX, self.mouseY)):
            pygame.draw.rect(self.gameDisplay, (218,165,32), strategicButton)
            pygame.draw.rect(self.gameDisplay, (255, 255, 255), defensiveButton)
            pygame.draw.rect(self.gameDisplay, (255, 255, 255), aggressiveButton)
        elif aggressiveButton.collidepoint((self.mouseX, self.mouseY)):
            pygame.draw.rect(self.gameDisplay, (218,165,32), aggressiveButton)
            pygame.draw.rect(self.gameDisplay, (255, 255, 255), strategicButton)
            pygame.draw.rect(self.gameDisplay, (255, 255, 255), defensiveButton)
        else:
            pygame.draw.rect(self.gameDisplay, (255, 255, 255), defensiveButton)
            pygame.draw.rect(self.gameDisplay, (255, 255, 255), strategicButton)
            pygame.draw.rect(self.gameDisplay, (255, 255, 255), aggressiveButton)
        self.gameDisplay.blit(defensiveText, (self.width/2 - 6*self.cellSize, self.height-1.8*self.cellSize))
        self.gameDisplay.blit(strategicText, (self.width/2 - self.cellSize, self.height-1.8*self.cellSize))
        self.gameDisplay.blit(aggressiveText, (self.width/2 + 4*self.cellSize, self.height-1.8*self.cellSize))

    def loadUISettings(self):
        self.gameDisplay.fill((255, 255, 255))
        self.gameDisplay.blit(self.styleBackground, (0, 0))
        x, y = self.boardWidth/2-self.cellSize, self.boardHeight/3
        font = pygame.font.Font('Livingst.ttf', 60)
        # livingst font from: https://www.urbanfonts.com/fonts/Livingstone.font
        font2 = pygame.font.Font('Shade.ttf', 20)
        # Shade font from: https://www.myfonts.com/fonts/intellecta/antiqua-shaded/?refby=urbanfonts
        title = font.render('Select Board Theme', True, self.black)
        self.gameDisplay.blit(title, (x, y))
        classicText = font2.render('Classic', True, (0,0,0))
        classicButton = pygame.Rect(self.width/2 - 3*self.cellSize, self.height-2*self.cellSize, 2*self.cellSize, self.cellSize)
        modernText = font2.render('Modern', True, (0,0,0))
        modernButton = pygame.Rect(self.width/2 + .5*self.cellSize, self.height-2*self.cellSize, 2*self.cellSize, self.cellSize)
        if self.mouseClicked and classicButton.collidepoint((self.mouseX, self.mouseY)):
            self.classic = True
            self.newPhase()
        elif self.mouseClicked and modernButton.collidepoint((self.mouseX, self.mouseY)):
            self.modern = True
            self.newPhase()
        elif classicButton.collidepoint((self.mouseX, self.mouseY)):
            pygame.draw.rect(self.gameDisplay, (218,165,32), classicButton)
            pygame.draw.rect(self.gameDisplay, (255, 255, 255), modernButton)
        elif modernButton.collidepoint((self.mouseX, self.mouseY)):
            pygame.draw.rect(self.gameDisplay, (218,165,32), modernButton)
            pygame.draw.rect(self.gameDisplay, (255, 255, 255), classicButton)
        else:
            pygame.draw.rect(self.gameDisplay, (255, 255, 255), classicButton)
            pygame.draw.rect(self.gameDisplay, (255, 255, 255), modernButton)
        self.gameDisplay.blit(classicText, (self.width/2 - 2.5*self.cellSize, self.height-1.7*self.cellSize))
        self.gameDisplay.blit(modernText, (self.width/2 + self.cellSize, self.height-1.7*self.cellSize))
        pygame.display.update()

    def getPieceList(self): # list with frequency of piece
        pieceList = []
        for piece in [(self.spy, 1), (self.bomb, 6), (self.flag, 1), 
        (self.scout, 8), (self.three, 5),
        (self.four, 4), (self.five, 4), (self.six, 4), (self.seven, 3), 
        (self.eight, 2), (self.nine, 1), (self.ten, 1)]:
            image, count = piece
            for i in range(count):
                pieceList.append(image)
        return pieceList

    def initializeBoard(self):
        pygame.init()
        pygame.display.set_caption('Stratego - Single Player')

    def boardDisplay(self, x, y):
        self.gameDisplay.blit(self.board, (x, y))

    def getCoordinates(self, row, col): # turn inputted row/col index into image pixel positions
        cellSize = self.height/10
        x = col * cellSize
        y = row * cellSize
        return (x, y)
    
    def getRowCol(self, x, y): # pixel coord to row/col
        col = x // self.cellSize
        row = y // self.cellSize
        return (row, col)
    
    def checkBoundaries(self, row, col): # check if coordinates within board bounds
        if (row < 6 or row > 9) or (col < 0 or col > 9):
            return False
        return True

    def getArrayRep(self, tupleBoard):
        boardArray = []
        for i in range (0, 100, 10):
            boardRow = []
            for j in range (10):
                boardRow.append(tupleBoard[j+i])
            boardArray.append(boardRow)
        return boardArray

    def eventHandler(self): # main function that handles all events
        self.mouseClicked = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                os._exit(1)
                quit()
            elif event.type == MOUSEMOTION:
                self.mouseX, self.mouseY = event.pos
            elif event.type == MOUSEBUTTONUP:
                self.mouseX, self.mouseY = event.pos
                self.mouseClicked = True
    
    def drawBoard(self):
        self.boardDisplay(0, 0)
        for row in range(len(self.boardData)):
            for col in range(len(self.boardData[0])):
                if self.boardData[row][col] == None:
                    continue
                else:
                    (piece, pieceType, color, (row, col)) = self.boardData[row][col]
                    x, y = self.getCoordinates(row, col)
                    self.drawPiece(x, y, piece)
    
    def drawPiece(self, x, y, item):
        pieceRect = pygame.Rect(x, y, self.cellSize-15, self.cellSize-5)
        pygame.draw.rect(self.gameDisplay, (32, 90, 255), pieceRect)
        self.gameDisplay.blit(item, (x, y))
        return pieceRect

    def distanceFromCenter(self, center, radius):
        x1, y1 = center
        x2, y2 = self.mouseX, self.mouseY
        xQuant = (x2 - x1)**2
        yQuant = (y2 - y1)**2
        dist = (xQuant + yQuant)**0.5
        if dist <= radius:
            return True
        return False
#holds: [[[object for each game square, piece occupying square, occupying piece team], ...], ...]
#[row[col[piece list]]]
#boardData = [[],[],[],[],[],[],[],[],[],[]]
#self.boardData, I want to store the piece in position and its color
    def getObstaclePos(self):
        #removes square data for obstacle squares
        self.illegalMoves = []
        for position in [(4,2), (4,3), (4,6), (4,7), (5,2), (5,3), (5,6), (5,7)]:
            self.illegalMoves.append(position)
        return self.illegalMoves
                
    def dragPieces(self):
        if self.mouseClicked == True:
            if self.selectedPiece == None:
                if self.classic:
                    pieceData = self.classicPieceData
                else:
                    pieceData = self.pieceData
                for item in pieceData:
                    pieceRect = pieceData[item][2]
                    if pieceRect.left <= self.mouseX <= pieceRect.right and\
                         pieceRect.top <= self.mouseY <= pieceRect.bottom and pieceData[item][0] > 0:
                        self.selectedPiece = item
                        pieceData[item][0] -= 1
                        print("You've found a piece! good job")
                for row in range(len(self.boardData)):
                    for col in range(len(self.boardData[0])):
                        x, y = self.getCoordinates(row, col)
                        if self.boardData[row][col] != None and x <= self.mouseX <= x + self.cellSize\
                            and y <= self.mouseY <= y + self.cellSize: # piece is occupying area 
                            print('Getting from board')
                            piece, pieceType, color, position = self.boardData[row][col]
                            self.selectedPiece = piece
                            self.boardData[row][col] = None
            else: 
                print('calling place from click...')
                self.placePieceFromClick()
        if self.selectedPiece != None:
            self.drawPiece(self.mouseX - self.cellRadius, self.mouseY-self.cellRadius, self.selectedPiece)

    def getRowCol(self, x, y):
        if x > self.boardWidth or y > self.boardHeight:
            return None
        row = int(y / self.cellSize)
        col = int(x / self.cellSize)
        return (row, col)

    def placePieceFromClick(self): # setting the pieces onto the board after dragging
        validCell = False
        rows = len(self.boardData)
        cols = len(self.boardData[0])
        if self.getRowCol(self.mouseX, self.mouseY) != None:
            mouseRow, mouseCol = self.getRowCol(self.mouseX, self.mouseY)
        else:
            return
        if self.classic:
            pieceData = self.classicPieceData
        else:
            pieceData = self.pieceData
        if self.boardData[mouseRow][mouseCol] == None and mouseRow >= 6:
            print('Worked!')
            validCell = True
            self.boardData[mouseRow][mouseCol] = (self.selectedPiece, pieceData[self.selectedPiece][1], 'blue', (mouseRow, mouseCol))
            self.drawBoard()
        if not validCell:
            pieceData[self.selectedPiece][0] += 1
        self.selectedPiece = None

    def setupPhase(self):
        self.gameDisplay.fill((255, 255, 255)) 
        self.drawBoard()
        self.ready = True
        if self.randomSetup:
            self.randomizePlayerSetup()
            self.drawBoard()
        elif not self.randomSetup:
            x, y = self.boardWidth+self.cellSize, self.cellSize
            if self.classic and not self.randomSetup:
                pieceData = self.classicPieceData
            else:
                pieceData = self.pieceData
            for item in pieceData:
                if pieceData[item][0] != 0:
                    self.ready = False
                    pieceRect = self.drawPiece(x, y, item)
                    pieceData[item] = [pieceData[item][0], pieceData[item][1], pieceRect]
                countFont = pygame.font.Font('Livingst.ttf', 16)
                # livingst font from: https://www.urbanfonts.com/fonts/Livingstone.font
                count = countFont.render(f'x{pieceData[item][0]}', True, (0,0,0))
                self.gameDisplay.blit(count, (x+.25*self.cellSize, y + self.cellSize + 10))
                if x >= self.width-2*self.cellSize:
                    x = self.boardWidth+self.cellSize
                    y += 2*self.cellSize
                else: 
                    x += self.cellSize
            self.dragPieces()
        if self.ready == True and self.selectedPiece == None:
            self.gameDisplay.fill((255, 255, 255))
            if self.classic:
                self.pieceData = {self.classicTen: [1, 'Ten'], self.classicNine: [1, 'Nine'], self.classicEight: [2, 'Eight'], self.classicSeven: [3, 'Seven'], 
        self.classicSix: [4, 'Six'], self.classicFive: [4, 'Five'], self.classicFour: [4, 'Four'], self.classicThree: [5, 'Three'], 
        self.classicScout: [8, 'Scout'], self.classicSpy: [1, 'Spy'], self.classicBomb: [6, 'Bomb'], self.classicFlag: [1, 'Flag']}
            else:
                self.pieceData = {self.ten: [1, 'Ten'], self.nine: [1, 'Nine'], self.eight: [2, 'Eight'], self.seven: [3, 'Seven'], 
            self.six: [4, 'Six'], self.five: [4, 'Five'], self.four: [4, 'Four'], self.three: [5, 'Three'], 
            self.scout: [8, 'Scout'], self.spy: [1, 'Spy'], self.bomb: [6, 'Bomb'], self.flag: [1, 'Flag']}
            self.randomAISetup()
            self.drawBoard()
            self.newPhase()
        self.drawQuitButton()
        if not self.ready:
            self.drawRandomizeButton()
        self.drawHelpButton()
    
    def randomizePlayerSetup(self):
        #self.boardData = [ ([None] * 10) for row in range(10) ]
        pieceSet = set()
        flagRow = 9
        flagCol = random.randint(0, 9)
        if self.classic:
            self.pieceData = self.getClassicPieceData()
            self.boardData[flagRow][flagCol] = (self.classicFlag, self.pieceData[self.classicFlag][1], 'blue', (flagRow, flagCol))
            self.pieceData[self.classicFlag][0] -= 1
        else: 
            self.pieceData = self.getPieceData()
            self.boardData[flagRow][flagCol] = (self.flag, self.pieceData[self.flag][1], 'blue', (flagRow, flagCol))
            self.pieceData[self.flag][0] -= 1
        tenRow = 6
        tenCol = random.randint(0, 9)
        pieceSet.add((flagRow, flagCol))
        if self.classic:
            self.boardData[tenRow][tenCol] = (self.classicTen, self.pieceData[self.classicTen][1], 'blue', (tenRow, tenCol))
            self.pieceData[self.classicTen][0] -= 1
        else:
            self.boardData[tenRow][tenCol] = (self.ten, self.pieceData[self.ten][1], 'blue', (tenRow, tenCol))
            self.pieceData[self.ten][0] -= 1
        pieceSet.add((tenRow, tenCol))
        nineRow = random.choice([9, 8])
        if flagCol != 0:
            nineCol = flagCol - 1
        else: nineCol = flagCol + 1
        pieceSet.add((nineRow, nineCol))
        if self.classic:
            self.boardData[nineRow][nineCol] = (self.classicNine, self.pieceData[self.classicNine][1], 'blue', (nineRow, nineCol))
            self.pieceData[self.classicNine][0] -= 1
        else:
            self.boardData[nineRow][nineCol] = (self.nine, self.pieceData[self.nine][1], 'blue', (nineRow, nineCol))
            self.pieceData[self.nine][0] -= 1
        for piece in self.pieceData:
            while self.pieceData[piece][0] > 0:
                col = random.randint(0, 9)
                row = random.randint(6,9)
                if (row, col) not in pieceSet:
                    self.boardData[row][col] = (piece, self.pieceData[piece][1], 'blue', (row, col))
                    pieceSet.add((row, col))
                    x, y = self.getCoordinates(row, col)
                    #pygame.draw.rect(piece, (255, 0, 0), (x, y, self.cellSize, self.cellSize))
                    self.pieceData[piece][0] -= 1
                else:
                    continue
        self.ready = True
        self.randomSetup = False

    def randomAISetup(self): #setting initial AI setup randomly
        aiPieceSet = set()
        flagRow = 0
        flagCol = random.randint(0, 9)
        if self.classic:
            self.boardData[flagRow][flagCol] = (self.red, self.pieceData[self.classicFlag][1], 'red', (flagRow, flagCol))
            self.pieceData[self.classicFlag][0] -= 1
        else: 
            self.boardData[flagRow][flagCol] = (self.red, self.pieceData[self.flag][1], 'red', (flagRow, flagCol))
            self.pieceData[self.flag][0] -= 1
        tenRow = 3
        tenCol = random.randint(0, 9)
        aiPieceSet.add((flagRow, flagCol))
        if self.classic:
            self.boardData[tenRow][tenCol] = (self.red, self.pieceData[self.classicTen][1], 'red', (tenRow, tenCol))
            self.pieceData[self.classicTen][0] -= 1
        else:
            self.boardData[tenRow][tenCol] = (self.red, self.pieceData[self.ten][1], 'red', (tenRow, tenCol))
            self.pieceData[self.ten][0] -= 1
        aiPieceSet.add((tenRow, tenCol))
        nineRow = random.choice([0, 1])
        if flagCol != 0:
            nineCol = flagCol - 1
        else: nineCol = flagCol + 1
        aiPieceSet.add((nineRow, nineCol))
        if self.classic:
            self.boardData[nineRow][nineCol] = (self.red, self.pieceData[self.classicNine][1], 'red', (nineRow, nineCol))
            self.pieceData[self.classicNine][0] -= 1
        else:
            self.boardData[nineRow][nineCol] = (self.red, self.pieceData[self.nine][1], 'red', (nineRow, nineCol))
            self.pieceData[self.nine][0] -= 1
        for piece in self.pieceData:
            while self.pieceData[piece][0] > 0:
                col = random.randint(0, 9)
                row = random.randint(0,3)
                if (row, col) not in aiPieceSet:
                    self.boardData[row][col] = (self.red, self.pieceData[piece][1], 'red', (row, col))
                    aiPieceSet.add((row, col))
                    x, y = self.getCoordinates(row, col)
                    #pygame.draw.rect(piece, (255, 0, 0), (x, y, self.cellSize, self.cellSize))
                    self.pieceData[piece][0] -= 1
                else:
                    continue
        #self.hideOpponentPieces()

    def playPhase(self): # player selects piece and then I highlight the squares they can move to
        #if self.playMode:
            #moveDir, attackDir = None, None
        if self.twoPlayer == True:
            pass
        elif self.turn == 'blue':
            if self.processClick() != None:
                self.processClick()
        elif self.turn == 'red':
            if self.AIMode == 'defensive':
                self.randomAIMove()
            elif self.AIMode == 'aggressive':
                self.randomAIMoveMedium()
            elif self.AIMode == 'strategic':
                self.mctsMove()
                self.drawBoard()
            elif self.twoPlayer == True:
                self.getSecondPlayerInput()
                self.drawBoard()
        elif self.gameOver == True and self.win:
            self.showWin()
        elif self.gameOver == True and self.lose:
            self.showLose()
        self.drawBoard()
        self.drawQuitButton()
        self.drawHelpButton()
        pygame.display.update()

    def drawQuitButton(self):
        font = pygame.font.Font('Shade.ttf', 20)
        # Shade font from: https://www.myfonts.com/fonts/intellecta/antiqua-shaded/?refby=urbanfonts
        buttonText = font.render('Quit', True, (0,0,0))
        button = pygame.Rect(self.width - 3*self.cellSize, self.height-1.2*self.cellSize, 2*self.cellSize, 0.8*self.cellSize)
        if self.mouseClicked and button.collidepoint((self.mouseX, self.mouseY)):
            self.quit = True
            self.gamePhase = 0
        elif button.collidepoint((self.mouseX, self.mouseY)):
            pygame.draw.rect(self.gameDisplay, (218,165,32), button)
        else:
            pygame.draw.rect(self.gameDisplay, (204, 0, 0), button)
        self.gameDisplay.blit(buttonText, (self.width - 2.5*self.cellSize, self.height-self.cellSize))

    def drawRandomizeButton(self):
        font = pygame.font.Font('Shade.ttf', 20)
        # Shade font from: https://www.myfonts.com/fonts/intellecta/antiqua-shaded/?refby=urbanfonts
        buttonText = font.render('Auto Setup', True, (0,0,0))
        button = pygame.Rect(self.width - 3*self.cellSize, self.height-3*self.cellSize, 2*self.cellSize, 0.8*self.cellSize)
        if self.mouseClicked and button.collidepoint((self.mouseX, self.mouseY)):
            self.randomSetup = True
        elif button.collidepoint((self.mouseX, self.mouseY)):
            pygame.draw.rect(self.gameDisplay, (218,165,32), button)
        else:
            pygame.draw.rect(self.gameDisplay, (204, 0, 0), button)
        self.gameDisplay.blit(buttonText, (self.width - 2.8*self.cellSize, self.height-2.8*self.cellSize))

    def drawHelpButton(self):
        x, y = (self.width - 0.5*self.cellSize, 0.5*self.cellSize)
        font = pygame.font.Font('Shade.ttf', 18)
        # Shade font from: https://www.myfonts.com/fonts/intellecta/antiqua-shaded/?refby=urbanfonts
        buttonText = font.render('?', True, (0,0,0))
        pygame.draw.circle(self.gameDisplay, (174,176,182), (int(x), int(y)), int(self.cellSize*0.25))
        if self.distanceFromCenter((x, y), self.cellSize*0.25):
            if self.mouseClicked:
                self.help = True
                self.returnPhase = self.gamePhase
                self.gamePhase = 1
            else:
                pygame.draw.circle(self.gameDisplay, (221,242,35), (int(x), int(y)), int(self.cellSize*0.25))
        else:
            pygame.draw.circle(self.gameDisplay, (174,176,182), (int(x), int(y)), int(self.cellSize*0.25))
        self.gameDisplay.blit(buttonText, (x-5, y-10))

    def switchTurn(self):
        if self.turn == 'blue':
            self.turn = 'red'
        elif self.turn == 'red':
            self.turn = 'blue'  

    def getSecondPlayerInput(self):
        pass

    def randomAIMove(self):
        for row in range (len(self.boardData)):
            if self.turn == 'red':
                for col in range (len(self.boardData[0])):
                    if self.turn == 'red':
                        if self.boardData[row][col] != None:
                            piece, pieceType, color, position = self.boardData[row][col]
                            if color == 'red':
                                legalMoves = self.getLegalMoves(self.boardData[row][col])
                                if legalMoves != []:
                                    for move in legalMoves:
                                        if ((row, col), move) in self.aiMoveSet:
                                            continue
                                        else:
                                            self.aiMoveSet.add(((row, col), move))
                                            newRow, newCol = move
                                            if self.boardData[newRow][newCol] != None and self.boardData[row][col] != None:
                                                movePiece, moveType, moveColor, movePosition = self.boardData[newRow][newCol]
                                                if moveColor != 'red':
                                                    if self.attackPiece(self.boardData[row][col], (newRow, newCol)):
                                                        #self.boardData[newRow][newCol] = piece, pieceType, 'red', (newRow, newCol)
                                                        #self.boardData[row][col] = None
                                                        self.drawBoard()
                                                        self.switchTurn()
                                                    else:
                                                        #self.boardData[row][col] = None
                                                        self.drawBoard()
                                                        self.switchTurn()
                                                    self.drawCapturedPieces()
                                                    break 
                                            else:
                                                self.boardData[row][col] = None
                                                self.boardData[newRow][newCol] = piece, pieceType, 'red', (newRow, newCol)
                                                self.drawBoard()
                                                self.switchTurn()   
                                                break
        pygame.display.update()  

    def randomAIMoveMedium(self):
        for row in range (10):
            for col in range (10):
                if self.boardData[row][col] != None:
                    piece, pieceType, color, position = self.boardData[row][col]
                    if color == 'red':
                        legalMoves = self.getLegalMoves(self.boardData[row][col])
                        if legalMoves == []: continue
                        for move in legalMoves:
                            moveRow, moveCol = move
                            if self.boardData[moveRow][moveCol] is None: continue
                            movePiece, moveType, moveColor, movePosition = self.boardData[moveRow][moveCol]
                            if moveColor == 'blue':
                                if moveType == 'Bomb':
                                    choice = random.randint(0, 25)
                                    if choice <= 5:
                                        self.attackPiece(self.boardData[row][col], (moveRow, moveCol))
                                        self.drawBoard()
                                        self.drawCapturedPieces()
                                elif (moveType == 'Flag' or (moveType == 'Ten' and pieceType == 'Spy') \
                                    or self.rankData[moveType] < self.rankData[pieceType]) and moveType != 'Bomb':
                                    self.attackPiece(self.boardData[row][col], (moveRow, moveCol))
                                    self.drawBoard()
                                    self.drawCapturedPieces()
                                    if moveType == 'Flag':
                                        self.lose = True
                                        self.gameOver = True
                                    self.switchTurn()
                                    pygame.display.update()
                                    return
                                else:
                                    continue
                            else:
                                continue
        self.normalAIMove()
    
    def normalAIMove(self):
        for row in range (9, 0, -1):
            for col in range (10):
                if self.boardData[row][col] != None:
                    piece, pieceType, color, position = self.boardData[row][col]
                    if color == 'red':
                        legalMoves = self.getLegalMoves(self.boardData[row][col])
                        if legalMoves == []:
                            continue
                        else:
                            for move in legalMoves:
                                moveRow, moveCol = move
                                if self.boardData[moveRow][moveCol] == None:
                                    self.boardData[moveRow][moveCol] = piece, pieceType, 'red', (moveRow, moveCol)
                                    self.boardData[row][col] = None
                                    self.drawBoard()
                                    self.switchTurn()
                                    pygame.display.update()
                                    return       

    def mctsMove(self):
        emptySpots = self.mcts_ai.getEmptySpots()
        board = self.mcts_ai.make_move(choice(emptySpots))
        if self.mcts_ai.terminal:
            self.gameOver = True
            return
        # You can train as you go, or only at the beginning.
        # Here, we train as we go, doing fifty rollouts each turn.
        for _ in range (10): # training the algorithm by assigning weights to different board states to represent their idealness
            self.tree.do_rollout(board)
        board = self.tree.choose(board)
        #self.findNewMove(board.boardListData)
        #boardList = self.getArrayRep(board)
        mctsMove = self.findBoardDifference(board.boardListData)
        if mctsMove is None:
            self.randomAIMoveMedium()
            return
        else:
            position, piece = mctsMove
            row, col = position
            self.boardData[row][col] = piece
            #self.boardData = board.boardListData
            #self.drawBoard()
            self.switchTurn()
            pygame.display.update()
            if self.mcts_ai.terminal:
                self.gameOver = True
                return
            return

    def findBoardDifference(self, boardMCTSData):
        for row in range (9, 1, -1):
            mctsRow = boardMCTSData[row]
            currentRow = self.boardData[row]
            diff = list(set(mctsRow) - set(currentRow))
            if diff == []: continue
            for move in diff:
                if move is None:
                    col = mctsRow.index(move)
                    oldPiece, oldType, oldColor, oldPosition = self.boardData[row][col]
                    if oldColor == 'red':
                        legalMoves = self.getLegalMoves(self.boardData[row][col])
                        if legalMoves != []:
                            for move1 in legalMoves:
                                moveRow, moveCol = move1
                                if self.boardData[moveRow][moveCol] != None:
                                    movePiece, moveType, moveColor, movePos = self.boardData[moveRow][moveCol]
                                    if self.rankData[moveType] >= self.rankData[oldType]:
                                        self.capturedPieceSet.add(oldType)
                                        self.capturedPieces.append(oldType)
                                        return ((row, col), move)
                else:
                    piece, pieceType, color, position = move # new move made through MCTS
                    if color == 'red': # check if new move was made by red piece
                        row, col = position # get new position of move
                        if self.boardData[row][col] != None: # check to see if there used to be a piece in this position
                            oldPiece, oldType, oldColor, oldPosition = self.boardData[row][col] # get this piece
                            if oldColor == 'blue': # check to make sure this attacked piece was blue
                                oldPos = self.findOldPieceLocation(move, boardMCTSData)
                                oldRow, oldCol = oldPos
                                if self.rankData[oldType] < self.rankData[pieceType]:
                                    self.boardData[oldRow][oldCol] = None # old pos of moved piece
                                    self.capturedPieceSet.add(oldType)
                                    self.capturedPieces.append(oldType)
                                    self.drawCapturedPieces()
                                    return (position, move) # set new position to new move piece
                                elif self.rankData[oldType] == self.rankData[pieceType]:
                                    self.boardData[oldRow][oldCol] = None # old move positions
                                    self.capturedPieceSet.add(oldType)
                                    self.capturedPieceSet.add(pieceType)
                                    self.capturedPieces.extend([oldType, pieceType])
                                    return (position, None)
                                else:
                                    piece = self.boardData[row][col]
                                    self.boardData[oldRow][oldCol] = None
                                    self.capturedPieceSet.add(oldType)
                                    self.capturedPieces.append(oldType)
                                    return (position, piece)
                                #return self.findOldPiece(currentRow, move)
                            else:
                                if self.checkOldLegalMoves(self.boardData[row][col], position):
                                    return (position, move)
                        else: #the new location was previously empty
                            oldPos = self.findOldPieceLocation(move, boardMCTSData)
                            if oldPos is None:
                                continue
                            oldRow, oldCol = oldPos
                            self.boardData[oldRow][oldCol] = None
                            return (position, move)
                    else:
                        continue

    def findOldPieceLocation(self, currPiece, boardData):
        piece, pieceType, color, position = currPiece
        row, col = position
        if pieceType != "Scout":
            pieceMove = 2
        else: pieceMove = 10
        for i in range (1, pieceMove):
            if row-i >= 0:
                if self.boardData[row-i][col] == (piece, pieceType, color, ((row-i), col)):
                    #self.boardData[row-1][col] = None
                    return ((row-i), col)
            if row+i <= 9:
                if self.boardData[row+i][col] == (piece, pieceType, color, ((row+i), col)):
                    #self.boardData[row+1][col] = None
                    return ((row+i), col)
            if col-i >= 0:
                if self.boardData[row][col-i] == (piece, pieceType, color, (row, (col-i))):
                    #self.boardData[row][col-1] = None
                    return (row, (col-i))
            if col+i <= 9:
                if self.boardData[row][col+i] == (piece, pieceType, color, (row, (col+i))):
                    #self.boardData[row][col+1] = None
                    return (row, (col+1))

    def checkOldLegalMoves(self, oldPiece, newPosition):
        legalMoves = self.getLegalMoves(oldPiece)
        if newPosition in legalMoves:
            return True
        return False

    def findOldPiece(self, currentRow, move):
        piece, pieceType, color, position = move
        for oldCell in currentRow: # try to find the old position of the mcts attacking piece
            if oldCell != None:
                cellPiece, cellType, cellColor, cellPosition = oldCell # get the piece
                if cellPiece == piece and cellType == pieceType and cellColor == color: # attacking piece found
                    cellRow, cellCol = cellPosition 
                    self.boardData[cellRow][cellCol] = None # change its old location to None as it has moved
                    return (position, move)

    def drawCapturedPieces(self):
        x, y = self.boardWidth, 2*self.cellSize
        font = pygame.font.Font('Deutsch.ttf', 36)
        # Deustche font from: https://www.myfonts.com/fonts/alterlittera/deutsche-schrift/?refby=urbanfonts
        text = font.render('Captured Pieces', True, (0,0,0))
        textRect = text.get_rect() 
        spaceCenter = (self.width - self.boardWidth)/2
        textRect.center = (spaceCenter+self.boardWidth, self.cellSize)
        for piece in self.capturedPieceSet:
            capturedPiece = self.pieceImageDict[piece]
            capturedCount = self.capturedPieces.count(piece)
            countFont = pygame.font.Font('Livingst.ttf', 16)
            # livingst font from: https://www.urbanfonts.com/fonts/Livingstone.font
            count = countFont.render(f'x{capturedCount}', True, (0,0,0))
            self.gameDisplay.blit(text, textRect)
            self.drawPiece(x, y, capturedPiece)
            self.gameDisplay.blit(count, (x+.25*self.cellSize, y + self.cellSize + 10))
            if x >= self.width-self.cellSize:
                x = self.boardWidth
                y += 2*self.cellSize
            else: 
                x += self.cellSize
        #pygame.display.update() 

    def send_data(self):
        """
        Send position to server
        :return: None
        """
        data = str(self.net.id) + ":" + str(self.player.x) + "," + str(self.player.y)
        reply = self.net.send(data)
        return reply

    @staticmethod
    def parse_data(data):
        try:
            d = data.split(":")[1].split(",")
            return int(d[0]), int(d[1])
        except:
            return 0,0  

    def processClick(self):
        #What this function does is check for what the player wants to do during playphase using
        #mouseclicked, loop thru board, if player clicks occupied space, check if color is player or not
        #if yes, you get the move dir, if no, you get the attack dir, else, if the piece is not occupied, you simply
        #move the piece into the empty space
        if self.displayingEnemyPiece != None:
            enemy, attacker = self.displayingEnemyPiece
            self.displayEnemyPiece(enemy, attacker)
        attackDir = None
        moveDir = None
        if self.win or self.lose: 
            self.newPhase()
        if self.mouseClicked:
            for row in range (len(self.boardData)):
                for col in range (len(self.boardData[0])):
                    x, y = self.getCoordinates(row, col)
                    if self.boardData[row][col] != None:
                        if x <= self.mouseX <= x + self.cellSize and\
                            y <= self.mouseY <= y + self.cellSize:
                            if self.boardData[row][col] != None:
                                piece, pieceType, color, position = self.boardData[row][col]
                                if color != 'red':
                                    self.currPiece = (self.boardData[row][col])
                                    self.selectedPiece = piece
                                elif color != 'blue' and self.selectedPiece != None:
                                    attackDir = self.getLegalMoves(self.currPiece)
                                    if attackDir == None:
                                        self.selectedPiece = None
                                    else: 
                                        mouseRow, mouseCol = self.getRowCol(self.mouseX, self.mouseY)
                                        if (mouseRow, mouseCol) in attackDir:
                                            self.displayingEnemyPiece = None
                                            self.attackPiece(self.currPiece, (mouseRow, mouseCol))
                                            self.drawBoard()
                                            self.drawCapturedPieces()
                                            self.switchTurn()
                                        #self.selectedPiece = None
                                        pygame.display.update()
                    elif self.boardData[row][col] == None:
                        if self.selectedPiece != None:
                            if self.getRowCol(self.mouseX, self.mouseY) == None:
                                return
                            else:
                                mouseRow, mouseCol = self.getRowCol(self.mouseX, self.mouseY)
                            if (mouseRow, mouseCol) == (row, col):
                                legalMoves = self.getLegalMoves(self.currPiece)
                                if (mouseRow, mouseCol) in legalMoves and self.selectedPiece != None:
                                    mouseRow, mouseCol = self.getRowCol(self.mouseX, self.mouseY)
                                    self.boardData[row][col] = None
                                    pieceType = self.pieceData[self.selectedPiece][1]
                                    self.boardData[mouseRow][mouseCol] = self.selectedPiece, pieceType, 'blue', (mouseRow, mouseCol)
                                    piece, pieceType, color, (oldRow, oldCol) = self.currPiece
                                    self.boardData[oldRow][oldCol] = None
                                    self.drawBoard()
                                    pygame.display.update()
                                    self.switchTurn()
                                    self.displayingEnemyPiece = None
                                    break                                
                                
    def getLegalMoves(self, currPiece):
        # get direction should return list of possible moves I think rather than string 
        # currently this is just getting the legal positions from the enemy you're trying to attack
        # not from the player's current position, I need to change that....
        piece, pieceType, color, position = currPiece
        moves = []
        row, col = position
        if pieceType == 'Scout':
            moveRow, moveCol = row, col
            for _ in range (10):
                moveRow += 1
                if moveRow > 9:
                    break
                if (moveRow, col) in self.illegalMoves:
                    break
                else:
                    if self.boardData[moveRow][col] != None:
                        piece, pieceType, color, position = self.boardData[moveRow][col]
                        if color == self.turn:
                            break
                        else: 
                            moves.append((moveRow, col))
                            break
                    else:
                        moves.append((moveRow, col))
            for _ in range (10):
                moveCol += 1
                if moveCol > 9:
                    break
                if (row, moveCol) in self.illegalMoves:
                    break
                else:
                    if self.boardData[row][moveCol] != None:
                        piece, pieceType, color, position = self.boardData[row][moveCol]
                        if color == self.turn:
                            break
                        else: 
                            moves.append((row, moveCol))
                            break
                    else:
                        moves.append((row, moveCol))
            moveRow = row
            for _ in range (10):
                moveRow -= 1
                if moveRow < 0:
                    break
                if (moveRow, col) in self.illegalMoves:
                    break
                else:
                    if self.boardData[moveRow][col] != None:
                        piece, pieceType, color, position = self.boardData[moveRow][col]
                        if color == self.turn:
                            break
                        else: 
                            moves.append((moveRow, col))
                            break
                    else:
                        moves.append((moveRow, col))
            moveCol = col
            for _ in range (10):
                moveCol -= 1
                if moveCol < 0:
                    break
                if (row, moveCol) in self.illegalMoves:
                    break
                else:
                    if self.boardData[row][moveCol] != None:
                        piece, pieceType, color, position = self.boardData[row][moveCol]
                        if color == self.turn:
                            break
                        else: 
                            moves.append((row, moveCol))
                            break
                    else:
                        moves.append((row, moveCol))
        elif pieceType in {'Bomb', 'Flag'}:
            return []
        else:
            moveRow = row + 1
            if (moveRow, col) in self.illegalMoves:
                pass
            elif moveRow < len(self.boardData) and moveRow >= 0:
                if self.boardData[moveRow][col] != None:
                    piece, pieceType, color, position = self.boardData[moveRow][col]
                    if color != self.turn:
                        moves.append((moveRow, col))
                else:
                    moves.append((moveRow, col))
            moveRow = row - 1
            if (moveRow, col) in self.illegalMoves:
                pass
            elif moveRow < len(self.boardData) and moveRow >= 0:
                if self.boardData[moveRow][col] != None:
                    piece, pieceType, color, position = self.boardData[moveRow][col]
                    if color != self.turn:
                        moves.append((moveRow, col))
                else:
                    moves.append((moveRow, col))
            moveCol = col + 1
            if (row, moveCol) in self.illegalMoves:
                pass
            elif moveCol < len(self.boardData) and moveCol >= 0:
                if self.boardData[row][moveCol] != None:
                    piece, pieceType, color, position = self.boardData[row][moveCol]
                    if color != self.turn:
                        moves.append((row, moveCol))
                else:
                    moves.append((row, moveCol))
            moveCol = col - 1
            if (row, moveCol) in self.illegalMoves:
                pass
            elif moveCol < len(self.boardData) and moveCol >= 0:
                if self.boardData[row][moveCol] != None:
                    piece, pieceType, color, position = self.boardData[row][moveCol]
                    if color != self.turn:
                        moves.append((row, moveCol))
                else:
                    moves.append((row, moveCol))
        return moves
       
    def attackPiece(self, pieceTuple, attackedPos):
        piece, pieceType, color, position = pieceTuple
        row, col = position
        row1, col1 = attackedPos
        currPieceRank = self.rankData[pieceType]
        enemyPiece, enemyType, enemyColor, enemyPosition = self.boardData[row1][col1]
        opponentRank = self.rankData[enemyType]
        self.displayingEnemyPiece = (enemyType, pieceType)
        if enemyType == 'Bomb':
            self.capturedPieces.extend([pieceType, enemyType])
            self.capturedPieceSet.add(pieceType)
            self.capturedPieceSet.add(enemyType)
            self.boardData[row1][col1] = None
            self.boardData[row][col] = None
            return False
        elif enemyType == 'Flag':
            if enemyColor == 'blue':
                self.lose = True
            else:
                self.win = True
            self.gameOver = True
            return True
        elif enemyType == 'Ten' and pieceType == 'Spy':
            self.capturedPieceSet.add(enemyType)
            self.capturedPieces.append(enemyType)
            self.boardData[row][col] = None
            self.boardData[row1][col1] = piece, pieceType, color, (row1, col1)
        elif opponentRank > currPieceRank:
            self.boardData[row][col] = None
            self.capturedPieces.append(pieceType)
            self.capturedPieceSet.add(pieceType)
            return False
        elif opponentRank == currPieceRank:
            self.capturedPieces.extend([pieceType, enemyType])
            self.capturedPieceSet.add(pieceType)
            self.capturedPieceSet.add(enemyType)
            self.boardData[row1][col1] = None
            self.boardData[row][col] = None
            return False
        else:
            self.capturedPieceSet.add(enemyType)
            self.capturedPieces.append(enemyType)
            self.boardData[row][col] = None
            self.boardData[row1][col1] = piece, pieceType, color, (row1, col1)
            return True
        self.drawCapturedPieces()
    
    def displayEnemyPiece(self, enemyType, pieceType):
        capturedPiece = self.pieceImageDict[enemyType]
        font = pygame.font.Font('Livingst.ttf', 20)
        # livingst font from: https://www.urbanfonts.com/fonts/Livingstone.font
        x = self.boardWidth + (self.width-self.boardWidth)/2
        pieceDescription = font.render(f'{pieceType} attacked a {enemyType}', True, (0,0,0))
        backgroundRect = pygame.Rect(x-2*self.cellSize, self.height/2+2.5*self.cellSize, 4*self.cellSize, self.cellSize)
        pygame.draw.rect(self.gameDisplay, (255, 255, 255), backgroundRect)
        self.gameDisplay.blit(capturedPiece, (x-.5*self.cellSize, self.height/2+self.cellSize))
        self.gameDisplay.blit(pieceDescription, (x-1.5*self.cellSize, self.height/2+2.5*self.cellSize, 4*self.cellSize, self.cellSize))

    def showWin(self):
        self.gameDisplay.fill((255, 255, 255))
        x, y = self.width/2, self.height/2
        font = pygame.font.Font('Deutsch.ttf', 58)
        # Deutsch font from: https://www.myfonts.com/fonts/alterlittera/deutsche-schrift/?refby=urbanfonts
        text = font.render('You Win!', True, (0,0,0))
        textRect = text.get_rect() 
        textRect.center = (x, y)
        self.gameDisplay.blit(text, textRect)
        font = pygame.font.Font('Shade.ttf', 20)
        # Shade font from: https://www.myfonts.com/fonts/intellecta/antiqua-shaded/?refby=urbanfonts
        buttonText = font.render('Restart', True, (0,0,0))
        button = pygame.Rect(self.width/2 - self.cellSize, self.height-2*self.cellSize, 2*self.cellSize, self.cellSize)
        if self.mouseClicked and button.collidepoint((self.mouseX, self.mouseY)):
            pygame.mixer.music.stop()
            self.__init__()
        elif button.collidepoint((self.mouseX, self.mouseY)):
            pygame.draw.rect(self.gameDisplay, (218,165,32), button)
        else:
            pygame.draw.rect(self.gameDisplay, (204, 0, 0), button)
        self.gameDisplay.blit(buttonText, (self.width/2-.5*self.cellSize, self.height-1.7*self.cellSize))
        pygame.mixer.music.load('Fanfare.ogg')
        # Fanfare from: https://freesound.org/people/Robinhood76/sounds/62176/
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(0)
        pygame.mixer.music.fadeout(2000)
        pygame.display.update()
    
    def showLose(self):
        self.gameDisplay.fill((255, 255, 255))
        x, y = self.width/2, self.height/2
        font = pygame.font.Font('Deutsch.ttf', 58)
        # Deutsche font from: https://www.myfonts.com/fonts/alterlittera/deutsche-schrift/?refby=urbanfonts
        text = font.render('You Lose...', True, (0,0,0))
        textRect = text.get_rect() 
        textRect.center = (x, y)
        self.gameDisplay.blit(text, textRect)
        font = pygame.font.Font('Shade.ttf', 20)
        # Shade font from: https://www.myfonts.com/fonts/intellecta/antiqua-shaded/?refby=urbanfonts
        buttonText = font.render('Restart', True, (0,0,0))
        button = pygame.Rect(self.width/2 - self.cellSize, self.height-2*self.cellSize, 2*self.cellSize, self.cellSize)
        if self.mouseClicked and button.collidepoint((self.mouseX, self.mouseY)):
            pygame.mixer.music.stop()
            self.__init__()
        elif button.collidepoint((self.mouseX, self.mouseY)):
            pygame.draw.rect(self.gameDisplay, (218,165,32), button)
        else:
            pygame.draw.rect(self.gameDisplay, (204, 0, 0), button)
        self.gameDisplay.blit(buttonText, (self.width/2-.5*self.cellSize, self.height-1.7*self.cellSize))
        pygame.mixer.music.load('SadTrombone.ogg')
        # Sad trombone from: https://commons.wikimedia.org/wiki/File:Sad_Trombone-Joe_Lamb-665429450.ogg
        pygame.mixer.music.set_volume(0.6)
        pygame.mixer.music.play(0)
        pygame.mixer.music.fadeout(2800)
        pygame.display.update()

    def runGUI(self, x, y): # main game loop   
        while True:
            self.eventHandler()
            if self.gamePhase == 0:
                self.gameDisplay.fill(self.black)
                self.loadTitleScreen()
                pygame.display.update()
            if self.gamePhase == 1:
                self.gameDisplay.fill((255, 255, 255))
                self.loadInstructionScreen()
                pygame.display.update()
            if self.gamePhase == 2:
                self.gameDisplay.fill((255, 255, 255))
                self.loadGameModeSelection()
                pygame.display.update()
            if self.gamePhase == 3:
                self.gameDisplay.fill((255, 255, 255))
                self.loadUISettings()
            if self.gamePhase == 4:
                self.setupPhase()
            if self.gamePhase == 5:
                tupleData = self.getTupleRep(self.boardData)
                self.mcts_ai = StrategoBoard(10, 10, False, tupleData, self.rankData, self.illegalMoves, 'red', None)
                self.tree = MonteCarlo()
                self.playMode = True
                self.playPhase()
            if self.gamePhase == 6:
                if self.win == True:
                    self.showWin()
                elif self.lose == True:
                    self.showLose()
                else:
                    self.gamePhase = 0
            pygame.display.update()

class Node(ABC): # MCTS framework from https://gist.github.com/qpwo/c538c6f73727e254fdc7fab81024f6e1
    """
    A representation of a single board state.
    MCTS works by constructing a tree of these Nodes.
    Could be e.g. a chess or checkers board state.
    """

    @abstractmethod
    def find_children(self):
        "All possible successors of this board state"
        return set()

    @abstractmethod
    def find_random_child(self):
        "Random successor of this board state (for more efficient simulation)"
        return None

    @abstractmethod
    def is_terminal(self):
        "Returns True if the node has no children"
        return True

    @abstractmethod
    def reward(self):
        "Assumes `self` is terminal node. 1=win, 0=loss, .5=tie, etc"
        return 0

    @abstractmethod
    def __hash__(self):
        "Nodes must be hashable"
        return 123456789

    @abstractmethod
    def __eq__(node1, node2):
        "Nodes must be comparable"
        return True

class StrategoBoard(Node): # MCTS example from https://gist.github.com/qpwo/c538c6f73727e254fdc7fab81024f6e1
    def __init__(board, rows, cols, terminal, boardData, rankData, illegalMoves, turn, winner):
        board.rows = rows
        board.cols = cols
        board.terminal = False
        board.boardTupleData = boardData
        board.boardListData = board.getArrayRep(board.boardTupleData)
        board.turn = turn
        board.rankData = rankData
        board.aiMoveSet = set()
        board.illegalMoves = illegalMoves
        board.winner = winner
    
    def __repr__(board):
        return (f'StrategoBoard({board.rows}, {board.cols}, {board.terminal}, {board.boardTupleData}, {board.rankData}, {tuple(board.illegalMoves)})')
    
    def __hash__(board):
        return hash((f'StrategoBoard({board.rows}, {board.cols}, {board.terminal}, {board.boardTupleData}, {board.rankData}, {board.illegalMoves})'))
    
    def __eq__(board, other):
        return isinstance(other, StrategoBoard) and (board.boardTupleData == other.boardTupleData)

    def getArrayRep(board, tupleBoard):
        boardArray = []
        for i in range (0, 100, 10):
            boardRow = []
            for j in range (10):
                boardRow.append(tupleBoard[j+i])
            boardArray.append(boardRow)
        return boardArray

    def getTupleRep(board, boardData):
        dataTuple = ()
        for row in range (board.rows):
            for col in range (board.cols):
                dataTuple += (boardData[row][col],)
        return dataTuple

    def find_children(board):
        if board.terminal:  # If the game is finished then no moves can be made
            return set()
        emptySpots = board.getEmptySpots()
        # Otherwise, you can make a move in each of the empty spots
        return {board.make_move(choice(emptySpots))}

    def AIattackPiece(board, pieceTuple, attackedPos, boardData):
        piece, pieceType, color, position = pieceTuple
        row, col = position
        row1, col1 = attackedPos
        currPieceRank = board.rankData[pieceType]
        enemyPiece, enemyType, enemyColor, enemyPosition = boardData[row1][col1]
        opponentRank = board.rankData[enemyType]
        GUI.displayingEnemyPiece = (enemyType, pieceType)
        if enemyType == 'Bomb':
            boardData[row1][col1] = None
            boardData[row][col] = None
            return boardData
        elif enemyType == 'Flag':
            boardData[row1][col1] = None
            return boardData
        elif opponentRank > currPieceRank:
            boardData[row][col] = None
            return boardData
        elif opponentRank == currPieceRank:
            boardData[row1][col1] = None
            boardData[row][col] = None
            return boardData
        else:
            boardData[row][col] = None
            boardData[row1][col1] = piece, pieceType, color, (row1, col1)
            return boardData

    def getLegalMoves(board, currPiece, boardListData):
        # get direction should return list of possible moves I think rather than string 
        # currently this is just getting the legal positions from the enemy you're trying to attack
        # not from the player's current position, I need to change that....
        piece, pieceType, color, position = currPiece
        moves = []
        row, col = position
        if pieceType == 'Scout':
            moveRow, moveCol = row, col
            for _ in range (10):
                moveRow += 1
                if moveRow > 9:
                    pass
                elif (moveRow, col) in board.illegalMoves:
                    pass
                else:
                    if boardListData[moveRow][col] != None:
                        piece, pieceType, color, position = boardListData[moveRow][col]
                        if color == board.turn:
                            break
                        else: 
                            moves.append((moveRow, col))
                            break
                    else:
                        moves.append((moveRow, col))
            for _ in range (10):
                moveCol += 1
                if moveCol > 9:
                    break
                elif (row, moveCol) in board.illegalMoves:
                    break
                else:
                    if boardListData[row][moveCol] != None:
                        piece, pieceType, color, position = boardListData[row][moveCol]
                        if color == board.turn:
                            break
                        else: 
                            moves.append((row, moveCol))
                            break
                    else:
                        moves.append((row, moveCol))
            moveRow = row
            for _ in range (10):
                moveRow -= 1
                if moveRow < 0:
                    break
                elif (moveRow, col) in board.illegalMoves:
                    break
                else:
                    if boardListData[moveRow][col] != None:
                        piece, pieceType, color, position = boardListData[moveRow][col]
                        if color == board.turn:
                            break
                        else: 
                            moves.append((moveRow, col))
                            break
                    else:
                        moves.append((moveRow, col))
            moveCol = col
            for _ in range (10):
                moveCol -= 1
                if moveCol < 0:
                    break
                elif (row, moveCol) in board.illegalMoves:
                    break
                else:
                    if boardListData[row][moveCol] != None:
                        piece, pieceType, color, position = boardListData[row][moveCol]
                        if color == board.turn:
                            break
                        else: 
                            moves.append((row, moveCol))
                            break
                    else:
                        moves.append((row, moveCol))
        elif pieceType in {'Bomb', 'Flag'}:
            return []
        else:
            moveRow = row + 1
            if (moveRow, col) in board.illegalMoves:
                pass
            elif moveRow < len(boardListData) and moveRow >= 0:
                if boardListData[moveRow][col] != None:
                    piece, pieceType, color, position = boardListData[moveRow][col]
                    if color != board.turn:
                        moves.append((moveRow, col))
                else:
                    moves.append((moveRow, col))
            moveRow = row - 1
            if (moveRow, col) in board.illegalMoves:
                pass
            elif moveRow < len(boardListData) and moveRow >= 0:
                if boardListData[moveRow][col] != None:
                    piece, pieceType, color, position = boardListData[moveRow][col]
                    if color != board.turn:
                        moves.append((moveRow, col))
                else:
                    moves.append((moveRow, col))
            moveCol = col + 1
            if (row, moveCol) in board.illegalMoves:
                pass
            elif moveCol < len(boardListData) and moveCol >= 0:
                if boardListData[row][moveCol] != None:
                    piece, pieceType, color, position = boardListData[row][moveCol]
                    if color != board.turn:
                        moves.append((row, moveCol))
                else:
                    moves.append((row, moveCol))
            moveCol = col - 1
            if (row, moveCol) in board.illegalMoves:
                pass
            elif moveCol < len(boardListData) and moveCol >= 0:
                if boardListData[row][moveCol] != None:
                    piece, pieceType, color, position = boardListData[row][moveCol]
                    if color != board.turn:
                        moves.append((row, moveCol))
                else:
                    moves.append((row, moveCol))
        return moves

    def randomAIMCTSMove(board, boardData): # MCTS AI uses game results produced from child states found using the previously created medium AI move generator algorithm
        for row in range (10):
            for col in range (10):
                if boardData[row][col] != None:
                    piece, pieceType, color, position = boardData[row][col]
                    if color == board.turn:
                        legalMoves = board.getLegalMoves(boardData[row][col], boardData)
                        if legalMoves == []: continue
                        for move in legalMoves:
                            moveRow, moveCol = move
                            if boardData[moveRow][moveCol] is None: continue
                            movePiece, moveType, moveColor, movePosition = boardData[moveRow][moveCol]
                            if moveColor != board.turn:
                                if board.rankData[moveType] < board.rankData[pieceType] or moveType == 'Flag':
                                    boardData = board.AIattackPiece(boardData[row][col], (moveRow, moveCol), boardData)
                                    boardTupleData = board.getTupleRep(boardData)
                                    return boardTupleData
                                else:
                                    continue
                            else:
                                continue
        return board.normalAIMove(boardData)
    
    def normalAIMove(board, boardData):
        for row in range (10):
            for col in range (10):
                if boardData[row][col] != None:
                    piece, pieceType, color, position = boardData[row][col]
                    if color == board.turn:
                        legalMoves = board.getLegalMoves(boardData[row][col], boardData)
                        if legalMoves == []:
                            continue
                        else:
                            for move in legalMoves:
                                moveRow, moveCol = move
                                if boardData[moveRow][moveCol] == None:
                                    boardData[moveRow][moveCol] = piece, pieceType, board.turn, (moveRow, moveCol)
                                    boardData[row][col] = None
                                    boardTupleData = board.getTupleRep(boardData)
                                    return boardTupleData
    
    def find_random_child(board):
        if board.terminal:
            return None  # If the game is finished then no moves can be made
        emptySpots = board.getEmptySpots()
        if emptySpots == []:
            return None
        return board.make_move(choice(emptySpots))
    
    def getEmptySpots(board): # make it a tuple of the color that can move there along with actual position, then in find children only do the move if the color == board.turn
        moveList = []
        for row in range (10):
            for col in range (10):
                if board.boardListData[row][col] != None:
                    piece, pieceType, color, location = board.boardListData[row][col]
                    if color == board.turn:
                        legalMoves = board.getLegalMoves(board.boardListData[row][col], board.boardListData)
                        if legalMoves != []:
                            moveList.extend(legalMoves)
        return moveList

    def emptySpaceMove(board, move):
        boardData = board.boardListData
        for row in range(10):
            for col in range (10):
                if board.boardListData[row][col] != None:
                    piece, pieceType, color, position = board.boardListData[row][col]
                    legalMoves = board.getLegalMoves(board.boardListData[row][col], board.boardListData)
                    if move in legalMoves:
                        newRow, newCol = move
                        if board.boardListData[newRow][newCol] != None:
                            movePiece, moveType, moveColor, movePosition = board.boardListData[newRow][newCol]
                            if color != moveColor:
                                boardListData = board.AIattackPiece(board.boardListData[row][col], (newRow, newCol), board.boardListData)
                                boardTupleData = board.getTupleRep(boardListData)
                                return boardTupleData
                            else: continue
                        else:
                            boardData[newRow][newCol] = piece, pieceType, board.turn, (newRow, newCol)
                            boardData[row][col] = None
                            boardTupleData = board.getTupleRep(boardData)
                            return boardTupleData
                    else: continue

    def reward(board):
        if not board.terminal:
            raise RuntimeError(f"reward called on nonterminal board {board}")
        if board.winner == board.turn:
            # It's your turn and you've already won. Should be impossible.
            raise RuntimeError(f"reward called on unreachable board {board}")
        if board.turn != board.winner:
            return 0  # Your opponent has just won. Bad.
        if board.winner is None:
            return 0.5  # Board is a tie
        if board.turn == board.winner:
            return 1
        # The winner is neither True, False, nor None
        raise RuntimeError(f"board has unknown winner type {board.winner}")

    def is_terminal(board):
        return board.terminal

    def _find_winner(board, boardState):
        "Returns None if no winner, True if X wins, False if O wins"
        blueFlag = False
        for row in range(board.rows):
            for col in range(board.cols):
                if boardState[row][col] != None:
                    piece, pieceType, color, position = boardState[row][col]
                    if color == 'blue' and pieceType == 'Flag':
                        blueFlag = True
                    elif color == 'red' and blueFlag == True and pieceType != 'Flag':
                        continue
        if blueFlag == True:
            return None
        else: 
            return True
    
    def pieceApproachingFlag(board, boardState):
        for row in range (10):
            for col in range (10):
                if boardState[row][col] != None:
                    piece, pieceType, color, position = boardState[row][col]
                    if pieceType == 'Flag':
                        if board.checkFlagArea(boardState[row][col], boardState):
                            if color == 'blue':
                                return ('red', True)
                            else:
                                return ('blue', True)
        return (None, False)
    
    def checkFlagArea(board, currPiece, boardState): # check if enemy piece is in immediate surrounding area of other team's flag
        piece, pieceType, color, position = currPiece
        row, col = position
        for i in range (2):
            if row >= 6: # if flag on blue or red side
                newRow = row - i
            else:
                newRow = row + i
            newCol = col + i
            newCol1 = col - i
            if boardState[newRow][col] != None:
                otherPiece, otherPieceType, otherColor, otherPos = boardState[newRow][col]
                if otherColor != color:
                    return True
            if newCol <= 9 and newCol >= 0:
                if boardState[row][newCol] != None:
                    otherPiece, otherPieceType, otherColor, otherPos = boardState[row][newCol]
                    if otherColor != color:
                        return True
            if newCol1 <= 9 and newCol1 >= 0:
                if boardState[row][newCol1] != None:
                    otherPiece, otherPieceType, otherColor, otherPos = boardState[row][newCol1]
                    if otherColor != color:
                        return True
        return False

    def make_move(board, move):
        boardTuple = board.emptySpaceMove(move)
        if boardTuple != None:
            boardState = board.getArrayRep(boardTuple)
        else:
            boardState = board.boardListData
        if board.turn == 'red':
            turn = 'blue'
        else:
            turn = 'red'
        winner = board.pieceApproachingFlag(boardState)
        color, terminal = winner
        if terminal == True:
            winner = color
            is_terminal = True
        else:
            winner = None
            is_terminal = False
        return StrategoBoard(10, 10, is_terminal, boardTuple, board.rankData, board.illegalMoves, turn, winner)

class MonteCarlo(object): # MCTS framework from https://gist.github.com/qpwo/c538c6f73727e254fdc7fab81024f6e1
    "Monte Carlo tree searcher. First rollout the tree then choose a move."

    def __init__(self, exploration_weight=1):
        self.Q = defaultdict(int)  # total reward of each node
        self.N = defaultdict(int)  # total visit count for each node
        self.children = dict()  # children of each node
        self.exploration_weight = exploration_weight

    def choose(self, node):
        "Choose the best successor of node. (Choose a move in the game)"
        if node.is_terminal():
            raise RuntimeError(f"choose called on terminal node {node}")

        if node not in self.children:
            return node.find_random_child()

        def score(n):
            if self.N[n] == 0:
                return float("-inf")  # avoid unseen moves
            return self.Q[n] / self.N[n]  # average reward
        return max(self.children[node], key=score)

    def do_rollout(self, node):
        "Make the tree one layer better. (Train for one iteration.)"
        path = self._select(node)
        leaf = path[-1]
        print(f'\nNode = \n{node} in do_rollout\n')
        self._expand(leaf)
        reward = self._simulate(leaf)
        self._backpropagate(path, reward)

    def _select(self, node):
        "Find an unexplored descendent of `node`"
        path = []
        while True:
            path.append(node)
            if node not in self.children or not self.children[node]:
                # node is either unexplored or terminal
                return path
            unexplored = self.children[node] - self.children.keys()
            if unexplored:
                n = unexplored.pop()
                path.append(n)
                return path
            node = self._uct_select(node)  # descend a layer deeper
    
    def getSetFromNodeList(self, state):
        exploredSet = set()
        for row in range(len(state)):
            for col in range(len(state[0])):
                exploredSet.add(state[row][col])
        return exploredSet
    
    # node should be instance of StrategoBoard Class with specified initial params
    # while the self.children dict is dictionay of possible path of different nodes, all class instances
    
    def _expand(self, node):
        "Update the `children` dict with the children of `node`"
        if node in self.children:
            return  # already expanded
        self.children[node] = node.find_children()

    def _simulate(self, node):
        "Returns the reward for a random simulation (to completion) of `node`"
        invert_reward = True
        i = 0
        while True:
            if node.is_terminal():
                reward = node.reward()
                return 1 - reward if invert_reward else reward
            node = node.find_random_child()
            if node == None:
                return
            i += 1
            invert_reward = not invert_reward

    def _backpropagate(self, path, reward):
        "Send the reward back up to the ancestors of the leaf"
        for node in reversed(path):
            self.N[node] += 1
            if reward == None:
                reward = 0
            self.Q[node] += reward
            reward = 1 - reward  # 1 for me is 0 for my enemy, and vice versa

    def _uct_select(self, node):
        "Select a child of node, balancing exploration & exploitation"

        # All children of node should already be expanded:
        assert all(n in self.children for n in self.children[node])

        log_N_vertex = math.log(self.N[node])

        def uct(n):
            "Upper confidence bound for trees"
            return self.Q[n] / self.N[n] + self.exploration_weight * math.sqrt(
                log_N_vertex / self.N[n]
            )

        return max(self.children[node], key=uct)

gui = GUI()                       
gui.runGUI(0, 0) 

#seckbond value in self.q should be next child state or something
#n should be a entire game state/instance of StrategoBoard

#################################################################
#Implement custom variables into MCTS framework, integrate into overall structure
#################################################################


