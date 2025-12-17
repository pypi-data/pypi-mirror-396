from dataclasses import replace
from functools import cached_property
from typing import TYPE_CHECKING, Self, override

from nextrpg.config.system.key_mapping_config import KeyMappingConfig
from nextrpg.core.dataclass_with_default import (
    dataclass_with_default,
)
from nextrpg.core.time import Millisecond
from nextrpg.drawing.sprite import Sprite
from nextrpg.event.base_event import BaseEvent
from nextrpg.event.io_event import is_key_press
from nextrpg.game.game_state import GameState
from nextrpg.scene.scene import Scene
from nextrpg.widget.sizable_widget import SizableWidget
from nextrpg.widget.widget import Widget

if TYPE_CHECKING:
    from nextrpg.widget.button_spec import BaseButtonSpec


@dataclass_with_default(frozen=True, kw_only=True)
class Button(SizableWidget):
    spec: BaseButtonSpec

    @override
    @cached_property
    def sprite(self) -> Sprite:
        if self.is_selected:
            return self.spec.active
        return self.spec.idle

    @override
    def _event_after_selected(
        self, event: BaseEvent, state: GameState
    ) -> tuple[Scene, GameState]:
        if not is_key_press(event, KeyMappingConfig.confirm):
            return self, state

        if isinstance(res := self.spec.on_click(self, state), tuple):
            res, state = res
        match res:
            case Widget():
                return res.select, state
            case Scene():
                return self.exit(res), state
        return self, state

    @override
    def _tick_without_parent_and_animation(
        self, time_delta: Millisecond, state: GameState
    ) -> tuple[Self, GameState]:
        if self.is_selected:
            active = self.spec.active.tick(time_delta)
            idle = self.spec.idle
        else:
            active = self.spec.active
            idle = self.spec.idle.tick(time_delta)
        spec = replace(self.spec, idle=idle, active=active)
        ticked = replace(self, spec=spec)
        return ticked, state
