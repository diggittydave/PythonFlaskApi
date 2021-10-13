import os.path
import time
import pickle

def get_number_of_procs():
    # Read first line from /proc/stat. It should start with "cpu"
    # and contains times spend in various modes by all CPU's totalled.
    with open(r'/proc/stat','rb') as procfile:
        cpustats = procfile.read().decode('utf-8').split('\n')
    # Sanity check
    if 'cpu' not in cpustats[0]:
        raise ValueError("First line of /proc/stat not recognised")
    for i in range(len(cpustats)):
        if 'cpu' in cpustats[i]:
            proc_id = cpustats[i][3]
            if proc_id != ' ':
                number_of_procs = int(i)
    return number_of_procs


def get_cpu_times(stats_cpu:dict):
    # Read first line from /proc/stat. It should start with "cpu"
    # and contains times spend in various modes by all CPU's totalled.
    #
    with open(r'/proc/stat','rb') as procfile:
        cpustats = procfile.read().decode('utf-8').split('\n')
        #print(cpustats)
    # Sanity check
    #
    if 'cpu' not in cpustats[0]:
        raise ValueError("First line of /proc/stat not recognised")
    # Refer to "man 5 proc" (search for /proc/stat) for information
    # about which field means what.
    #
    # Here we do calculation as simple as possible:
    #
    # CPU% = 100 * time-doing-things / (time_doing_things + time_doing_nothing)
    #
    # cpu total use numbers
    for i in range((stats_cpu['number_of_procs'] + 1 )):
        #print(cpustats[i])
        if 'cpu' in cpustats[i]:
            proc_id = cpustats[i][3]
            if proc_id != ' ':
                stats_cpu[f'cpu{proc_id}'] = cpustats[i].split()
                stats_cpu[f'user_time_cpu{proc_id}'] = int(stats_cpu[f'cpu{proc_id}'][1])    # time spent in user space
                stats_cpu[f'nice_time_cpu{proc_id}'] = int(stats_cpu[f'cpu{proc_id}'][2])    # 'nice' time spent in user space
                stats_cpu[f'system_time_cpu{proc_id}'] = int(stats_cpu[f'cpu{proc_id}'][3])  # time spent in kernel space
                stats_cpu[f'idle_time_cpu{proc_id}'] = int(stats_cpu[f'cpu{proc_id}'][4])    # time spent idle
                stats_cpu[f'iowait_time_cpu{proc_id}'] = int(stats_cpu[f'cpu{proc_id}'][5])    # time spent waiting is also doing nothing
                stats_cpu[f'time_doing_things_cpu{proc_id}'] = int(stats_cpu[f'user_time_cpu{proc_id}'] + stats_cpu[f'nice_time_cpu{proc_id}'] + stats_cpu[f'system_time_cpu{proc_id}'])
                stats_cpu[f'time_doing_nothing_cpu{proc_id}'] = int(stats_cpu[f'idle_time_cpu{proc_id}'] + stats_cpu[f'iowait_time_cpu{proc_id}'])
            else:
                statstring = cpustats[i].split()
                stats_cpu['total_stats']= statstring
                stats_cpu['user_time_total'] = int(stats_cpu['total_stats'][1])    # time spent in user space
                stats_cpu['nice_time_total'] = int(stats_cpu['total_stats'][2])    # 'nice' time spent in user space
                stats_cpu['system_time_total'] = int(stats_cpu['total_stats'][3])  # time spent in kernel space
                stats_cpu['idle_time_total'] = int(stats_cpu['total_stats'][4])    # time spent idly
                stats_cpu['iowait_time_total'] = int(stats_cpu['total_stats'][5])  #time spent waiting is also doing nothing
                stats_cpu['time_doing_things_total'] = int(stats_cpu['user_time_total'] + stats_cpu['nice_time_total'] + stats_cpu['system_time_total'])
                stats_cpu['time_doing_nothing_total'] = int(stats_cpu['idle_time_total'] + stats_cpu['iowait_time_total'])
    return stats_cpu


