# CS 140 24.1 Project 1
# Submitted by:
# Purisima, Gabbie (THR/FUV)
# Ramos, Nico Sebastian (THR/FQR)
# Sapitula, Nina Patricia (THR/FQR)
# Sopungco, Andrew (THR/FQR)

# ================================================================ LIBRARIES AND CLASS ================================================================
from collections import deque                   # Importing deque for queue management

# Class representing a process with attributes like name, arrival time, operations, and states
class proc:
    def __init__(self, name, arrival, operations, op_marker, q1_quota, q2_quota, in_q1, in_q2, in_q3, in_io, turnaround, waiting):
        self.name = name                                                            # Process name
        self.arrival = arrival                                                      # Arrival time of the process
        self.operations = operations                                                # List of CPU and I/O burst times
        self.op_marker = op_marker                                                  # Current operation index
        self.q1_quota = q1_quota                                                    # Time used in Q1
        self.q2_quota = q2_quota                                                    # Time used in Q2
        self.in_q1 = in_q1                                                          # Boolean whether the process is in Q1
        self.in_q2 = in_q2                                                          # Boolean whether the process is in Q2
        self.in_q3 = in_q3                                                          # Boolean whether the process is in Q3
        self.in_io = in_io                                                          # Time when the process started I/O
        self.turnaround = turnaround                                                # Turnaround time of the process
        self.waiting = 0                                                            # Waiting time of the process
        self.completion_time = 0                                                    # Completion time of the process
        self.cpu_time = 0                                                           # Total CPU time used by the process
        self.io_time = 0                                                            # Total IO time used by the process
        self.pending_demotion = False                                               # Flag to track pending demotions
        self.demotion_target = None                                                 # Attribute to track where to demote to
        self.entered_io = False                                                     # Check if the process just entered I/O

    def __str__(self):                                  
        return self.name                                                            # String representation of the process

    def __repr__(self):                                 
        return self.name                                                            # Representation of the process in lists

# Function to create a process object from user input
def make_proc(input_details):
    return proc(input_details[0], int(input_details[1]), [int(x) for x in input_details[2:]], 0, 0, 0, 0, 0, 0, 0, 0, 0)

# Function for handling I/O operations
def handle_io(ticks):
    completed_io = []                                                               # List to store processes that complete I/O

    if io:                                                                          # Print current I/O queue
        print(f"I/O: {io}")

    for p in io[:]:                                                                 # Iterate over a copy of the I/O queue
        p.operations[p.op_marker] -= 1                                              # Decrement the remaining I/O burst time
        p.io_time += 1                                                              # Increment the process's I/O time

        if p.operations[p.op_marker] == 0:                                          # Check if I/O operation is complete
            io.remove(p)                                                            # Remove process from I/O queue
            p.op_marker += 1                                                        # Move to the next operation

            if p.op_marker >= len(p.operations):                                    # If no more operations remain
                p.completion_time = ticks + 1                                       # Set completion time
                donep_for_printing.append(p)                                        # Mark process as done
            else:
                # Reset time allotment when returning from I/O
                if p.in_q1:
                    p.q1_quota = 0
                    q1.append(p)                                                    # Add process back to Q1
                elif p.in_q2:
                    p.q2_quota = 0
                    q2.append(p)                                                    # Add process back to Q2
                else:
                    q3.append(p)                                                    # Add process back to Q3

                completed_io.append(p)                                              # Add to completed I/O list

    return completed_io                                                             # Return processes that completed I/O

# Function for handling context switching
def handle_context_switch(context_switch_remaining, ticks, demoted_process):
    if context_switch_remaining > 0:                                                # Check if a context switch is ongoing

        if demoted_process:                                                         # Handle demoted process
            current_proc = demoted_process.pop(0)                                   # Get the process to demote
            if current_proc.demotion_target == "Q2":
                print(f"{current_proc} DEMOTED TO Q2")
            elif current_proc.demotion_target == "Q3":
                print(f"{current_proc} DEMOTED TO Q3")
            elif current_proc.demotion_target == "Q1":
                print(f"{current_proc} QUANTUM FINISHED - BACK TO Q1")
            current_proc.pending_demotion = False                                   # Clear demotion flags
            current_proc.demotion_target = None

        context_switch_remaining -= 1                                               # Decrease context switch timer
        print(f"Context switching... {context_switch_remaining} ticks left")
        return context_switch_remaining, ticks + 1, True                            # Indicate a skipped tick

    return context_switch_remaining, ticks, False                                   # No context switch ongoing

