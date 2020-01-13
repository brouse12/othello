'''
Brian Rouse
CS5001
Homework 7 - othello_test.py
December 2, 2018

1. unittest for Othello class (includes unittests for Board, flipFinder, and
   Point classes)
2. unittest for score module
'''
'''
Notes on why certain functions are excluded from unit test:
1. all of othello_viz module - these are drawing functions only.

2. Othello.start - calls a drawing function and initiates a difficult-to-test
                   sequence of ongoing turns.
3. Othello.human_turn - calls a drawing function and initiates a difficult-to-
                        test sequence of ongoing turns.
4. Othello.computer_turn - calls a drawing function and initiates a difficult-
                           to-test sequence of ongoing turns.
5. Othello.pass_turn - creates one of two different scenarios that are
                       difficult to test: 1) an ongoing sequence of turns or
                       2) exiting the program.
6. Othello.end_the_game - exits the program - difficult to test.  I believe
                          I could test this with something like
                          assertRaises(SystemExit), but I ran out of time and
                          need to save it for another day!

7. Othello.save_score - complexity arising from needing user input and making
                        different kinds of file updates.  I believe I could test
                        this using unittest.mock and patch, but I ran out of
                        time and need to save it for another day!

8. Board.place_tile - calls a drawing function
                   
Each of these functions can be tested by manually playing the game.  Any non-
drawing functions that they call are included in the unit test.
'''

INITIALIZED_4X4_BOARD = [[0, 0, 0, 0],
                         [0, 'black', 'white', 0],
                         [0, 'white', 'black', 0],
                         [0, 0, 0, 0]]

INITIALIZED_8X8_BOARD = [[0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 'black', 'white', 0, 0, 0],
                         [0, 0, 0, 'white', 'black', 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0],
                         [0, 0, 0, 0, 0, 0, 0, 0]]

DUMMY_SCORES = 'dummy_scores.txt'

import unittest
from unittest.mock import patch, call
from othello import Othello, flipFinder, Board, Point
import score

