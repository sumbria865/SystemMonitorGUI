import time
import psutil
import tkinter as tk
from tkinter import ttk
import threading
import subprocess
import re

started = False

def get_sensor_data():    
    result = subprocess.run(['sensors'], capture_output=True, text=True)
    output = result.stdout
        
    sensor_data = {}
        
    for line in output.splitlines():
                
        if "fan" in line:            
            match = re.search(r'fan(\d+):\s+(\d+)\s+RPM\s+\(min\s+=\s+\d+\s+RPM,\s+max\s+=\s+(\d+)\s+RPM\)', line)
            if match:
                fan_number = match.group(1)
                fan_speed = int(match.group(2))  # Current fan speed
                max_fan_speed = int(match.group(3))  # Maximum fan speed
                                
                sensor_data[f'Fan {fan_number} Speed'] = fan_speed                
                sensor_data[f'Fan {fan_number} Max Speed'] = max_fan_speed
                
        if "Core" in line:
            match = re.search(r'Core (\d+):\s+\+([\d.]+)°C', line)
            if match:
                core_number = match.group(1)
                core_temp = float(match.group(2))                
                sensor_data[f'CPU Core {core_number} Temperature'] = core_temp
    return sensor_data


def show_cpu_info():
    root.geometry('600x330')
    started = False
    def cpu_stat(): 
        started = True
        while True and started:
            freq = psutil.cpu_freq()[0]
            freq = round(freq, 2)
            freq_count_lbl.config(text=f'{freq} MHz')   

            cpu_usage = psutil.cpu_percent()
            cpu_usage_progress["value"] = cpu_usage
            cpu_usage_label.config(text=f'CPU Usage : {cpu_usage}%')

            sensor_data = get_sensor_data()

            sum = 0

            cpu_keys = []

            for key in sensor_data.keys():
                if 'CPU Core' in key:
                    cpu_keys.append(key)


            for i in cpu_keys:
                sum += sensor_data[i]

            avg = round(sum / cpu_count,1)

            temp_count.config(text=f'{avg} °C')
            try:
                fan_count_lbl.config(text=f'{sensor_data["Fan 1 Speed"]} RPM')
            

                speed = sensor_data[f'Fan 1 Speed']
                max_speed = sensor_data[f'Fan 1 Max Speed']

                if speed > max_speed : speed = max_speed

                progress['value'] = speed
                fan_count_lbl.config(text=f'{speed} RPM / {max_speed} RPM')  
            except Exception:
                pass


            time.sleep(1)   
    
    def show_advanced():

        started = False


        for widget in stat_frame.winfo_children():
            widget.destroy() # Remove all elements

        started = True
        sensor_data = get_sensor_data()

        cols = 5

        root.geometry('650x800')

        cpu_arr = []
        cpu_lbl_arr = []

        cpu_keys = []

        for key in sensor_data.keys():
            if 'CPU Core' in key:
                cpu_keys.append(key)


        lbl = tk.Label(stat_frame,text='CPU Tempratures : ')
        lbl.grid(row=4,column=0,pady=(30,20),columnspan=cols)

        r = 5
        c = 0

        for i in range(len(cpu_keys)):

            cpu_lbl = tk.Label(stat_frame,text=f'CPU {i}')
            cpu_lbl.grid(row=r,column=c,padx=10,pady=5)

            temp = sensor_data[cpu_keys[i]]

            temp_progress = ttk.Progressbar(stat_frame, orient="vertical", length=80, mode="determinate")
            temp_progress["maximum"] = 100
            temp_progress['value'] = temp
            temp_progress.grid(row=r+1,column=c,padx=10,pady=10)
            cpu_arr.append(temp_progress)

            temp_lbl = tk.Label(stat_frame,text=f'{temp} °C')
            temp_lbl.grid(row=r+2,column=c,padx=5,pady=5)
            cpu_lbl_arr.append(temp_lbl)

            c += 1
            if((i+1) % 5 == 0):
                r += 3
                c = 0

        def advance_stat():

            while True and started:

                sensor_data = get_sensor_data()

                for i in range(len(cpu_keys)):
                    temp = sensor_data[cpu_keys[i]]

                    cpu_arr[i]['value'] = temp
                    cpu_lbl_arr[i].config(text=f'{temp} °C')

                time.sleep(1)

        thread = threading.Thread(target=advance_stat)     
        thread.start() 


    for widget in stat_frame.winfo_children():
        widget.destroy() # Remove all elements
    
    sensor_data = get_sensor_data()

    cpu_count = psutil.cpu_count(logical=False)
    log_cpu_count = psutil.cpu_count(logical=True)
    core_label = tk.Label(stat_frame,text='Physical CPU count : ')
    core_count = tk.Label(stat_frame,text=cpu_count)

    core_log_label = tk.Label(stat_frame,text='Logical CPU count : ')
    core_log_count = tk.Label(stat_frame,text=log_cpu_count)

    core_label.grid(row=0,column=0,padx=10,pady=5)
    core_count.grid(row=0,column=1,padx=10,pady=5)
    core_log_label.grid(row=1,column=0,padx=10,pady=5)
    core_log_count.grid(row=1,column=1,padx=10,pady=5)   

    freq_label = tk.Label(stat_frame,text='CPU Frequency : ')
    freq_count_lbl = tk.Label(stat_frame,text=' MHz')

    freq_label.grid(row=2,column=0,padx=10,pady=5)
    freq_count_lbl.grid(row=2,column=1,padx=10,pady=5)       

    temp_label = tk.Label(stat_frame,text='CPU Temperature : ')
    temp_count = tk.Label(stat_frame,text=' °C')


    temp_label.grid(row=3,column=0,padx=10,pady=5)
    temp_count.grid(row=3,column=1,padx=10,pady=5)    

    try:
        speed = sensor_data[f'Fan 1 Speed']
        max_speed = sensor_data[f'Fan 1 Max Speed']

        if speed > max_speed : speed = max_speed

        progress = ttk.Progressbar(stat_frame, orient="horizontal", length=80, mode="determinate")
        progress["maximum"] = max_speed
        progress['value'] = speed
        progress.grid(row=4,column=1,padx=10,pady=5)
        
        fan_label = tk.Label(stat_frame,text='Fan Speed : ')
        fan_label.grid(row=4,column=0,padx=10,pady=5)

        fan_count_lbl = tk.Label(stat_frame,text=' RPM')
        fan_count_lbl.grid(row=5,column=0,padx=10,pady=5,columnspan=2)  
        
    except Exception:
        pass

    cpu_usage_progress = ttk.Progressbar(stat_frame, orient="horizontal", length=200, mode="determinate")
    cpu_usage_progress["maximum"] = 100
    cpu_usage_progress.grid(row=6,pady=(10,3),padx=5,columnspan=2)

    cpu_usage_label = tk.Label(stat_frame,text='CPU Usage : ')
    cpu_usage_label.grid(row=7,padx=5,columnspan=2)

    # Button for showing advance cpu information
    advance_btn = tk.Button(stat_frame,text='Advanced',command=show_advanced)
    advance_btn.grid(row=8,column=0,columnspan=2,pady=5)

    thread = threading.Thread(target=cpu_stat)     
    thread.start()    

    
