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
        self.CHUNK_SIZE = 16

        self.current_index = 0
        self.current_disk_index = 0

        self.P_INDEX =  self.NUMBER_OF_DISKS - 2
        self.Q_INDEX =  self.NUMBER_OF_DISKS - 1

        self.ENFORCING_CHECK = True

        self.WRITING_INFO = 'b'

        #name:[{index, disk, offset, lenght}, ...]
        self.FILES_INFO = {}

        #available_place
        self.ERASED_INFO = []

        self.DISKS_INFO = []

        # Removing old directory
        try:
            shutil.rmtree(self.PATH)
        except:
            pass
        for i in range(self.NUMBER_OF_DISKS):
            directory = "disk_" + str(i)
            if not os.path.exists(self.PATH + directory):
                os.makedirs(self.PATH + directory)

    def increase_disk_index(self, ret=False):
        self.current_disk_index = (self.current_disk_index + 1) % (self.NUMBER_OF_DISKS - 2)

    def update_disk_info(self, index, disk_index, lenght):
        try:
            self.DISKS_INFO[index][disk_index] = lenght
        except:
            self.DISKS_INFO.append([0 for i in range(self.NUMBER_OF_DISKS)]) 
            self.DISKS_INFO[index][disk_index] = lenght

        #print(self.DISKS_INFO)
        #input()

    def store_parity(self, index_number):
        data, par = self.read_one_chunk(index_number,self_recovering=False)
        current_data = [[] for loop in range(self.CHUNK_SIZE)]
        for x in data:
            for i in range(len(x)):
                current_data[i].append(x[i])

        P = []
        Q = []
        for x in current_data:
            if len(x) > 0:
                P.append(parity.calculate_P(x))
                Q.append(parity.calculate_Q(x))

        self.update_disk_info(self.current_index, (self.P_INDEX + self.current_index) % self.NUMBER_OF_DISKS, len(P))
        self.update_disk_info(self.current_index, (self.Q_INDEX + self.current_index) % self.NUMBER_OF_DISKS, len(Q))

        with open(self.PATH + 'disk_' + str((self.P_INDEX + self.current_index) % self.NUMBER_OF_DISKS) + '/' + str(self.current_index), 'wb') as f:
            for x in P:
                f.write(struct.pack('b', x - 128))
        with open(self.PATH + 'disk_' + str((self.Q_INDEX + self.current_index) % self.NUMBER_OF_DISKS) + '/' + str(self.current_index), 'wb') as f:
            for x in Q:        
                f.write(struct.pack('b', x - 128))

    def write_data(self, data, name):
        data_as_bytes = str.encode(data)

        with open(self.PATH + 'temp', 'wb') as f:
            f.write(data_as_bytes)

        return self.write_data_from_file(self.PATH + 'temp', name)
    
    def write_data_from_file(self, file, name, chunk_to_write=[], offset=0):
        stat_info = os.stat(file)
        size = stat_info.st_size

        
        if len(chunk_to_write) == 0:
            places_to_write = []

            for x in self.ERASED_INFO[:]:
                places_to_write.append(x)
                self.ERASED_INFO.remove(x)
                size -= x['lenght']
                if size <= 0:
                    break
            if size > 0:
                places_to_write.append({'index': self.current_index, 'disk': self.current_disk_index, 'offset': 0, 'lenght': size})
        else:
            places_to_write = chunk_to_write


        with open(file, "rb") as in_file:
            if offset > 0:
                in_file.read(offset)
            for place_to_write in places_to_write:
                starting_index = place_to_write['index']
                starting_disk = place_to_write['disk']
                starting_offset = place_to_write['offset']
                index = place_to_write['index']
                disk = place_to_write['disk']


                lenght_to_write = place_to_write['lenght']
                lenght_data = 0

                heading_offset = 0
                if starting_offset > 0:
                    lenght_data = 0
                    while lenght_data + self.CHUNK_SIZE <= starting_offset:
                        lenght_data += self.CHUNK_SIZE
                        disk = (disk + 1) 
                        if disk == self.P_INDEX:
                            index += 1
                            disk = 0
                    heading_offset = starting_offset - lenght_data
                    #print("HeadingOffset",index, disk, heading_offset)

                live = False
                if index == self.current_index and disk == self.current_disk_index:
                    live = True

                lenght_data = starting_offset
                if heading_offset > 0:
                    chunk_data = []
                    with open(self.PATH + 'disk_' + str((disk + index) % self.NUMBER_OF_DISKS) + '/' + str(index), 'rb') as f:
                        for _ in range(heading_offset):
                            chunk_data.append(struct.unpack("b", f.read(1))[0] + 128)
                else:
                    chunk_data = []

                
                ### MAIN LOOP ###
                while lenght_data < lenght_to_write:
                    value = in_file.read(1)
                    value = int.from_bytes(value, byteorder='big')
                    chunk_data.append(value)
                    lenght_data += 1

                    if (len(chunk_data) == self.CHUNK_SIZE):
                        with open(self.PATH + 'disk_' + str((disk + index) % self.NUMBER_OF_DISKS) + '/' + str(index), 'wb') as f:
                            for j in range(self.CHUNK_SIZE):
                                x = chunk_data[j]
                                f.write(struct.pack('b', x - 128)) # write an int                            
                           
                        self.update_disk_info(index, (disk + index) % self.NUMBER_OF_DISKS, self.CHUNK_SIZE)
                        if live:
                            self.increase_disk_index()
                        disk += 1
                        chunk_data = []
                        if disk == self.P_INDEX:
                            self.store_parity(self.current_index)
                            if live:
                                self.current_index += 1
                            index += 1
                            disk = 0
                    

                if len(chunk_data) > 0:
                    with open(self.PATH + 'disk_' + str((index + disk) % self.NUMBER_OF_DISKS) + '/' + str(index), 'wb') as f:
                        #print(self.PATH + 'disk_' + str((index + disk) % self.NUMBER_OF_DISKS) + '/' + str(index), chunk_data, "Live:",live)
                        for j in range(len(chunk_data)):
                            x = chunk_data[j]
                            f.write(struct.pack('b', x - 128)) # write an int

                        for j in range(len(chunk_data), self.CHUNK_SIZE):	
                            f.write(struct.pack('b', 0 - 128)) # write an int	
                    self.update_disk_info(self.current_index, (index + disk) % self.NUMBER_OF_DISKS, len(chunk_data))
                    if live:
                        self.increase_disk_index()
                    disk += 1
                    if disk == self.P_INDEX:
                        self.store_parity(self.current_index)
                        if live:
                            self.current_index += 1
                        index += 1
                        disk = 0
                
                if disk > 0:
                    self.store_parity(self.current_index)


                #Files Data
                try:
                    self.FILES_INFO[name].append({'index':starting_index, 'disk':starting_disk, 'offset':0, 'lenght':lenght_data})
                except:
                    self.FILES_INFO[name] = [{'index':starting_index, 'disk':starting_disk, 'offset':0, 'lenght':lenght_data}]

        return True

    def is_P_index(self, chunk_index, disk_index):
        if (chunk_index + self.P_INDEX) % self.NUMBER_OF_DISKS == disk_index:
            return True
        return False

    def is_Q_index(self, chunk_index, disk_index):
        if (chunk_index + self.Q_INDEX) % self.NUMBER_OF_DISKS == disk_index:
            return True
        return False

    def read_one_chunk(self, chunk_index, exclude=[], already_recovered=False, self_recovering=True):
        if chunk_index > self.current_index:
            return False
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
                        try:
                            if i % self.NUMBER_OF_DISKS == self.P_INDEX:
                                p.append(struct.unpack("b", f.read(1))[0] + 128)
                            elif i % self.NUMBER_OF_DISKS == self.Q_INDEX:
                                q.append(struct.unpack("b", f.read(1))[0] + 128)
                            else:
                                data[i].append(struct.unpack("b", f.read(1))[0] + 128)
                        except:
                            break

            except Exception as error:
                if self_recovering:
                    #print(error)
                    failed.append((chunk_index + i) % self.NUMBER_OF_DISKS)

        if len(failed) > 0 and self_recovering: 
            if self.ENFORCING_CHECK and len(exclude) == 0:
                #print("Error", p, data)
                return data, (p,q)
                if p != parity.calculate_P(data) or q != parity.calculate_Q(data):
                    raise IOError("Error")

                    if not already_recovered:            
                        print("[!] Error disk:",failed,"; Attempting recovery ...")
                        self.recovering_disks(failed)
                        return self.read_one_chunk(chunk_index, exclude, True)
                    else:
                        raise IOError("Unrecoverable error")


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

    def actual_disk_index(self, index, disk):
        return (disk + (index % self.NUMBER_OF_DISKS) + self.NUMBER_OF_DISKS) % self.NUMBER_OF_DISKS

    def read_data_to_file(self, file, starting_index, starting_disk, lenght, add=False):
        local_index = starting_index
        #print("\n Starting", file, starting_index, starting_disk, lenght)

        i = 0
        writing_method = "wb"
        if add:
            writing_method = "ab"

        with open(file, writing_method) as out_file:
            data, par  = self.read_one_chunk(local_index)
            ## Starting Trim for different files
            for j in range(starting_disk, len(data)):
                chunk_data = data[j]

                if (i + len(chunk_data) <= lenght):
                    size_readable = self.DISKS_INFO[local_index][self.actual_disk_index(local_index, j)]
                    chunk_data = chunk_data[:size_readable]
                    i += len(chunk_data[:size_readable])
                    out_file.write(bytes(chunk_data[:size_readable]))
                else:
                    out_file.write(bytes(chunk_data[:lenght - i]))
                    i = lenght
                    break

            
            local_index += 1

            while i < lenght:
                data, par  = self.read_one_chunk(local_index)
                for j in range(len(data)):
                    chunk_data = data[j]
                    if (i + len(chunk_data) <= lenght):
                        size_readable = self.DISKS_INFO[local_index][self.actual_disk_index(local_index, j)]
                        chunk_data = chunk_data[:size_readable]
                        i += len(chunk_data[:size_readable])
                        out_file.write(bytes(chunk_data[:size_readable]))
                    else:
                        out_file.write(bytes(chunk_data[:lenght - i]))
                        i = lenght
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
            max_index = self.current_index
            if self.current_disk_index > disk_number:
                max_index += 1
            #Introduce this in 2 disks recovery

            while index < max_index:
                data, par = self.read_one_chunk(index, disks_number)


                P,Q = par
                data_packed = [[] for _ in range(self.CHUNK_SIZE)]

                for x in data:
                    for i in range(len(x)):
                        data_packed[i].append(x[i])
                

                if P != [] and Q != []:
                    dat = [] 
                    for i in range(len(data_packed)):
                        dat.append(parity.recover_one_chunk_with_P(data_packed[i], P[i]))

                    try:
                        if self.DISKS_INFO[index][disk_number] < self.CHUNK_SIZE:
                            dat = dat[:self.DISKS_INFO[index][disk_number]]
                    except:
                        return

                    with open(self.PATH + 'disk_' + str(disk_number) + '/' + str(index), 'wb') as f:
                        for value in dat:
                            f.write(struct.pack('b', value - 128))

                elif P == []:
                    with open(self.PATH + 'disk_' + str(disk_number) + '/' + str(index), 'wb') as f:
                        for i in range(len(data_packed)):
                            p = parity.calculate_P(data_packed[i])
                            f.write(struct.pack('b', p - 128))

                elif Q == []:
                    with open(self.PATH + 'disk_' + str(disk_number) + '/' + str(index), 'wb') as f:
                        for i in range(len(data_packed)):
                            q = parity.calculate_Q(data_packed[i])
                            f.write(struct.pack('b', q - 128))
                index += 1

        ## 2 Disks Recovery
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
                    self.store_parity(i)


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

    def delete_data(self, name):
        try:
            position_info = self.FILES_INFO.pop(name)
            for x in position_info:
                self.ERASED_INFO.append(x)

            return True
        except:
            return False

    def update_data_from_file(self, filename, name):
        stat_info = os.stat(filename)
        total_size = stat_info.st_size

        saved_data = self.get_data_from_name(name)
        similar_size = 0
        with open(filename, "rb") as in_file:
            while similar_size < total_size:
                try:
                    data = in_file.read(1)
                    if data == str.encode(saved_data[similar_size]):
                        similar_size += 1
                    else:
                        break
                except:
                    break
        file_info = self.FILES_INFO[name]
        total_size_saved = 0
        for x in file_info:
            total_size_saved += x['lenght']


        #Getting the place to write
        size_to_write = total_size - similar_size
        similar_ = similar_size
        writing_to = []
        totally_written = False
        already_written = 0
        for x in file_info[:]:
            #Removing trailing data blocks
            if totally_written:
                file_info.remove(x)
                self.ERASED_INFO.append(x)
            similar_ -= x['lenght']
            if similar_ < 0:
                a = x.copy()
                file_info.remove(x)
                added_size_to_fill = 0

                if a['lenght'] % self.CHUNK_SIZE != 0:
                    added_size_to_fill = a['lenght']
                    a['lenght'] = a['lenght'] + (self.CHUNK_SIZE - a['lenght'] % self.CHUNK_SIZE)
                    added_size_to_fill = a['lenght'] - added_size_to_fill

                if similar_ + a['lenght'] > 0:
                    a['offset'] = similar_ + a['lenght']



                already_written += a['lenght'] - a['offset']
                if a['lenght'] - a['offset'] >= size_to_write:
                    totally_written = True
                    old_size = a['lenght']
                    a['lenght'] = size_to_write + similar_ + a['lenght'] - added_size_to_fill
                    #freeing space
                    index = a['index']
                    disk = a['disk']
                    data_w = 0
                    while data_w < a['lenght']:
                        data_w += self.CHUNK_SIZE
                        disk = (disk + 1) 
                        if disk == self.P_INDEX:
                            index += 1
                            disk = 0
                    self.ERASED_INFO.append({'index':index, 'disk':disk, 'offset':0, 'lenght':old_size - data_w})


                writing_to.append(a)

        if already_written < size_to_write:
            writing_to.append({'index':self.current_index, 'disk':self.current_disk_index, 'offset':0, 'lenght':size_to_write - already_written})

        #print("Writing_to",writing_to, similar_size)
        return self.write_data_from_file(filename, name, chunk_to_write=writing_to, offset=similar_size)

            
        


    def get_data_from_name(self, name):
        try:
            position_info = self.FILES_INFO[name]
            data = ""
            for x in position_info:
                data += self.read_data(x['index'], x['disk'], x['lenght'])
            return data
        except:
            return False
    
    def get_data_to_file_from_name(self, filename, name):
        try:
            position_info = self.FILES_INFO[name]
            success = self.read_data_to_file(filename, position_info[0]['index'], position_info[0]['disk'], position_info[0]['lenght'])
            for x in position_info[1:]:
                success = success and self.read_data_to_file(filename, x['index'], x['disk'], x['lenght'], add=True)
            return success
        except:
            return False


R = RAID6()

R.write_data("Test1DataDataDat", "test")
R.write_data("Test2DataDataDat", "test2")
R.write_data("Test21DataDataDa", "test21")
R.write_data("Test22DataDataDa", "test22")

R.delete_data("test")
R.delete_data("test21")

R.write_data_from_file("test.txt", "test3")
#print(R.FILES_INFO["test3"])

#print("Test", R.get_data_from_name("test2"))
R.update_data_from_file("test2.txt", "test3")
print("Test3", R.get_data_to_file_from_name("test_out.txt","test3"))

print(R.FILES_INFO["test3"])
print(R.ERASED_INFO)


"""
with open('disks/disk_0/0', 'rb') as f:
    print(f.read())"""