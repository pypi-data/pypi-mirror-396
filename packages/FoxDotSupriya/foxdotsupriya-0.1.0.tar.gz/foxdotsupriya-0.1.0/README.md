# FoxDotSupriya - Integration with FoxDot and Supriya to white SynthDefs/Effects.

## Instalation

``` shell
pip install FoxDotSupriya
# or
pip install git+https://codeberg.org/FoxDotExtensions/FoxDotSupriya
```

## Usage

Import lib

``` python
from FoxDot.lib.Extensions.Supriya import *
```

### Effects

TODO: examples

### SynthDef

- `sine`: Simples sine oscilator.

	``` python
	p1 >> sine()
	```

### Your Own SynthDef

See [Using Your Own Synthdefs](https://foxdot.org/docs/using-your-own-synthdefs/) for more details.

Write/modifier your synths

``` python
from supriya import Envelope
from supriya.ugens import EnvGen, ReplaceOut, Pan2, In, LFTri, SinOsc, LFSaw, Pulse

@SynthDef
def mysynth(amp=1, sus=1, pan=0, freq=0, bus=0, atk=0.01):
	freq = In.kr(bus=bus, channel_count=1)  # see https://foxdot.org/docs/using-your-own-synthdefs/
	osc = LFTri.ar(frequency=freq) * amp
	env = EnvGen.ar(
		envelope=Envelope.percussive(attack_time=atk, release_time=sus),
		done_action=0  # every doneAction must be 0, see https://foxdot.org/docs/using-your-own-synthdefs/
	)
	osc = Pan2.ar(source=osc * env, position=pan)
	ReplaceOut.ar(bus=bus, source=osc)  # ReplaceOut is needed to FoxDot, see https://foxdot.org/docs/using-your-own-synthdefs/

m1 >> mysynth([0,2,4,2], dur=[[1,.5], PDur(7,8)], shape=0.15, chop=2)
```

You can modify the synth definition in runtime. Try change `LFTri` for `LFSaw` or `Pulse`.

Feel free to submit new synths to the library for others to use.
