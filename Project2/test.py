import struct



index = 0
disk = 0
while True:
    data = []
    with open('disks/disk_'+ str(disk) +'/' + str(index), 'rb') as f:
        for loop in range(16):
            data.append(chr(struct.unpack("b", f.read(1))[0] + 128))
    print(index, disk, data)
    disk = (disk + 1) 
    if disk == 8:
        index += 1
        disk = 0
    input()
