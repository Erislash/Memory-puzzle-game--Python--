# Memory Puzzle Game
# By Erik Gimenez eri.gim208@gmail.com
# Released under a "MIT" license

import random, pygame, sys
from pygame.locals import *
from __colors import *

FPS = 30 # Frames per second
WINDOW_WIDTH = 640  # Size of window's width in pixels
WINDOW_HEIGHT = 480 # Size of window's height in pixels

REVEAL_SPEED = 8 # Speed boxes' sliding reveals and covers

BOX_SIZE = 40 # Size of box height & width in pixels
GAP_SIZE = 10 # Size of gap between boxes in pixels

BOARD_WIDTH = 5 # Number of columns of icons
BOARD_HEIGHT = 4 # Number of rows of icons
assert (BOARD_WIDTH * BOARD_HEIGHT) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches'

X_MARGIN = int((WINDOW_WIDTH - (BOARD_WIDTH * (BOX_SIZE + GAP_SIZE))) / 2)
Y_MARGIN = int((WINDOW_HEIGHT - (BOARD_WIDTH * (BOX_SIZE + GAP_SIZE))) / 2)

BG_COLOR = NAVYBLUE
LIGHT_BG_COLOR = GRAY
BOX_COLOR = WHITE
HIGHLIGHT_COLOR = BLUE

ALL_COLORS = (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)
ALL_SHAPES = ('donut', 'square', 'diamond', 'lines', 'oval')

assert len(ALL_COLORS) * len(ALL_SHAPES) * 2 >= BOARD_WIDTH * BOARD_HEIGHT, "Board is too big for the number of shapes/colors defined."


def main():
    global FPS_CLOCK, DISPLAY_SURFACE
    pygame.init()

    FPS_CLOCK = pygame.time.Clock()
    DISPLAY_SURFACE = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    

    mouseX = 0 # Used to store x coordinate of mouse event
    mouseY = 0 # Used to store y coordinate of mouse event
    pygame.display.set_caption('Memory Game')

    mainBoard = getRandomizedBoard()
    revealedBoxes = generateRevealedBoxesData(False)

    firstSelection = None # stores the (x, y) of the first box clicked.

    DISPLAY_SURFACE.fill(BG_COLOR)
    startGameAnimation(mainBoard)

    # GAME LOOP
    while True:
        mouseClicked = False

        DISPLAY_SURFACE.fill(BG_COLOR)
        drawBoard(mainBoard, revealedBoxes)

        events = pygame.event.get() # Events
    ################ Event handling loop
        for event in events:
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            elif event.type == MOUSEMOTION:
                (mouseX, mouseY)= event.pos

            elif event.type == MOUSEBUTTONUP:
                mouseX, mouseY = event.pos
                mouseClicked = True
    ################ End Event loop

        boxX, boxY = getBoxAtPixel(mouseX, mouseY)

        if boxX != None and boxY != None:
            # The mouse is currently over a box.
            if not revealedBoxes[boxX][boxY]:
                drawHighlightBox(boxX, boxY)
            if not revealedBoxes[boxX][boxY] and mouseClicked:
                revealBoxesAnimation(mainBoard, [(boxX, boxY)])
                revealedBoxes[boxX][boxY] = True # Set the box as "revealed"

                if firstSelection == None: # the current box was the first box clicked
                    firstSelection = (boxX, boxY)
                else: # the current box was the second box clicked
                    # Check if there is a match between the two icons.
                    icon1shape, icon1color = getShapeAndColor(mainBoard, firstSelection[0], firstSelection[1])
                    icon2shape, icon2color = getShapeAndColor(mainBoard, boxX, boxY)

                    if icon1shape != icon2shape or icon1color != icon2color:
                        # Icons don't match. Re-cover up both selections.
                        pygame.time.wait(1000) # 1000 milliseconds = 1 sec
                        coverBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), (boxX, boxY)])

                        revealedBoxes[firstSelection[0]][firstSelection[1]] = False
                        revealedBoxes[boxX][boxY] = False
                        
                    elif hasWon(revealedBoxes): # check if all pairs found
                        gameWonAnimation(mainBoard)
                        pygame.time.wait(2000)

                        # Reset the board
                        mainBoard = getRandomizedBoard()
                        revealedBoxes = generateRevealedBoxesData(False)

                        # Show the fully unrevealed board for a second.
                        drawBoard(mainBoard, revealedBoxes)
                        pygame.display.update()
                        pygame.time.wait(1000)

                        # Replay the start game animation.
                        startGameAnimation(mainBoard)

                    firstSelection = None # reset firstSelection variable
    # Redraw the screen and wait a clock tick.
    pygame.display.update()
    FPS_CLOCK.tick(FPS)






