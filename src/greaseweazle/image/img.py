# greaseweazle/image/img.py
#
# Written & released by Keir Fraser <keir.xen@gmail.com>
#
# This is free and unencumbered software released into the public domain.
# See the file COPYING for more details, or visit <http://unlicense.org>.

from greaseweazle import error
from greaseweazle.codec.ibm import mfm
from .image import Image

class IMG(Image):

    sides_swapped = False
    
    def __init__(self, name, fmt):
        self.to_track = dict()
        error.check(fmt is not None, """\
Sector image requires a disk format to be specified""")
        self.filename = name
        self.fmt = fmt


    @classmethod
    def from_file(cls, name, fmt):

        with open(name, "rb") as f:
            dat = f.read()

        img = cls(name, fmt)

        pos = 0
        for t in fmt.tracks:
            cyl, head = t.cyl, t.head
            if img.sides_swapped:
                head ^= 1
            track = fmt.mk_track(cyl, head)
            if track is not None:
                pos += track.set_img_track(dat[pos:])
                img.to_track[cyl,head] = track

        return img


    @classmethod
    def to_file(cls, name, fmt, noclobber):
        error.check(not cls.read_only,
                    "%s: Cannot create %s image files" % (name, cls.__name__))
        img = cls(name, fmt)
        img.noclobber = noclobber
        return img


    def get_track(self, cyl, side):
        if (cyl,side) not in self.to_track:
            return None
        return self.to_track[cyl,side]


    def emit_track(self, cyl, side, track):
        self.to_track[cyl,side] = track


    def get_image(self):

        tdat = bytearray()

        for t in self.fmt.tracks:
            cyl, head = t.cyl, t.head
            if self.sides_swapped:
                head ^= 1
            if (cyl,head) in self.to_track:
                tdat += self.to_track[cyl,head].get_img_track()
            else:
                tdat += self.fmt.mk_track(cyl, head).get_img_track()

        return tdat


# Local variables:
# python-indent: 4
# End:
