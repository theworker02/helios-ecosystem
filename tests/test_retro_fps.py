import pathlib, sys, math
SERVER=pathlib.Path(__file__).parents[1]/"core"/"helios-chatgpt"/"server"
sys.path.insert(0,str(SERVER))
from retro_fps import RetroMap, cast_rays, move, ascii_frame

def test_raycast_hits_walls():
    level=RetroMap.from_text("#####\n#...#\n#.P.#\n#...#\n#####")
    x,y=level.spawn()
    rays=cast_rays(level,x,y,0,rays=20)
    assert len(rays)==20
    assert all(r["distance"]>0 for r in rays)
    assert ascii_frame(rays,12).count("\n")==11

def test_collision_prevents_escape():
    level=RetroMap.from_text("#####\n#P..#\n#####")
    x,y=level.spawn()
    for _ in range(50):
        x,y,a=move(level,x,y,math.pi,forward=.1)
    assert x>1.0
