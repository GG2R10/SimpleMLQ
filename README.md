# Simulación MLQ - Práctica 1 Sistemas Operativos

**Autor:** Sebastián Calvo Carvajal  
**Código:** 2419118  
**Universidad:** Universidad del Valle

## Descripción
Este repositorio contiene la implementación de un **Multi-Level Queue (MLQ)** con:
- Cola 1: Round Robin (quantum 3)
- Cola 2: Round Robin (quantum 5)
- Cola 3: FCFS

El programa lee un archivo de entrada con procesos y genera un archivo de salida con las métricas de planificación.

## Archivos
- `mlq.py`: código principal del MLQ
- `mlq001.txt`: ejemplo de entrada
- `solved_mlq001.txt`: ejemplo de salida generado
- `README.md`: descripción del proyecto

## Uso
```bash
python mlq.py archivo.txt
