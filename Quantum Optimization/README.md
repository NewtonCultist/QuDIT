# Quantum Optimization

## El algoritmo cumple la funcion de:
-apartir de un csv con la informacion de errores del backend IBM, encontrar un subconjunto de n qbits que esten conectados entre si y minimicen uno o varios errores. Ademas, se puede pedir que este sea Direccionado


## El algoritmo cuenta con 5 archivos archivos:

1. :white_check_mark: *graph_theory.py*: Archivo py que contiene funciones varias entorno a grafos. 
2. :white_check_mark: *qiskit_tools.py*: Archivo py que contiene funciones encargadas de comunicarse con los computadores cuanticos via Qiskit
3. :wrench: *simulator.ipynb*: EN PROGRESO codigo que realiza el mismo experimento pero en el Fake Backend
4. :white_check_mark: *main_graph.ipynb*: Codigo principal, corre el algoritmo, corre controles de optimizacion 0 y 3 y finalmente recopila la informacion calculando las distancias de hellinger en contra del 3 layer state graficando los resultados

# **IMPORTANTE**

-Cambiar el token en qiskit tools

-Cambiar el job_id manualmente en main_graph

-Actualizar la Data antes de cualquier iteraicon en [Quantum IBM](https://quantum.ibm.com/)