# Function to sort Q3 queue using SJF (Shortest Job First)
def sort_sjf_queue():
    global q3                                                                       # Use global variable for Q3 queue
    q3_list = list(q3)                                                              # Convert deque to list for sorting
    q3_list.sort(key=lambda x: x.operations[x.op_marker])                           # Sort by current CPU burst
    q3 = deque(q3_list)                                                             # Convert back to deque

# ================================================================ SCHEDULER DETAILS ================================================================
# Scheduler Details Input Section
print("# Enter Scheduler Details #")
proc_num = int(input())                                                             # Number of processes
q1_allotment = int(input())                                                         # Time allotment for Q1
q2_allotment = int(input())                                                         # Time allotment for Q2
cswitch = int(input())                                                              # Context switch time
# ================================================================ PROCESS DETAILS ================================================================
# Process Details Input Section
print(f"# Enter {proc_num} Process Details #")
processes = []
for _ in range(proc_num):
    temp = make_proc(input().split(";"))                                            # Parse and create process objects
    processes.append(temp)
print(processes)
# ================================================================ SCHEDULE PROPER ================================================================
# Scheduler Initialization
ticks = 0                                                                           # Simulation time ticks
q1_rr_quantum = 4                                                                   # Quantum for Round Robin in Q1 (Set to 4ms according to the Project Specs)
q1, q2, q3 = deque(), deque(), deque()                                              # Queues for different priority levels
io = []                                                                             # List of processes in I/O
cpu = []                                                                            # Current process in CPU
context_switch_remaining = 0                                                        # Remaining time for context switch
current_quantum = 0                                                                 # Remaining quantum for the CPU process
completed_processes = []                                                            # List of completed processes
donep_for_printing = []                                                             # List of processes marked as done for reporting
process_complete = False                                                            # Flag indicating the completion of all processes
demoted_process = []                                                                # List of processes to be demoted during context switching
# ================================================================ SCHEDULE RESULTS ================================================================
print("# Scheduling Results #")

