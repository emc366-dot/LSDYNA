

import numpy as np
import matplotlib.pylab as plt
import matplotlib.patches as patches
import random

def rand(N=None, pct=None): #take in N and pct
   
    # if no inputs:
    if N is None:
        N = int(np.random.uniform(low=5, high=100))  
    if pct is None:
        pct = int(np.random.uniform(low=15, high=75))

    boardWidth = 50 #5 cm // 50 mm // X
    boardHeight = 50 #5 cm // 50 mm // Y
    boardArea = boardWidth * boardHeight

    components = {}
    placedComponents = []  # Store (x, y, width, height)
   
    # specific components. Just one for testing purposes
    electronics = {
        'block': {'min_width': 3, 'max_width': 10, 'min_height': 3, 'max_height': 20, 'color': 'red'},
    }

    count = 0
    tempArea = 0
    maxIter = 10000
    iteration = 0
    while (iteration < maxIter):
        coverage = tempArea / boardArea * 100
        coverageMin = coverage >= (pct - 5) #pct +/- 5%
        coverageMax = coverage <= (pct + 5)


        if (count >= N) or ((coverageMin) and (coverageMax)):  #greater than pct - 5% and less than pct + 5%
            if coverageMin and coverageMax:
                print(f"Reached desired coverage: {coverage:.2f}% (which is within {pct - 5}% and {pct + 5}%)")
                break
            elif (count >= N):
                print(f"Reached desired number of components: {count}")
                break


        temp = 'block'
        info = electronics[temp]
       
        # random dimensions based on info given // uniform randomness
        width = np.random.uniform(low=info['min_width'], high=info['max_width']) # random size between 3 and 20 mm
        height = np.random.uniform(low=info['min_height'], high=info['max_height']) #random size between 3 and 40 mm
       
        placed = 0
        buffer = 1  # 1 mm buffer
        positionAttempts = 0
        # finding the left bottom corner position of each component to figure out collisions
        while placed == 0 and positionAttempts < maxIter:
            x = np.random.uniform(low=buffer, high=boardWidth - width - buffer)
            y = np.random.uniform(low=buffer, high=boardHeight - height - buffer)
           
            # Check collisions with buffer // make this an algorithm for the report maybe !!!!!!!!!!!!!!!!!!!!!!!!!!!
            collision = 0
            for comp_x, comp_y, comp_w, comp_h in placedComponents:
                if ((x - buffer < comp_x + comp_w + buffer) and (x + width + buffer > comp_x - buffer) and (y - buffer < comp_y + comp_h + buffer) and (y + height + buffer > comp_y - buffer)):
                    collision = 1
                    positionAttempts += 1
                    break
           
            if collision == 0:
                components[f'{temp}{count}'] = {
                    'type': temp,  
                    'position': (x, y),
                    'dimensions': (width, height), #no thickness for now
                    'bounds': (x, y, x + width, y + height),
                    'color': info['color']  # Store the color with the component // for plotting purposes
                }
                placedComponents.append((x, y, width, height))
                placed = 1
                count += 1
                tempArea += (width * height)
                print(f"printed {count} components || iteration number {iteration}")
                break

        iteration += 1

        if iteration >= maxIter:
            print(f"Reached maximum iterations without satisfying conditions. Final coverage: {coverage:.2f}%. Final Component count: {count}")
            break
   
    return components, boardWidth, boardHeight

def plot(components, boardWidth, boardHeight):
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot()
       
    # Draw board
    board = patches.Rectangle((0, 0), boardWidth, boardHeight, linewidth=2, edgecolor='black', facecolor='lightgray')
    ax.add_patch(board)
       
    for name, comp in components.items():        
        #get componenet position and dimensions
        x, y = comp['position']
        width, height = comp['dimensions']
       
        # draw each componenent on the board/graph
        rect = patches.Rectangle((x, y), width, height,linewidth=1, edgecolor='black', facecolor=comp['color'], alpha=0.7)
        ax.add_patch(rect)
           
        # Add label
        ax.text(x + width/2, y + height/2, name, ha='center', va='center', fontsize=8)
       
    ax.set_xlim(-5, boardWidth + 5)
    ax.set_ylim(-5, boardHeight + 5)
    ax.set_aspect('equal')
    ax.set_title('Circuit Board Components Layout')
    ax.set_xlabel('Width (mm)')
    ax.set_ylabel('Height (mm)')
    plt.grid(True, alpha=0.3)
    plt.show()