def generateRevealedBoxesData(val):
    revealedBoxes = []
    for i in range(BOARD_WIDTH):
        revealedBoxes.append([val] * BOARD_HEIGHT)
    return revealedBoxes


#Get a 2D array representing the board, filled with icons of diferent shapes and colors. 
def getRandomizedBoard():
    # Get a list of every possible shape in every possible color.
    icons = []  ##All possible mixes will be stored here
    for color in ALL_COLORS:
        for shape in ALL_SHAPES:
            icons.append((shape, color))
    
    random.shuffle(icons) # randomize the order of the icons list
    numIconsUsed = int(BOARD_WIDTH * BOARD_HEIGHT / 2) # calculate how many icons are needed

    icons = icons[:numIconsUsed] * 2 # make two of each
    random.shuffle(icons)

    # Create the board data structure, with randomly placed icons.
    board = []
    for x in range(BOARD_WIDTH):
        column = []
        for y in range(BOARD_HEIGHT):
            column.append(icons[0])
            del icons[0] # remove the icons as we assign them
        board.append(column)
    return board













def splitIntoGroupsOf(groupSize, theList):
    # splits a list into a list of lists, where the inner lists have at
    # most groupSize number of items.
    result = []
    for i in range(0, len(theList), groupSize):
        result.append(theList[i:i + groupSize])
    return result


def leftTopCoordsOfBox(boxX, boxY):
    # Convert board coordinates to pixel coordinates
    left = boxX * (BOX_SIZE + GAP_SIZE) + X_MARGIN
    top = boxY * (BOX_SIZE + GAP_SIZE) + X_MARGIN
    return (left, top)


def getBoxAtPixel(x, y):
    for boxX in range(BOARD_WIDTH):
        for boxY in range(BOARD_HEIGHT):
            left, top = leftTopCoordsOfBox(boxX, boxY)
            boxRect = pygame.Rect(left, top, BOX_SIZE, BOX_SIZE)
            if boxRect.collidepoint(x, y):
                return (boxX, boxY)
    return (None, None)


def drawIcon(shape, color, boxX, boxY):
    quarter = int(BOX_SIZE * 0.25) # syntactic sugar
    half = int(BOX_SIZE * 0.5) # syntactic sugar

    left, top = leftTopCoordsOfBox(boxX, boxY) # get pixel coords from board coords

    # Draw the shapes
    if shape == 'donut':
        pygame.draw.circle(DISPLAY_SURFACE, color, (left + half, top + half), half - 5)
        pygame.draw.circle(DISPLAY_SURFACE, BG_COLOR, (left + half, top + half), quarter - 5)

    elif shape == 'square':
        pygame.draw.rect(DISPLAY_SURFACE, color, (left + quarter, top + quarter, BOX_SIZE - half, BOX_SIZE - half))

    elif shape == 'diamond':
        pygame.draw.polygon(DISPLAY_SURFACE, color, ((left + half, top), (left + BOX_SIZE - 1, top + half), (left + half, top + BOX_SIZE - 1), (left, top + half)))

    elif shape == 'lines':
        for i in range(0, BOX_SIZE, 4):
            pygame.draw.line(DISPLAY_SURFACE, color, (left, top + i), (left + i, top))
            pygame.draw.line(DISPLAY_SURFACE, color, (left + i, top + BOX_SIZE - 1), (left + BOX_SIZE - 1, top + i))

    elif shape == 'oval':
        pygame.draw.ellipse(DISPLAY_SURFACE, color, (left, top + quarter, BOX_SIZE, half))