def show_ram_info():
    root.geometry('600x330')
    started = False
    def ram_stat(): 

        started = True
        while True and started:
            vm = psutil.virtual_memory()
            avail = vm.available / 1000000
            avail = round(avail,2) 
            used = vm.used / 1000000
            used = round(used,2)

            total_used = vm.total - vm.available
            usage = total_used / vm.total * 100
            usage = round(usage,2)

            ram_usage_progress['value']=usage
            mem_used_count.config(text=f'{used} MegaBytes')
            mem_avail_count.config(text=f'{avail} MegaBytes')
            ram_usage_label.config(text=f'RAM Usage : {usage}%')

            time.sleep(1)
        
    for widget in stat_frame.winfo_children():
        widget.destroy() # Remove all elements

    total_mem = psutil.virtual_memory().total / 1000000
    total_mem = round(total_mem,2)     

    mem_label = tk.Label(stat_frame,text='Total Memory : ')
    mem_count = tk.Label(stat_frame,text=f'{total_mem} MegaBytes')

    mem_label.grid(row=0,column=0,padx=10,pady=10)
    mem_count.grid(row=0,column=1,padx=10,pady=10)      

    mem_avail_label = tk.Label(stat_frame,text='Available Memory : ')
    mem_avail_count = tk.Label(stat_frame,text=f'0 MegaBytes')

    mem_avail_label.grid(row=1,column=0,padx=10,pady=10)
    mem_avail_count.grid(row=1,column=1,padx=10,pady=10)   

    mem_used_label = tk.Label(stat_frame,text='Used Memory : ')
    mem_used_count = tk.Label(stat_frame,text=f'0 MegaBytes')

    mem_used_label.grid(row=2,column=0,padx=10,pady=10)
    mem_used_count.grid(row=2,column=1,padx=10,pady=10)   

    ram_usage_progress = ttk.Progressbar(stat_frame, orient="horizontal", length=200, mode="determinate")
    ram_usage_progress["maximum"] = 100
    ram_usage_progress.grid(row=3,pady=(20,3),padx=10,columnspan=2)

    ram_usage_label = tk.Label(stat_frame,text=f'RAM Usage : ')
    ram_usage_label.grid(row=4,padx=10,columnspan=2)

    thread = threading.Thread(target=ram_stat)     
    thread.start()


