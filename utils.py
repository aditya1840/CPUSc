from .algorithms import Process

def parse_input(text):
    lines = text.strip().split('\n')
    processes = []
    for idx, line in enumerate(lines):
        parts = list(map(int, line.replace(',', ' ').split()))
        if len(parts) == 3:
            arrival, burst, priority = parts
        elif len(parts) == 2:
            arrival, burst = parts
            priority = 0
        else:
            raise ValueError("Each line must have 2 or 3 integers")
        processes.append(Process(idx, arrival, burst, priority))
    return processes

def compute_metrics(processes):
    total_wait = sum(p.waiting for p in processes)
    total_turn = sum(p.turnaround for p in processes)
    n = len(processes)
    avg_wait = total_wait / n
    avg_turn = total_turn / n
    end_time = max(p.arrival + p.turnaround for p in processes)
    total_burst = sum(p.burst for p in processes)
    utilization = (total_burst / end_time) * 100
    throughput = n / end_time
    return avg_wait, avg_turn, utilization, throughput
