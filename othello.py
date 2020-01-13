'''
Brian Rouse
CS5001
Homework 7 - othello.py
December 2, 2018

Module for playing a game of Othello.  Contains Othello, Board, Point, and
flipFinder classes.  Uses othello_viz module to draw the board.  Uses score
module to record the game scores.
'''

SQUARE = 50
TILE_OFFSET_X = 4
TILE_OFFSET_Y = 25

# Custom modules
import othello_viz as v
import score as s

# Python library modules
import turtle
import sys
from random import choice
from time import sleep
from copy import deepcopy

class Othello:
    '''Class to represent a game of Othello
       Attributes: board, active_color.
       __init__ function requires board_size (an int, multiple of 4) to create
       a board object as an attribute.  Active_color designates the current
       player turn.

       Methods: __init__, __eq__, start (to start the game), human_turn,
                computer_turn, pass_turn, determine_ai_move, get_valid_flips,
                has_valid_move, end_the_game, report_winner, save_score, and
                get_high_score.
    '''
    def __init__(self, board_size):
        self.board = Board(board_size)
        self.active_color = 'black'

    def __eq__(self, other):
        return self.board == other.board and \
               self.active_color == other.active_color

    def start(self):
        '''parameters: none
           returns: nothing
           does: starts the Othello game.  Draws the board and begins turn flow.
        '''
        v.draw_board(self.board.size, self.board.get_initial_tiles_to_draw(),
                     SQUARE)
        print("Let's play Othello on a {} by {} board.  Place tiles by clicking"
              " on the board.".format(self.board.size, self.board.size))
        
        # Player will get an opportunity to click the screen.  Onscreen
        # coordinates will be passed to human_turn method.
        turtle.onscreenclick(self.human_turn)
        
    def human_turn(self, x, y):
        '''parameters: x and y coordinates (both ints)
           returns: nothing
           does: takes x, y coordinates of a potential tile location. Validates
                 input, places tile, and ends the game or proceeds to next turn,
                 as applicable.
                 Coordinates are obtained via turtle's onscreenclick function.
        '''
        # Disable player's ability to click more squares
        turtle.onscreenclick(None)

        # Convert clicked turtle coordinates to Othello square
        clicked_turtle_coord = Point(int(x), int(y))
        square_coord = self.board.convert_turtle_to_square(clicked_turtle_coord)

        # If the clicked square is a valid move, place a tile.
        new_tile_positions = self.get_valid_flips(square_coord)
        if new_tile_positions:
            new_tile_positions.insert(0, square_coord)
            for position in new_tile_positions:
                self.board.place_tile(position, self.active_color)
            # If the board is full, end the game.  Otherwise, pass the turn.
            if self.board.is_full():
                self.end_the_game()
            self.pass_turn()
        else:
            # If human did not select a valid tile, restart human turn
            turtle.onscreenclick(self.human_turn)

    def computer_turn(self):
        '''parameters: none
           returns: nothing
           does: selects a move for the computer and places the tile.  Then
                 ends the game or proceeds to next turn, as applicable.
        '''
        new_tiles = self.determine_ai_move()
        # Draw the computer's move but wait before flipping other tiles; humans
        # need time to process what is happening
        computer_move = new_tiles[0]
        self.board.place_tile(computer_move, self.active_color)
        sleep(0.5)
        for i in range(1, len(new_tiles)):
            self.board.place_tile(new_tiles[i], self.active_color)
        # If the board is full, end the game.  Otherwise, pass the turn.
        if self.board.is_full():
            self.end_the_game()
        self.pass_turn()

    def pass_turn(self, strike=False):
        '''parameters: strike, an optional boolean
           returns: nothing
           does: if human turn, calls computer turn, and vice versa.  If no
                 valid moves exist for the upcoming turn, skips that turn with
                 with a strike - if two consecutive strikes, ends the game.
        '''
        # If it's the human's turn, check if computer will have a valid move.
        if self.active_color == 'black':
            self.active_color = 'white'
            # If yes, pass the turn to computer
            if self.has_valid_move():
                print("It's white's turn (the computer)!")
                self.computer_turn()
            # If no, decide whether to end the game or skip computer's turn
            else:
                if strike:
                    self.end_the_game()
                else:
                    print("No valid move for computer.")
                    self.pass_turn(True)
                    
        # If it's the computer's turn, check if human will have a valid move.          
        else:
            self.active_color = 'black'
            # If yes, pass the turn to human
            if self.has_valid_move():
                print("It's black's turn (that's you)!")
                turtle.onscreenclick(self.human_turn)
            # If no, decide whether to end the game or skip human's turn
            else:
                if strike:
                    self.end_the_game()
                else:
                    print("No valid move for you.")
                    self.pass_turn(True)
                
    def determine_ai_move(self):
        '''parameters: none
           returns: computer's move and the resulting tile flips (a list of
                    positions).  Returns nothing if no valid moves exist.
           does: determines computer's move by randomly selecting a valid move.
                 Truly, a skilled opponent.
        '''
        # Make a list of all empty positions on the board
        test_positions = []
        for i in range(self.board.size):
            for j in range(self.board.size):
                if self.board.positions[i][j] == 0:
                    test_positions.append(Point(i, j))

        # Randomly choose from empty positions until a valid move is found,
        # removing invalid moves from testing pool as they come
        while test_positions:
            random_move = choice(test_positions)
            new_tiles = self.get_valid_flips(random_move)
            if new_tiles:
                new_tiles.insert(0, random_move)
                return new_tiles
            else:
                test_positions.remove(random_move)

    def get_valid_flips(self, point):
        '''parameters: a proposed Othello move (a point)
           returns: a list of all tile points that the move would flip, or an
                    empty list if no flips would occur.
                    Returns empty list if function is passed None or if point
                    is not an empty square on the board.
        '''
        # Note: function needs to check that point is not None, as other
        # functions, such as board.convert_turtle_to_square, will return a None
        # point for edge cases
        if not point or not self.board.is_empty_square(point):
            return []
        flip_finder = flipFinder(self.board.size, self.board.positions, \
                                 self.active_color)
        flip_positions = flip_finder.find_flips_all(point)
        return flip_positions

    def has_valid_move(self):
        '''parameters: none
           returns: a boolean, True if active player has a valid move available,
                    otherwise False.
           Note: a valid move is any move that would outflank (flip) at least
                 one opposing tile.
        '''
        for i in range(self.board.size):
            for j in range(self.board.size):
                if self.board.positions[i][j] == 0:
                    flips = self.get_valid_flips(Point(i, j))
                    if flips:
                        return True
        return False

    def end_the_game(self):
        '''parameters: none
           returns: nothing
           does: reports the game winner and then exits the game
        '''
        self.report_winner()
        self.save_score()
        sys.exit()
                
    def report_winner(self):
        '''parameters: none
           returns: nothing
           does: prints final game score and winner
        '''
        print("Game over! Score is {} for black and {} for white."
              .format(self.board.black_tiles, self.board.white_tiles))
        if self.board.black_tiles > self.board.white_tiles:
            print("Black wins!")
        elif self.board.white_tiles > self.board.black_tiles:
            print("White wins!")
        else:
            print("It's a tie!")

    def save_score(self):
        '''parameters: none
           returns: nothing
           does: records player's name and updates the score file (a flat file)
                 with player's score.  New high scores will be placed at the
                 top of file, all other scores at bottom.  Creates a new score
                 file if one does not already exist.
        '''
        player_name = input("Enter your name to save your score:\n")
        formatted_score = player_name + ' ' + str(self.board.black_tiles) + '\n'
        current_scores = s.read_scores()

        # If cannot find or open score file, create a new file and add the score
        if not current_scores:
            print("You're the first person to enter a score!")
            s.append_score(formatted_score)
        # If file exists, update it
        else:
            high_score = self.get_high_score(current_scores)
            if self.board.black_tiles >= high_score:
                print("You're the new high scorer!")
                current_scores.insert(0, formatted_score)
                s.write_scores(current_scores)
            else:
                s.append_score(formatted_score)

    def get_high_score(self, score_lst):
        '''parameters: a list of scores to search
           returns: highest score, or nothing if score_lst is empty
           note: score format must be ["text goes here 5\n", . . .] with score
           at the end of each element.
        '''
        if not score_lst:
            return
        
        # Make a copy of scores list then parse the copy
        temp_scores = deepcopy(score_lst)
        for i in range(len(temp_scores)):
            temp_scores[i] = temp_scores[i].replace('\n', '')
            temp_scores[i] = temp_scores[i].split()

        # Get highest score from parsed list of lists
        high_score = int(temp_scores[0][-1])
        for entry in temp_scores:
            score = int(entry[-1])
            if score > high_score:
                high_score = score
        return high_score

            
