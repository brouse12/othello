'''
Brian Rouse
CS5001
Homework 7 - othello_driver.py
December 2, 2018

Driver for playing a game of Othello.  Calls Othello module.
'''

BOARD_SIZE = 8

from othello import Othello

def main():
    game = Othello(BOARD_SIZE)
    game.start()
    
main()