while True:
    if not process_complete:
        print(f"\nAt Time = {ticks}")
        
        # Handle new arrivals
        arriving = [x for x in processes if x.arrival == ticks]                     # Processes arriving at the current tick
        if arriving:
            arriving.sort(key=lambda x: x.name)                                     # Sort by name for tie-breaking
            print("Arriving:", arriving)
            for proc in arriving:
                proc.in_q1 = 1                                                      # Mark process as in Q1
                if not (cpu or q1 or q2 or q3):                                     # Check if CPU or queues are idle
                    context_switch_remaining = cswitch                              # Trigger context switch
                q1.append(proc)                                                     # Add process to Q1

        # Print processes that completed in the previous tick
        if donep_for_printing:
            for p in donep_for_printing:
                print(f"{p} DONE")
                completed_processes.append(p)                                       # Move to completed list
                donep_for_printing.remove(p)                                        # Remove from temporary done list

        # Handle process demotion in CPU
        if cpu and cpu[0].pending_demotion:
            current_proc = cpu[0]
            if current_proc.demotion_target == "Q2":
                print(f"{current_proc} DEMOTED TO Q2")
            elif current_proc.demotion_target == "Q3":
                print(f"{current_proc} DEMOTED TO Q3")
            elif current_proc.demotion_target == "Q1":
                print(f"{current_proc} QUANTUM EXPIRED - BACK TO Q1")
            current_proc.pending_demotion = False                                   # Clear demotion flags
            current_proc.demotion_target = None
            demoted_process.remove(current_proc)

        # Handle CPU scheduling
        if not cpu and context_switch_remaining == 0:
            next_proc = None                                                        # Determine next process to run

            if q1:
                next_proc = q1.popleft()                                            # Fetch from Q1
                current_quantum = q1_rr_quantum                                     # Set Round Robin quantum
            elif q2:
                next_proc = q2.popleft()                                            # Fetch from Q2
                current_quantum = float('inf')                                      # FCFS, no quantum
            elif q3:
                sort_sjf_queue()                                                    # Sort Q3 by SJF
                next_proc = q3.popleft()                                            # Fetch shortest job
                current_quantum = float('inf')                                      # SJF, no quantum

            if next_proc:
                cpu.append(next_proc)                                               # Add to CPU

        # Handle context switching
        context_switch_remaining, ticks, skipped = handle_context_switch(context_switch_remaining, ticks, demoted_process)

        # Handle I/O
        handle_io(ticks)

        if skipped:
            continue                                                                # Skip the tick during context switching
        
        print(f"Queues: {list(q1)}; {list(q2)}; {list(q3)}")
        print(f"CPU: {cpu}")
        
        # Process running in CPU
        if cpu:
            current_proc = cpu[0]
            current_proc.cpu_time += 1                                              # Increment CPU time used

            # Update time allotment based on queue
            if current_proc.in_q1:
                current_proc.q1_quota += 1
            elif current_proc.in_q2:
                current_proc.q2_quota += 1

            # Check if current burst is complete
            if current_proc.operations[current_proc.op_marker] == 1:
                current_proc.op_marker += 1                                         # Move to the next operation

                if current_proc.op_marker >= len(current_proc.operations):          # If process is complete
                    current_proc.completion_time = ticks + 1
                    donep_for_printing.append(cpu.pop())
                    if q1 or q2 or q3:
                        context_switch_remaining = cswitch
                else:                                                               # Move to I/O
                    current_proc.in_io = ticks
                    if q1 or q2 or q3:
                        context_switch_remaining = cswitch
                        if cpu:
                            io.append(cpu.pop())
            else:
                current_proc.operations[current_proc.op_marker] -= 1                # Decrement current burst

            # Handle demotion flags
            if not current_proc.pending_demotion:
                if current_proc.in_q1 and current_quantum == 1:
                    if current_proc.q1_quota >= q1_allotment:  # Check Q1 time allotment
                        current_proc.in_q1 = 0
                        current_proc.in_q2 = 1
                        current_proc.pending_demotion = True
                        current_proc.demotion_target = "Q2"
                        demoted_process.append(current_proc)
                        if cpu:
                            q2.append(cpu.pop())
                        if q1:
                            context_switch_remaining = cswitch
                    else:  # Move back to Q1
                        current_proc.pending_demotion = True
                        current_proc.demotion_target = "Q1"
                        demoted_process.append(current_proc)
                        if q1 and cpu:
                            context_switch_remaining = cswitch
                            q1.append(cpu.pop())
                elif current_proc.in_q2 and current_proc.q2_quota >= q2_allotment:
                    current_proc.in_q2 = 0
                    current_proc.in_q3 = 1
                    current_proc.pending_demotion = True
                    current_proc.demotion_target = "Q3"
                    demoted_process.append(current_proc)
                    if q1 or q2:
                        context_switch_remaining = cswitch
                    q3.append(cpu.pop())

            if current_quantum != float('inf'):
                current_quantum -= 1  # Decrease quantum

    else:                                                                           # Check termination conditions
        print("\nSIMULATION DONE\n")

        total_turnaround = 0
        completed_processes.sort(key=lambda x: x.name)                              # Sort completed processes by name

        for p in completed_processes:
            turnaround = p.completion_time - p.arrival                              # Calculate turnaround time
            print(f"Turn-around time for Process {p} : {p.completion_time} - {p.arrival} = {turnaround} ms")
            total_turnaround += turnaround
            p.waiting = turnaround - p.cpu_time - p.io_time                         # Calculate waiting time

        avg_turnaround = total_turnaround / len(completed_processes)                # Average turnaround time
        print(f"Average Turn-around time = {avg_turnaround:.2f} ms")

        for p in completed_processes:
            print(f"Waiting time for Process {p} : {p.waiting} ms")

        break

    if not (q1 or q2 or q3 or cpu or io) and len(completed_processes) == proc_num:
        process_complete = True                                                     # All processes are complete

    ticks += 1                                                                      # Increment simulation time
    if ticks > 1000:                                                                # Safety limit to prevent infinite loop
        print("\nScheduler stopped due to time limit")
        break