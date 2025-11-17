import os, subprocess
def run_dyna_local(kfile,
                      exe=r"file name",
                      ncpu=2, mem_mb=300000):
    if not os.path.exists(exe):
        raise RuntimeError("Set the correct solver EXE path.")
    cmd = f'"{exe}" i="{kfile}" ncpu={ncpu} memory={mem_mb} jobid=pcb'
    print("Running:", cmd)
    subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(kfile)) or ".", check=True)
