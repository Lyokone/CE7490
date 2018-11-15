DEBUG = True

CHUNK_SIZE = 8

DISK_P = "disk3"
DISK_Q = "disk4"


def calculate_P(list_chunks):
    c = list_chunks[0]
    for x in list_chunks[1:]:
        c = c ^ x

    return c

def shift(x, n):
    s = str(bin(x))[2:]
    for i in range(CHUNK_SIZE - len(s)):
        s = "0" + s
    for i in range(n):
        s = s[1:] + s[0]
    return int(s, base=2)


def calculate_Q(list_chunks):
    c = list_chunks[0]
    for i in range(1,len(list_chunks)):
        c = c ^ shift(list_chunks[i], i)

    return c
        




if (DEBUG):
    TEST_LIST = [0b11111111,0b01010101]

    print(bin(calculate_P(TEST_LIST)))
    print(bin(shift(0b00010011, 1)))
    print(bin(shift(0b00010011, 2)))

    print(bin(calculate_Q(TEST_LIST)))


