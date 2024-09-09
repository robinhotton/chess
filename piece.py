from abc import ABC, abstractmethod

class Piece(ABC):
    def __init__(self, color:str, position: tuple):
        self.color = color
        self.position = position

    def move(self, new_position: tuple):
        self.position = new_position
        
    @abstractmethod
    def get_legal_moves(self, board):
        pass