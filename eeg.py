import socket
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal


MCLK=3276800
OSR=4096
PRESCALE=1

DRCLK=MCLK/(4*OSR*PRESCALE)

fs = DRCLK  # Sample frequency (Hz)
f0 = 60.0  # Frequency to be removed from signal (Hz)
Q = 30.0  # Quality factor
sos = signal.iirfilter(30, [55, 65], btype='bandstop', fs=fs, output='sos')
# Design notch filter
#b, a = signal.iirnotch(f0, Q, fs)

Vref=1.2
G=51*2
scale=Vref/(8388608*G*1.5)

plt.style.use('ggplot')

def live_plotter(x_vec,y1_data,line1,identifier='',pause_time=0.001):
    if line1==[]:
        # this is the call to matplotlib that allows dynamic plotting
        plt.ion()
        fig = plt.figure(figsize=(13,6))
        ax = fig.add_subplot(111)
        # create a variable for the line so we can later update it
        line1, = ax.plot(x_vec,y1_data,'-',alpha=0.8)        
        #update plot label/title
        plt.ylabel('Y Label')
        plt.title('Title: {}'.format(identifier))
        plt.show()
    
    # after the figure, axis, and line are created, we only need to update the y-data
    line1.set_ydata(y1_data)
    # adjust limits if new data goes beyond bounds
    if np.min(y1_data)<=line1.axes.get_ylim()[0] or np.max(y1_data)>=line1.axes.get_ylim()[1]:
        plt.ylim([np.min(y1_data)-np.std(y1_data),np.max(y1_data)+np.std(y1_data)])
    # this pauses the data so the figure/axis can catch up - the amount of pause can be altered above
    plt.pause(pause_time)
    
    # return line so we can update it again in the next iteration
    return line1


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('', 10000)
sock.bind(server_address)
sock.setblocking(1)


length = 5
x_vec = np.linspace(0,length,int(length*fs)+1)[0:-1]
y1_vec = np.random.randn(len(x_vec))
y2_vec = np.random.randn(len(x_vec))
y3_vec = np.random.randn(len(x_vec))
y4_vec = np.random.randn(len(x_vec))

plt.ion()
fig = plt.figure(figsize=(26,12))

ax1 = fig.add_subplot(221)
plt.ylabel('Amplitude (uV)')
plt.xlabel('Time (sec)')
plt.title('Left Motor')

ax2 = fig.add_subplot(222)
plt.ylabel('Amplitude (uV)')
plt.xlabel('Time (sec)')
plt.title('Right Motor')

ax3 = fig.add_subplot(223)
plt.ylabel('Amplitude (uV)')
plt.xlabel('Time (sec)')
plt.title('Left Visual')

ax4 = fig.add_subplot(224)
plt.ylabel('Amplitude (uV)')
plt.xlabel('Time (sec)')
plt.title('Right Visual')


# create a variable for the line so we can later update it
line1, = ax1.plot(x_vec,y1_vec,'-',alpha=0.8)
line2, = ax2.plot(x_vec,y2_vec,'-',alpha=0.8)
line3, = ax3.plot(x_vec,y3_vec,'-',alpha=0.8)
line4, = ax4.plot(x_vec,y4_vec,'-',alpha=0.8)
#update plot label/title
plt.show()




a=np.zeros(20,dtype='int64')
b=np.zeros(20,dtype='int64')
c=np.zeros(20,dtype='int64')
d=np.zeros(20,dtype='int64')
while True:
    data, address = sock.recvfrom(4096)
    i=0
    while i<20:
        a[i] = int.from_bytes(data[i*8:i*8+2],byteorder='big',signed=True)
        b[i] = int.from_bytes(data[i*8+2:i*8+4],byteorder='big',signed=True)
        c[i] = int.from_bytes(data[i*8+4:i*8+6],byteorder='big',signed=True)
        d[i] = int.from_bytes(data[i*8+6:i*8+8],byteorder='big',signed=True)
        i+=1

    y1_vec[-20:] = a*256*scale*1000000
    y2_vec[-20:] = b*256*scale*1000000
    y3_vec[-20:] = c*256*scale*1000000
    y4_vec[-20:] = d*256*scale*1000000

    y1_filt = signal.sosfilt(sos,y1_vec)
    y2_filt = signal.sosfilt(sos,y2_vec)
    y3_filt = signal.sosfilt(sos,y3_vec)
    y4_filt = signal.sosfilt(sos,y4_vec)
 
    line1.set_ydata(y1_filt)
    line2.set_ydata(y2_filt)
    line3.set_ydata(y3_filt)
    line4.set_ydata(y4_filt)

    ax1.set_ylim(np.min(y1_filt), np.max(y1_filt))
    ax2.set_ylim(np.min(y2_filt), np.max(y2_filt))
    ax3.set_ylim(np.min(y3_filt), np.max(y3_filt))
    ax4.set_ylim(np.min(y4_filt), np.max(y4_filt))
    
    y1_vec = np.append(y1_vec[20:],np.zeros(20))
    y2_vec = np.append(y2_vec[20:],np.zeros(20))
    y3_vec = np.append(y3_vec[20:],np.zeros(20))
    y4_vec = np.append(y4_vec[20:],np.zeros(20))

    plt.pause(.001)