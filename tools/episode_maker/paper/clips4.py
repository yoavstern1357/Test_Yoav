"""CODE clips of Episode 1 v4.4 (the same paper-cut / map / title art as clips3, re-timed to the v4.4 clip lengths).
C04 journal + map web (4 s), C05 Qinglong port (5 s), C27-C29 the legend scroll world (4.5 / 4.5 / 4 s), C35I route-south insert (1.2 s), C90 series title.
Render: python3 -m paper.render3 --module clips4 [C04 ...] --both -> out/ep01v44/code/"""
from .clips3 import *
from . import clips3 as c3


class C04(c3.C03):
    name, dur = "C04", 4.0
    K = 4.5 / 4.0


class C05(c3.C04):
    name, dur = "C05", 5.0
    K = 4.5 / 5.0


class C27(c3.C20):
    name, dur = "C27", 4.5

    def draw(self, t, land):
        return super().draw(t * 6.0 / 4.5, land)


class C28(c3.C21):
    name, dur = "C28", 4.5

    def draw(self, t, land):
        return super().draw(t * 5.0 / 4.5, land)


class C29(c3.C22):
    name, dur = "C29", 4.0
    STALL = "C30"

    def draw(self, t, land):
        return super().draw(t * 3.0 / 4.0 * 1.0, land)


class C35I(c3.C27I):
    name, dur = "C35I", 1.2

    def frame(self, t, ts):
        return c3.C27I.frame(self, t * 1.6 / 1.2, step_t(t * 1.6 / 1.2, 12))


class C90(c3.C90):
    pass
