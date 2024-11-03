from itertools import combinations
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def abrir_datos_g(ruta, indices, direccionado):
    """
    Esta funcion se encarga de abrir los datos desde el archivo csv y transformarlo en un grafo
    inputs
    ruta: nombre del archivo
    indices: errores a considerar
    direccionado: True si es direccionado y False si es no direccionado
    se recomienda implementar el direccionado para todo circuito que utilice ecr gates
    output
    grafo
    """
    
    
    #Ruta del archivo CSV
    # Definir una lista vacía para almacenar los datos por fila
    datos_por_fila = []
    ruta_archivo_csv = ruta  # Cambia esto por la ruta de tu archivo CSV

    try:
        # Abrir el archivo CSV en modo lectura
        with open(ruta_archivo_csv, 'r') as archivo:
            # Iterar sobre cada línea del archivo
            for linea in archivo:
                # Dividir la línea en campos separados por comas
                campos = linea.strip().split(',')
                
                # Agregar los campos a la lista de datos por fila
                datos_por_fila.append(campos)
                
    except FileNotFoundError:
        print("El archivo no fue encontrado.")
    except Exception as e:
        print("Ocurrió un error:", e)

    datos_por_fila.pop(0)
    #TERMINA LA EXTRACCION DE DATOS DEL ARCHIVO
    #COMIENZA LA CREACION DEL GRAFO


    if direccionado:
        grafo = nx.DiGraph()
    else:
        grafo = nx.Graph()

    for linea in datos_por_fila:
        #breakpoint()
        QBIT = int(linea[0].strip('"'))
        ECR_error = linea[13]
        REA_error = float(linea[5].strip('"'))
        RZ_error = float(linea[10].strip('"'))
        SX_error = float(linea[11].strip('"'))
        X_error = float(linea[12].strip('"'))
        P_false = (float(linea[6].strip('"')) + float(linea[7].strip('"')))/10
        ECR_error = ECR_error.replace('"', "")
        ECR_error = ECR_error.split(";")

        v_error = [REA_error, RZ_error, SX_error, X_error]
            
        v_reducido = []
        if P_false > 0.4:
            v_reducido.append(1)
        else:
            pass

        for i in indices:
            if i != 0:
                v_reducido.append(v_error[int(i) - i])
            else:
                pass

        grafo.add_node(QBIT, weight = np.linalg.norm(v_reducido))
        
        for conexion in range(len(ECR_error)):
            ECR_error[conexion] = ECR_error[conexion].split(":")
            ECR_error[conexion][0] = ECR_error[conexion][0].split("_") 
            if ECR_error[conexion] != [[""]]:
                Inicio = int(ECR_error[conexion][0][0])
                Fin = int(ECR_error[conexion][0][1])
                error_conexion = float(ECR_error[conexion][1])
                if 0 in indices:
                    grafo.add_edge(Inicio, Fin, Weight = error_conexion)
                else:
                    grafo.add_edge(Inicio, Fin, Weight = 0)

                
    return grafo

def agregar_qubit(norma, q_bits, matrix):
    min_norm = 1000
    min_pos = ()

    #posibilidad_1
    posibilidades = list(range(127))

    for i in posibilidades:

        pos_1 = [i] + list(q_bits)
        e_1 = []

        for j in range(len(pos_1) - 1):
            e_1.append(matrix[pos_1[j]][pos_1[j + 1]])

        if 1 in e_1:
            pass
            
        elif np.linalg.norm(e_1) <= np.linalg.norm(min_norm) and len(pos_1) == len(set(pos_1)):
            min_pos = tuple(pos_1)
            min_norm = np.linalg.norm(e_1)

    #posibilidad 2
            
    for i in posibilidades:

        pos_2 = list(q_bits) + [i]
        e_2 = []

        for j in range(len(pos_2) - 1):
            e_2.append(matrix[pos_2[j]][pos_2[j + 1]])

        if 1 in e_2:
            pass
            
        elif np.linalg.norm(e_2) <= np.linalg.norm(min_norm) and len(pos_2) == len(set(pos_2)):
            min_pos = tuple(pos_2)
            min_norm = np.linalg.norm(e_2)



    print(f"para {len(min_pos)} qubits el vector con menor error es {min_pos}, con norma {min_norm}")

    return list((min_pos, min_norm))

