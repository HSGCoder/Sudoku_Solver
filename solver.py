"""
This file provides functions for solving a sudoku
Author: Jonathan Vontobel (15-604-853), Vasily Taran (20-624-987) and Péter Liszkai (20-624-730)
"""


def find_next_cell_to_fill(sudoku):
    """
    This function finds the first value which is empty (=0)
    """
    for x in range(9):
        for y in range(9):
            if sudoku[x][y] == 0:
                return x, y
    #-1 indicates nothing found            
    return -1, -1


def is_valid(sudoku, i, j, k):
    """
    This function checks for a given sudou if its correct

    i,j: current coordinate
    k: number to fill in
    """
    #check if not same number in row
    legal_row = all([k != sudoku[i][x] for x in range(9)])
    if legal_row:
        #check if not same number in col
        legal_col = all([k != sudoku[x][j] for x in range(9)])
        if legal_col:
            #if col and row valid, check if not same number in 3x3 box
            x = 3 * (i // 3)
            y = 3 * (j // 3)
            for x_ in range(x, x + 3):
                for y_ in range(y, y + 3):
                    if sudoku[x_][y_] == k:
                        return False
            return True
    return False


def solve_sudoku(sudoku, i=0, j=0):
    """
    This function solves a given sudoku recursively

    i,j is thecurrent coordinate
    """
    i, j = find_next_cell_to_fill(sudoku)
    if i == -1:
        return True

    for k in range(1, 10):
        if is_valid(sudoku, i, j, k):
            sudoku[i][j] = k
            if solve_sudoku(sudoku, i, j):
                return True
            sudoku[i][j] = 0
    return False


def print_sudoku(sudoku):
    """
    This function prints out a given sudoku to the console/terminal
    """
    print("\n\n\n\n\n")
    for i in range(len(sudoku)):
        line = ""
        if i == 3 or i == 6:
            print("---------------------")
        for j in range(len(sudoku[i])):
            if j == 3 or j == 6:
                line += "| "
            line += str(sudoku[i][j]) + " "
        print(line)
