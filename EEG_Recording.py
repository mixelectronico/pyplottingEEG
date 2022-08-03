import json
import serial
import time
import numpy as np
from datetime import datetime

#Parameters
sample_rate = 250 #Hertz
buffer_channels = 2
buffer_length = 100
sample_count = 0
saving_interval = 1

#Bluetooth communication protocol
ser = serial.Serial()
ser.baudrate = 19200
ser.port = 'COM13'
ser.timeout = None
ser.open()
print(ser.is_open)


time_init = datetime.now()
output_file = 'C:/EEG_data_visualization_' + str(time_init) + '.txt'
buffer = np.zeros((buffer_channels, buffer_length))
time_stamps = np.zeros(buffer_length)

try:
    while True:
        #Collect json data from bluetooth signal
        raw_message = ser.readline()

        #convert json to python dictionary
        eeg_data_line = json.loads(raw_message)

        #convert dictionary to list
        buffer_line = [eeg_data['c2'],eeg_data['c3']]

        #obtain current timestamp
        time_stamp_now = datetime.now() - time_init

        # Sample to numpy array  
        sample = np.array([sample])

        # Transpose vector
        sample = np.transpose(sample)

        # Concatenate vector
        update_buffer = np.concatenate((buffer, sample), axis=1)

        # save to new buffer
        buffer = update_buffer[:, 1:]

        # Save time_stamp
        time_stamps = np.append(time_stamps, time_stamp_now)
        time_stamps = time_stamps[1:]

        master_write_data(buffer, time_stamps, output_file)
except KeyboardInterrupt:
    pass
    

def master_write_data(eeg_data, time_stamps, output_file):
    # =================================================================
    # This method verifies if the EEG data has to be saved since saving
    # occurs perioically. If conditions are satisfied, it calls for a 
    # thread that will save the EEG data chunk on disk
    # =================================================================
    sample_count   = sample_count + 1
    if sample_count < sample_rate * saving_interval:
        return # too early
    elif sample_count > sample_rate * saving_interval:
        raise Exception('Wrong number of buffer fetches')

    new_buffer          = eeg_data[:, -saving_interval * sample_rate:]
    new_time_stamps     = time_stamps[-saving_interval * sample_rate:]
    sample_count   = 0 # Important: reset outside of thread
        
    save_thread = Thread(target=write_data_thread,
        args=(new_buffer, new_time_stamps, output_file))
    save_thread.start()

    
def write_data_thread(eeg_data, time_stamps, output_file):
    # checklist
    assert time_stamps.shape[0] == eeg_data.shape[1], "Problem with buffer length"

    # Append the data points to the end of the file
    with open(output_file, 'a', encoding=self.encoding) as file:
        buffer_length = time_stamps.shape[0]

        for sample_index in range(buffer_length):
            # Format time stamp
            time_stamp = time_stamps[sample_index]
            # format eeg data
            eeg_data_points = eeg_data[:,sample_index].tolist()
            eeg_data_points = [str(value) for value in eeg_data_points]
            eeg_data_points = ",".join(eeg_data_points)     
            
            # Write line to file
            file.write(f"{time_stamp}, {eeg_data_points} \n")
        file.close() # Important for data to get written