def dfs(graph, node, depth, target_depth, visited=None, path=None, results=None):
    if visited is None:
        visited = set()
    if path is None:
        path = []
    if results is None:
        results = []
    
    visited.add(node)
    path.append(node)
    
    if depth == target_depth:
        results.append(path[:])
    elif depth < target_depth:
        for neighbor, _ in graph[node]:
            if neighbor not in visited:
                dfs(graph, neighbor, depth + 1, target_depth, visited.copy(), path, results)
    
    path.pop()
    visited.remove(node)

def find_node_pairs_at_distance(graph, distance):
    results = []
    for node in graph:
        dfs(graph, node, 0, distance, results=results)
    return results

def calcular_distancia_recorrido(graph, recorrido):
    distancia_total = 0
    for i in range(len(recorrido) - 1):
        nodo_actual = recorrido[i]
        nodo_siguiente = recorrido[i + 1]
        for vecino, distancia in graph[nodo_actual]:
            if vecino == nodo_siguiente:
                distancia_total += distancia
                break
    return distancia_total

def Qubits_optimos_g(graph, distance):
    distance = distance - 1
    error_min = 100
    qbits = tuple()
    pairs_at_distance = find_node_pairs_at_distance(graph, distance)
    #"print("Pares de nodos a una distancia de", distance, "nodos entre ellos:")
    for pair in pairs_at_distance:
        #print(pair)
        error = calcular_distancia_recorrido(graph, pair)
        if error < error_min:
            error_min = error
            qbits = pair

    print(f"para {distance + 1}, el conjunto es {qbits}, {error_min}")
    return [qbits, error_min]

def find_paths_of_length_n(G, start_node, n):
    def dfs(current_node, path):
        if len(path) == n + 1:  # +1 porque el path incluye el nodo inicial
            paths.append(path)
            return
        for neighbor in G.neighbors(current_node):
            if neighbor not in path:  # Evitar ciclos simples
                dfs(neighbor, path + [neighbor])

    paths = []
    dfs(start_node, [start_node])
    return paths

def calculate_path_length(G, path):
    weights = []
    
    # Agregar los pesos de los nodos en el camino
    for node in path:
        if 'weight' in G.nodes[node]:
            weights.append(G.nodes[node]['weight'])
    
    # Agregar los pesos de las aristas en el camino
    for i in range(len(path) - 1):
        edge = (path[i], path[i + 1])
        if G.edges[edge] != 0:
            weights.append(G.edges[edge]["Weight"])
    
    return np.linalg.norm(weights)

def qbits_optimos_g2(G, n):
    error_min = 1000
    camino_emin = [""]
    for nodo in G.nodes:
        caminos = find_paths_of_length_n(G, nodo, n)
        for camino in caminos:
            error = calculate_path_length(G, camino)
            if error < error_min:
                error_min = error
                camino_emin = camino
    
    print(f"para {n} qbits, {camino_emin}, {error_min}")
    return camino_emin

def calcular_error(qbits: list, backend: str):
    """
    Esta funcion calcula el error de una cadena en especifico de qbits
    Input 
    qbits: Lista de qbits en cuestion
    backend: Backend a calcular el error
    Output
    Error especifico de esos qbits
    """
    error_sx = list()
    error_ecr = list()
    import csv
    with open(f'{backend}.csv', mode='r') as archivo:
        lector = csv.reader(archivo)
        
        for linea in lector:
            if linea:
                try:
                    n_qbit = linea[0]
                    if int(n_qbit) in qbits:
                        #print(linea)
                        #print(linea[0])
                        error_sx.append(linea[11])
                        """
                        Falta agregar el error de ECR, aunque si victor trabaja con grafo
                        mejor trabajar la funcion como un grafo
                        """
                        ECR_error = linea[13]
                        ECR_error = ECR_error.split(";")       
                except ValueError:
                    pass
    #print(f"{np.linalg.norm(error_sx)}")
    return np.linalg.norm(error_sx)

def cadena_optima(subconjuntos: list, backend:str):
    """
    Esta funcion debe de una lista de cadenas de qbits de un mismo tamaño,
    retornar la cadena que tenga menor error
    Input: lista de subconjunto de qbits. backend
    Output: qbits con menor error y el error
    """
    error_min = 1000
    cadena_optima = []
    
    for cadena in subconjuntos:
        if calcular_error(cadena, backend) <= error_min:
            error_min = calcular_error(cadena, backend)
            cadena_optima = cadena
    print(f"para {len(cadena_optima)} qbits, {cadena_optima}, {error_min}")
    return cadena_optima

