import os
from random import randint

PATH = 'disks/'
NUMBER_OF_DISKS = 6

def write_file(name, number_of_bytes, start_disk):
    for i in range(number_of_bytes):
        with open(PATH + 'disk_' + str((start_disk + i) % NUMBER_OF_DISKS) + '/' + name + '_' + str(i), 'wb') as f:
            f.write(bytes([randint(0, 255)]))
        
        f.close()

def clear_disks():
    folder = 'disks/disk_'
    for i in range(NUMBER_OF_DISKS):
        for the_file in os.listdir(folder + str(i)):
            file_path = os.path.join(folder + str(i), the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)
                
write_file('asd', 7, 0)
write_file('qwe', 9, 2)
clear_disks()