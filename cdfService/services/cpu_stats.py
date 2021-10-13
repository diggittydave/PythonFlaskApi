import os.path
import time
import pickle


def get_cpu_times():
    # Read first line from /proc/stat. It should start with "cpu"
    # and contains times spend in various modes by all CPU's totalled.
    #
    with open(r'/proc/stat','rb') as procfile:
        cpustats = procfile.read().decode('utf-8').split('\n')

    # Sanity check
    #
    if 'cpu' not in cpustats[0]:
        raise ValueError("First line of /proc/stat not recognised")
    
    cpu_total = cpustats[0].split()
    cpu0_stats = cpustats[1].split()
    cpu1_stats = cpustats[2].split() 
    cpu2_stats = cpustats[3].split()
    cpu3_stats= cpustats[4].split()
    # Refer to "man 5 proc" (search for /proc/stat) for information
    # about which field means what.
    #
    # Here we do calculation as simple as possible:
    #
    # CPU% = 100 * time-doing-things / (time_doing_things + time_doing_nothing)
    #
    # cpu total use numbers
    user_time_total = int(cpu_total[1])    # time spent in user space
    nice_time_total = int(cpu_total[2])    # 'nice' time spent in user space
    system_time_total = int(cpu_total[3])  # time spent in kernel space
    idle_time_total = int(cpu_total[4])    # time spent idly
    iowait_time_total = int(cpu_total[5])    # time spent waiting is also doing nothing
    # cpu0 use
    user_time_cpu0 = int(cpu0_stats[1])    # time spent in user space
    nice_time_cpu0 = int(cpu0_stats[2])    # 'nice' time spent in user space
    system_time_cpu0 = int(cpu0_stats[3])  # time spent in kernel space
    idle_time_cpu0 = int(cpu0_stats[4])    # time spent idly
    iowait_time_cpu0 = int(cpu0_stats[5])    # time spent waiting is also doing nothing
    # cpu1 use
    user_time_cpu1 = int(cpu1_stats[1])    # time spent in user space
    nice_time_cpu1 = int(cpu1_stats[2])    # 'nice' time spent in user space
    system_time_cpu1 = int(cpu1_stats[3])  # time spent in kernel space
    idle_time_cpu1 = int(cpu1_stats[4])    # time spent idly
    iowait_time_cpu1 = int(cpu1_stats[5])    # time spent waiting is also doing nothing
    #cpu2 use
    user_time_cpu2 = int(cpu2_stats[1])    # time spent in user space
    nice_time_cpu2 = int(cpu2_stats[2])    # 'nice' time spent in user space
    system_time_cpu2 = int(cpu2_stats[3])  # time spent in kernel space
    idle_time_cpu2 = int(cpu2_stats[4])    # time spent idly
    iowait_time_cpu2 = int(cpu2_stats[5])    # time spent waiting is also doing nothing
    #cpu3 use
    user_time_cpu3 = int(cpu3_stats[1])    # time spent in user space
    nice_time_cpu3 = int(cpu3_stats[2])    # 'nice' time spent in user space
    system_time_cpu3 = int(cpu3_stats[3])  # time spent in kernel space
    idle_time_cpu3 = int(cpu3_stats[4])    # time spent idly
    iowait_time_cpu3 = int(cpu3_stats[5])    # time spent waiting is also doing nothing

    time_doing_things_total = user_time_total + nice_time_total + system_time_total
    time_doing_nothing_total = idle_time_total + iowait_time_total
    time_doing_things_cpu0 = user_time_cpu0 + nice_time_cpu0 + system_time_cpu0
    time_doing_nothing_cpu0 = idle_time_cpu0 + iowait_time_cpu0
    time_doing_things_cpu1 = user_time_cpu1 + nice_time_cpu1 + system_time_cpu1
    time_doing_nothing_cpu1 = idle_time_cpu1 + iowait_time_cpu1
    time_doing_things_cpu2 = user_time_cpu2 + nice_time_cpu2 + system_time_cpu2
    time_doing_nothing_cpu2 = idle_time_cpu2 + iowait_time_cpu2
    time_doing_things_cpu3 = user_time_cpu3 + nice_time_cpu3 + system_time_cpu3
    time_doing_nothing_cpu3 = idle_time_cpu3 + iowait_time_cpu3

    return [time_doing_things_total, time_doing_nothing_total, time_doing_things_cpu0, time_doing_things_cpu1, time_doing_things_cpu2, time_doing_things_cpu3,
    time_doing_nothing_cpu0, time_doing_nothing_cpu1, time_doing_nothing_cpu2, time_doing_nothing_cpu3]


