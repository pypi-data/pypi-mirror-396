"""
https://gitlab.com/iShapeNoise/foxdot/-/blob/e809b4f776820bb94d3ad6dfcda887a7bbf6acec/FoxDot/osc/scsyndef/wsaw.scd

metadata: (
	credit: "Credit",
	modified_by: "Modifier",
	decription: "Description",
	category: \category,
	tags: [\tag, \tag]
)
"""
from supriya import Envelope
from supriya.ugens import In, VarSaw, Lag, Mix, LPF, Pan2, ReplaceOut, EnvGen, LFSaw, Splay

from ..SynthDef import SynthDef

__all__ = ['wsaw']


@SynthDef
def wsaw(
    bus=0, amp=1, gate=1, pan=0, fmod=0, spread=0.8, freq=0, atk=.01, sus=1,
    rel=.3,
    iphase1=.4, iphase2=.5, iphase3=.0,
    offnote1=1, offnote2=.99, offnote3=1.005
):
    freq = In.kr(bus=bus, channel_count=1)
    freq = [freq, freq+fmod]
    amp = amp / 10
    env = EnvGen.kr(envelope=Envelope.linen(atk, sus, rel), done_action=0)
    osc1 = LFSaw.ar(frequency=freq * offnote1 + [0.04, -0.04], initial_phase=iphase1) * (1/8)
    osc2 = LFSaw.ar(frequency=freq * offnote2, initial_phase=iphase2) * (1/8)
    osc3 = LFSaw.ar(frequency=freq * offnote3, initial_phase=iphase3) * (1/8)
    osc = osc1 + osc2 + osc2
    osc = Mix.multichannel(osc, channel_count=4)
    osc = Splay.ar(source=osc, spread=spread, center=pan)
    osc = osc * env * amp * 0.7
    osc = Pan2.ar(source=osc, position=pan)
    ReplaceOut.ar(bus=bus, source=osc)