def bfs(grafo, nodo, M):
    queue = [(nodo, [nodo])]
    resultados = []
    while queue:
        actual, camino = queue.pop(0)
        if len(camino) == M:
            resultados.append(camino)
        elif len(camino) < M:
            for vecino in grafo.successors(actual):
                if vecino not in camino:
                    queue.append((vecino, camino + [vecino]))
    return resultados

def encontrar_subconjuntos_bfs(grafo, M):
    m = M
    subconjuntos_conectados = []
    for nodo in grafo.nodes():
        subconjuntos = bfs(grafo, nodo, M)
        subconjuntos_conectados.extend(subconjuntos)
        
        
    while len(subconjuntos_conectados) == 0:
        for nodo in grafo.nodes():
            subconjuntos = bfs(grafo, nodo, m - 1)
            subconjuntos_conectados.extend(subconjuntos)
        m -= 1
        
    while len(subconjuntos_conectados[0]) != M:
        for i in range(len(subconjuntos_conectados)):
            subconjuntos_conectados[i] = agregar_qbit_grafo(grafo, subconjuntos_conectados[i])
        
    return subconjuntos_conectados
    
def agregar_qbit_grafo(G, lista: list):
    print("No direccionado")
    """
    Desde un grafo direccionado, considera un subconjunto de qbits "lista, se añade
    un qbit al inicio o al final sin considerar las direcciones del gardo
    
    :param G: Grado dirigido(nx.DiGrapg)
    :param lista: subconjunto de los nombres de los nodos en una misma direccion
    :return Optimo: lista con 1 nodo mas que representa el menor error
    """
    Inicio, Fin = lista[0], lista[-1]
    G = nx.Graph(G)
    Optimo = None
    no_nodes = None
    
    for nodo in G.neighbors(Inicio):
        if nodo not in lista:
            Optimo_1 = [nodo] + lista
        else:
            no_nodes = True
            
    for nodo in G.neighbors(Fin):
        if nodo not in lista:
            Optimo_2 = lista + [nodo]
        else:
            Optimo = Optimo_1
            
    if no_nodes and Optimo == None:
        Optimo = Optimo_2
    
    if Optimo == None:        
        largo_1 = calculate_path_length(G, Optimo_1)
        largo_2 = calculate_path_length(G, Optimo_2)
        if largo_1 > largo_2:
            Optimo = Optimo_1
        else:
            Optimo = Optimo_2
            
    return Optimo
            
def get_connected_nodes(G, node):
    """
    Devuelve un conjunto de nodos que tienen una conexión con el nodo dado en un grafo dirigido, 
    independientemente de la dirección de la conexión.
    
    :param G: Grafo dirigido (nx.DiGraph)
    :param node: Nodo del que se buscan las conexiones
    :return: Conjunto de nodos conectados al nodo dado
    """
    # Obtener predecesores (nodos que apuntan al nodo dado)
    predecessors = set(G.predecessors(node))
    
    # Obtener sucesores (nodos a los que apunta el nodo dado)
    successors = set(G.successors(node))
    
    # Unir ambos conjuntos
    connected_nodes = predecessors.union(successors)
    
    return connected_nodes
   
def shortest_path_undirected(G, node1, node2):
    """
    Calcula la distancia más corta entre dos nodos en un grafo dirigido,
    sin tener en cuenta la dirección de las aristas.
    
    :param G: Grafo dirigido (nx.DiGraph)
    :param node1: Nodo de inicio
    :param node2: Nodo de destino
    :return: Longitud del camino más corto entre node1 y node2
    """
    # Convertir el grafo dirigido en un grafo no dirigido
    undirected_G = G.to_undirected()
    
    # Calcular la distancia más corta en el grafo no dirigido
    distance = nx.shortest_path_length(undirected_G, source=node1, target=node2)
    
    return distance 

if __name__ == "__main__":
    G = abrir_datos_g("ibm_sherbrooke.csv", (0,3), direccionado=True)
    
    ideal_path = cadena_optima(encontrar_subconjuntos_bfs(G, 13), "ibm_sherbrooke")
    #print(ideal_path)
    #pos = nx.spring_layout(G, k=0.15, iterations=30)
    #nx.draw(G, pos, with_labels=True, node_size=200, node_color='skyblue', font_size=8, font_weight='bold', arrows=True)
    #plt.title("Grafo Dirigido")
    #plt.show()
    
    

        