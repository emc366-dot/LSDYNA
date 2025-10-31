# %%
def mesh(length=100, height=50):
    nodes = []
    elements = []
    
    # Create nodes
    for i in range(length + 1):
        for j in range(height + 1): 
            nodes.append(f"{(i*(height+1)+j+1):8d}{i*1.0:15.1f}{j*1.0:15.1f}      0.0       0       0")
    
    # Create elements
    for i in range(length):
        for j in range(height):
            n1 = i * (height + 1) + j + 1
            elements.append(f"{(i*height+j+1):8d}       1{n1:8d}{n1+1:8d}{n1+height+2:8d}{n1+height+1:8d}")
    
    # Write file
    with open("simple_mesh.k", "w") as f:
        f.write("*KEYWORD\n*TITLE\nSimple Generated Mesh\n*NODE\n" + 
                "\n".join(nodes) + "\n*ELEMENT_SHELL\n" + 
                "\n".join(elements) + "\n*END")
    

mesh()

# %%
# def mesh(length=10, height=10 ,box_height=1.0):
#     nodes = []
#     elements = []
    
#     # Create nodes
#     for i in range(length + 1):
#         for j in range(height + 1):
#             x = i * 1.0
#             y = j * 1.0
#             z = box_height if (i > 0 and i < length and j > 0 and j < height) else 0.0
#             nodes.append(f"{(i*(height+1)+j+1):8d}{x:15.1f}{y:15.1f}{z:15.1f}       0       0")
    
#     # Create elements
#     for i in range(length):
#         for j in range(height):
#             n1 = i * (height + 1) + j + 1
#             elements.append(f"{(i*height+j+1):8d}       1{n1:8d}{n1+1:8d}{n1+height+2:8d}{n1+height+1:8d}")
    
#     # Write file
#     with open("simple_mesh.k", "w") as f:
#         f.write("*KEYWORD\n*TITLE\nSimple Generated Mesh\n*NODE\n" + 
#                 "\n".join(nodes) + "\n*ELEMENT_SHELL\n" + 
#                 "\n".join(elements) + "\n*END")
    
#     print(f"Created: simple_mesh.k with {len(nodes)} nodes and {len(elements)} elements")

# # Examples:
# mesh(10, 10, 2.0)    # 6x4 mesh with 2.0 height box in middle



