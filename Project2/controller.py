import os
import sys
import shutil
import parity
import struct


class RAID6:
    def __init__(self):
        self.PATH = 'disks/'
        self.NUMBER_OF_DISKS = 8
        self.BYTE_SIZE = 8
        self.CHUNK_SIZE = 128

        self.current_index = 0
        self.current_disk_index = 0

        self.P_INDEX =  self.NUMBER_OF_DISKS - 2
        self.Q_INDEX =  self.NUMBER_OF_DISKS - 1

        self.ENFORCING_CHECK = False

        self.WRITING_INFO = 'b'

        
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
        P = []
        Q = []
        for x in chunk_list:
            P.append(parity.calculate_P(x))
            Q.append(parity.calculate_Q(x))
        with open(self.PATH + 'disk_' + str((self.P_INDEX + self.current_index) % self.NUMBER_OF_DISKS) + '/' + str(self.current_index), 'wb') as f:
            for x in P:
                f.write(struct.pack('b', x - 128))
        with open(self.PATH + 'disk_' + str((self.Q_INDEX + self.current_index) % self.NUMBER_OF_DISKS) + '/' + str(self.current_index), 'wb') as f:
            for x in Q:        
                f.write(struct.pack('b', x - 128))

    def write_data(self, data):
        data_as_bytes = str.encode(data)
        starting_index = self.current_index
        starting_disk = self.current_disk_index
        lenght_data = 0
        i = self.current_disk_index
        current_data = [[] for loop in range(self.CHUNK_SIZE)]

        #getting current disk_data for mid index writing
        if self.current_disk_index != 0:
            data, par = self.read_one_chunk(starting_index)
            for k in range(self.CHUNK_SIZE):
                for j in range(len(data)):
                    if data[j][k] != 0:
                        current_data[k].append(data[j][k])
                    else:
                        break

        chunk_data = []
        for value in data_as_bytes:
            chunk_data.append(value)
            if (len(chunk_data) == self.CHUNK_SIZE):
                with open(self.PATH + 'disk_' + str((i + self.current_index) % self.NUMBER_OF_DISKS) + '/' + str(self.current_index), 'wb') as f:
                    for j in range(self.CHUNK_SIZE):
                        x = chunk_data[j]
                        current_data[j].append(x)
                        f.write(struct.pack('b', x - 128)) # write an int
                        lenght_data += 1
                self.current_disk_index = (self.current_disk_index + 1) % self.NUMBER_OF_DISKS
                i += 1
                chunk_data = []
                if i == self.P_INDEX:
                    self.store_parity(current_data)
                    self.current_index += 1
                    i = 0
                    current_data = [[] for loop in range(self.CHUNK_SIZE)]

        if len(chunk_data) > 0:
            with open(self.PATH + 'disk_' + str((i + self.current_index) % self.NUMBER_OF_DISKS) + '/' + str(self.current_index), 'wb') as f:
                for j in range(len(chunk_data)):
                    x = chunk_data[j]
                    current_data[j].append(x)
                    f.write(struct.pack('b', x - 128)) # write an int
                    lenght_data += 1
                for j in range(len(chunk_data), self.CHUNK_SIZE):
                    current_data[j].append(0)
                    f.write(struct.pack('b', 0 - 128)) # write an int
            self.current_disk_index = (self.current_disk_index + 1) % self.NUMBER_OF_DISKS
            i += 1

        if i != self.P_INDEX and i > 0:
            while i < self.P_INDEX:
                with open(self.PATH + 'disk_' + str((i + self.current_index) % self.NUMBER_OF_DISKS) + '/' + str(self.current_index), 'wb') as f:
                    for j in range(self.CHUNK_SIZE):
                        f.write(struct.pack('b', -128))
                        current_data[j].append(0)
                i += 1
            self.store_parity(current_data)
        return starting_index, starting_disk, lenght_data
    
    def write_data_from_file(self, file):
        starting_index = self.current_index
        starting_disk = self.current_disk_index
        lenght_data = 0
        i = self.current_disk_index
        current_data = [[] for loop in range(self.CHUNK_SIZE)]
        chunk_data = []

         #getting current disk_data for mid index writing
        if self.current_disk_index != 0:
            data, par = self.read_one_chunk(starting_index)
            for k in range(self.CHUNK_SIZE):
                for j in range(len(data)):
                    if data[j][k] != 0:
                        current_data[k].append(data[j][k])
                    else:
                        break


        with open(file, "rb") as in_file:
            value = in_file.read(1)
            while value:
                value = int.from_bytes(value, byteorder='big')
                chunk_data.append(value)

                if (len(chunk_data) == self.CHUNK_SIZE):
                    with open(self.PATH + 'disk_' + str((i + self.current_index) % self.NUMBER_OF_DISKS) + '/' + str(self.current_index), 'wb') as f:
                        for j in range(self.CHUNK_SIZE):
                            x = chunk_data[j]
                            current_data[j].append(x)
                            f.write(struct.pack('b', x - 128)) # write an int
                            lenght_data += 1
                    self.current_disk_index = (self.current_disk_index + 1) % self.NUMBER_OF_DISKS
                    i += 1
                    chunk_data = []
                    if i == self.P_INDEX:
                        self.store_parity(current_data)
                        self.current_index += 1
                        i = 0
                        current_data = [[] for loop in range(self.CHUNK_SIZE)]
                
                value = in_file.read(1)

        if len(chunk_data) > 0:
            with open(self.PATH + 'disk_' + str((i + self.current_index) % self.NUMBER_OF_DISKS) + '/' + str(self.current_index), 'wb') as f:
                for j in range(len(chunk_data)):
                    x = chunk_data[j]
                    current_data[j].append(x)
                    f.write(struct.pack('b', x - 128)) # write an int
                    lenght_data += 1
                for j in range(len(chunk_data), self.CHUNK_SIZE):
                    current_data[j].append(0)
                    f.write(struct.pack('b', 0 - 128)) # write an int
            self.current_disk_index = (self.current_disk_index + 1) % self.NUMBER_OF_DISKS
            i += 1



        if i != self.P_INDEX and i > 0:
            while i < self.P_INDEX:
                with open(self.PATH + 'disk_' + str((i + self.current_index) % self.NUMBER_OF_DISKS) + '/' + str(self.current_index), 'wb') as f:
                    for j in range(self.CHUNK_SIZE):
                        f.write(struct.pack('b', -128))
                        current_data[j].append(0)
                i += 1
            self.store_parity(current_data)

        return starting_index, starting_disk, lenght_data

    def is_P_index(self, chunk_index, disk_index):
        if (chunk_index + self.P_INDEX) % self.NUMBER_OF_DISKS == disk_index:
            return True
        return False

    def is_Q_index(self, chunk_index, disk_index):
        if (chunk_index + self.Q_INDEX) % self.NUMBER_OF_DISKS == disk_index:
            return True
        return False

    def read_one_chunk(self, chunk_index, exclude=[], already_recovered=False):
        data = [[] for loop in range(self.NUMBER_OF_DISKS - 2)]
        p = []
        q = []
        failed = []
        for i in range(self.NUMBER_OF_DISKS):
            if (chunk_index + i) % self.NUMBER_OF_DISKS in exclude:
                continue
            try:
                with open(self.PATH + 'disk_' + str((chunk_index + i) % self.NUMBER_OF_DISKS) + '/' + str(chunk_index), 'rb') as f:
                    for _ in range(self.CHUNK_SIZE):
                        if i % self.NUMBER_OF_DISKS == self.P_INDEX:
                            p.append(struct.unpack("b", f.read(1))[0] + 128)
                        elif i % self.NUMBER_OF_DISKS == self.Q_INDEX:
                            q.append(struct.unpack("b", f.read(1))[0] + 128)
                        else:
                            data[i].append(struct.unpack("b", f.read(1))[0] + 128)

            except Exception as error:
                print(error, data)
                failed.append(i)

        if len(failed) > 0:
            if not already_recovered:            
                print("[!] Error disk:",failed,"; Attempting recovery ...")
                self.recovering_disks(failed)
                return self.read_one_chunk(chunk_index, exclude, True)
            else:
                raise IOError("Unrecoverable error")

        if self.ENFORCING_CHECK and len(exclude) == 0:
            if p != parity.calculate_P(data) or q != parity.calculate_Q(data):
                raise IOError("Error")

        if already_recovered:
            print("[✓] Error recovered !")

        return data, (p,q)

    def read_data(self, starting_index, starting_disk, lenght):
        final_data = []
        local_index = starting_index

        i = 0
        data, par = self.read_one_chunk(local_index)
        data = data[starting_disk:]
        i += self.CHUNK_SIZE * (len(data))
        final_data.extend(data)
        local_index += 1

        while i < lenght:
            data, par = self.read_one_chunk(local_index)
            i += self.CHUNK_SIZE * (self.NUMBER_OF_DISKS - 2)
            final_data.extend(data)
            local_index += 1
        
        original_data = ""
        i = 0
        for chunk_data in final_data:
            for x in chunk_data:
                original_data += chr(x)
                i += 1
                if i >= lenght:
                    break
            if i >= lenght:
                    break

        return original_data
 
    def read_data_to_file(self, file, starting_index, starting_disk, lenght):
        local_index = starting_index

        i = 0
        with open(file, "wb") as out_file:
            data, par  = self.read_one_chunk(local_index)
            data = data[starting_disk:]
            for chunk_data in data:
                if (i + self.CHUNK_SIZE <= lenght):
                    i += self.CHUNK_SIZE
                    out_file.write(bytes(chunk_data))
                else:
                    j = lenght - i
                    i += j
                    out_file.write(bytes(chunk_data[0:j]))
                    break

            local_index += 1

            while i < lenght:
                data, par  = self.read_one_chunk(local_index)
                for chunk_data in data:
                    if (i + self.CHUNK_SIZE <= lenght):
                        i += self.CHUNK_SIZE
                        out_file.write(bytes(chunk_data))
                    else:
                        j = lenght - i
                        i += j
                        out_file.write(bytes(chunk_data[0:j]))
                        break

                local_index += 1
        
        return True

    def recovering_disks(self, disks_number):
        for i in disks_number:
            try:
                os.makedirs("disks/disk_" + str(i))
            except:
                pass

        if len(disks_number) == 1:
            disk_number = disks_number[0]
            index = 0
            while index < self.current_index:
                data, par = self.read_one_chunk(index, disks_number)
                

                P,Q = par
                data_packed = [[] for _ in range(self.CHUNK_SIZE)]

                for i in range(self.CHUNK_SIZE):
                    for j in range(len(data)):
                        try:
                            data_packed[i].append(data[j][i])
                        except:
                            pass

                if P != [] and Q != []:
                    with open(self.PATH + 'disk_' + str(disk_number) + '/' + str(index), 'wb') as f:
                        for i in range(len(data_packed)):
                            f.write(struct.pack('b', parity.recover_one_chunk_with_P(data_packed[i], P[i]) - 128))

                elif P == []:
                    with open(self.PATH + 'disk_' + str(disk_number) + '/' + str(index), 'wb') as f:
                        for i in range(len(data_packed)):
                            P = parity.calculate_P(data_packed[i])
                            f.write(struct.pack('b', P - 128))

                elif Q == []:
                    with open(self.PATH + 'disk_' + str(disk_number) + '/' + str(index), 'wb') as f:
                        for i in range(len(data_packed)):
                            Q = parity.calculate_Q(data_packed[i])
                            f.write(struct.pack('b', Q - 128))

                index += 1

        elif len(disks_number) == 2:
            disk1_number = disks_number[0]
            disk2_number = disks_number[1]

            i = 0
            while i < self.current_index:
                data, par = self.read_one_chunk(i, disks_number)
                P,Q = par

                data_packed = [[] for _ in range(self.CHUNK_SIZE)]

                for k in range(self.CHUNK_SIZE):
                    for j in range(len(data)):
                        try:
                            data_packed[k].append(data[j][k])
                        except:
                            data_packed[k].append(0)

                if P == [] and Q == []:
                    p_index = disk1_number
                    q_index = disk2_number
                    if self.is_P_index(i, disk2_number):
                        p_index, q_index = q_index, p_index

                    with open(self.PATH + 'disk_' + str(p_index) + '/' + str(i), 'wb') as f:
                        for k in range(len(data_packed)):
                            P = parity.calculate_P(data_packed[k])
                            f.write(struct.pack('b', P - 128))

                    with open(self.PATH + 'disk_' + str(q_index) + '/' + str(i), 'wb') as f:
                        for k in range(len(data_packed)):
                            Q = parity.calculate_Q(data_packed[k])
                            f.write(struct.pack('b', Q - 128))


                elif P != [] and Q != []:
                    #Get current position of the data in the list
                    actual_index1 = (disk1_number - (i % self.NUMBER_OF_DISKS) + self.NUMBER_OF_DISKS) % self.NUMBER_OF_DISKS
                    actual_index2 = (disk2_number - (i % self.NUMBER_OF_DISKS) + self.NUMBER_OF_DISKS) % self.NUMBER_OF_DISKS
                    #data.insert(actual_index1, 0)
                    #data.insert(actual_index2, 0)
                    with open(self.PATH + 'disk_' + str(disk1_number) + '/' + str(i), 'wb') as f1, open(self.PATH + 'disk_' + str(disk2_number) + '/' + str(i), 'wb') as f2:
                        for k in range(len(data_packed)):   
                            a,b = parity.recover_two_chunk(data_packed[k], P[k], Q[k], actual_index1, actual_index2)
                            f1.write(struct.pack('b', a - 128))
                            f2.write(struct.pack('b', b - 128))

                elif P == [] :
                    data_index = disk1_number
                    p_index = disk2_number
                    if self.is_P_index(i, disk1_number):
                        data_index = disk2_number
                        p_index = disk1_number

                    with open(self.PATH + 'disk_' + str(data_index) + '/' + str(i), 'wb') as f1, open(self.PATH + 'disk_' + str(p_index) + '/' + str(i), 'wb') as f2:
                        #Get current position of the data in the list
                        actual_index = int((data_index - (i % self.NUMBER_OF_DISKS) + self.NUMBER_OF_DISKS) % self.NUMBER_OF_DISKS)
                        #data.insert(actual_index, 0)
                        for k in range(len(data_packed)):
                            data_packed[k][actual_index] = parity.recover_one_chunk_with_Q(data_packed[k], Q[k], actual_index)
                            f1.write(struct.pack('b', data_packed[k][actual_index] - 128))
                            f2.write(struct.pack('b', parity.calculate_P(data_packed[k]) - 128))
                        

                elif Q == [] :
                    data_index = disk1_number
                    q_index = disk2_number
                    if self.is_Q_index(i, disk1_number):
                        data_index = disk2_number
                        q_index = disk1_number

                    with open(self.PATH + 'disk_' + str(data_index) + '/' + str(i), 'wb') as f1, open(self.PATH + 'disk_' + str(q_index) + '/' + str(i), 'wb') as f2:
                        #Get current position of the data in the list
                        actual_index = int((data_index - (i % self.NUMBER_OF_DISKS) + self.NUMBER_OF_DISKS) % self.NUMBER_OF_DISKS)
                        for k in range(len(data_packed)):
                            data_packed[k][actual_index] = parity.recover_one_chunk_with_P(data_packed[k], P[k])
                            f1.write(struct.pack('b', data_packed[k][actual_index] - 128))
                            f2.write(struct.pack('b', parity.calculate_Q(data_packed[k]) - 128))
                        

                i += 1




R = RAID6()
#a, b, c = R.write_data("abcdefghabcdefghabcdefghabcd")
#print(a,b,c)
#d, e, f = R.write_data("jesuisgenialjemappelleguillaume")

R.write_data("abcdefghabcdefghabcdefghabcd")
a, b, c = R.write_data_from_file("in_big.jpg")
print(a,b,c)
print(R.read_data_to_file("out_big.jpg",a,b,c))

#print(R.read_data(a,b,c))
#print(R.read_data(d,e,f))

#print(value, len(value))
#shutil.rmtree("disks/disk_3")
#shutil.rmtree("disks/disk_4")
#R.recovering_disks([3,4])
#print(R.read_data_to_file("out_big.jpg",a,b))