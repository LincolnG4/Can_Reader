from asammdf import MDF, SUPPORTED_VERSIONS, Signal,Source
import numpy as np

sigs = []
mdf = MDF()
timestamp = []
array = []
databyte = []

types = [('CAN_DataFrame.ID', '<u4'), 
        ('CAN_DataFrame.IDE', 'u1'), 
        ('CAN_DataFrame.DLC', 'u1'), 
        ('CAN_DataFrame.DataBytes', 'u1', (8,)), 
        ('CAN_DataFrame.BusChannel', 'u1')]
count = 0

with open(r'C:\Users\g97sa\OneDrive\Área de Trabalho\Bosch\examples\bombeiro.txt') as f:
    while True:
        try:
            line = f.readline()

            if line == '\n':
                break

            if line[0] != '*' :
                lines = line.split()
                if lines[5] != '0':
                    t = lines[0].split(':')
                    timestamp.append(int(t[0])*3600 + int(t[0])*60 + int(t[0]) + count + int(t[0])/10000)
                    count = count + 1
                    for i in range (6,14):
                        databyte.append(int(lines[i],16))

                    array.append(((int(lines[3],16)),0,int(lines[5]),tuple(databyte),int(lines[2])))
                    databyte = []
                
        except Exception as e:
            print(e)
            continue

arr = np.rec.array(array,dtype=types)
t   = np.array(timestamp,dtype=np.float64)

sig = Signal(
    arr,
    t,
    name='CAN_DataFrame',
    comment='',
    master_metadata= ['Timestamp', 1],
    source=Source(
        source_type=Source.SOURCE_BUS,
        bus_type=Source.BUS_TYPE_CAN,
        name="CAN bus",
        path="CAN bus",
        comment="",
    )
)


sigs.append(sig)
#print(sigs)
mdf.append(sigs, comment='CAN_DataFrame', common_timebase=True)
print(mdf)
mdf.save('demo_start.mf4', overwrite=True)
print('save')