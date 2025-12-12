from pathlib import Path
from tempfile import mkdtemp

from supriya import synthdef
from FoxDot.lib.SCLang.SynthDef import SynthDefBaseClass, SynthDef as _SynthDef


class SynthDef(SynthDefBaseClass):
    TMP_SYNTHDEF_DIR = mkdtemp()

    def __init__(self, synth):
        if not callable(synth):
            self.__class__ = _SynthDef
            super().__init__(synth)
            return

        self.supriya_synth = synthdef()(synth)
        self.synth_added = False
        super().__init__(self.supriya_synth.name)
        self.filename = f'{self.TMP_SYNTHDEF_DIR}/{self.name}.scsyndef'

        self.add()

    def __str__(self):
        return str(self.supriya_synth)

    def write(self):
        path =  Path(self.filename)
        if path.exists():
            path.unlink()
        path.write_bytes(bytes(self.supriya_synth.compile()))

    def load(self):
        self.server.loadCompiled(self.filename)
        self.synth_added = True
