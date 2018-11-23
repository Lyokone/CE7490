import struct
import controller
import time

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

R = controller.RAID6()

R.write_data("Test1DataDataDat", "test")
R.write_data("Test2DataDataDat", "test2")
R.write_data("Test21DataDataDa", "test21")
R.write_data("Test22DataDataDa", "test22")

R.delete_data("test")
R.delete_data("test21")

R.write_data_from_file("test.txt", "test3")

start = time.time()
R.delete_data("test3")
R.write_data_from_file("test1.txt", "test3")
end = time.time()
print(end - start)

R.delete_data("test3")
R.write_data_from_file("test.txt", "test3")

start = time.time()
R.update_data_from_file("test1.txt", "test3")
end = time.time()
print(end - start)

#start = time.time()
#shutil.rmtree("disks/disk_3")
#shutil.rmtree("disks/disk_4")
#R.recovering_disks([3,4])
#end = time.time()
#print(end - start)
#print("Test3", R.get_data_to_file_from_name("picture_out.jpg","test3"))


#print("Test", R.get_data_from_name("test2"))
#R.update_data_from_file("test2.txt", "test3")
#print("Test3", R.get_data_to_file_from_name("test_out.txt","test3"))

#print(R.FILES_INFO["test3"])
#print(R.ERASED_INFO)


"""
with open('disks/disk_0/0', 'rb') as f:
    print(f.read())"""