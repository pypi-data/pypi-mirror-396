from FoxDot import Clock, TempoClock, TimeVar
from link import Link as _Link

_bpm = Clock.bpm

# Ableton Link
_link = _Link(_bpm)
_link.enabled = True
_link.startStopSyncEnabled = True


def _tempo_callback(tempo=None):
    bpm = Clock.bpm
    if isinstance(bpm, TimeVar) and  tempo in list(bpm.values):
        return
    Clock.set_tempo(tempo, override=True)


_link.setTempoCallback(_tempo_callback)


def _sync_bpm(tempo=None):
    session = _link.captureSessionState()
    session.setTempo(tempo or Clock.get_bpm(), _link.clock().micros())
    _link.commitSessionState(session)


# --- TimeCLock.bpm property
def _get_bpm(self):
    return getattr(self, '_bpm', _bpm)


def _set_bpm(self, bpm):
    self._bpm = bpm
    _sync_bpm(self.get_bpm())


setattr(TempoClock, 'bpm', property(_get_bpm, _set_bpm))
Clock.every(.1, _sync_bpm)  # To TimeVar values
