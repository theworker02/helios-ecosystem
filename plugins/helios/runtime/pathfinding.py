from __future__ import annotations
import heapq, math

def astar(level, start, goal, blocked=None, max_nodes=4096):
    blocked = set(blocked or [])
    start = (int(start[0]), int(start[1]))
    goal = (int(goal[0]), int(goal[1]))
    if start == goal:
        return [start]
    def h(a,b): return abs(a[0]-b[0])+abs(a[1]-b[1])
    open_heap=[(h(start,goal),0,start)]
    came={}
    g={start:0}
    seen=0
    while open_heap and seen<max_nodes:
        _,cost,node=heapq.heappop(open_heap); seen+=1
        if node==goal:
            path=[node]
            while node in came:
                node=came[node]; path.append(node)
            path.reverse(); return path
        x,y=node
        for nxt in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if nxt in blocked or level.solid(nxt[0]+0.5,nxt[1]+0.5):
                continue
            nc=cost+1
            if nc<g.get(nxt,1e18):
                g[nxt]=nc; came[nxt]=node
                heapq.heappush(open_heap,(nc+h(nxt,goal),nc,nxt))
    return []

def line_of_sight(level, a, b, step=0.1, max_steps=2048):
    ax,ay=float(a[0]),float(a[1]); bx,by=float(b[0]),float(b[1])
    dx,dy=bx-ax,by-ay; dist=math.hypot(dx,dy)
    if dist<=1e-9: return True
    n=min(max_steps,max(1,int(dist/step)))
    for i in range(1,n):
        t=i/n
        if level.solid(ax+dx*t, ay+dy*t):
            return False
    return True