def cpu_percentage_loop(stats_cpu:dict):
    #reset values on new loop
    #check number of procs
    for i in range(stats_cpu['number_of_procs']):
        proc_id = i
        stats_cpu[f'prev_time_doing_things_cpu{proc_id}'] = 0
        stats_cpu[f'prev_time_doing_nothing_cpu{proc_id}'] = 0
    stats_cpu['prev_time_doing_things_total'] = 0
    stats_cpu['prev_time_doing_nothing_total'] = 0
    cycleCounter = 0        
    # loop forever setting new values to pickle files
    while True:
        try:
            # get new values
            stats_cpu = get_cpu_times(stats_cpu)
            #calculate total cpu useage
            stats_cpu['diff_time_doing_things_total'] = int(stats_cpu['time_doing_things_total'] - stats_cpu['prev_time_doing_things_total'])
            stats_cpu['diff_time_doing_nothing_total'] = int(stats_cpu['time_doing_nothing_total'] - stats_cpu['prev_time_doing_nothing_total'])
            try:
                stats_cpu['cpu_percent_total'] = 100 * stats_cpu['diff_time_doing_things_total'] / (stats_cpu['diff_time_doing_things_total'] + stats_cpu['diff_time_doing_nothing_total'])
            except:
                stats_cpu['cpu_percent_total'] = 0
            # store new values for next loop
            # calculate individual proc useage
            #
            for i in range(stats_cpu['number_of_procs']):
                proc_id = i
                stats_cpu[f'diff_time_doing_things_cpu{proc_id}'] = int(stats_cpu[f'time_doing_things_cpu{proc_id}'] - stats_cpu[f'prev_time_doing_things_cpu{proc_id}'])
                stats_cpu[f'diff_time_doing_nothing_cpu{proc_id}'] = int(stats_cpu[f'time_doing_nothing_cpu{proc_id}'] - stats_cpu[f'prev_time_doing_nothing_cpu{proc_id}'])
                try:
                    stats_cpu[f'cpu_percent_cpu{proc_id}'] = 100 * stats_cpu[f'diff_time_doing_things_cpu{proc_id}'] / (stats_cpu[f'diff_time_doing_things_cpu{proc_id}'] + stats_cpu[f'diff_time_doing_nothing_cpu{proc_id}'])
                except:
                    stats_cpu[f'cpu_percent_cpu{proc_id}'] = 0
            # remember current values
            #
            stats_cpu['prev_time_doing_things_total'] = stats_cpu['time_doing_things_total']
            stats_cpu['prev_time_doing_nothing_total'] = stats_cpu['time_doing_nothing_total']
            for i in range(stats_cpu['number_of_procs']):
                proc_id = i
                stats_cpu[f'prev_time_doing_things_cpu{proc_id}'] = stats_cpu[f'time_doing_things_cpu{proc_id}']
                stats_cpu[f'prev_time_doing_nothing_cpu{proc_id}'] = stats_cpu[f'time_doing_nothing_cpu{proc_id}']
            # output latest percentages
            #
            if cycleCounter < 60:
                time.sleep(1)
                cycleCounter = cycleCounter + 1
            else:
                total = stats_cpu['cpu_percent_total']
                print(f'CPU TOTAL {total} %')
                for i in range(stats_cpu['number_of_procs']):
                    proc_id = i
                    proc = stats_cpu[f'cpu_percent_cpu{proc_id}']
                    print(f'CPU{proc_id} {proc} %')
                    pickle.dump(total, open('./cdfService/services/cpu_total.p', 'wb'))
                for i in range(stats_cpu['number_of_procs']):
                    proc_id = i
                    proc = stats_cpu[f'cpu_percent_cpu{proc_id}']
                    pickle.dump(stats_cpu[f'cpu_percent_cpu{proc_id}'], open(f'./cdfService/services/cpu_percent_cpu{proc_id}.p ', 'wb'))
                cycleCounter = 0
        except Exception as e:
            print('error')
            print(e)
            time.sleep(1)





if __name__ == '__main__':
    stats_cpu = {}
    stats_cpu['number_of_procs'] = get_number_of_procs()
    cpu_percentage_loop(get_cpu_times(stats_cpu))
    