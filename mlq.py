from typing import List, Optional
import sys

# Clase Proceso
# Escencial 
class Proceso:
    def __init__(self, tag, burst_time, arrival_time, queque, priority):
        self.tag = tag
        self.burst_time = burst_time
        self.arrival_time = arrival_time
        self.queque = queque
        self.priority = priority

        self.remaining_time = burst_time
        self.response_time = -1
        self.waiting_time = 0
        self.completion_time = 0
        self.turnaround_time = 0

    def __repr__(self):
        return f"{self.tag}(BT={self.burst_time}, AT={self.arrival_time}, Q={self.queque}, RT={self.remaining_time})"

# Parser para leer y escribir archivos
# Le llamamos parser aunque tambien devuelve el output
class Parser:
    @staticmethod
    def read_file(filename: str) -> List[Proceso]:
        procesos = []
        Parser.original_order = {}  # guardar orden
        with open(filename, "r") as f:
            for index, line in enumerate(f):
                if not line.strip():
                    continue
                tag, bt, at, q, p = line.strip().split(";")
                proceso = Proceso(tag.strip(), int(bt), int(at), int(q), int(p))
                procesos.append(proceso)
                Parser.original_order[proceso.tag] = index
        return procesos

    @staticmethod
    def make_output(filename: str, procesos: List[Proceso]):
        # Ordenar por el orden original del archivo
        procesos_ordenados = sorted(procesos, key=lambda p: Parser.original_order[p.tag])

        with open(filename, "w") as f:
            av_wt = 0
            av_ct = 0
            av_rt = 0
            av_tat = 0
        
            for p in procesos_ordenados:
                av_wt += p.waiting_time
                av_ct += p.completion_time
                av_rt += p.response_time
                av_tat += p.turnaround_time
                
                f.write(f"{p.tag};{p.burst_time};{p.arrival_time};{p.queque};{p.priority};"
                        f"{p.waiting_time};{p.completion_time};{p.response_time};{p.turnaround_time}\n")

            av_wt /= len(procesos_ordenados)
            av_ct /= len(procesos_ordenados)
            av_rt /= len(procesos_ordenados)
            av_tat /= len(procesos_ordenados)

            f.write(f"\nWT={av_wt};CT={av_ct};RT={av_rt};TAT={av_tat}")

# "Interfaz" de Algoritmo de planificación
# :3
class SchedulingAlgorithm:
    def __init__(self, quantum=None):
        self.processes_queue: List[Proceso] = []
        self.time = None
        self.queque_priority = None
        self.quantum = quantum
        self.expropiative = False

    def set_context(self, time_ref: int, queque_priority: int):
        self.time = time_ref
        self.queque_priority = queque_priority

    def set_queue(self, processes_queue: List[Proceso]):
        self.processes_queue = processes_queue

    def update_time(self, time_ref):
        self.time = time_ref

    def execute_tick(self, processes_by_at: List[Proceso]) -> Optional[Proceso]:
        raise NotImplementedError

# Round Robin
# Es una impelentacion de nuestra "interfaz" de schedulingAlgorithm
class RoundRobin(SchedulingAlgorithm):
    def __init__(self, quantum):
        super().__init__(quantum)
        self.expropiative = True

    def execute_tick(self, processes_by_at: List[Proceso]) -> Optional[Proceso]:
        if not self.processes_queue:
            return None

        actual_process = self.processes_queue[0]
        execution_time = self.quantum

        # RT logic
        if actual_process.response_time == -1:
            actual_process.response_time = self.time

        # Arrival logic
        new_arrivals = [p for p in processes_by_at if p.arrival_time <= self.time + self.quantum and p.queque == self.queque_priority]
        for p in new_arrivals:
            self.processes_queue.append(p)
            processes_by_at.remove(p)

        # Execution
        if actual_process.remaining_time <= execution_time:
            self.time += actual_process.remaining_time
            actual_process.remaining_time = 0
            actual_process.completion_time = self.time
            actual_process.turnaround_time = actual_process.completion_time - actual_process.arrival_time
            actual_process.waiting_time = actual_process.turnaround_time - actual_process.burst_time
            self.processes_queue.pop(0)
            return actual_process
        else:
            self.time += execution_time
            actual_process.remaining_time -= execution_time
            self.processes_queue.pop(0)
            self.processes_queue.append(actual_process)
            return None

# FCFS
# Otra implementacion
class FCFS(SchedulingAlgorithm):
    def __init__(self):
        super().__init__()
        self.expropiative = False

    def execute_tick(self, processes_by_at: List[Proceso]) -> Optional[Proceso]:
        if not self.processes_queue:
            return None

        actual_process = self.processes_queue[0]

        if actual_process.response_time == -1:
            actual_process.response_time = self.time

        self.time += actual_process.remaining_time
        actual_process.remaining_time = 0
        actual_process.completion_time = self.time
        actual_process.turnaround_time = actual_process.completion_time - actual_process.arrival_time
        actual_process.waiting_time = actual_process.turnaround_time - actual_process.burst_time

        self.processes_queue.pop(0)
        return actual_process

# Clase QuequeMLQ
# Son las colas de nuestro MLQ
class QuequeMLQ:
    def __init__(self, priority, algorithm: SchedulingAlgorithm, time_ref):
        self.priority = priority
        self.algorithm = algorithm
        self.algorithm.set_context(time_ref, priority)
        self.processes_queue: List[Proceso] = []
        self.algorithm.set_queue(self.processes_queue)

    def add_process(self, proceso: Proceso):
        self.processes_queue.append(proceso)

    def execute_tick(self, processes_by_at: List[Proceso]) -> Optional[Proceso]:
        return self.algorithm.execute_tick(processes_by_at)

    def update_algorithm_time(self, time_ref):
        self.algorithm.update_time(time_ref)
        
# Clase MLQ principal
class MLQ:
    def __init__(self, queues: List[QuequeMLQ], file_in: str):
        self.processes = Parser.read_file(file_in)
        self.processes_by_at = sorted(self.processes, key=lambda x: x.arrival_time)
        self.queues = queues
        self.finished_processes: List[Proceso] = []
        self.time = 0
        self.total = len(self.processes)
        self.filename = file_in

        # Actualizar referencia temporal para cada cola
        for q in self.queues:
            q.algorithm.time = self.time

    def execute(self):
        while len(self.finished_processes) < self.total:
            # Agregar procesos que llegan
            for p in self.processes_by_at[:]:
                if p.arrival_time <= self.time:
                    self.queues[p.queque - 1].add_process(p)
                    self.processes_by_at.remove(p)

            # Ejecutar una cola por tick (MLQ)
            executed = False
            for q in self.queues:
                if q.processes_queue:
                    q.update_algorithm_time(self.time)
                    result = q.execute_tick(self.processes_by_at)
                    self.time = q.algorithm.time  # sincronizar tiempo global
                    if result:
                        self.finished_processes.append(result)
                    executed = True
                    break

            if not executed:
                # Si no hay procesos en ninguna cola, avanzar el tiempo
                self.time += 1

        Parser.make_output("solved_" + self.filename, self.finished_processes)


# Parte de ejecucion 
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python mlq.py <archivo_de_entrada>")
        sys.exit(1)

    archivo = sys.argv[1]

    rr3 = QuequeMLQ(1, RoundRobin(3), 0)
    rr5 = QuequeMLQ(2, RoundRobin(5), 0)
    fcfs = QuequeMLQ(3, FCFS(), 0)

    mlq = MLQ([rr3, rr5, fcfs], archivo)
    mlq.execute()

    print(f"Simulación terminada. Resultados guardados en archivo solved_{archivo} :D")