class othelloTest(unittest.TestCase):
    def test_init(self):
        game = Othello(4)
        self.assertEqual(game.board, Board(4))
        self.assertEqual(game.active_color, 'black')

        game = Othello(8)
        self.assertEqual(game.board, Board(8))
        self.assertEqual(game.active_color, 'black')

    def test_eq(self):
        # Set up test games with different attributes
        game_one = Othello(8)
        game_two = Othello(8)
        game_three = Othello(16)
        game_four = Othello(8)
        game_four.active_color = 'white'

        # Test equality
        self.assertEqual(game_one, game_two)
        self.assertNotEqual(game_one, game_three)
        self.assertNotEqual(game_one, game_four)

    def test_determine_ai_move(self):
        # Test that computer finds the only valid move on a board
        game = Othello(4)
        game.active_color = 'white'
        game.board.positions = [['white', 'black', 'black', 'black'],
                                ['black', 'black', 'white', 'black'],
                                ['black', 'white', 'black', 'black'],
                                ['black', 'black', 'black', 0]]
        ai_move = game.determine_ai_move()
        self.assertEqual(ai_move, [Point(3, 3), Point(2, 2), Point(1, 1)])

        # Test that computer picks a valid move from multiple possibilities
        game = Othello(4)
        game.active_color = 'white'
        game.board.positions = [[0, 0, 'white', 0],
                                [0, 'black', 'white', 0],
                                [0, 'white', 'black', 0],
                                [0, 0, 0, 'white']]
        ai_move = game.determine_ai_move()
        # Use get_valid_flips function to test that computer's move is valid
        move_test = (True if game.get_valid_flips(ai_move[0]) else False)
        self.assertTrue(move_test)
        
        # Test computer behavior when it cannot make a valid move
        game = Othello(4)
        game.active_color = 'white'
        game.board.positions = [['black', 'black', 'black', 'black'],
                                ['black', 'black', 'white', 'black'],
                                ['black', 'white', 'white', 'black'],
                                ['black', 'black', 'black', 0]]
        ai_move = game.determine_ai_move()
        self.assertIsNone(ai_move)
    
    def test_get_valid_flips(self):
        # Set up a testable game
        game = Othello(8)
        game.active_color = 'white'
        game.board.record_tile(Point(2, 2), 'white')
        game.board.record_tile(Point(5, 4), 'black')
        game.board.record_tile(Point(6, 5), 'black')
        game.board.record_tile(Point(7, 5), 'white')
        game.board.record_tile(Point(6, 6), 'white')
        game.board.record_tile(Point(5, 6), 'black')
        game.board.record_tile(Point(5, 7), 'black')
        game.board.record_tile(Point(4, 6), 'black')
        
        # Test good input (a move that results in a variety of flips or lack
        # thereof in each direction)
        test_move = game.get_valid_flips(Point(5, 5))
        expected_outcome = [Point(6, 5), Point(4, 4), Point(3, 3)]
        self.assertEqual(test_move, expected_outcome)

        # Test bad inputs:
        # 1. Move outside the board
        # 2. Move that targets an occupied square
        # 3. Argument is None instead of a point
        outside_board_test = game.get_valid_flips(Point(100, 100))
        occupied_board_test = game.get_valid_flips(Point(2, 2))
        none_point_test = game.get_valid_flips(None)
        self.assertEqual(outside_board_test, [])
        self.assertEqual(occupied_board_test, [])
        self.assertEqual(none_point_test, [])

    def test_has_valid_move(self):
        # Test a board where a valid move exists for black
        game = Othello(4)
        game.board.positions = [['black', 'black', 'black', 'black'],
                                ['black', 'black', 'white', 'black'],
                                ['black', 'white', 'black', 'white'],
                                ['black', 'black', 'black', 0]]
        self.assertTrue(game.has_valid_move())

        # Test a board with no valid moves for black
        game = Othello(4)
        game.board.positions = [['black', 'black', 'black', 'black'],
                                ['black', 'black', 'white', 'black'],
                                ['black', 'white', 'black', 'black'],
                                ['black', 'black', 'black', 0]]
        self.assertFalse(game.has_valid_move())

        # Test a board where a valid move exists for white
        game = Othello(4)
        game.active_color = 'white'
        game.board.positions = [['white', 'black', 'black', 'black'],
                                ['black', 'black', 'white', 'black'],
                                ['black', 'white', 'black', 'black'],
                                ['black', 'black', 'black', 0]]
        self.assertTrue(game.has_valid_move())

        # Test a board with no valid moves for white
        game = Othello(4)
        game.active_color = 'white'
        game.board.positions = [['black', 'black', 'black', 'black'],
                                ['black', 'black', 'white', 'black'],
                                ['black', 'white', 'black', 'black'],
                                ['black', 'black', 'black', 0]]
        self.assertFalse(game.has_valid_move())

    @patch('builtins.print')
    def test_report_winner(self, mocked_print):
        game = Othello(4)
        game.report_winner()
        game = Othello(4)
        game.board.black_tiles = 3
        game.report_winner()
        game = Othello(4)
        game.board.white_tiles = 4
        game.report_winner()

        # Check that report_winner prints correct text to the terminal
        self.assertEqual(mocked_print.mock_calls, \
          [call("Game over! Score is 2 for black and 2 for white."),
           call("It's a tie!"),
           call("Game over! Score is 3 for black and 2 for white."),
           call("Black wins!"),
           call("Game over! Score is 2 for black and 4 for white."),
           call("White wins!")])

    def test_get_high_score(self):
        # Test with input from a dummy score file
        game = Othello(8)
        try:
            infile = open(DUMMY_SCORES, 'r')
            all_scores = infile.readlines()
            infile.close()
        except OSError:
            print("Could not find or open", DUMMY_SCORES)
        high_score = game.get_high_score(all_scores)
        self.assertEqual(high_score, 50)

        # Test behavior for when input list is length zero
        game = Othello(8)
        high_score = game.get_high_score([])
        self.assertIsNone(high_score)

