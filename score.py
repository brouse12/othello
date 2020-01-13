'''
Brian Rouse
CS5001
Homework 7 - score.py
December 2, 2018

Module for creating/updating high score file for games.
'''

SCORE_FILE = 'scores.txt'

def write_scores(scores, file_name=SCORE_FILE):
    '''parameters: scores (a list of strings) and file name (a string)
       returns: nothing
       does: writes each element of scores list as a separate line.  Overwrites
             any existing file with file name or creates a new file as
             applicable.  If OSError, does nothing.
    '''
    try:
        outfile = open(file_name, 'w')
        outfile.writelines(scores)
        outfile.close()
    except OSError:
        print("Could not write ", file_name, ".", sep='')

def append_score(score, file_name=SCORE_FILE):
    '''parameters: score (a string) and file name (a string)
       returns: nothing
       does: adds the score string to the end of file with file name. Creates
             a new file if one does not already exist.  If OSError, does
             nothing.
    '''
    try:
        outfile = open(file_name, 'a')
        outfile.write(score)
        outfile.close()
    except OSError:
        print("Could not write ", file_name, ".", sep='')

def read_scores(file_name=SCORE_FILE):
    '''parameters: file name (a string)
       returns: scores from score file (a list of strings).  Returns nothing if
                cannot open file.
       does: returns each line in score file as an element in a list
    '''
    try:
        infile = open(file_name, 'r')
        all_scores = infile.readlines()
        infile.close()
    except OSError:
        return
    return all_scores
        