def mesh(boardWidth, boardHeight,components):
    res = 1  # 1 node per mm
    length = boardWidth * res
    height = boardHeight * res
   
    nodes = []
    elements = []
    node_coords = {}
   
    # Create nodes
    for i in range(length + 1):
        for j in range(height + 1):
            node_id = i * (height + 1) + j + 1
            x = i / res  # Convert back to mm
            y = j / res
           
            # Default z = 0
            z = 0.0
           
            # Check if this node is inside any component
            for comp_id, comp_data in components.items():
                comp_x, comp_y = comp_data['position']
                comp_w, comp_h = comp_data['dimensions']
               
                # Check if node is within component bounds
                if (comp_x <= x <= comp_x + comp_w and
                    comp_y <= y <= comp_y + comp_h):
                    z = 3  # Raise to component height
                    break
           
            nodes.append(f"{node_id:8d}{x:15.1f}{y:15.1f}{z:15.1f}       0       0")
            node_coords[node_id] = (x, y, z)
   
   
    # Create elements
    matID = 1 #steel
    for i in range(length):
        for j in range(height):
            n1 = i * (height + 1) + j + 1 #bottom left
            n2 = n1 + 1                   #bottom right
            n3 = n1+height+2              #top right
            n4 = n1+height+1              #top left
            elements.append(f"{(i*height+j+1):8d}{matID:8d}{n1:8d}{n2:8d}{n3:8d}{n4:8d}")
            #starts on the inside, does the whole row,
   
    # write file
    with open("board.k", "w") as f:
        f.write("*KEYWORD\n")
        f.write("*TITLE\n")
        f.write("Combined Grid for Testing 1031\n")
        f.write("*NODE\n")
        f.write("\n".join(nodes) + "\n")
        f.write("*ELEMENT_SHELL\n")
        f.write("\n".join(elements) + "\n")
        f.write("*END")

    print(f"Done")



# ------------------- PyDYNA-based build + local run (keep your gens) -------------------
import os, sys, subprocess
os.environ["PATH"] = os.path.dirname(sys.executable) + os.pathsep + os.environ.get("PATH","")


def write_geom_with_pids(components, infile="board.k", outfile="board_geom_pids.k",
                         pid_start=2):
    """Read mesh() output (NODE + ELEMENT_SHELL) and rewrite ELEMENT_SHELL with PIDs per component footprint.
       Writes *KEYWORD,*TITLE,*NODE,*ELEMENT_SHELL (NO *END). Returns [1] + component PIDs."""
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


def stitch_full_keyword_from_geometry_ordered(geom_k="board_geom_pids.k",
                                              out_k="board_full.k",
                                              pid_list=None,
                                              pcb_pid=1, pcb_thk=1.6, comp_thk=3.0,
                                              E=200, nu=0.30, rho=1.90e-4,
                                              tstop=1.0, d3plot_dt=0.2):
    """
    Build a clean LS-DYNA deck from a geometry-with-PIDs file.
    Output order:
      *KEYWORD
      *TITLE
      *MAT_ELASTIC
      *SECTION_SHELL (PCB)
      *SECTION_SHELL (components)
      *PART (one per PID actually used)
      *NODE
      *ELEMENT_SHELL
      *CONTROL_TERMINATION
      *DATABASE_...
      *END
    All numeric data are comma-separated to enforce free-format parsing.
    """
    def toks(s):  # safe splitter
        return [t for t in s.replace(",", " ").split() if t]

    # ----- read geometry (strip any *END) -----
    with open(geom_k, "r", encoding="ascii", errors="ignore") as f:
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
    if i_node < 0 or i_elem < 0:
        raise RuntimeError("Malformed geometry keyword: need *NODE and *ELEMENT_SHELL in geometry file")

    # ----- parse nodes -----
    node_recs = lines[i_node+1 : i_elem]
    nodes = {}
    for rec in node_recs:
        tk = toks(rec)
        if len(tk) < 4:
            continue
        nid = int(tk[0]); x = float(tk[1]); y = float(tk[2]); z = float(tk[3])
        nodes[nid] = (x, y, z)
    if not nodes:
        raise RuntimeError("No nodes parsed from geometry file.")

    # ----- parse elements (expect eid, pid, n1, n2, n3, n4) -----
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

    # Build parts only for PIDs that actually appear in elements (+ ensure PCB pid exists)
    all_pids = sorted(pids_in_use | {pcb_pid})
    MID = 1
    SEC_PCB, SEC_COMP = 1, 2

    out = []
    out.append("*KEYWORD")
    out.append("*TITLE")
    out.append("Auto-stitched PCB + components")

    # *MAT_ELASTIC (use comma-separated, include 4 required fields)
    out.append("*MAT_ELASTIC")
    out.append(f"{MID}, {rho:.4E}, {E:.4E}, {nu:.6f}")

    # *SECTION_SHELL for PCB and components (two-line form: header + thickness line)
    out.append("*SECTION_SHELL")
    out.append(f"{SEC_PCB}, 2, 0.8333, 5, 0")
    out.append(f"{pcb_thk:.6f}")
    out.append("*SECTION_SHELL")
    out.append(f"{SEC_COMP}, 2, 0.8333, 5, 0")
    out.append(f"{comp_thk:.6f}")

    # *PART per PID: title line (label OK), then numeric line
    for pid in all_pids:
        secid = SEC_PCB if pid == pcb_pid else SEC_COMP
        out.append("*PART")
        out.append(f"PART_{pid}")
        # pid, secid, mid, eosid, hgid, grav, adpopt, tmid
        out.append(f"{pid}, {secid}, {MID}, 0, 0, 0, 0, 0")

    # *NODE block (comma-separated)
    out.append("*NODE")
    for nid in sorted(nodes):
        x, y, z = nodes[nid]
        out.append(f"{nid}, {x:.6f}, {y:.6f}, {z:.6f}")

    # *ELEMENT_SHELL block (comma-separated)
    out.append("*ELEMENT_SHELL")
    for (eid, pid, n1, n2, n3, n4) in elems:
        out.append(f"{eid}, {pid}, {n1}, {n2}, {n3}, {n4}")

    # minimal controls / output
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

    # quick sanity print of the head (what LS-DYNA will see first)
    with open(out_k, "r", encoding="ascii") as g:
        head = "".join([next(g) for _ in range(24)])
    print("--- board_full.k head ---\n" + head + "-------------------------")
    return out_k