class boardTest(unittest.TestCase):
    def test_init(self):
        board = Board(4)
        self.assertEqual(board.size, 4)
        self.assertEqual(board.center, Point(1, 1))
        self.assertEqual(board.positions, INITIALIZED_4X4_BOARD)
        self.assertEqual(board.black_tiles, 2)
        self.assertEqual(board.white_tiles, 2)

        board = Board(8)
        self.assertEqual(board.size, 8)
        self.assertEqual(board.center, Point(3, 3))
        self.assertEqual(board.positions, INITIALIZED_8X8_BOARD)
        self.assertEqual(board.black_tiles, 2)
        self.assertEqual(board.white_tiles, 2)

    def test_eq(self):
        # Set up test boards with different attributes
        board_one = Board(4)
        board_two = Board(4)
        board_three = Board(8)
        board_four = Board(4)
        board_four.center = Point(3, 3)
        board_five = Board(4)
        board_five.positions = INITIALIZED_8X8_BOARD
        board_six = Board(4)
        board_six.black_tiles = 10
        board_seven = Board(4)
        board_seven.white_tiles = 10

        # Test for equality or lack thereof
        self.assertEqual(board_one, board_two)
        self.assertNotEqual(board_one, board_three)
        self.assertNotEqual(board_one, board_four)
        self.assertNotEqual(board_one, board_five)
        self.assertNotEqual(board_one, board_six)
        self.assertNotEqual(board_one, board_seven)

    def test_find_center(self):
        board = Board(4)
        center = board.find_center()
        self.assertEqual(center, Point(1, 1))

        board = Board(8)
        center = board.find_center()
        self.assertEqual(center, Point(3, 3))

        board = Board(12)
        center = board.find_center()
        self.assertEqual(center, Point(5, 5))
    
    def test_initialize_positions(self):
        board = Board(4)
        expected_output = INITIALIZED_4X4_BOARD
        self.assertEqual(board.initialize_positions(), expected_output)

        board = Board(8)
        expected_output = INITIALIZED_8X8_BOARD
        self.assertEqual(board.initialize_positions(), expected_output)

        board = Board(0)
        expected_output = []
        self.assertEqual(board.initialize_positions(), expected_output)

    def test_get_initial_tiles_to_draw(self):
        expected_outcome = [(Point(-4, -25), 'black'),
                            (Point(46, -25), 'white'),
                            (Point(46, 25), 'black'),
                            (Point(-4, 25), 'white')]
        board = Board(4)
        tiles = board.get_initial_tiles_to_draw()
        self.assertEqual(tiles, expected_outcome)

        board = Board(8)
        tiles = board.get_initial_tiles_to_draw()
        self.assertEqual(tiles, expected_outcome)

    def test_convert_turtle_to_square(self):
        board = Board(4)
        # Testing function normally
        # Good inputs
        square_one = board.convert_turtle_to_square(Point(-27, -74))
        square_two = board.convert_turtle_to_square(Point(0, 0))
        # Bad inputs - point is outside of the board in various ways
        square_three = board.convert_turtle_to_square(Point(-101, 50))
        square_four = board.convert_turtle_to_square(Point(101, 50))
        square_five = board.convert_turtle_to_square(Point(50, 101))
        square_six = board.convert_turtle_to_square(Point(50, -101))
        self.assertEqual(square_one, Point(1, 0))
        self.assertEqual(square_two, Point(2, 2))
        self.assertIsNone(square_three)
        self.assertIsNone(square_four)
        self.assertIsNone(square_five)
        self.assertIsNone(square_six)
        
        # Testing reverse version of function
        # Good inputs
        turtle_one = board.convert_turtle_to_square(Point(0, 0), 'r')
        turtle_two = board.convert_turtle_to_square(Point(3, 1), 'r')
        # Bad inputs - point is outside of the board in various ways
        turtle_three = board.convert_turtle_to_square(Point(4, 0), 'r')
        turtle_four = board.convert_turtle_to_square(Point(-1, 0), 'r')
        turtle_five = board.convert_turtle_to_square(Point(0, 4), 'r')
        turtle_six = board.convert_turtle_to_square(Point(0, -1), 'r')
        self.assertEqual(turtle_one, Point(-54, -75))
        self.assertEqual(turtle_two, Point(96, -25))
        self.assertIsNone(turtle_three)
        self.assertIsNone(turtle_four)
        self.assertIsNone(turtle_five)
        self.assertIsNone(turtle_six)

        board = Board(8)
        # Testing function normally
        # Good inputs
        square_one = board.convert_turtle_to_square(Point(199, -101))
        square_two = board.convert_turtle_to_square(Point(-199, 158))
        # Bad inputs - point is outside of the board in various ways
        square_three = board.convert_turtle_to_square(Point(201, 0))
        square_four = board.convert_turtle_to_square(Point(-201, 0))
        square_five = board.convert_turtle_to_square(Point(0, 201))
        square_six = board.convert_turtle_to_square(Point(0, -201))
        self.assertEqual(square_one, Point(7, 1))
        self.assertEqual(square_two, Point(0, 7))
        self.assertIsNone(square_three)
        self.assertIsNone(square_four)
        self.assertIsNone(square_five)
        self.assertIsNone(square_six)
        
        # Testing reverse version of function
        # Good inputs
        turtle_one = board.convert_turtle_to_square(Point(7, 5), 'r')
        turtle_two = board.convert_turtle_to_square(Point(5, 7), 'r')
        # Bad inputs - point is outside of the board in various ways
        turtle_three = board.convert_turtle_to_square(Point(8, 1), 'r')
        turtle_four = board.convert_turtle_to_square(Point(-1, 0), 'r')
        turtle_five = board.convert_turtle_to_square(Point(6, 8), 'r')
        turtle_six = board.convert_turtle_to_square(Point(6, -1), 'r')
        self.assertEqual(turtle_one, Point(196, 75))
        self.assertEqual(turtle_two, Point(96, 175))
        self.assertIsNone(turtle_three)
        self.assertIsNone(turtle_four)
        self.assertIsNone(turtle_five)
        self.assertIsNone(turtle_six)
        
    def test_record_tile(self):
        board = Board(4)
        # Inputs that result in a tile placement
        board.record_tile(Point(1, 3), 'white')
        board.record_tile(Point(0, 2), 'black')
        board.record_tile(Point(1, 2), 'black')
        # Inputs that don't result in a tile placement
        board.record_tile(Point(4, 3), 'white')
        board.record_tile(Point(1, 1), 'black')
        board.record_tile(Point(-1, 3), 'black')
        board.record_tile(Point(0, 5), 'black')
        board.record_tile(Point(0, -1), 'white')
        board.record_tile(Point(1, 2), 'red')
        expected_output = [[0, 0, 'black', 0],
                           [0, 'black', 'black', 'white'],
                           [0, 'white', 'black', 0],
                           [0, 0, 0, 0]]
        self.assertEqual(board.positions, expected_output)
        self.assertEqual(board.black_tiles, 4)
        self.assertEqual(board.white_tiles, 2)

        board = Board(8)
        # Inputs that result in a tile placement
        board.record_tile(Point(6, 2), 'white')
        board.record_tile(Point(0, 7), 'black')
        board.record_tile(Point(3, 4), 'black')
        # Inputs that don't result in a tile placement
        board.record_tile(Point(3, 3), 'black')
        board.record_tile(Point(8, 3), 'white')
        board.record_tile(Point(-1, 3), 'black')
        board.record_tile(Point(0, 10), 'black')
        board.record_tile(Point(0, -1), 'white')
        board.record_tile(Point(2, 4), 'green')
        expected_output = [[0, 0, 0, 0, 0, 0, 0, 'black'],
                           [0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 'black', 'black', 0, 0, 0],
                           [0, 0, 0, 'white', 'black', 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 'white', 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0]]
        self.assertEqual(board.positions, expected_output)
        self.assertEqual(board.black_tiles, 4)
        self.assertEqual(board.white_tiles, 2)
        
    def test_is_empty_square(self):
        # Set up a board with various tiles
        board = Board(4)
        board.record_tile(Point(3, 1), 'black')
        board.record_tile(Point(2, 2), 'white')
        board.record_tile(Point(2, 0), 'black')

        # Test for empty and non-empty sauares
        self.assertTrue(board.is_empty_square(Point(0, 2)))
        self.assertTrue(board.is_empty_square(Point(2, 3)))
        self.assertTrue(board.is_empty_square(Point(1, 3)))
        self.assertFalse(board.is_empty_square(Point(3, 1)))
        self.assertFalse(board.is_empty_square(Point(2, 2)))
        self.assertFalse(board.is_empty_square(Point(2, 0)))
        
        # Test for postions outside of board
        self.assertFalse(board.is_empty_square(Point(5, 0)))
        self.assertFalse(board.is_empty_square(Point(-1, 0)))
        self.assertFalse(board.is_empty_square(Point(0, 4)))
        self.assertFalse(board.is_empty_square(Point(0, -1))) 

    def test_is_a_square(self):
        board = Board(4)
        # Test for inside and outside of board range
        self.assertTrue(board.is_a_square(Point(0, 0)))
        self.assertTrue(board.is_a_square(Point(3, 3)))
        self.assertTrue(board.is_a_square(Point(1, 2)))
        self.assertFalse(board.is_a_square(Point(5, 0)))
        self.assertFalse(board.is_a_square(Point(-1, 0)))
        self.assertFalse(board.is_a_square(Point(0, 4)))
        self.assertFalse(board.is_a_square(Point(0, -1)))

        board = Board(8)
        # Test for inside and outside of board range
        self.assertTrue(board.is_a_square(Point(0, 0)))
        self.assertTrue(board.is_a_square(Point(7, 7)))
        self.assertTrue(board.is_a_square(Point(1, 2)))
        self.assertFalse(board.is_a_square(Point(8, 0)))
        self.assertFalse(board.is_a_square(Point(-1, 0)))
        self.assertFalse(board.is_a_square(Point(0, 8)))
        self.assertFalse(board.is_a_square(Point(0, -1)))

    def test_is_full(self):
        # Test for boards of size 4 and 8 that are completely full
        board = Board(4)
        board.white_tiles = 9
        board.black_tiles = 7
        self.assertTrue(board.is_full())
        board = Board(8)
        board.white_tiles = 40
        board.black_tiles = 24
        self.assertTrue(board.is_full())

        # Test for boards of size 4 and 8 that have an open space
        board = Board(4)
        board.white_tiles = 8
        board.black_tiles = 7
        self.assertFalse(board.is_full())
        board = Board(8)
        board.white_tiles = 39
        board.black_tiles = 24
        self.assertFalse(board.is_full())

