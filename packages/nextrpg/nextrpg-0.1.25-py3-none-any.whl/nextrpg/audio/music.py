from dataclasses import dataclass
from pygame import mixer_music

from nextrpg.audio.music_spec import MusicSpec
from nextrpg.event.user_event import UserEvent, post_user_event


def play_music(spec: MusicSpec | None) -> None:
    global _playing
    if not spec or _playing == spec:
        return

    if _playing:
        stop_music()
        delay = _playing.config.fade_out_duration
    else:
        delay = 0
    _playing = spec
    event = PlayMusicEvent(spec)
    post_user_event(event, delay)


def stop_music() -> None:
    if _playing:
        mixer_music.fadeout(_playing.config.fade_out_duration)


_playing: MusicSpec | None = None


@dataclass(frozen=True)
class PlayMusicEvent(UserEvent):
    spec: MusicSpec

    def play(self) -> None:
        mixer_music.load(self.spec.file)
        mixer_music.play(
            self.spec.loop_flag, fade_ms=self.spec.config.fade_in_duration
        )
