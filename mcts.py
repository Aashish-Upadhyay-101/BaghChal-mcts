import math
import random 
import time

class TreeNode():
    def __init__(self, board, parent): 
        self.board = board
        self.parent = parent 
        self.children = {} 
        self.score = 0
        self.visits = 0 

        if self.board.is_tiger_win() or self.board.is_goat_win():
            self.is_terminal = True 
        else: 
            self.is_terminal = False 
        
        self.is_fully_expanded = self.is_terminal


class MCTS():
    def search(self, initial_state):
        """This function returns best move to play"""
        self.root = TreeNode(initial_state, None)
        
        for i in range(5000):
            # select
            print(i)
            node = self.select(self.root)

            # simulate 
            score = self.simulate(node.board)
            if score == 0: 
                print("Draw\n")
            elif score == 1: 
                print("Goat\n")
            else:
                print("Tiger\n")

            # backpropagation 
            self.backpropagation(node, score) 

        try: 
            return self.get_best_move(self.root, 0)
        except:
            pass

    
    def select(self, node):
        while not node.is_terminal:
            if node.is_fully_expanded: 
                node = self.get_best_move(node, 2)
            else: 
                return self.expand(node)

        return node

    def expand(self, node):
        states = node.board.generate_states() 
        for state in states: 
            if str(state.position) not in node.children:
                new_node = TreeNode(state, node)   
                node.children[str(state.position)] = new_node 

                if len(states) == len(node.children):
                    node.is_fully_expanded = True 
                return new_node

    def simulate(self, board):
        while not board.is_tiger_win() and not board.is_goat_win() and not board.is_draw():
            try:
                board = random.choice(board.generate_states())
            except: 
                return 0

        if board.is_draw(): return 0
        elif board.player_2 == "G": return 1 
        elif board.player_2 == "T": return -1 


    def backpropagation(self, node, score):
        while node is not None: 
            node.visits += 1
            node.score += score 
            node = node.parent 

    def get_best_move(self, node, exploration_constant):
        best_score = float("-inf")
        best_moves = [] 

        for child_node in node.children.values():
            if child_node.board.player_2 == "G": current_player = 1
            elif child_node.board.player_2 == "T": current_player = -1

            move_score = current_player * child_node.score / child_node.visits + math.sqrt(exploration_constant) * math.sqrt(math.log(node.visits) / child_node.visits)

            if move_score > best_score:
                best_score = move_score
                best_moves = [child_node]
            elif move_score == best_score: 
                best_moves.append(child_node)
        
        return random.choice(best_moves)