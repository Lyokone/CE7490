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
            if not os.path.exists(self.PATH + directory):
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
    

    def read_one_chunk(self, chunk_index, exclude=[]):
        data = []
        p = None
        q = None
        for i in range(NUMBER_OF_DISKS):
            if chunk_index + i in exclude:
                    continue
            with open(self.PATH + 'disk_' + str((chunk_index + i) % NUMBER_OF_DISKS) + '/' + str(chunk_index), 'rb') as f:
                if i % NUMBER_OF_DISKS == 4:
                    p = struct.unpack("i", f.read())[0]
                elif i % NUMBER_OF_DISKS == 5:
                    q = struct.unpack("i", f.read())[0]
                else:
                    data.append(struct.unpack("i", f.read())[0])

        return data, (p,q)

    def read_data(self, starting_index, lenght):
        final_data = []
        parity_data = []
        local_index = starting_index

        p = 0
        q = 0
        for i in range(lenght):
            with open(self.PATH + 'disk_' + str((local_index + i) % NUMBER_OF_DISKS) + '/' + str(local_index), 'rb') as f:
                if i % NUMBER_OF_DISKS == 4:
                    p = struct.unpack("i", f.read())[0]
                elif i % NUMBER_OF_DISKS == 5:
                    q = f.read()
                    parity_data.append((p,q))
                    local_index += 1
                else:
                    final_data.append(struct.unpack("i", f.read())[0])
        
        original_data = ""
        for x in final_data:
            original_data += chr(x)

        return original_data

    
    def recovering_disks(self, disks_number):
        if len(disks_number) == 1:
            disk_number = disks_number[0]
            i = 0
            partial_data = []
            parity_data = []
            while i < self.current_index:
                data, par = self.read_one_chunk(i, disks_number)
                P,Q = par
                if P != None:
                    with open(self.PATH + 'disk_' + str(disk_number) + '/' + str(i), 'wb') as f:
                        f.write(struct.pack('i', parity.recover_one_chunk_with_P(data, P)))

                else:
                    P = parity.calculate_P(data)
                    with open(self.PATH + 'disk_' + str(disk_number) + '/' + str(i), 'wb') as f:
                        f.write(struct.pack('i', P))
                i += 1
                



if DEBUG:
    R = RAID6()

    print("### Test writing/reading ###")
    a,b = R.write_data("coucou c'est moi")
    print(R.read_data(a,b))

    print("### Test recovering disk3 ###")
    shutil.rmtree("disks/disk_3")
    os.makedirs("disks/disk_3")
    R.recovering_disks([3])
    print(R.read_data(a,b))