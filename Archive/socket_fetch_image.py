from socket_instr import SocketInstr
from datetime import datetime
import time

scope = SocketInstr('192.168.86.40', 4000, timeout=20)  # Default port = 4000
scope.clear()               # clears read buffer
scope.write('*cls')         # clears event status register

ID = scope.query('*idn?').split(',')
model = ID[1]
serial = ID[2]
print(f'Connected to: {model}, {serial}')

start = time.time()
dt = datetime.now()  # timestamp for PC filename
fname_local = dt.strftime(('{:s}_{:s}_%Y%m%d_%H%M%S.%f')[:-3] + '.png').format(model, serial)    # model/serial, date/time filename on host PC, year/month/day_hour/minute/second/millisecond    fname_scope = 'temp.png'
path_scope = scope.query('filesystem:homedir?')
fname_scope = 'temp.png'

# print('scope dir: {:s}'.format(path_scope))
scope.write('filesystem:cwd {:s}'.format(path_scope))
img_data = scope.fetch_screen(fname_scope)  # fetch_screen, is a robust method for importing a screen capture
with open(fname_local, 'wb') as f:
    f.write(img_data)

print('saved image successfully')
print('Time to complete:', time.time() - start)

# error checking
print('Event Status Register:', scope.query('*esr?'))
print("All event codes/messages:", scope.query('allev?'))   # displays event codes and messages, also clears EVMsg? queue

# close socket
scope.close()
