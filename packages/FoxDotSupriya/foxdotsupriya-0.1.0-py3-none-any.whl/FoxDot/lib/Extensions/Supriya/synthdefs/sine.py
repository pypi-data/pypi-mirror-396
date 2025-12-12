from supriya import Envelope
from supriya.ugens import EnvGen, Out, SinOsc, ReplaceOut, Pan2, In, LFTri

from ..SynthDef import SynthDef

__all__ = ['sine']


@SynthDef
def sine(amp=1, sus=1, pan=0, freq=0, bus=0):
    freq = In.kr(bus=bus, channel_count=1)
    osc = SinOsc.ar(frequency=freq) * amp
    env = EnvGen.ar(
        envelope=Envelope.percussive(attack_time=0.01, release_time=sus),
        done_action=0
    )
    osc = Pan2.ar(source=osc * env, position=pan)
    ReplaceOut.ar(bus=bus, source=osc)
