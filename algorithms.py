class Process:
    def __init__(self, pid, arrival, burst, priority=0):
        self.pid = pid
        self.arrival = arrival
        self.burst = burst
        self.remaining = burst
        self.priority = priority
        self.waiting = 0
        self.turnaround = 0

def fcfs(processes):
    processes.sort(key=lambda x: x.arrival)
    time = 0
    schedule = []
    for p in processes:
        start = max(time, p.arrival)
        end = start + p.burst
        schedule.append({'pid': p.pid, 'start': start, 'end': end})
        p.waiting = start - p.arrival
        p.turnaround = end - p.arrival
        time = end
    return schedule, processes

def sjf(processes):
    ready = []
    schedule = []
    time = 0
    processes.sort(key=lambda p: p.arrival)
    i = 0
    while i < len(processes) or ready:
        while i < len(processes) and processes[i].arrival <= time:
            ready.append(processes[i])
            i += 1
        if ready:
            ready.sort(key=lambda p: p.burst)
            p = ready.pop(0)
            start = time
            end = time + p.burst
            schedule.append({'pid': p.pid, 'start': start, 'end': end})
            p.waiting = start - p.arrival
            p.turnaround = end - p.arrival
            time = end
        else:
            time = processes[i].arrival
    return schedule, processes

def priority_scheduling(processes):
    ready = []
    schedule = []
    time = 0
    processes.sort(key=lambda p: p.arrival)
    i = 0
    while i < len(processes) or ready:
        while i < len(processes) and processes[i].arrival <= time:
            ready.append(processes[i])
            i += 1
        if ready:
            ready.sort(key=lambda p: p.priority)
            p = ready.pop(0)
            start = time
            end = time + p.burst
            schedule.append({'pid': p.pid, 'start': start, 'end': end})
            p.waiting = start - p.arrival
            p.turnaround = end - p.arrival
            time = end
        else:
            time = processes[i].arrival
    return schedule, processes

def round_robin(processes, quantum):
    time = 0
    queue = sorted(processes, key=lambda p: p.arrival)
    schedule = []
    waiting_queue = []
    i = 0
    while i < len(queue) or waiting_queue:
        while i < len(queue) and queue[i].arrival <= time:
            waiting_queue.append(queue[i])
            i += 1
        if not waiting_queue:
            time = queue[i].arrival
            continue
        p = waiting_queue.pop(0)
        exec_time = min(quantum, p.remaining)
        start = time
        end = time + exec_time
        schedule.append({'pid': p.pid, 'start': start, 'end': end})
        p.remaining -= exec_time
        time += exec_time
        while i < len(queue) and queue[i].arrival <= time:
            waiting_queue.append(queue[i])
            i += 1
        if p.remaining > 0:
            waiting_queue.append(p)
        else:
            p.turnaround = time - p.arrival
            p.waiting = p.turnaround - p.burst
    return schedule, processes
