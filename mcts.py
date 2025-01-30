import math
import random 


class TreeNode():
    def __init__(self, board, parent): 
        self.board = board
        self.parent = parent 
        self.children = {} 
        self.score = 0
        self.visits = 0 

        if self.board.is_tiger_win() or self.board.is_goat_win() or self.board.is_draw():
            self.is_terminal = True 
        else: 
            self.is_terminal = False 
        
        self.is_fully_expanded = self.is_terminal


class MCTS():
    def evaluate(self, board):
        score = 0 

        tiger_alive = 4 - board.tiger_captured
        score += tiger_alive * 10

        score += board.goat_eaten * 40

        best_tiger_position_score = board.best_tiger_positions_score()
        score += best_tiger_position_score * 10

        goat_safety_score = board.get_goat_cluster_score()
        score -= goat_safety_score * 30

        goat_remaining = board.goat_counts - board.goat_eaten
        score -= goat_remaining * 10

        goat_tiger_distance = board.goat_tiger_distance()
        score -= goat_tiger_distance * 10

        return score if board.is_goat_win() else -score


    def search(self, initial_state):
        """This function returns best move to play"""
        self.root = TreeNode(initial_state, None)
        
        for i in range(60000):
            # select
            node = self.select(self.root)

            # simulate 
            score = self.simulate(node.board)

            # backpropagation 
            self.backpropagation(node, score) 

        try: 
            return self.get_most_visited_node()
        except:
            pass

    def get_most_visited_node(self):
        children = self.root.children.values()
        best_node = next(iter(children))

        for child_node in children:
            if child_node.visits >= best_node.visits:
                best_node = child_node
        return best_node

    
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
            state_position_str = str(state.position)
            if state_position_str not in node.children:
                new_node = TreeNode(state, node)   
                node.children[state_position_str] = new_node 

                if len(states) == len(node.children):
                    node.is_fully_expanded = True 
                return new_node

    def simulate(self, board):
        depth = 0
        while depth <= 15 and not board.is_tiger_win() and not board.is_goat_win() and not board.is_draw():
            try:
                board = random.choice(board.generate_states()) 
                depth += 1
            except: 
                return 0
            
        # if board.is_draw(): return 0
        # elif board.is_goat_win(): return 1 
        # elif board.is_tiger_win(): return -1

        return self.evaluate(board)

    def backpropagation(self, node, score):
        while node is not None: 
            node.visits += 1

            if node.board.player_1 == "T":
                node.score -= score
            else:
                node.score += score

            node = node.parent 


    def get_best_move(self, node, exploration_constant):
        best_score = float("-inf")
        best_moves = [] 

        for child_node in node.children.values():            
            if child_node.board.player_2 == "G": current_player = 1
            elif child_node.board.player_2 == "T": current_player = -1

            move_score = current_player * child_node.score / child_node.visits + exploration_constant * math.sqrt(math.log(node.visits) / child_node.visits)

            if move_score > best_score:
                best_score = move_score
                best_moves = [child_node]
            elif move_score == best_score: 
                best_moves.append(child_node)

        return random.choice(best_moves)

