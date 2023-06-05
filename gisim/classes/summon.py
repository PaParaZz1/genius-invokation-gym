"""Base class of summons generated by character skills: abstract class
A character in the game should be an instant of the specific character class defined in each file"""
import itertools
from abc import ABC, abstractmethod
from queue import PriorityQueue
from typing import OrderedDict, cast
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from gisim.classes.enums import AttackType, CharPos, ElementType, PlayerID
from gisim.classes.message import DealDamageMsg, Message, RoundEndMsg,TriggerSummonEffectMsg

from .entity import Entity


class Summon(Entity, ABC):

    name: str
    usages: int
    player_id: PlayerID
    position: int = -1
    """Range from 0~3, should be set when adding a new summon to the summon zone. Initialized by -1"""
    active: bool = True
    _uuid: UUID = Field(default_factory=uuid4)

    def encode(self):
        return self.dict(exclude={"_uuid", "_logger"})

    @abstractmethod
    def msg_handler(self, msg_queue: PriorityQueue) -> bool:
        ...


class AttackSummon(Summon):
    damage_element: ElementType
    damage_value: int

    def msg_handler(self, msg_queue):
        msg = msg_queue.queue[0]
        if self._uuid in msg.responded_entities:
            return False
        updated = False
        if isinstance(msg, TriggerSummonEffectMsg):
            msg = cast(TriggerSummonEffectMsg,msg)
            new_msg = DealDamageMsg(
                attack_type=AttackType.SUMMON,
                sender_id=self.player_id,
                attacker=(self.player_id, CharPos.NONE),
                targets=[
                    (
                        ~self.player_id,
                        CharPos.ACTIVE,
                        self.damage_element,
                        self.damage_value
                    )
                ]
            )
            msg_queue.put(new_msg)
            if msg.consume_available_times:
                self.usages -= 1
                if self.usages == 0:
                    self.active = False
            msg.responded_entities.append(self._uuid)
            updated = True

        if isinstance(msg, RoundEndMsg):
            msg = cast(RoundEndMsg, msg)
            new_msg = DealDamageMsg(
                attack_type=AttackType.SUMMON,
                sender_id=self.player_id,
                attacker=(self.player_id, CharPos.NONE),
                targets=[
                    (
                        ~self.player_id,
                        CharPos.ACTIVE,
                        self.damage_element,
                        self.damage_value,
                    )
                ],
            )
            msg_queue.put(new_msg)
            self.usages -= 1
            if self.usages == 0:
                self.active = False
            msg.responded_entities.append(self._uuid)
            updated = True
        return updated

