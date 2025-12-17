from collections.abc import Callable

import pygame
from pygame import USEREVENT, Event

from nextrpg.core.time import Millisecond
from nextrpg.event.base_event import BaseEvent
from nextrpg.game.game_state import GameState


class UserEvent(BaseEvent):
    pass


NEXTRPG_USER_EVENT_ID = USEREVENT + len("nextrpg")


def post_user_event(
    event: UserEvent,
    delay: Millisecond | Callable[[GameState], bool] = 0,
) -> None:
    event = Event(NEXTRPG_USER_EVENT_ID, user_event=event, delay=delay)
    pygame.event.post(event)
