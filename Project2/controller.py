import os
import sys
import shutil
import parity
import struct

from random import randint

DEBUG = True
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


class RAID6:
    def __init__(self):
        self.PATH = 'disks/'
        self.NUMBER_OF_DISKS = 6
        self.CHUNK_SIZE = 8

        self.current_index = 0

        # Removing old directory
        shutil.rmtree(PATH)
        for i in range(NUMBER_OF_DISKS):
            directory = "disk_" + str(i)
            if not os.path.exists(PATH + directory):
                os.makedirs(PATH + directory)


    def store_parity(self, chunk_list):
        P = parity.calculate_P(chunk_list)
        Q = parity.calculate_Q(chunk_list)
        with open(PATH + 'disk_' + str((4 + self.current_index) % NUMBER_OF_DISKS) + '/' + str(self.current_index), 'wb') as f:
            f.write(struct.pack('i', P))
        with open(PATH + 'disk_' + str((5 + self.current_index) % NUMBER_OF_DISKS) + '/' + str(self.current_index), 'wb') as f:
            f.write(struct.pack('i', Q))


    def write_data(self, data):
        data_as_bytes = str.encode(data)
        starting_index = self.current_index
        lenght_data = 0
        i = 0
        current_data = []
        for value in data_as_bytes:
            with open(PATH + 'disk_' + str((i + self.current_index) % NUMBER_OF_DISKS) + '/' + str(self.current_index), 'wb') as f:
                if isinstance(value, int):
                    f.write(struct.pack('i', value)) # write an int
                    current_data.append(value)
                    lenght_data += 1
            i += 1
            
            if i == NUMBER_OF_DISKS - 2:
                self.store_parity(current_data)
                self.current_index += 1
                i = 0
                current_data = []
                lenght_data += 2


        while len(current_data) < 4:
            current_data.append(0)
            self.store_parity(current_data)

        return starting_index, lenght_data
    

    def read_data(self, starting_index, lenght):
        final_data = []
        parity_data = []
        local_index = starting_index

        p = 0
        q = 0
        for i in range(lenght):
            with open(PATH + 'disk_' + str((local_index + i) % NUMBER_OF_DISKS) + '/' + str(local_index), 'rb') as f:
                if i % NUMBER_OF_DISKS == 4:
                    p = f.read()
                elif i % NUMBER_OF_DISKS == 5:
                    q = f.read()
                    parity_data.append((p,q))
                    local_index += 1
                else:
                    final_data.append(f.read())
        
        original_data = ""
        for x in final_data:
            original_data += chr(struct.unpack("i", x)[0])

        return original_data

        


if DEBUG:
    R = RAID6()
    a,b = R.write_data("coucou c'est moi")
    print(R.read_data(a,b))