def cpu_percentage_loop():
    prev_time_doing_things_total = 0
    prev_time_doing_nothing_total = 0
    prev_time_doing_things_cpu0 = 0
    prev_time_doing_nothing_cpu0 = 0
    prev_time_doing_things_cpu1 = 0
    prev_time_doing_nothing_cpu1 = 0
    prev_time_doing_things_cpu2 = 0
    prev_time_doing_nothing_cpu2 = 0
    prev_time_doing_things_cpu3 = 0
    prev_time_doing_nothing_cpu3 = 0
    while True:  # loop forever printing CPU usage percentage
        [time_doing_things_total, time_doing_nothing_total, time_doing_things_cpu0, time_doing_things_cpu1, time_doing_things_cpu2, time_doing_things_cpu3,
        time_doing_nothing_cpu0, time_doing_nothing_cpu1, time_doing_nothing_cpu2, time_doing_nothing_cpu3] = get_cpu_times()
        
        # total cpu usage
        diff_time_doing_things_total = time_doing_things_total - prev_time_doing_things_total
        diff_time_doing_nothing_total = time_doing_nothing_total - prev_time_doing_nothing_total
        try:
            cpu_percentage_total = 100.0 * diff_time_doing_things_total/ (diff_time_doing_things_total + diff_time_doing_nothing_total)
        except:
            cpu_percentage_total = 0
        #cpu0 usage
        diff_time_doing_things_cpu0 = time_doing_things_cpu0 - prev_time_doing_things_cpu0
        diff_time_doing_nothing_cpu0 = time_doing_nothing_cpu0 - prev_time_doing_nothing_cpu0
        try:
            cpu_percentage_cpu0 = 100.0 * diff_time_doing_things_cpu0/ (diff_time_doing_things_cpu0 + diff_time_doing_nothing_cpu0)
        except:
            cpu_percentage_cpu0 = 0
        
        #cpu1 usage
        diff_time_doing_things_cpu1 = time_doing_things_cpu1 - prev_time_doing_things_cpu1
        diff_time_doing_nothing_cpu1 = time_doing_nothing_cpu1 - prev_time_doing_nothing_cpu1
        try:
            cpu_percentage_cpu1 = 100.0 * diff_time_doing_things_cpu1/ (diff_time_doing_things_cpu1 + diff_time_doing_nothing_cpu1)
        except:
            cpu_percentage_cpu1 = 0
        
        #cpu2 usage
        diff_time_doing_things_cpu2 = time_doing_things_cpu2 - prev_time_doing_things_cpu2
        diff_time_doing_nothing_cpu2 = time_doing_nothing_cpu2 - prev_time_doing_nothing_cpu2
        try:
            cpu_percentage_cpu2 = 100.0 * diff_time_doing_things_cpu2/ (diff_time_doing_things_cpu2 + diff_time_doing_nothing_cpu2)
        except:
            cpu_percentage_cpu2 = 0
        
        #cpu3 usage
        diff_time_doing_things_cpu3 = time_doing_things_cpu3 - prev_time_doing_things_cpu3
        diff_time_doing_nothing_cpu3 = time_doing_nothing_cpu3 - prev_time_doing_nothing_cpu3
        try:
            cpu_percentage_cpu3 = 100.0 * diff_time_doing_things_cpu3/ (diff_time_doing_things_cpu3 + diff_time_doing_nothing_cpu3)
        except:
            cpu_percentage_cpu3 = 0
        
        # remember current values to subtract next iteration of the loop
        #
        prev_time_doing_things_total = time_doing_things_total
        prev_time_doing_nothing_total = time_doing_nothing_total
        prev_time_doing_things_cpu0 = time_doing_things_cpu0
        prev_time_doing_nothing_cpu0 = time_doing_nothing_cpu0
        prev_time_doing_things_cpu1 = time_doing_things_cpu1
        prev_time_doing_nothing_cpu1 = time_doing_nothing_cpu1
        prev_time_doing_things_cpu2 = time_doing_things_cpu2
        prev_time_doing_nothing_cpu2 = time_doing_nothing_cpu2
        prev_time_doing_things_cpu3 = time_doing_things_cpu3
        prev_time_doing_nothing_cpu3 = time_doing_nothing_cpu3

        # Output latest perccentage
        #
        print(f'CPU TOTAL {cpu_percentage_total} %')
        print(f'cpu0  {cpu_percentage_cpu0} %')
        print(f'cpu1  {cpu_percentage_cpu1} %')
        print(f'cpu2  {cpu_percentage_cpu2} %')
        print(f'cpu3  {cpu_percentage_cpu3} %')
        pickle.dump(cpu_percentage_total, open('cpu_total.p', 'wb'))
        pickle.dump(cpu_percentage_cpu0, open('cpu0.p', 'wb'))
        pickle.dump(cpu_percentage_cpu1, open('cpu1.p', 'wb'))
        pickle.dump(cpu_percentage_cpu2, open('cpu2.p', 'wb'))
        pickle.dump(cpu_percentage_cpu3, open('cpu3.p', 'wb'))
        # Loop delay
        #
        time.sleep(1)


if __name__ == "__main__":
    cpu_percentage_loop()