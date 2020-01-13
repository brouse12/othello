'''
Brian Rouse
CS5001
Homework 7 - othello_viz.py
December 2, 2018

Module for drawing a game of Othello.
Note: some functions take Point objects as arguments.  See othello.py module.
'''

TILE_RADIUS = 20

import turtle

def draw_tile(point, color):
    '''parameters: x,y coordinates for turtle to draw an Othello tile (a point);
                   and tile color (a string, typically 'white' or 'black')
       returns: nothing
    '''
    # Setup turtle to draw tile.
    turtle.hideturtle()
    turtle.speed(0)
    turtle.color('black', color)
    turtle.setheading(90)
        
    # Go to point and draw the tile.
    turtle.penup()
    turtle.goto(point.x, point.y)
    turtle.pendown()
    turtle.begin_fill()
    turtle.circle(TILE_RADIUS)
    turtle.end_fill()

def draw_board(n, tile_positions, square_size):
    '''parameters: n,  an int for # of squares;
                   tile_positions, a nested list with positions and colors
                   for initial tiles (format: [[point, color]...]);
                   square_size - an int for length/width of each square
       returns: nothing
       does: draws an nxn Othello board with a green background and 4 starting
             tiles
    '''
    turtle.setup(n * square_size + square_size, n * square_size + square_size)
    turtle.screensize(n * square_size, n * square_size)
    turtle.bgcolor('white')

    # Create the turtle to draw the board
    othello = turtle.Turtle()
    othello.penup()
    othello.speed(0)
    othello.hideturtle()

    # Line color is black, fill color is green
    othello.color("black", "forest green")
    
    # Move the turtle to the upper left corner
    corner = -n * square_size / 2
    othello.setposition(corner, corner)
  
    # Draw the green background
    othello.begin_fill()
    for i in range(4):
        othello.pendown()
        othello.forward(square_size * n)
        othello.left(90)
    othello.end_fill()

    # Draw the horizontal lines
    for i in range(n + 1):
        othello.setposition(corner, square_size * i + corner)
        draw_lines(othello, n, square_size)

    # Draw the vertical lines
    othello.left(90)
    for i in range(n + 1):
        othello.setposition(square_size * i + corner, corner)
        draw_lines(othello, n, square_size)

    draw_initial_game_tiles(tile_positions)

def draw_lines(turt, n, square_size):
    '''parameters: turt, a turtle object;
                   n, the number of squares, an int;
                   square_size, an int
       returns: nothing
       does: draws a line, called by draw_board function
    '''
    turt.pendown()
    turt.forward(square_size * n)
    turt.penup()

def draw_initial_game_tiles(tile_positions):
    '''parameters: tile_positions, a nested list with positions and colors
                   for initial game tiles (format: [[point, color]...])
       returns: nothing
    '''
    for tile in tile_positions:
        draw_tile(tile[0], tile[1])

