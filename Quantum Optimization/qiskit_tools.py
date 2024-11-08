from qiskit import QuantumRegister, ClassicalRegister, QuantumCircuit, transpile
from qiskit.visualization import circuit_drawer, plot_histogram
from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
import matplotlib.pyplot as plt
from qiskit.primitives import StatevectorSampler
from qiskit_ibm_runtime import SamplerV2 as Sampler
from qiskit_ibm_runtime.fake_provider import FakeKyiv
from qiskit.visualization import plot_histogram

token = "f357e84602c6054693aa4b405885636006fd0814819b4b5be7c2839059ae57b029bdf5092d66b9d84d0878d9daa7ea8f74497eeec41a075c54d59924f03ae020" 
 
def creacion_GHZ(qbits, q_r):
    """
    Esta funcion se encarga de crear una instancia QuantumCircuit con un estado preparado GHZ
    
    INPUT
    qbits: el layout deseado para el GHZ
    q_r: la instancia QuantumRegister a utilizar en el circuito
    
    OUTPUT
    QuantumCircuit con el GHZ
    """
    
    
    c_r = ClassicalRegister(len(qbits))
    c = QuantumCircuit(q_r, c_r)
    c.h(q_r[qbits[0]])

    for i in range(len(qbits) - 1):
        c.cx(q_r[qbits[i]], q_r[qbits[i + 1]])

    for i in range(len(c_r)):
        try:
            c.measure(qbits[i], i)
        except IndexError:
            pass

    return c
    
def enviar_experimento(circuitos, backend, shot):
    
    """
    Esta funcion se encarga de enviar un experimento con optimizacion 0
    
    INPUT
    circuits: instancias QuantumCircuit con los experimentos a enviar
    backend: backend fisico donde se quiere enviar el experimento
    shot: numero de shots para el experimento
    
    OUTPUT
    instancia job con el trabajo enviado
    """
    
    service = QiskitRuntimeService(channel= "ibm_quantum", token=token)
    computador = service.backend(name=backend)
    pm = generate_preset_pass_manager(optimization_level=0, backend=computador)
    transpiled = pm.run(circuitos)
    job = computador.run(transpiled, shots=shot)
    return job
    
def enviar_experimento_layout(circuitos, backend, shot, layout):
    
    """
    Esta funcion se encarga de enviar un experimento con optimizacion 0 y un layout especifico
    
    INPUT
    circuits: instancias QuantumCircuit con los experimentos a enviar
    backend: backend fisico donde se quiere enviar el experimento
    shot: numero de shots para el experimento
    layout: layout a usar
    
    OUTPUT
    instancia job con el trabajo enviado
    """
    
    service = QiskitRuntimeService(channel= "ibm_quantum", token=token)
    computador = service.backend(name=backend)
    pm = generate_preset_pass_manager(optimization_level=0,initial_layout= layout, backend=computador)
    transpiled = pm.run(circuitos)
    job = computador.run(transpiled, shots=shot)

def experimento_GHZ(listas_de_qbits, backend, shots):
    
    """
    Esta funcion se encarga de enviar un experimento GHZ con optimizacion 0
    
    INPUT
    listas_de_qbits: layouts para los experimentos GHZ
    backend:  backend fisico
    shots: numero de shots
    
    OUTPUT
    instancia job con el trabajo enviado
    """
    
    
    max_qbits = 0
    max_len_qbits = 0
    for i in listas_de_qbits:
        if max(i) > max_qbits:
            max_qbits = max(i)
        if max_len_qbits < len(i):
            max_len_qbits = len(i)

    q_r = QuantumRegister(max_qbits + 1, "q")
    circuitos = list()

    for j in listas_de_qbits:
        circuitos.append(creacion_GHZ(j, q_r))
    
    return enviar_experimento(circuitos=circuitos, backend=backend, shot=shots)
    
