

""" Put in the form for
*KEYWORD
*TITLE
*MAT_ELASTIC
*SECTION_SHELL (PCB)
*SECTION_SHELL (components)
*PART (one per PID)
*NODE
*ELEMENT_SHELL
*END"""

def assemble_PIDs(components, infile="board.k", outfile="board.k",
                         pid_start=2):
    with open(infile, "r", encoding="ascii", errors="ignore") as f:
        lines = [ln.rstrip("\r\n") for ln in f]

    mode = None
    nodes_raw, elems_raw = [], []
    for ln in lines:
        s = ln.strip()
        if not s: continue
        up = s.upper()
        if up.startswith("*NODE"):            mode = "node"; continue
        if up.startswith("*ELEMENT_SHELL"):   mode = "elem"; continue
        if up.startswith("*"):                mode = None;   continue
        if mode == "node": nodes_raw.append(s)
        elif mode == "elem": elems_raw.append(s)

    if not nodes_raw or not elems_raw:
        raise RuntimeError("Could not find *NODE / *ELEMENT_SHELL in 'board.k'")

    # parse nodes: id->(x,y,z)
    nodes = {}
    for rec in nodes_raw:
        toks = rec.replace(",", " ").split()
        if len(toks) < 4:
            raise RuntimeError(f"Bad *NODE line: '{rec}'")
        nid = int(toks[0]); x,y,z = map(float, toks[1:4])
        nodes[nid] = (x,y,z)

    # component rectangles -> PID
    rects, next_pid = [], pid_start
    for _, comp in components.items():
        (x0,y0) = comp["position"]; (w,h) = comp["dimensions"]
        rects.append((x0, y0, x0+w, y0+h, next_pid))
        next_pid += 1

    def pid_for_xy(xc, yc):
        for x0,y0,x1,y1,p in rects:
            if x0 <= xc <= x1 and y0 <= yc <= y1:
                return p
        return 1  # PCB

    # rewrite elements with centroid-based PID
    elems_out = []
    for rec in elems_raw:
        toks = rec.replace(",", " ").split()
        if len(toks) < 6:  # eid pid n1 n2 n3 n4
            continue
        eid = int(toks[0])
        n1, n2, n3, n4 = map(int, toks[-4:])
        x1,y1,_ = nodes[n1]; x2,y2,_ = nodes[n2]; x3,y3,_ = nodes[n3]; x4,y4,_ = nodes[n4]
        xc = 0.25*(x1+x2+x3+x4); yc = 0.25*(y1+y2+y3+y4)
        newpid = pid_for_xy(xc, yc)
        elems_out.append(f"{eid}, {newpid}, {n1}, {n2}, {n3}, {n4}")

    # write geometry-only (NO *END)
    out = []
    out.append("*KEYWORD")
    out.append("*TITLE")
    out.append("Geometry only (nodes+elements with PIDs)")
    out.append("*NODE")
    for nid in sorted(nodes):
        x,y,z = nodes[nid]
        out.append(f"{nid}, {x:.6f}, {y:.6f}, {z:.6f}")
    out.append("*ELEMENT_SHELL")
    out.extend(elems_out)

    with open(outfile, "w", encoding="ascii") as g:
        g.write("\n".join(out) + "\n")

    return [1] + [p for *_unused, p in rects]


def build_full_keyword(geom_k="board.k",
                                              out_k="board_full.k",
                                              pcb_pid=1, pcb_thk=1.6, comp_thk=3.0,
                                              E=200, nu=0.30, rho=100,
                                              tstop=1.0, d3plot_dt=0.2):

    def toks(s):  # splits comma separated values
        return [t for t in s.replace(",", " ").split() if t]

    #  read geometry and remove *END
    with open(geom_k, "r") as f:
        lines = [ln.rstrip("\r\n") for ln in f if ln.strip().upper() != "*END"]

    # locate blocks
    def find(tag):
        T = tag.upper()
        for i, ln in enumerate(lines):
            if ln.strip().upper().startswith(T):
                return i
        return -1

    i_node = find("*NODE")
    i_elem = find("*ELEMENT_SHELL")


    # parse nodes
    node_recs = lines[i_node+1 : i_elem]
    nodes = {}
    for rec in node_recs:
        tk = toks(rec)
        if len(tk) < 4:
            continue
        nid = int(tk[0]); x = float(tk[1]); y = float(tk[2]); z = float(tk[3])
        nodes[nid] = (x, y, z)


    #  parse elements
    elem_recs = lines[i_elem+1 :]
    elems = []
    pids_in_use = set()
    for rec in elem_recs:
        tk = toks(rec)
        if len(tk) < 6:
            # skip malformed/short lines
            continue
        eid = int(tk[0]); pid = int(tk[1])
        n1 = int(tk[2]); n2 = int(tk[3]); n3 = int(tk[4]); n4 = int(tk[5])
        # sanity: skip degenerate quads where 3+ nodes repeat
        if len({n1, n2, n3, n4}) < 3:
            continue
        elems.append((eid, pid, n1, n2, n3, n4))
        pids_in_use.add(pid)
    if not elems:
        raise RuntimeError("No valid elements parsed from geometry file.")

    # --------------------- Build parts -----------------------
    all_pids = sorted(pids_in_use | {pcb_pid})
    MID = 1
    SEC_PCB, SEC_COMP = 1, 2

    out = []
    out.append("*KEYWORD")
    out.append("*TITLE")
    out.append("Auto-stitched PCB + components")

    # *MAT_ELASTIC 
    out.append("*MAT_ELASTIC")
    out.append(f"{MID}, {rho:.4E}, {E:.4E}, {nu:.4f}")

    # *SECTION_SHELL for PCB 
    out.append("*SECTION_SHELL")
    out.append(f"{SEC_PCB}, 2, 0.8333, 5, 0")
    out.append(f"{pcb_thk:.6f}")
    out.append("*SECTION_SHELL")
    out.append(f"{SEC_COMP}, 2, 0.8333, 5, 0")
    out.append(f"{comp_thk:.6f}")

    # *PART per PID
    for pid in all_pids:
        secid = SEC_PCB if pid == pcb_pid else SEC_COMP
        out.append("*PART")
        out.append(f"PART_{pid}")
        # pid, secid, mid, eosid, hgid, grav, adpopt, tmid
        out.append(f"{pid}, {secid}, {MID}, 0, 0, 0, 0, 0")

    # *NODE 
    out.append("*NODE")
    for nid in sorted(nodes):
        x, y, z = nodes[nid]
        out.append(f"{nid}, {x:.6f}, {y:.6f}, {z:.6f}")

    # *ELEMENT_SHELL
    out.append("*ELEMENT_SHELL")
    for (eid, pid, n1, n2, n3, n4) in elems:
        out.append(f"{eid}, {pid}, {n1}, {n2}, {n3}, {n4}")

    # Keyword definitions
    out.append("*CONTROL_TERMINATION")
    out.append(f"{tstop:.6f}")
    out.append("*DATABASE_BINARY_D3PLOT")
    out.append(f"{d3plot_dt:.6f}")
    out.append("*DATABASE_GLSTAT")
    out.append(f"{d3plot_dt:.6f}")
    out.append("*DATABASE_MATSUM")
    out.append(f"{d3plot_dt:.6f}")
    out.append("*END")

    with open(out_k, "w", encoding="ascii") as g:
        g.write("\n".join(out) + "\n")

    return out_k

