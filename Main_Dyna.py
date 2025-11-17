import numpy as np



import os, sys, subprocess
from Build_Base import rand, plot, mesh
from run import run_dyna_local
from Key_Param import  build_full_keyword, assemble_PIDs

os.environ["PATH"] = os.path.dirname(sys.executable) + os.pathsep + os.environ.get("PATH","")

# ------------------- PyDYNA local run  -------------------
"""
    Builds a Keyword model for a PCB board in 4 steps: 

    1). Imports meshing and randomized values for board geometry.

    2). Takes the base board.k file and reorganizes it to 
        have readable Part IDs (PIDs) for a usable keyword file.

    3). Builds the keyword deck, assigining material properties
        and keyword required components

    4). Run the LS-Dyna Model
"""

# 1) Build Base Model Board.k
components, boardWidth, boardHeight = rand(10, 60)
mesh(boardWidth, boardHeight, components)   

# 2) Call for Assembly of PIDs
assemble_PIDs(components, infile="board.k", outfile="board.k",
                         pid_start=2)

# 3) Build a complete keyword deck
full_k = build_full_keyword(
    geom_k="board.k",
    out_k="board_full.k",
    pcb_pid=1, pcb_thk=1.6, comp_thk=3.0,
    E=200, nu=0.30, rho=100,
    tstop=1.0, d3plot_dt=0.2
)

# 4) run DYNA (locally)
run_dyna_local(
    full_k,
    exe=r"C:\Program Files\ANSYS Inc\v252\ansys\bin\winx64\LSDYNA.exe",

    #Use this line to open up LS-Dyna Application, otherwise run in command window 
    # exe=r"C:\Program Files\ANSYS Inc\v252\ansys\bin\winx64\lsprepost413\LS-Run\lsrun.exe"
    
    ncpu=2, mem_mb=300000
)