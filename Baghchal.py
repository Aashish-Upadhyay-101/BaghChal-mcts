from copy import deepcopy
from mcts import *


class Board():
    def __init__(self, board=None):
        self.player_1 = "G"
        self.player_2 = "T" 
        self.empty_point = "."
        self.size = 5

        self.tiger_positions = []
        self.goat_counts = 20
        self.goat_placed = 0 
        self.goat_eaten = 0

        self.position = {} 
        self.invalid_moves = {frozenset(move) for move in [
            ((0, 1), (1, 0)), ((0, 1), (1, 2)), ((0, 3), (1, 2)), ((0, 3), (1, 4)),
            ((2, 1), (1, 0)), ((2, 1), (1, 2)), ((2, 3), (1, 2)), ((2, 3), (1, 4)),
            ((2, 1), (3, 0)), ((2, 1), (3, 2)), ((2, 3), (3, 2)), ((2, 3), (3, 4)),
            ((4, 1), (3, 0)), ((4, 1), (3, 2)), ((4, 3), (3, 2)), ((4, 3), (3, 4)),
        ]}

        self.position_history = {}
        self.moves_without_progress = 0 

        self.init_board()
        
        if board is not None: 
            self.__dict__ = deepcopy(board.__dict__)


    def init_board(self):
        for row in range(self.size):
            for col in range(self.size):
                self.position[row, col] = self.empty_point
        
        # set tiger in four corners
        tiger_positions = [(0, 0), (0, self.size - 1), (self.size - 1, 0), (self.size - 1, self.size - 1)]
        for position in tiger_positions:
            self.position[position] = self.player_2
            self.tiger_positions.append(position)

    
    def is_draw(self): 
        if self.moves_without_progress >= 50:
            return True 
        
        repeat_states = 0
        for value in self.position_history.values():
            if value >= 3:
                repeat_states += 1 
        
        if repeat_states >= 2: 
            return True
    
        return False
            

    def is_valid_move(self, start, end):
        if not (0 <= end[0] < self.size and 0 <= end[1] < self.size): 
            return False 

        if self.position[end] != self.empty_point:
            return False

        if frozenset((start, end)) in self.invalid_moves:
            return False
        
        row_diff = abs(start[0] - end[0])
        col_diff = abs(start[1] - end[1])

        if (row_diff, col_diff) in [(1, 0), (0, 1), (1, 1)]:
            return True
        elif self.player_1 == "T" and (row_diff, col_diff) in [(2, 0), (0, 2), (2,2)]:
            mid_row = (start[0] + end[0]) // 2 
            mid_col = (start[1] + end[1]) // 2

            if self.position[mid_row, mid_col] == self.player_2: 
                return True

        return False

    def is_goat_win(self):
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1), # horizontal and vertical moves
            (-1, -1), (1, 1), (-1, 1), (1, -1),  # Diagonals
            (-2, 0), (2, 0), (0, -2), (0, 2),  # horizontal and vertical jumps
            (-2, -2), (2, 2), (-2, 2), (2, -2),  # Diagonal jumps
        ]

        # if any one tiger can move then goat hasn't won 
        for tiger_position in self.tiger_positions: 
            row, col = tiger_position
            for dr, dc in directions:
                row_end = row + dr 
                col_end = col + dc
                if self.is_valid_move(tiger_position, (row_end, col_end)):
                    return False
            # for row in range(self.size):
            #     for col in range(self.size): 
            #         if self.is_valid_move(tiger_position, (row, col)):
            #             return False 
        return True


    def is_tiger_win(self):
        return self.goat_eaten >= 5 

    
    def move_tiger(self, start, end):
        board = Board(self)
        board.position[start] = board.empty_point
        board.position[end] = board.player_1

        board.tiger_positions.remove(start)
        board.tiger_positions.append(end)

        # check if goat captured during tiger movement
        row_dff = abs(start[0] - end[0])
        col_diff = abs(start[1] - end[1])   
        if (row_dff, col_diff) in [(2, 0), (0, 2), (2, 2)]: 
            mid_row = (start[0] + end[0]) // 2 
            mid_col = (start[1] + end[1]) // 2 

            if board.position[mid_row, mid_col] == board.player_2: 
                board.position[mid_row, mid_col] = board.empty_point
                board.goat_eaten += 1
        
        board.player_1, board.player_2 = board.player_2, board.player_1
        return board

    
    def move_goat(self, start, end):
        board = Board(self)
        board.position[start] = board.empty_point
        board.position[end] = board.player_1

        board.player_1, board.player_2 = board.player_2, board.player_1
        return board


    def place_goat(self, row, col): 
        board = Board(self)
        board.position[row, col] = board.player_1 
        board.goat_placed += 1

        board.player_1, board.player_2 = board.player_2, board.player_1
        return board


    def generate_states(self):
        actions = [] 

        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1), # horizontal and vertical moves
            (-1, -1), (1, 1), (-1, 1), (1, -1),  # Diagonals
            (-2, 0), (2, 0), (0, -2), (0, 2),  # horizontal and vertical jumps
            (-2, -2), (2, 2), (-2, 2), (2, -2),  # Diagonal jumps
        ]

        # either place goat
        if self.player_1 == "G" and self.goat_placed < 20:
            for row in range(self.size):
                for col in range(self.size):
                    if self.position[row, col] == self.empty_point:
                        actions.append(self.place_goat(row, col))

        # or move goat 
        elif self.player_1 == "G" and self.goat_placed >= 20: 
            for row in range(self.size):
                for col in range(self.size):
                    if self.position[row, col] == "G":
                        for dr, dc in directions: 
                            row_end = row + dr 
                            col_end = col + dc
                            if self.is_valid_move((row, col), (row_end, col_end)):
                                actions.append(self.move_goat((row, col), (row_end, col_end)))

        # or move tiger
        elif self.player_1 == "T": 
            for tiger_position in self.tiger_positions:
                row, col = tiger_position
                for dr, dc in directions:
                    row_end = row + dr 
                    col_end = col + dc
                    if self.is_valid_move((row ,col), (row_end, col_end)):
                        actions.append(self.move_tiger((row ,col), (row_end, col_end)))

        return actions
    
    
    def game_loop(self): 
        print("Welcome to Baghchal!\n")

        print(self)

        mcts = MCTS()

        while True: 
            if self.is_tiger_win():
                print("------ Tigers win! ------")
                break
            if self.is_goat_win():
                print("------ Goats win! ------")
                break 
            if self.is_draw():
                print("------ Game draw! ------")
                break

            print("Player: {} turn to play\n".format(self.player_1))
            
            try:
                if self.player_1 == "G" and self.goat_placed < 20: 
                    # place goat
                    print("Place a goat:")
                    user_input = input("> ")
                    if user_input == "exit": break 
                    if user_input == "": continue

                    row = int(user_input.split(",")[0]) - 1 
                    col = int(user_input.split(",")[1]) - 1 
                    
                    if self.position[row, col] != self.empty_point:
                       print("This position is already occupied!")
                       print(self)
                       continue 

                    last_goat_eaten = self.goat_eaten
                    has_tiger_moves = not self.is_goat_win()

                    self = self.place_goat(row, col) 

                    if len(self.position_history) >= 2: 
                        first_key = next(iter(self.position_history))
                        self.position_history.pop(first_key)

                    hashed_state = hash(self)

                    if hashed_state in self.position_history:
                        self.position_history[hashed_state] += 1 
                    else: 
                        self.position_history[hashed_state] = 1
                    #

                    if (self.player_1 == "T" and has_tiger_moves) or (self.player_1 == "G" and last_goat_eaten == self.goat_eaten):
                        self.moves_without_progress += 1
                    else:
                        self.moves_without_progress = 0
                    #
                    

                elif self.player_1 == "G" and self.goat_placed >= 20: 
                    # move goat 
                    print("Select a goat to move:")
                    start = input("> ")
                    start = (int(start.split(",")[0]) - 1, int(start.split(",")[1]) - 1)

                    if self.position[start] != self.player_1:
                        print("This position doesn't have a goat to move!")
                        print(self)
                        continue

                    print("Place that goat:")
                    end = input("> ")
                    end = (int(end.split(",")[0]) - 1, int(end.split(",")[1]) - 1)

                    if not self.is_valid_move(start, end): 
                        print("Invalid goat move!")
                        print(self)
                        continue 
                        

                    last_goat_eaten = self.goat_eaten
                    has_tiger_moves = not self.is_goat_win()
                    
                    self = self.move_goat(start, end)

                    if len(self.position_history) >= 2: 
                        first_key = next(iter(self.position_history))
                        self.position_history.pop(first_key)

                    hashed_state = hash(self)

                    if hashed_state in self.position_history:
                        self.position_history[hashed_state] += 1 
                    else: 
                        self.position_history[hashed_state] = 1

                    #
                    if (self.player_1 == "T" and has_tiger_moves) or (self.player_1 == "G" and last_goat_eaten == self.goat_eaten):
                        self.moves_without_progress += 1
                    else:
                        self.moves_without_progress = 0
                    #

                     
                elif self.player_1 == "T": 
                    # move tiger
                    print("Tiger's turn(AI): ")

                     # AI move 
                    last_goat_eaten = self.goat_eaten
                    has_tiger_moves = not self.is_goat_win()
                
                    best_move = mcts.search(self)

                    try:
                        self = best_move.board

                        if len(self.position_history) >= 2: 
                            first_key = next(iter(self.position_history))
                            self.position_history.pop(first_key)

                        hashed_state = hash(self)

                        if hashed_state in self.position_history:
                            self.position_history[hashed_state] += 1 
                        else: 
                            self.position_history[hashed_state] = 1
                        
                        #
                        if (self.player_1 == "T" and has_tiger_moves) or (self.player_1 == "G" and last_goat_eaten == self.goat_eaten):
                            self.moves_without_progress += 1
                        else:
                            self.moves_without_progress = 0
                        #
                    except: 
                        pass

                    # start = input("> ")
                    # start = (int(start.split(",")[0]) - 1, int(start.split(",")[1]) - 1)

                    # if start not in self.tiger_positions: 
                    #     print("This position doesn't have a tiger")
                    #     print(self)
                    #     continue

                    # print("Place that tiger:")
                    # end = input("> ")
                    # end = (int(end.split(",")[0]) - 1, int(end.split(",")[1]) - 1)

                    # if not self.is_valid_move(start, end):
                    #     print("Invalid tiger move!")
                    #     print(self)
                    #     continue 

                    # self = self.move_tiger(start, end)
  
            except Exception as e:
                print("Error: {}".format(e)) 
            
            print(self)


    def __str__(self):
        board_string = "" 
        for row in range(self.size):
            for col in range(self.size):
                board_string += "    {}".format(self.position[row, col])

            board_string += "\n\n"

        return board_string


if __name__ == "__main__":
    board = Board()
    board.game_loop()

    # # ai vs ai 
    # while True: 
    #     best_move = mcts.search(board) 
    #     board = best_move.board 

    #     print(board)

    #     input()