class pointTest(unittest.TestCase):
    def test_init(self):
        point = Point(0, 3.5)
        self.assertEqual(point.x, 0)
        self.assertEqual(point.y, 3.5)

        point = Point(-6.2, -3)
        self.assertEqual(point.x, -6.2)
        self.assertEqual(point.y, -3)

    def test_str(self):
        point = Point(3, -6)
        expected_output = '(3, -6)'
        self.assertEqual(point.__str__(), expected_output)

        point = Point(0, 2.63)
        expected_output = '(0, 2.63)'
        self.assertEqual(point.__str__(), expected_output)

    def test_eq(self):
        point_one = Point(2.1, -6.5)
        point_two = Point(2.1, -6.5)
        point_three = Point(2.1, 5)
        point_four = Point(6, -6.5)
        point_five = Point(8, 8)
        self.assertEqual(point_one, point_two)
        self.assertNotEqual(point_one, point_three)
        self.assertNotEqual(point_one, point_four)
        self.assertNotEqual(point_one, point_five)


class flipFinderTest(unittest.TestCase):
    def test_init(self):
        board = Board(4)
        finder = flipFinder(board.size, board.positions, 'white')
        self.assertEqual(finder.size, board.size)
        self.assertEqual(finder.positions, board.positions)
        self.assertEqual(finder.color, 'white')

        board = Board(8)
        finder = flipFinder(board.size, board.positions, 'black')
        self.assertEqual(finder.size, board.size)
        self.assertEqual(finder.positions, board.positions)
        self.assertEqual(finder.color, 'black')

    def test_find_flips_all(self):
        # Set up a testable board
        board = Board(8)
        board.record_tile(Point(2, 2), 'white')
        board.record_tile(Point(5, 4), 'black')
        board.record_tile(Point(6, 5), 'black')
        board.record_tile(Point(7, 5), 'white')
        board.record_tile(Point(6, 6), 'white')
        board.record_tile(Point(5, 6), 'black')
        board.record_tile(Point(5, 7), 'black')
        board.record_tile(Point(4, 6), 'black')
        flips_b = flipFinder(board.size, board.positions, 'white')
        
        # Test good input (a move that results in a variety of flips or lack
        # thereof in each direction)
        test_move = flips_b.find_flips_all(Point(5, 5))
        expected_outcome = [Point(6, 5), Point(4, 4), Point(3, 3)]
        self.assertEqual(test_move, expected_outcome)
        
        # Test behavior for a move outside of the board
        outside_board_test = flips_b.find_flips_all(Point(100, 100))
        self.assertEqual(outside_board_test, [])

    def test_find_flips_north(self):
        # Set up move validators for black and white
        board = Board(8)
        board.record_tile(Point(4, 2), 'white')
        board.record_tile(Point(4, 1), 'white')
        board.record_tile(Point(3, 6), 'black')
        board.record_tile(Point(5, 7), 'white')
        flips_w = flipFinder(board.size, board.positions, 'white')
        flips_b = flipFinder(board.size, board.positions, 'black')

        # Test good input (1+ tiles flipped)
        one_flip = flips_w.find_flips_north(Point(3, 2))
        three_flips = flips_b.find_flips_north(Point(4, 0))
        self.assertEqual(one_flip, [Point(3, 3)])
        self.assertEqual(three_flips, [Point(4, 1), Point(4, 2), Point(4, 3)])
        
        # Test bad input (moves with no valid flips):
        #   1. Hits friendly tile without finding opposing tiles, or
        #   2. Hits edge of board or empty square without finding friendly tile
        #   3. Move is outside the board
        friendly_tile = flips_b.find_flips_north(Point(3, 2))
        empty_space = flips_w.find_flips_north(Point(3, 5))
        edge = flips_b.find_flips_north(Point(5, 6))
        outside = flips_w.find_flips_north(Point(100, 100))
        self.assertEqual(friendly_tile, [])
        self.assertEqual(empty_space, [])
        self.assertEqual(edge, [])
        self.assertEqual(outside, [])

    def test_find_flips_south(self):
        # Set up move validators for black and white
        board = Board(8)
        board.record_tile(Point(4, 5), 'black')
        board.record_tile(Point(4, 6), 'black')
        board.record_tile(Point(5, 0), 'black')
        board.record_tile(Point(3, 1), 'black')
        flips_w = flipFinder(board.size, board.positions, 'white')
        flips_b = flipFinder(board.size, board.positions, 'black')

        # Test good input (1+ tiles flipped)
        one_flip = flips_b.find_flips_south(Point(3, 5))
        three_flips = flips_w.find_flips_south(Point(4, 7))
        self.assertEqual(one_flip, [Point(3, 4)])
        self.assertEqual(three_flips, [Point(4, 6), Point(4, 5), Point(4, 4)])

        # Test bad input (moves with no valid flips):
        #   1. Hits friendly tile without finding opposing tiles, or
        #   2. Hits edge of board or empty square without finding friendly tile
        #   3. Move is outside the board
        friendly_tile = flips_w.find_flips_south(Point(3, 5))
        empty_space = flips_b.find_flips_south(Point(3, 2))
        edge = flips_w.find_flips_south(Point(5, 1))
        outside = flips_w.find_flips_south(Point(100, 100))
        self.assertEqual(friendly_tile, [])
        self.assertEqual(empty_space, [])
        self.assertEqual(edge, [])
        self.assertEqual(outside, [])

    def test_find_flips_east(self):
        # Set up move validators for black and white
        board = Board(8)
        board.record_tile(Point(1, 3), 'black')
        board.record_tile(Point(2, 3), 'black')
        board.record_tile(Point(5, 6), 'white')
        board.record_tile(Point(7, 0), 'black')
        flips_w = flipFinder(board.size, board.positions, 'white')
        flips_b = flipFinder(board.size, board.positions, 'black')

        # Test good input (1+ tiles flipped)
        one_flip = flips_b.find_flips_east(Point(2, 4))
        three_flips = flips_w.find_flips_east(Point(0, 3))
        self.assertEqual(one_flip, [Point(3, 4)])
        self.assertEqual(three_flips, [Point(1, 3), Point(2, 3), Point(3, 3)])

        # Test bad input (moves with no valid flips):
        #   1. Hits friendly tile without finding opposing tiles, or
        #   2. Hits edge of board or empty square without finding friendly tile
        #   3. Move is outside the board
        friendly_tile = flips_w.find_flips_east(Point(2, 4))
        empty_space = flips_b.find_flips_east(Point(5, 5))
        edge = flips_w.find_flips_east(Point(6, 0))
        outside = flips_w.find_flips_south(Point(100, 100))
        self.assertEqual(friendly_tile, [])
        self.assertEqual(empty_space, [])
        self.assertEqual(edge, [])
        self.assertEqual(outside, [])

    def test_find_flips_west(self):
        # Set up move validators for black and white
        board = Board(8)
        board.record_tile(Point(5, 4), 'black')
        board.record_tile(Point(6, 4), 'black')
        board.record_tile(Point(2, 5), 'white')
        board.record_tile(Point(0, 5), 'black')
        flips_w = flipFinder(board.size, board.positions, 'white')
        flips_b = flipFinder(board.size, board.positions, 'black')

        # Test good input (1+ tiles flipped)
        one_flip = flips_b.find_flips_west(Point(5, 3))
        three_flips = flips_w.find_flips_west(Point(7, 4))
        self.assertEqual(one_flip, [Point(4, 3)])
        self.assertEqual(three_flips, [Point(6, 4), Point(5, 4), Point(4, 4)])

        # Test bad input (moves with no valid flips):
        #   1. Hits friendly tile without finding opposing tiles, or
        #   2. Hits edge of board or empty square without finding friendly tile
        #   3. Move is outside the board
        friendly_tile = flips_w.find_flips_west(Point(5, 3))
        empty_space = flips_b.find_flips_west(Point(3, 5))
        edge = flips_w.find_flips_west(Point(1, 5))
        outside = flips_w.find_flips_west(Point(100, 100))
        self.assertEqual(friendly_tile, [])
        self.assertEqual(empty_space, [])
        self.assertEqual(edge, [])
        self.assertEqual(outside, [])

    def test_find_flips_ne(self):
        # Set up move validators for black and white
        board = Board(8)
        board.record_tile(Point(4, 5), 'black')
        board.record_tile(Point(2, 2), 'black')
        board.record_tile(Point(5, 5), 'white')
        board.record_tile(Point(4, 7), 'black')
        board.record_tile(Point(7, 2), 'white')
        flips_w = flipFinder(board.size, board.positions, 'white')
        flips_b = flipFinder(board.size, board.positions, 'black')

        # Test good input (1+ tiles flipped)
        one_flip = flips_b.find_flips_ne(Point(2, 3))
        three_flips = flips_w.find_flips_ne(Point(1, 1))
        self.assertEqual(one_flip, [Point(3, 4)])
        self.assertEqual(three_flips, [Point(2, 2), Point(3, 3), Point(4, 4)])

        # Test bad input (moves with no valid flips):
        #   1. Hits friendly tile without finding opposing tiles, or
        #   2. Hits edge of board or empty square without finding friendly tile
        #   3. Move is outside the board
        friendly_tile = flips_w.find_flips_ne(Point(3, 2))
        empty_space = flips_b.find_flips_ne(Point(3, 2))
        edge_north = flips_w.find_flips_ne(Point(3, 6))
        edge_east = flips_b.find_flips_ne(Point(6, 1))
        outside = flips_w.find_flips_ne(Point(-100, -100))
        self.assertEqual(friendly_tile, [])
        self.assertEqual(empty_space, [])
        self.assertEqual(edge_north, [])
        self.assertEqual(edge_east, [])
        self.assertEqual(outside, [])

    def test_find_flips_sw(self):
        # Set up move validators for black and white
        board = Board(8)
        board.record_tile(Point(3, 2), 'black')
        board.record_tile(Point(5, 5), 'black')
        board.record_tile(Point(2, 2), 'white')
        board.record_tile(Point(2, 0), 'black')
        board.record_tile(Point(0, 5), 'white')
        flips_w = flipFinder(board.size, board.positions, 'white')
        flips_b = flipFinder(board.size, board.positions, 'black')

        # Test good input (1+ tiles flipped)
        one_flip = flips_b.find_flips_sw(Point(5, 4))
        three_flips = flips_w.find_flips_sw(Point(6, 6))
        self.assertEqual(one_flip, [Point(4, 3)])
        self.assertEqual(three_flips, [Point(5, 5), Point(4, 4), Point(3, 3)])

        # Test bad input (moves with no valid flips:
        #   1. Hits friendly tile without finding opposing tiles, or
        #   2. Hits edge of board or empty square without finding friendly tile
        #   3. Move is outside the board
        friendly_tile = flips_w.find_flips_sw(Point(5, 4))
        empty_space = flips_b.find_flips_sw(Point(5, 5))
        edge_south = flips_w.find_flips_sw(Point(3, 1))
        edge_west = flips_b.find_flips_sw(Point(1, 6))
        outside = flips_w.find_flips_sw(Point(100, 100))
        self.assertEqual(friendly_tile, [])
        self.assertEqual(empty_space, [])
        self.assertEqual(edge_south, [])
        self.assertEqual(edge_west, [])
        self.assertEqual(outside, [])

    def test_find_flips_nw(self):
        # Set up move validators for black and white
        board = Board(8)
        board.record_tile(Point(3, 5), 'white')
        board.record_tile(Point(2, 5), 'white')
        board.record_tile(Point(1, 6), 'black')
        board.record_tile(Point(2, 7), 'white')
        board.record_tile(Point(0, 2), 'white')
        flips_w = flipFinder(board.size, board.positions, 'white')
        flips_b = flipFinder(board.size, board.positions, 'black')

        # Test good input (1+ tiles flipped)
        one_flip = flips_w.find_flips_nw(Point(5, 3))
        three_flips = flips_b.find_flips_nw(Point(5, 2))
        self.assertEqual(one_flip, [Point(4, 4)])
        self.assertEqual(three_flips, [Point(4, 3), Point(3, 4), Point(2, 5)])

        # Test bad input (moves with no valid flips:
        #   1. Hits friendly tile without finding opposing tiles, or
        #   2. Hits edge of board or empty square without finding friendly tile
        #   3. Move is outside the board
        friendly_tile = flips_w.find_flips_nw(Point(5, 2))
        empty_space = flips_w.find_flips_nw(Point(4, 2))
        edge_north = flips_b.find_flips_nw(Point(3, 6))
        edge_west = flips_b.find_flips_nw(Point(1, 1))
        outside = flips_w.find_flips_nw(Point(100, -100))
        self.assertEqual(friendly_tile, [])
        self.assertEqual(empty_space, [])
        self.assertEqual(edge_north, [])
        self.assertEqual(edge_west, [])
        self.assertEqual(outside, [])

    def test_find_flips_se(self):
        # Set up move validators for black and white
        board = Board(8)
        board.record_tile(Point(5, 3), 'white')
        board.record_tile(Point(5, 2), 'white')
        board.record_tile(Point(6, 1), 'black')
        board.record_tile(Point(6, 0), 'white')
        board.record_tile(Point(7, 5), 'white')
        flips_w = flipFinder(board.size, board.positions, 'white')
        flips_b = flipFinder(board.size, board.positions, 'black')

        # Test good input (1+ tiles flipped)
        one_flip = flips_w.find_flips_se(Point(3, 5))
        three_flips = flips_b.find_flips_se(Point(2, 5))
        self.assertEqual(one_flip, [Point(4, 4)])
        self.assertEqual(three_flips, [Point(3, 4), Point(4, 3), Point(5, 2)])

        # Test bad input (moves with no valid flips:
        #   1. Hits friendly tile without finding opposing tiles, or
        #   2. Hits edge of board or empty square without finding friendly tile
        #   3. Move is outside the board
        friendly_tile = flips_b.find_flips_se(Point(3, 5))
        empty_space = flips_w.find_flips_se(Point(2, 4))
        edge_south = flips_b.find_flips_se(Point(5, 1))
        edge_east = flips_b.find_flips_se(Point(6, 6))
        outside = flips_w.find_flips_se(Point(-100, 100))
        self.assertEqual(friendly_tile, [])
        self.assertEqual(empty_space, [])
        self.assertEqual(edge_south, [])
        self.assertEqual(edge_east, [])
        self.assertEqual(outside, [])