def experimento_3l(listas_de_qbits, backend, shots):
    
    """
    Esta funcion se encarga de enviar un experimento 3 layer state con optimizacion 0
    
    INPUT
    listas_de_qbits: layouts para los experimentos 3 layer
    backend:  backend fisico
    shots: numero de shots
    
    OUTPUT
    instancia job con el trabajo enviado
    """
    
    max_qbits = 0
    max_len_qbits = 0
    for i in listas_de_qbits:
        if max(i) > max_qbits:
            max_qbits = max(i)
        if max_len_qbits < len(i):
            max_len_qbits = len(i)

    q_r = QuantumRegister(max_qbits + 1, "q")
    circuitos = list()

    for j in listas_de_qbits:
        circuitos.append(state_3layers(len(j), j, q_r))

    return enviar_experimento(circuitos=circuitos, backend=backend, shot=shots)

def state_3layers(nq, layout, qr):
    """
    Generates a quantum circuit for an entangled state with 3 gates layers.
    The output state is equivalent to a 1-dimensional Cluster State.
    
    Input:
        nq: qubit number
        layout: the layout of the experiment
        qr: QuantumRegister of the experiment
        
    Output:
        qc: quantum circuit 
    """
    cr=ClassicalRegister(nq,'cr')
    qc=QuantumCircuit(qr,cr)
    
    if nq%2==0: 
        #Si el numero de qubits es par, 
        #se coloca una primera capa de puertas raiz de X a todos los qubits
        for i in layout:
            qc.sx(int(i))
    else:
        #Si el numero de qubits es impar, 
        #se coloca una primera capa de puertas raiz de X a todos los qubits salvo el último
        #al último qubit se la aplica una puerta X.
        for i in range(len(layout) - 1):
            qc.sx(layout[i])
        qc.x(layout[-1])
        
    for i in range(0,len(layout) - 1,2): #Primera capa de puertas ECR, van desde el qubit j->j+1 para j impar.
        qc.ecr(layout[i],layout[i + 1])
        
    for i in range(1,len(layout) - 1,2): #Segunda capa de puertas ECR, van desde el qubit j->j+1 para j par.    
        qc.ecr(layout[i],layout[i + 1]) 
    #Todas las puertas ECR van en la misma dirección. 
    
    qc.sx(layout[0]) #Se aplica una puerta raiz de X al qubit 0
    
    for i in range(len(layout)):
        qc.measure(layout[i], i)
        
        
    return qc

def Fake_experimento_GHZ(layouts, backend, shots):
    
    """
    Esta funcion se encarga de enviar un experimento GHZ con optimizacion 0 a un FakeBackend
    
    INPUT
    layouts: los layouts de los experimentos GHZ
    backend: el fake backend 
    shots: numero de shots del experimento
    
    OUTPUT
    resultados del experimento EN CONSTRUCCION
    """
    
    max_qbits = 0
    max_len_qbits = 0
    for i in layouts:
        if max(i) > max_qbits:
            max_qbits = max(i)
        if max_len_qbits < len(i):
            max_len_qbits = len(i)

    q_r = QuantumRegister(max_qbits + 1, "q")
    circuitos = list()
    
    for j in layouts:
        circuitos.append(creacion_GHZ(j, q_r))
        
    pm = generate_preset_pass_manager(backend=backend, optimization_level=0)
    job = pm.run(circuitos)
    sampler = Sampler(backend=backend)
    result = sampler.run([job], shots=shots).result()
    return result


if __name__ == "__main__":
    #qbits = [[47, 48, 49, 55, 68, 69, 70, 74, 89, 88, 87, 93, 106, 105, 104, 103]]
    qbits = [0, 1, 2, 3, 4, 5, 6, 7]
    computador = "ibm_brisbane"
    q_r = QuantumRegister(8, "q")
    #c_r = ClassicalRegister(9, "c")
    qc = creacion_GHZ(qbits, q_r)
    backend = FakeKyiv()
    transpiled_circuit = transpile(qc, backend)
    backend = FakeKyiv()
    #pm = generate_preset_pass_manager(backend=fake_manila, optimization_level=0)
    #isa_qc = pm.run(qc)
    #result = isa_qc.result()
    
    sampler = Sampler(backend)
    job = sampler.run([transpiled_circuit], shots=1000)
    pub_result = job.result[0].data.counts[0].data
    plot_histogram(pub_result)
    plt.show()
    #qc.draw("text")
    #experimento(qbits, backend=computador, shots=20000)