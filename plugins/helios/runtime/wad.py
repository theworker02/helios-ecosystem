from __future__ import annotations
import os, struct

class WadFile:
    """Read classic Doom IWAD/PWAD directories and common map geometry lumps.

    This parser does not ship game data. Use only WAD files you are legally allowed to access.
    """
    MAP_LUMP_NAMES = {"THINGS","LINEDEFS","SIDEDEFS","VERTEXES","SEGS","SSECTORS","NODES","SECTORS","REJECT","BLOCKMAP"}

    def __init__(self, path):
        self.path = os.fspath(path)
        self.data = open(self.path, "rb").read()
        if len(self.data) < 12:
            raise ValueError("not a WAD file")
        ident, count, directory = struct.unpack_from("<4sii", self.data, 0)
        self.kind = ident.decode("ascii", "replace")
        if self.kind not in ("IWAD", "PWAD"):
            raise ValueError("unsupported WAD signature")
        if count < 0 or count > 100000 or directory < 0:
            raise ValueError("invalid WAD directory")
        self.lumps = []
        for i in range(count):
            off = directory + i * 16
            if off + 16 > len(self.data):
                raise ValueError("truncated WAD directory")
            pos, size, raw_name = struct.unpack_from("<ii8s", self.data, off)
            name = raw_name.split(b"\0",1)[0].decode("ascii","replace").upper()
            if pos < 0 or size < 0 or pos + size > len(self.data):
                raise ValueError("invalid WAD lump range")
            self.lumps.append({"name": name, "offset": pos, "size": size, "index": i})

    def lump_bytes(self, name, after_index=-1):
        name = name.upper()
        for l in self.lumps:
            if l["index"] > after_index and l["name"] == name:
                return self.data[l["offset"]:l["offset"]+l["size"]], l["index"]
        raise KeyError(name)

    def maps(self):
        out = []
        for i, l in enumerate(self.lumps[:-1]):
            n = l["name"]
            is_marker = (len(n)==4 and n.startswith("E") and n[2]=="M") or (len(n)==5 and n.startswith("MAP"))
            if is_marker and self.lumps[i+1]["name"] == "THINGS":
                out.append({"name": n, "index": i})
        return out

    def map_geometry(self, map_name):
        marker = next((m for m in self.maps() if m["name"] == map_name.upper()), None)
        if not marker:
            raise KeyError(map_name)
        start = marker["index"]
        verts_raw, vi = self.lump_bytes("VERTEXES", start)
        vertices = [list(struct.unpack_from("<hh", verts_raw, o)) for o in range(0, len(verts_raw)-3, 4)]
        lines_raw, _ = self.lump_bytes("LINEDEFS", start)
        linedefs = []
        for o in range(0, len(lines_raw)-13, 14):
            v1,v2,flags,special,tag,right,left = struct.unpack_from("<HHHHHHH", lines_raw, o)
            linedefs.append({"v1":v1,"v2":v2,"flags":flags,"special":special,"tag":tag,"right":right,"left":left})
        sectors_raw, _ = self.lump_bytes("SECTORS", start)
        sectors = []
        for o in range(0, len(sectors_raw)-25, 26):
            floor, ceil, ftex, ctex, light, special, tag = struct.unpack_from("<hh8s8shhh", sectors_raw, o)
            sectors.append({"floor":floor,"ceiling":ceil,"floor_tex":ftex.rstrip(b"\0").decode("ascii","replace"),"ceiling_tex":ctex.rstrip(b"\0").decode("ascii","replace"),"light":light,"special":special,"tag":tag})
        things_raw, _ = self.lump_bytes("THINGS", start)
        things = []
        for o in range(0, len(things_raw)-9, 10):
            x,y,angle,thing_type,flags = struct.unpack_from("<hhhhh", things_raw, o)
            things.append({"x":x,"y":y,"angle":angle,"type":thing_type,"flags":flags})
        return {"name": map_name.upper(), "vertices": vertices, "linedefs": linedefs, "sectors": sectors, "things": things}

    def summary(self):
        return {"kind": self.kind, "lump_count": len(self.lumps), "maps": [m["name"] for m in self.maps()]}