class scoreTest(unittest.TestCase):
    def test_write_scores(self):
        # Use function to write a copy of a dummy file, then compare for
        # equality
        dummy_scores = score.read_scores(DUMMY_SCORES)
        score.write_scores(dummy_scores, 'test_copy.txt')
        copy_scores = score.read_scores('test_copy.txt')
        self.assertEqual(dummy_scores, copy_scores)

    def test_append_score(self):
        # Create a copy of a dummy file and append to it using the function
        dummy_scores = score.read_scores(DUMMY_SCORES)
        score.write_scores(dummy_scores, 'test_copy.txt')
        score.append_score('Test score 15\n', 'test_copy.txt')
        # Then check the result
        appended_scores = score.read_scores('test_copy.txt')
        dummy_scores.append('Test score 15\n')
        self.assertEqual (appended_scores, dummy_scores)

    def test_read_scores(self):
        # Open up a dummy score file with and without the function, then
        # compare for equality
        try:
            infile = open(DUMMY_SCORES, 'r')
            expected_scores = infile.readlines()
            infile.close()
        except OSError:
            print("Could not find or open", DUMMY_SCORES)
        test_scores = score.read_scores(DUMMY_SCORES)
        self.assertEqual(test_scores, expected_scores)

        # Test for behavior when file does not exist
        test_scores = score.read_scores('no_file.txt')
        self.assertIsNone(test_scores)

def main():
    unittest.main(verbosity = 3)

main()