def show_nw_info():
    root.geometry('600x330')
    started = False
    def nw_stat(): 
        started = True
        while True and started:
            net_io = psutil.net_io_counters()

            bt_sent_count.config(text=net_io.bytes_sent)
            bt_rec_count.config(text=net_io.bytes_recv)
            pct_sent_count.config(text=net_io.packets_sent)
            pct_rec_count.config(text=net_io.packets_recv)

            time.sleep(1)
        
    for widget in stat_frame.winfo_children():
        widget.destroy() # Remove all elements

    bt_sent_lbl = tk.Label(stat_frame,text='Bytes sent : ')
    bt_sent_count = tk.Label(stat_frame)

    bt_sent_lbl.grid(row=0,column=0,padx=10,pady=10)
    bt_sent_count.grid(row=0,column=1,padx=10,pady=10)      

    bt_rec_lbl = tk.Label(stat_frame,text='Bytes Received : ')
    bt_rec_count = tk.Label(stat_frame)

    bt_rec_lbl.grid(row=1,column=0,padx=10,pady=10)
    bt_rec_count.grid(row=1,column=1,padx=10,pady=10)   

    pct_sent_lbl = tk.Label(stat_frame,text='Packets Sent : ')
    pct_sent_count = tk.Label(stat_frame)

    pct_sent_lbl.grid(row=2,column=0,padx=10,pady=10)
    pct_sent_count.grid(row=2,column=1,padx=10,pady=10)   

    pct_rec_lbl = tk.Label(stat_frame,text='Packets Received : ')
    pct_rec_count = tk.Label(stat_frame)

    pct_rec_lbl.grid(row=3,column=0,padx=10,pady=10)
    pct_rec_count.grid(row=3,column=1,padx=10,pady=10)   


    thread = threading.Thread(target=nw_stat)     
    thread.start()


# window initialization
root = tk.Tk()
root.title('System Monitor')
root.geometry('600x330')

# Frames
btn_frame = tk.Frame(root)
btn_frame.grid(row=0, column=0, padx=10, pady=10)

stat_frame = tk.Frame(root)
stat_frame.grid(row=0, column=1, padx=10, pady=10)


# Basic buttons in btn_frame
cpu_btn = tk.Button(btn_frame,text="Show CPU Information", command=show_cpu_info)
cpu_btn.pack(pady=(40,10),padx=10)

ram_btn = tk.Button(btn_frame,text="Show RAM Information", command=show_ram_info)
ram_btn.pack(pady=(40,10),padx=10)

nw_btn = tk.Button(btn_frame,text="Show Network Information", command=show_nw_info)
nw_btn.pack(pady=(40,10),padx=10)

root.mainloop()