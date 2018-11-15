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

        if len(current_data) != 0:
            while len(current_data) < NUMBER_OF_DISKS - 2:
                with open(PATH + 'disk_' + str((i + self.current_index) % NUMBER_OF_DISKS) + '/' + str(self.current_index), 'wb') as f:
                    if isinstance(0, int):
                        f.write(struct.pack('i', 0))
                i += 1
                lenght_data += 1
                current_data.append(0)
            self.store_parity(current_data)
            lenght_data += 2
            self.current_index += 1
        return starting_index, lenght_data
    

    def is_P_index(self, chunk_index, disk_index):
        if (chunk_index + self.NUMBER_OF_DISKS - 2) % self.NUMBER_OF_DISKS == disk_index:
            return True
        return False

    def is_Q_index(self, chunk_index, disk_index):
        if (chunk_index + self.NUMBER_OF_DISKS - 1) % self.NUMBER_OF_DISKS == disk_index:
            return True
        return False

    def read_one_chunk(self, chunk_index, exclude=[]):
        data = []
        p = None
        q = None
        for i in range(NUMBER_OF_DISKS):
            if (chunk_index + i) % self.NUMBER_OF_DISKS in exclude:
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
                    q = struct.unpack("i", f.read())[0]
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
            while i < self.current_index:
                data, par = self.read_one_chunk(i, disks_number)
                P,Q = par
                if P != None and Q != None:
                    with open(self.PATH + 'disk_' + str(disk_number) + '/' + str(i), 'wb') as f:
                        f.write(struct.pack('i', parity.recover_one_chunk_with_P(data, P)))

                elif P == None:
                    P = parity.calculate_P(data)
                    with open(self.PATH + 'disk_' + str(disk_number) + '/' + str(i), 'wb') as f:
                        f.write(struct.pack('i', P))

                elif Q == None:
                    Q = parity.calculate_Q(data)
                    with open(self.PATH + 'disk_' + str(disk_number) + '/' + str(i), 'wb') as f:
                        f.write(struct.pack('i', Q))

                i += 1

        elif len(disks_number) == 2:
            disk1_number = disks_number[0]
            disk2_number = disks_number[1]

            i = 0
            while i < self.current_index:
                data, par = self.read_one_chunk(i, disks_number)
                P,Q = par


                if P == None and Q == None:
                    p_index = disk1_number
                    q_index = disk2_number
                    if self.is_P_index(i, disk2_number):
                        p_index, q_index = q_index, p_index

                    with open(self.PATH + 'disk_' + str(p_index) + '/' + str(i), 'wb') as f:
                        f.write(struct.pack('i', parity.calculate_P(data)))

                    with open(self.PATH + 'disk_' + str(q_index) + '/' + str(i), 'wb') as f:
                        f.write(struct.pack('i', parity.calculate_Q(data)))

                elif P != None and Q != None:
                    #Get current position of the data in the list
                    actual_index1 = (disk1_number - (i % self.NUMBER_OF_DISKS) + self.NUMBER_OF_DISKS) % self.NUMBER_OF_DISKS
                    actual_index2 = (disk2_number - (i % self.NUMBER_OF_DISKS) + self.NUMBER_OF_DISKS) % self.NUMBER_OF_DISKS
                    data.insert(actual_index1, 0)
                    data.insert(actual_index2, 0)
                    a,b = parity.recover_two_chunk(data, P, Q, actual_index1, actual_index2)
                    with open(self.PATH + 'disk_' + str(disk1_number) + '/' + str(i), 'wb') as f:
                        f.write(struct.pack('i', a))
                    with open(self.PATH + 'disk_' + str(disk2_number) + '/' + str(i), 'wb') as f:
                        f.write(struct.pack('i', b))

                elif P == None :
                    data_index = disk1_number
                    p_index = disk2_number
                    if self.is_P_index(i, disk1_number):
                        data_index = disk2_number
                        p_index = disk1_number

                    with open(self.PATH + 'disk_' + str(data_index) + '/' + str(i), 'wb') as f:
                        #Get current position of the data in the list
                        actual_index = int((data_index - (i % self.NUMBER_OF_DISKS) + self.NUMBER_OF_DISKS) % self.NUMBER_OF_DISKS)
                        data.insert(actual_index, 0)
                        data[actual_index] = parity.recover_one_chunk_with_Q(data, Q, actual_index)
                        f.write(struct.pack('i', data[actual_index]))

                    with open(self.PATH + 'disk_' + str(p_index) + '/' + str(i), 'wb') as f:
                        f.write(struct.pack('i', parity.calculate_P(data)))

                elif Q == None :
                    data_index = disk1_number
                    q_index = disk2_number
                    if self.is_Q_index(i, disk1_number):
                        data_index = disk2_number
                        q_index = disk1_number

                    
                    #Get current position of the data in the list
                    actual_index = int((data_index - (i % self.NUMBER_OF_DISKS) + self.NUMBER_OF_DISKS) % self.NUMBER_OF_DISKS)
                    with open(self.PATH + 'disk_' + str(data_index) + '/' + str(i), 'wb') as f:
                        data_rec = parity.recover_one_chunk_with_P(data, P)
                        data.insert(actual_index, data_rec)
                        f.write(struct.pack('i', data_rec))

                    with open(self.PATH + 'disk_' + str(q_index) + '/' + str(i), 'wb') as f:
                        f.write(struct.pack('i', parity.calculate_Q(data)))


                i += 1

                



if DEBUG:
    R = RAID6()

    print("### Test writing/reading ###")
    a,b = R.write_data("abcdefghijklmnopqrstuvwxyz")
    print(R.read_data(a,b))

    print("### Test recovering disk 3 ###")
    shutil.rmtree("disks/disk_3")
    os.makedirs("disks/disk_3")
    R.recovering_disks([3])
    print(R.read_data(a,b))
    

    listes = [[0,1],[1,2],[2,3],[3,4],[4,5],[5,0]]
    for liste in listes:
        print("### Test recovering disk", liste[0] ,"& disk", liste[1]," ###")
        for i in liste:
            shutil.rmtree("disks/disk_" + str(i))
            os.makedirs("disks/disk_" + str(i))
        R.recovering_disks(liste)
        print(R.read_data(a,b))
        