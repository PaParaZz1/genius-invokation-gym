"""Base class of summons generated by character skills: abstract class
A character in the game should be an instant of the specific character class defined in each file"""
from abc import ABC, abstractmethod

from .entity import Entity


class Summon(Entity, ABC):
    def __init__(self):
        # TODO
        pass

    def encode():
        pass