def pydyna_build_and_save(geom_k="board_geom_pids.k",
                          out_local="board_full.k",
                          pid_list=None,
                          pcb_pid=1, pcb_thk=1.6, comp_thk=3.0,
                          E=200, nu=0.30, rho=1.90e-4):

    from ansys.dyna.core.pre import launch_dynapre
    from ansys.dyna.core.pre.dynamech import DynaMech, AnalysisType, ShellPart
    from ansys.dyna.core.pre.dynabase import ShellFormulation
    from ansys.dyna.core.pre.dynamaterial import MatElastic
    import os

    solution = launch_dynapre(ip="localhost")
    solution.open_files([os.path.abspath(geom_k)])

    # minimal controls
    solution.set_termination(termination_time=1.0)
    solution.set_output_database(glstat=1, matsum=1, sleout=0)
    solution.create_database_binary(dt=0)

    model = DynaMech(AnalysisType.NONE)
    solution.add(model)

    mat = MatElastic(mass_density=0, young_modulus=0, poisson_ratio=nu)

    # ensure PCB pid is included
    all_pids = sorted(set([pcb_pid] + (pid_list or [])))

    for pid in all_pids:
        #  no 'title=' here
        part = ShellPart(pid)


        part.set_material(mat)
        part.set_element_formulation(ShellFormulation.BELYTSCHKO_TSAY)
        part.set_integration_points(5)
        part.set_thickness(pcb_thk if pid == pcb_pid else comp_thk)
        model.parts.add(part)

    server_dir  = solution.save_file()
    server_file = "/".join((server_dir, os.path.basename(geom_k)))
    solution.download(server_file, out_local)
    print("Wrote:", os.path.abspath(out_local))
    return os.path.abspath(out_local)

def run_with_pydyna_solver(kfile):

    from ansys.dyna.core.solver import launch_dyna
    import os
    solver = launch_dyna(ip="localhost")
    for api in ("run", "solve", "submit"):
        if hasattr(solver, api):
            fn = getattr(solver, api)
            print(f"Solver.{api} -> {os.path.abspath(kfile)}")
            return fn(os.path.abspath(kfile))
    raise RuntimeError("Could not find a suitable solver run method on the PyDYNA solver object.")


import subprocess, os

def run_local_ls_dyna(kfile,
                      exe=r"C:\Program Files\ANSYS Inc\v252\ansys\bin\winx64\lsprepost413\LS-Run\lsrun.exe",
                      ncpu=2, mem_mb=300000):
    import os, subprocess
    if not os.path.exists(exe):
        raise RuntimeError("Set the correct solver EXE path.")
    cmd = f'"{exe}" i="{kfile}" ncpu={ncpu} memory={mem_mb} jobid=pcb'
    print("Running:", cmd)
    subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(kfile)) or ".", check=True)

# ------------------------ Main Script -------------------------------------
# 1) generate
components, boardWidth, boardHeight = rand(10, 60) #10 components. 60%
mesh(boardWidth, boardHeight, components)       # writes board.k

# 2) geometry with PIDs (no *END)
pid_list = write_geom_with_pids(components,
                                infile="board.k",
                                outfile="board_geom_pids.k",
                                pid_start=2)

# 3) stitch a complete, ordered deck
full_k = stitch_full_keyword_from_geometry_ordered(
    geom_k="board_geom_pids.k",
    out_k="board_full.k",
    pid_list=pid_list,
    pcb_pid=1, pcb_thk=1.6, comp_thk=3.0,
    E=200, nu=0.30, rho=1.90e-4,
    tstop=1.0, d3plot_dt=0.2
)

# 4) run DYNA
run_local_ls_dyna(
    full_k,
    exe=r"C:\Program Files\ANSYS Inc\v252\ansys\bin\winx64\lsprepost413\LS-Run\lsrun.exe",
    ncpu=2, mem_mb=300000
)

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
