import networkx as nx
import numpy as np

def abrir_datos_g(ruta, indices, direccionado):
    """
    Esta funcion se encarga de abrir los datos desde el archivo csv y transformarlo en un grafo
    inputs
    ruta: nombre del archivo
    indices: errores a considerar
    direccionado: True si es direccionado y False si es no direccionado
    se recomienda implementar el direccionado para todo circuito que utilice ecr gates
    output:
    grafo
    """
    
    datos_por_fila = []
    ruta_archivo_csv = f"Quantum Optimization\Data\{ruta}"
    print(ruta_archivo_csv)

    

    try:
        with open(ruta_archivo_csv, 'r') as archivo:
            for linea in archivo:

                campos = linea.strip().split(',')
                
                datos_por_fila.append(campos)
                
    except FileNotFoundError:
        print("El archivo no fue encontrado.")
    except Exception as e:
        print("Ocurrió un error:", e)

    datos_por_fila.pop(0)


    if direccionado:
        grafo = nx.DiGraph()
    else:
        grafo = nx.Graph()

    for linea in datos_por_fila:
        #breakpoint()
        QBIT = int(linea[0].strip('"'))
        REA_error = float(linea[5].strip('"'))
        RZ_error = float(linea[10].strip('"'))
        SX_error = float(linea[11].strip('"'))
        X_error = float(linea[12].strip('"'))
        P_false = float(linea[6].strip('"')) + float(linea[7].strip('"'))
        ECR_error = linea[13]
        ECR_error = ECR_error.replace('"', "")
        ECR_error = ECR_error.split(";")

        v_error = ["ecr", REA_error, RZ_error, SX_error, X_error, "Anharmonicity", "Frequency"]
            
        v_reducido = []
        if P_false > 0.5:
            v_reducido.append(1)
        else:
            pass

        for i in indices:
            if i != 0 and i != 5 and i !=6:
                v_reducido.append(v_error[i])
            else:
                pass

        grafo.add_node(QBIT, weight = np.linalg.norm(v_reducido))
        
        for conexion in range(len(ECR_error)):
            ECR_error[conexion] = ECR_error[conexion].split(":")
            ECR_error[conexion][0] = ECR_error[conexion][0].split("_") 
            if ECR_error[conexion] != [[""]]:
                Inicio = int(ECR_error[conexion][0][0])
                Fin = int(ECR_error[conexion][0][1])
                A_I = float(datos_por_fila[Inicio][4].strip('"'))
                A_F = float(datos_por_fila[Fin][4].strip('"'))
                
                if A_F == 0 and A_I ==0:
                    A_F = 0.01
                    A_I = 0.009
                elif A_F == 0 or A_I == 0:
                    A_F = A_I + 0.001
                    
                A_conexion = abs(1/(A_I - A_F))
                
                F_I = float(datos_por_fila[Inicio][3].strip('"'))
                F_F = float(datos_por_fila[Fin][3].strip('"'))
                F_conexion = abs(1/(F_I - F_F))
                
                ecr = ECR_error[conexion][1]
                
                error_conexion = list()
                
                #print(f"conexion {Inicio} -> {Fin}, error {ecr}")

                if 0 in indices:
                    error_conexion.append(ecr)
                if 5 in indices:
                    error_conexion.append(A_conexion)
                if 6 in indices:
                    error_conexion.append(F_conexion)
                
                grafo.add_edge(Inicio, Fin, weight = np.linalg.norm(error_conexion), length = 1)
    return grafo

def caminos_a_distancia_especifica(G, nodo_inicial, distancia_objetivo):
    # Calcular las distancias y los caminos más cortos desde el nodo_inicial
    distancias, caminos = nx.single_source_dijkstra(G, nodo_inicial, weight="length")
    
    # Filtrar y devolver los caminos cuyos nodos están a la distancia exacta especificada
    caminos_en_distancia = {}
    for nodo, camino in caminos.items():
        if distancias[nodo] == distancia_objetivo:
            caminos_en_distancia[nodo] = camino  # Guardar el camino completo

    return list(caminos_en_distancia.values())

def peso_del_camino(G, camino):
    peso_total = 0
    
    # Sumar los pesos de las aristas que componen el camino
    for i in range(len(camino) - 1):
        nodo_a = camino[i]
        nodo_b = camino[i + 1]
        peso_total += G[nodo_a][nodo_b]['weight']  # Acceder al peso de la arista
        peso_total += G.nodes[nodo_a]['weight'] 
        peso_total += G.nodes[nodo_b]['weight'] 
        

    return peso_total

def camino_min(G, distancia):
    dis_min = 100
    camino_min = []
    for node in G.nodes():
        caminos = caminos_a_distancia_especifica(G, node, distancia - 1)
        for camino in caminos:
            peso = peso_del_camino(G, camino)
            if peso <= dis_min:
                dis_min = peso
                camino_min = camino
    print(f"para {distancia} qbits, {camino_min}, {dis_min}")
    return camino_min

def Algoritmo(backend: str, Indices: list, n_q: int, N_Q: int, Direccionado: bool):
    G = abrir_datos_g(f"{backend}.csv", Indices, Direccionado)
    
    layouts=[]
    for distancia in range(n_q, N_Q + 1):
        layouts.append(camino_min(G, distancia))
    
    return layouts
    
if __name__ == "__main__":
    
    layouts = Algoritmo("ibm_kyiv", [1], 2, 10, Direccionado=True)
    
    
            
    
    