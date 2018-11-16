import os
import sys
import shutil
import parity
import struct

from random import randint

DEBUG = True

class RAID6:
    def __init__(self):
        self.PATH = 'disks/'
        self.NUMBER_OF_DISKS = 8
        self.CHUNK_SIZE = 8

        self.current_index = 0

        self.P_INDEX =  self.NUMBER_OF_DISKS - 2
        self.Q_INDEX =  self.NUMBER_OF_DISKS - 1

        # Removing old directory
        try:
            shutil.rmtree(self.PATH)
        except:
            pass
        for i in range(self.NUMBER_OF_DISKS):
            directory = "disk_" + str(i)
            if not os.path.exists(self.PATH + directory):
                os.makedirs(self.PATH + directory)


    def store_parity(self, chunk_list):
        P = parity.calculate_P(chunk_list)
        Q = parity.calculate_Q(chunk_list)
        with open(self.PATH + 'disk_' + str((self.P_INDEX + self.current_index) % self.NUMBER_OF_DISKS) + '/' + str(self.current_index), 'wb') as f:
            f.write(struct.pack('i', P))
        with open(self.PATH + 'disk_' + str((self.Q_INDEX + self.current_index) % self.NUMBER_OF_DISKS) + '/' + str(self.current_index), 'wb') as f:
            f.write(struct.pack('i', Q))


    def write_data(self, data):
        data_as_bytes = str.encode(data)
        starting_index = self.current_index
        lenght_data = 0
        i = 0
        current_data = []
        for value in data_as_bytes:
            with open(self.PATH + 'disk_' + str((i + self.current_index) % self.NUMBER_OF_DISKS) + '/' + str(self.current_index), 'wb') as f:
                if isinstance(value, int):
                    f.write(struct.pack('i', value)) # write an int
                    current_data.append(value)
                    lenght_data += 1
            i += 1
            
            if i == self.P_INDEX:
                self.store_parity(current_data)
                self.current_index += 1
                i = 0
                current_data = []
                lenght_data += 2

        if len(current_data) != 0:
            while len(current_data) < self.P_INDEX:
                with open(self.PATH + 'disk_' + str((i + self.current_index) % self.NUMBER_OF_DISKS) + '/' + str(self.current_index), 'wb') as f:
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
        if (chunk_index + self.P_INDEX) % self.NUMBER_OF_DISKS == disk_index:
            return True
        return False

    def is_Q_index(self, chunk_index, disk_index):
        if (chunk_index + self.Q_INDEX) % self.NUMBER_OF_DISKS == disk_index:
            return True
        return False

    def read_one_chunk(self, chunk_index, exclude=[]):
        data = []
        p = None
        q = None
        for i in range(self.NUMBER_OF_DISKS):
            if (chunk_index + i) % self.NUMBER_OF_DISKS in exclude:
                continue
            with open(self.PATH + 'disk_' + str((chunk_index + i) % self.NUMBER_OF_DISKS) + '/' + str(chunk_index), 'rb') as f:
                if i % self.NUMBER_OF_DISKS == self.P_INDEX:
                    p = struct.unpack("i", f.read())[0]
                elif i % self.NUMBER_OF_DISKS == self.Q_INDEX:
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
            with open(self.PATH + 'disk_' + str((local_index + i) % self.NUMBER_OF_DISKS) + '/' + str(local_index), 'rb') as f:
                if i % self.NUMBER_OF_DISKS == self.P_INDEX:
                    p = struct.unpack("i", f.read())[0]
                elif i % self.NUMBER_OF_DISKS == self.Q_INDEX:
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
        