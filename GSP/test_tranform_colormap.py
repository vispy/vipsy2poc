# -----------------------------------------------------------------------------
# Graphic Server Protocol (GSP) — reference implementation
# Copyright 2022 Nicolas P. Rougier - BSD 2 Clauses licence
# -----------------------------------------------------------------------------
import GSP
import numpy as np
from array import Array
from transform_colormap import TransformColormap

if __name__ == '__main__':

    GSP.mode("client", reset=True, output=False)
    # ------------------------------------------
    values = Array.from_numpy(np.linspace(0, 1, 10, dtype=np.float32))
    colormap = "Viridis"
    TransformColormap(values, colormap)
    client_objects = GSP.objects()
    
    GSP.mode("server", reset=True)
    # ------------------------------------------
    for command in GSP.commands():
        GSP.process(command, globals(), locals())
    server_objects = GSP.objects()

    print(f"Client: {client_objects}")
    print(f"Server: {server_objects}")
    print(f"Test result: {client_objects == server_objects}")

