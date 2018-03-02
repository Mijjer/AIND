"""Implement your own custom search agent using any combination of techniques
you choose.  This agent will compete against other students (and past
champions) in a tournament.

         COMPLETING AND SUBMITTING A COMPETITION AGENT IS OPTIONAL
"""
import random


class SearchTimeout(Exception):
    """Subclass base exception for code clarity. """
    pass


def custom_score(game, player):
    """Calculate the heuristic value of a game state from the point of view
    of the given player.

    This should be the best heuristic function for your project submission.

    Parameters
    ----------
    game : `isolation.Board`
        An instance of `isolation.Board` encoding the current state of the
        game (e.g., player locations and blocked cells).

    player : object
        A player instance in the current game (i.e., an object corresponding to
        one of the player objects `game.__player_1__` or `game.__player_2__`.)

    Returns
    -------
    float
        The heuristic value of the current game state to the specified player.
    """
    if game.is_loser(player):
        return float("-inf")

    if game.is_winner(player):
        return float("inf")

    own_moves = len(game.get_legal_moves(player))
    opp_moves = len(game.get_legal_moves(game.get_opponent(player)))
    return float(own_moves - 2.5*opp_moves)


class CustomPlayer:
    """Game-playing agent to use in the optional player vs player Isolation
    competition.

    You must at least implement the get_move() method and a search function
    to complete this class, but you may use any of the techniques discussed
    in lecture or elsewhere on the web -- opening books, MCTS, etc.

    **************************************************************************
          THIS CLASS IS OPTIONAL -- IT IS ONLY USED IN THE ISOLATION PvP
        COMPETITION.  IT IS NOT REQUIRED FOR THE ISOLATION PROJECT REVIEW.
    **************************************************************************

    Parameters
    ----------
    data : string
        The name of the search method to use in get_move().

    timeout : float (optional)
        Time remaining (in milliseconds) when search is aborted.  Note that
        the PvP competition uses more accurate timers that are not cross-
        platform compatible, so a limit of 1ms (vs 10ms for the other classes)
        is generally sufficient.
    """

    def __init__(self, search_depth=3, data=None, timeout=1.):
        self.search_depth = search_depth
        self.score = custom_score
        self.time_left = None
        self.TIMER_THRESHOLD = timeout

    def get_move(self, game, time_left):
        """Search for the best move from the available legal moves and return a
        result before the time limit expires.

        **********************************************************************
        NOTE: If time_left < 0 when this function returns, the agent will
              forfeit the game due to timeout. You must return _before_ the
              timer reaches 0.
        **********************************************************************

        Parameters
        ----------
        game : `isolation.Board`
            An instance of `isolation.Board` encoding the current state of the
            game (e.g., player locations and blocked cells).

        time_left : callable
            A function that returns the number of milliseconds left in the
            current turn. Returning with any less than 0 ms remaining forfeits
            the game.

        Returns
        -------
        (int, int)
            Board coordinates corresponding to a legal move; may return
            (-1, -1) if there are no available legal moves.
        """
        self.time_left = time_left

        if game.move_count == 0:
            return(int(game.height/2), int(game.width/2))
        
        legal_moves = game.get_legal_moves(self)
        if len(legal_moves) > 0:
            best_move = legal_moves[randint(0, len(legal_moves)-1)]
        else:
            best_move = (-1, -1)

        try:
            self.search_depth = 2
            while True:
                current_move = self.alphabeta(game, self.search_depth)
                if current_move == (-1, -1):
                    return best_move
                else:
                    best_move = current_move
                self.search_depth += 1
        except SearchTimeout:
            return best_move # Handle any actions required after timeout as needed

        # Return the best move from the last completed search iteration
        return best_move

    def alphabeta(self, game, depth, alpha=float("-inf"), beta=float("inf")):
        """
        Parameters
        ----------
        game : isolation.Board
            An instance of the Isolation game `Board` class representing the
            current game state

        depth : int
            Depth is an integer representing the maximum number of plies to
            search in the game tree before aborting

        alpha : float
            Alpha limits the lower bound of search on minimizing layers

        beta : float
            Beta limits the upper bound of search on maximizing layers

        Returns
        -------
        (int, int)
            The board coordinates of the best move found in the current search;
            (-1, -1) if there are no legal moves
        """
        if self.time_left() < self.TIMER_THRESHOLD:
            raise SearchTimeout()

        def terminal_test(game):
            """ Return True if the game is over for the active player
            and False otherwise.
            """
            if self.time_left() < self.TIMER_THRESHOLD:
                raise SearchTimeout()
            return not bool(game.get_legal_moves())  # by Assumption 1

        def min_value(game, depth, alpha, beta):
            """ Return the value for a win (+1) if the game is over,
            otherwise return the minimum value over all legal child
            nodes.
            """
            if self.time_left() < self.TIMER_THRESHOLD:
                raise SearchTimeout()
            best_move = (-1, -1)
            if terminal_test(game):
                return self.score(game, self), best_move
            if depth <= 0: 
                return self.score(game, self), best_move    
            min_val = float("inf")
            for move in game.get_legal_moves():
                out = max_value(game.forecast_move(move), depth - 1, alpha, beta)
                if out[0] < min_val:
                    min_val, _ = out
                    best_move = move
                if min_val <= alpha:
                    return min_val, best_move
                beta = min(beta, min_val)
            return min_val, best_move


        def max_value(game, depth, alpha, beta):
            """ Return the value for a loss (-1) if the game is over,
            otherwise return the maximum value over all legal child
            nodes.
            """
            if self.time_left() < self.TIMER_THRESHOLD:
                raise SearchTimeout()
            best_move = (-1, -1)
            if terminal_test(game):
                return self.score(game, self), best_move
            if depth <= 0: 
                return self.score(game, self), best_move
            max_val = float("-inf")
            for move in game.get_legal_moves():
                out = min_value(game.forecast_move(move), depth - 1, alpha, beta)
                if out[0] > max_val:
                    max_val, _ = out
                    best_move = move
                if max_val >= beta:
                    return max_val, best_move
                alpha = max(alpha, max_val)
            return max_val, best_move

        if not game.get_legal_moves():
            return (-1, -1)
        _, best_move = max_value(game, depth, alpha, beta)
        return best_move