class Board:
    '''Class to represent an Othello board
       Attributes: size, center, positions, black_tiles, white_tiles.
       __init__ function requires board size (an int, multiple of 4)

       Methods: __init__, __eq__, find_center, initialize_positions,
                get_initial_tiles_to_draw, convert_turtle_to_square, place_tile,
                record_tile, is_empty_square, is_a_square, is_full
    '''
    def __init__(self, board_size):
        self.size = board_size
        self.center = self.find_center()
        self.positions = self.initialize_positions()
        self.black_tiles = 2
        self.white_tiles = 2

    def __eq__(self, other):
        return self.size == other.size and \
               self.positions == other.positions and \
               self.black_tiles == other.black_tiles and \
               self.white_tiles == other.white_tiles and \
               self.center == other.center

    def find_center(self):
        '''parameters: none
           returns: central point of the board (a Point)
           does: used to initialize center attribute
        '''
        center = int(self.size / 2 - 1)
        center_coordinates = Point(center, center)
        return center_coordinates

    def initialize_positions(self):
        '''parameters: none
           returns: board positions - a nested list of possible tile positions,
                    all empty (set to 0).
                    Format: positions[x][y] corresponds to square in (x, y)
                    postion.
           does: used to initialize positions attribute.
        '''
        positions = [[0] * self.size for i in range(self.size)]
        if not positions:
            return []

        # Update positions with the four starting tiles
        x = self.center.x
        y = self.center.y
        positions[x][y] = 'black'
        positions[x + 1][y] = 'white'
        positions[x + 1][y + 1] = 'black'
        positions[x][y + 1] = 'white'
        return positions

    def get_initial_tiles_to_draw(self):
        '''parameters: none
           returns: a nested list of starting tiles, to be passed to draw_board
                    function in othello_viz module.
                    Format: [[point, color], [point, color]...] 
        '''
        x = self.center.x
        y = self.center.y
        tile_one = self.convert_turtle_to_square(self.center, 'r')
        tile_two = self.convert_turtle_to_square(Point(x + 1, y), 'r')
        tile_three = self.convert_turtle_to_square(Point(x + 1, y + 1), 'r')
        tile_four = self.convert_turtle_to_square(Point(x, y + 1), 'r')
        tiles = [tile_one, tile_two, tile_three, tile_four]
        colors = ['black', 'white', 'black', 'white']
        starting_tiles = list(zip(tiles, colors))
        return starting_tiles

    def convert_turtle_to_square(self, point, reverse=''):
        '''parameters: a point to convert (see Point class);
                       specify 'r' to have function convert square to turtle.
           returns: converted coordinates (a point).  Returns nothing if input
                    is outside the range of Othello board.
           does: converts an x,y point from Othello board in the turtle window
                 to x,y point that corresponds with board positions attribute.
                 In reverse, function will convert a square's x,y coordinates to
                 a point that can be used by draw_tile function in othello_viz.
        '''
        # Confirm that the onscreen point is within the board
        if reverse == '':
            turtle_coordinate_range = SQUARE * self.size / 2
            if point.x > turtle_coordinate_range or \
               point.x < -turtle_coordinate_range or \
               point.y > turtle_coordinate_range or \
               point.y < -turtle_coordinate_range:
                return
            # Convert clicked turtle coordinates into square coordinates
            x_coordinate = int((point.x + SQUARE) // SQUARE + self.center.x)
            y_coordinate = int((point.y + SQUARE) // SQUARE + self.center.y)
            square_coordinates = Point(x_coordinate, y_coordinate)
            return square_coordinates

        if reverse == 'r':
            # Confirm that the square is on the board
            if not self.is_a_square(point):
                return
            # Convert square coordinates into turtle coordinates
            # for v.draw_square function
            x_coordinate = SQUARE*(point.x - self.center.x) - TILE_OFFSET_X
            y_coordinate = SQUARE*(point.y - self.center.y) - TILE_OFFSET_Y
            turtle_coordinates = Point(x_coordinate, y_coordinate)
            return turtle_coordinates

    def place_tile(self, tile, color):
        '''parameters: a tile position (a point) and tile color (a string)
           returns: nothing
           does: records the tile in board_positions attribute and uses
                 othello_viz module to draw the tile
        '''
        self.record_tile(tile, color)
        draw_coord = self.convert_turtle_to_square(tile, 'r')
        v.draw_tile(draw_coord, color)

    def record_tile(self, point, color):
        '''parameters: an x,y point and a string color (black or white)
           returns: nothing
           does: takes a point corresponding to self.positions attribute and
                 updates the attribute with a new tile at that point.  Also
                 updates tile count attributes.  If point is outside board
                 range, function does nothing.
        '''
        # Confirm that designated point is actually on the board.
        if not self.is_a_square(point):
            return
        # Update attributes as applicable
        if color == 'black':
            other_color = 'white'
        elif color == 'white':
            other_color = 'black'
        else:
            other_color = None
        
        if self.positions[point.x][point.y] == 0:
            if color == 'black':
                self.black_tiles += 1
            elif color == 'white':
                self.white_tiles += 1
        elif self.positions[point.x][point.y] == other_color:
            if color == 'black':
                self.black_tiles += 1
                self.white_tiles -= 1
            elif color == 'white':
                self.white_tiles += 1
                self.black_tiles -= 1
        if color == 'black' or color == 'white':
            self.positions[point.x][point.y] = color
        
    def is_empty_square(self, point):
        '''parameters: an x,y point
           returns: a boolean, True if point position is empty in self.positions
                    attribute, otherwise False.  Returns False if point is
                    outside of board.
        '''
        if not self.is_a_square(point):
            return False
        
        if self.positions[point.x][point.y] == 0:
            return True
        else:
            return False

    def is_a_square(self, point):
        '''parameters: an x, y point corresponding to self.positions attribute.
           returns: a boolean, True if point is on the Othello board, otherwise
                    False.
        '''
        max_coordinate = self.size - 1
        if 0 <= point.x <= max_coordinate and \
           0 <= point.y <= max_coordinate:
            return True
        else:
            return False

    def is_full(self):
        '''parameters: none
           returns: a boolean, True if all squares on the board are full,
                    otherwise False
           note: function uses black_tiles and white_tiles attributes to
                 determine board state rather than positions attribute.
        '''
        num_squares = self.size * self.size
        if self.black_tiles + self.white_tiles >= num_squares:
            return True
        else:
            return False


class Point:
    '''Class to represent an x,y point on a Cartesian plane
       Attributes: x and y, both required for __init__ function
       Methods: __init__, __str__, __eq__
    '''
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ')'

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class flipFinder:
    '''Class that finds outflanking flips for moves an Othello board
       Attributes: size, positions, and color, all required for __init__
       Methods: __init__, find_flips_all, find_flips_north, find_flips_south,
                find_flips_east, find_flips_west, find_flips_ne, find_flips_nw,
                find_flips_se, find_flips_sw
       Notes: This class typically uses the paramenters from an existing board
             object.  Class methods do not check if proposed moves tie to empty
             squares.
    '''
    def __init__(self, board_size, board_positions, active_color):
        self.size = board_size
        self.positions = board_positions
        self.color = active_color

    def find_flips_all(self, move):
        '''parameters: a proposed Othello move (a point)
           returns: a list of tile positions (points) that the move would flip,
                    in all 4 cardinal and all 4 diagonal directions.
                    Returns nothing if no flips or if move is outside of the
                    board.
        '''
        flip_positions = []
        try:
            flip_positions.extend(self.find_flips_north(move))
            flip_positions.extend(self.find_flips_south(move))
            flip_positions.extend(self.find_flips_east(move))
            flip_positions.extend(self.find_flips_west(move))
            flip_positions.extend(self.find_flips_ne(move))
            flip_positions.extend(self.find_flips_nw(move))
            flip_positions.extend(self.find_flips_se(move))
            flip_positions.extend(self.find_flips_sw(move))
        except IndexError:
            return []
        return flip_positions

    def find_flips_north(self, move):
        '''parameters: a proposed Othello move (a point)
           returns: a list of tile positions (points) north of the move that
                    would be flipped.  Returns nothing if no flips or if move is
                    outside of the board.
        '''
        flip_positions = []
        possible_flips = []
        y = move.y
        while True:
            y += 1
            try:
                if y >= self.size or self.positions[move.x][y] == 0:
                    possible_flips.clear()
                    break
                if self.positions[move.x][y] == self.color:
                    break
            except IndexError:
                return []
            possible_flips.append(Point(move.x, y))
        flip_positions.extend(possible_flips)
        return flip_positions
            
    def find_flips_south(self, move):
        '''parameters: a proposed Othello move (a point)
           returns: a list of tile positions (points) south of the move that
                    would be flipped.  Returns nothing if no flips or if move is
                    outside of the board.
        '''
        flip_positions = []
        possible_flips = []
        y = move.y
        while True:
            y -= 1
            try:
                if y < 0 or self.positions[move.x][y] == 0:
                    possible_flips.clear()
                    break
                if self.positions[move.x][y] == self.color:
                    break
            except IndexError:
                return []
            possible_flips.append(Point(move.x, y))
        flip_positions.extend(possible_flips)   
        return flip_positions

    def find_flips_east(self, move):
        '''parameters: a proposed Othello move (a point)
           returns: a list of tile positions (points) east of the move that
                    would be flipped.  Returns nothing if no flips or if move is
                    outside of the board.
        '''
        flip_positions = []
        possible_flips = []
        x = move.x
        while True:
            x += 1
            try:
                if x >= self.size or self.positions[x][move.y] == 0:
                    possible_flips.clear()
                    break
                if self.positions[x][move.y] == self.color:
                    break
            except IndexError:
                return []
            possible_flips.append(Point(x, move.y))
        flip_positions.extend(possible_flips)   
        return flip_positions

    def find_flips_west(self, move):
        '''parameters: a proposed Othello move (a point)
           returns: a list of tile positions (points) west of the move that
                    would be flipped.  Returns nothing if no flips or if move is
                    outside of the board.
        '''
        flip_positions = []
        possible_flips = []
        x = move.x
        while True:
            try:
                x -= 1
                if x < 0 or self.positions[x][move.y] == 0:
                    possible_flips.clear()
                    break
                if self.positions[x][move.y] == self.color:
                    break
            except IndexError:
                return []
            possible_flips.append(Point(x, move.y))
        flip_positions.extend(possible_flips)   
        return flip_positions

    def find_flips_ne(self, move):
        '''parameters: a proposed Othello move (a point)
           returns: a list of tile positions (points) northeast of the move that
                    would be flipped.  Returns nothing if no flips or if move is
                    outside of the board.
        '''
        flip_positions = []
        possible_flips = []
        x = move.x
        y = move.y
        while True:
            x += 1
            y += 1
            try:
                if x >= self.size or y >= self.size or self.positions[x][y] == 0:
                    possible_flips.clear()
                    break
                if self.positions[x][y] == self.color:
                    break
            except IndexError:
                return []
            possible_flips.append(Point(x, y))
        flip_positions.extend(possible_flips)   
        return flip_positions

    def find_flips_sw(self, move):
        '''parameters: a proposed Othello move (a point)
           returns: a list of tile positions (points) southwest of the move that
                    would be flipped.  Returns nothing if no flips or if move is
                    outside of the board.
        '''
        flip_positions = []
        possible_flips = []
        x = move.x
        y = move.y
        while True:
            x -= 1
            y -= 1
            try:
                if x < 0 or y < 0 or self.positions[x][y] == 0:
                    possible_flips.clear()
                    break
                if self.positions[x][y] == self.color:
                    break
            except IndexError:
                return []
            possible_flips.append(Point(x, y))
        flip_positions.extend(possible_flips)   
        return flip_positions

    def find_flips_nw(self, move):
        '''parameters: a proposed Othello move (a point)
           returns: a list of tile positions (points) northwest of the move that
                    would be flipped.  Returns nothing if no flips or if move is
                    outside of the board.
        '''
        flip_positions = []
        possible_flips = []
        x = move.x
        y = move.y
        while True:
            x -= 1
            y += 1
            try:
                if x < 0 or y >= self.size or self.positions[x][y] == 0:
                    possible_flips.clear()
                    break
                if self.positions[x][y] == self.color:
                    break
            except IndexError:
                return []
            possible_flips.append(Point(x, y))
        flip_positions.extend(possible_flips)   
        return flip_positions

    def find_flips_se(self, move):
        '''parameters: a proposed Othello move (a point)
           returns: a list of tile positions (points) southeast of the move that
                    would be flipped.  Returns nothing if no flips or if move is
                    outside of the board.
        '''
        flip_positions = []
        possible_flips = []
        x = move.x
        y = move.y
        while True:
            x += 1
            y -= 1
            try:
                if x >= self.size or y < 0 or self.positions[x][y] == 0:
                    possible_flips.clear()
                    break
                if self.positions[x][y] == self.color:
                    break
            except IndexError:
                return []
            possible_flips.append(Point(x, y))
        flip_positions.extend(possible_flips)   
        return flip_positions