def getShapeAndColor(board, boxX, boxY):
    # Shape value for x, y spot is stored in board[x][y][0]
    # color value for x, y spot is stored in board[x][y][1]
    return board[boxX][boxY][0], board[boxX][boxY][1]


def drawBoxCovers(board, boxes, coverage):
    # Draws boxes being covered/revealed. "boxes" is a list of two-item lists, which have the x & y spot of the box.

    for box in boxes:
        left, top = leftTopCoordsOfBox(box[0], box[1])
        pygame.draw.rect(DISPLAY_SURFACE, BG_COLOR, (left, top, BOX_SIZE, BOX_SIZE))

        shape, color = getShapeAndColor(board, box[0], box[1])
        drawIcon(shape, color, box[0], box[1])

        if coverage > 0: # only draw the cover if there is an coverage
            pygame.draw.rect(DISPLAY_SURFACE, BOX_COLOR, (left, top, coverage, BOX_SIZE))

    pygame.display.update()
    FPS_CLOCK.tick(FPS)


def revealBoxesAnimation(board, boxesToReveal):
    # Do the "box reveal" animation.
    for coverage in range(BOX_SIZE, (-REVEAL_SPEED) - 1, - REVEAL_SPEED):
        drawBoxCovers(board, boxesToReveal, coverage)


def coverBoxesAnimation(board, boxesToCover):
    # Do the "box cover" animation.
    for coverage in range(0, BOX_SIZE + REVEAL_SPEED, REVEAL_SPEED):
        drawBoxCovers(board, boxesToCover, coverage)


def drawBoard(board, revealed):
    # Draws all of the boxes in their covered or revealed state.
    for boxX in range(BOARD_WIDTH):
        for boxY in range(BOARD_HEIGHT):
            left, top = leftTopCoordsOfBox(boxX, boxY)
            if not revealed[boxX][boxY]:
                # Draw a covered box.
                pygame.draw.rect(DISPLAY_SURFACE, BOX_COLOR, (left, top, BOX_SIZE, BOX_SIZE))
            else:
                # Draw the (revealed) icon
                shape, color = getShapeAndColor(board, boxX, boxY)
                drawIcon(shape, color, boxX, boxY)


def drawHighlightBox(boxX, boxY):
    (left, top) = leftTopCoordsOfBox(boxX, boxY)
    pygame.draw.rect(DISPLAY_SURFACE, HIGHLIGHT_COLOR, (left - 5, top - 5, BOX_SIZE + 10, BOX_SIZE + 10), 4)


def startGameAnimation(board):
    # Randomly reveal the boxes 8 at a time.
    coveredBoxes = generateRevealedBoxesData(False)
    boxes = []
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            boxes.append( (x, y) )
    random.shuffle(boxes)
    boxGroups = splitIntoGroupsOf(8, boxes)

    drawBoard(board, coveredBoxes)
    for boxGroup in boxGroups:
        revealBoxesAnimation(board, boxGroup)
        coverBoxesAnimation(board, boxGroup)



def gameWonAnimation(board):
    # flash the background color when the player has won
    coveredBoxes = generateRevealedBoxesData(True)
    color1 = LIGHT_BG_COLOR
    color2 = BG_COLOR
    for i in range(13):
        color1, color2 = color2, color1 # swap colors
        DISPLAY_SURFACE.fill(color1)
        drawBoard(board, coveredBoxes)
        pygame.display.update()
        pygame.time.wait(300)


def hasWon(revealedBoxes):
    # Returns True if all the boxes have been revealed, otherwise False
    for i in revealedBoxes:
        if False in i:
            return False # return False if any boxes are covered.
    return True

main()
# if __name__ == '__main__':
#     main()