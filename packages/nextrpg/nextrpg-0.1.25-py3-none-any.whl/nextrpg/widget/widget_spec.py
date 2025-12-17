from typing import ClassVar

from nextrpg.animation.timed_animation_on_screens import TimedAnimationOnScreens
from nextrpg.animation.timed_animation_spec import TimedAnimationSpec
from nextrpg.core.dataclass_with_default import dataclass_with_default, default
from nextrpg.core.metadata import HasMetadata, Metadata
from nextrpg.widget.widget import Widget


@dataclass_with_default(frozen=True)
class WidgetSpec[_Widget: Widget](HasMetadata):
    # Must be a subclass of Widget.
    widget_type: ClassVar[type]
    enter_animation: TimedAnimationSpec | None = None
    exit_animation: TimedAnimationSpec | None = default(
        lambda self: self._init_exit_animation
    )
    name: str | None = None
    metadata: Metadata = ()

    def with_parent(self, parent: Widget) -> _Widget:
        return self.widget_type(
            spec=self,
            name_to_on_screens=parent.name_to_on_screens,
            parent=parent,
        )

    @property
    def _init_exit_animation(self) -> TimedAnimationOnScreens | None:
        if self.enter_animation:
            return self.enter_animation.reverse
        return None
