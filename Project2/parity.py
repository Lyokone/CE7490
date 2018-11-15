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

def unshift(x, n):
    s = str(bin(x))[2:]
    for i in range(CHUNK_SIZE - len(s)):
        s = "0" + s
    for i in range(n):
        s =  s[-1] + s[:-1] 
    return int(s, base=2)

def calculate_Q(list_chunks):
    c = list_chunks[0]
    for i in range(1,len(list_chunks)):
        c = c ^ shift(list_chunks[i], i)

    return c
        

def recover_one_chunk_with_P(remaining_chunks, P_chunk):
    c = P_chunk
    print("c",c, type(c))
    for x in remaining_chunks:
        c = c ^ x 

    return c

def recover_one_chunk_with_Q(all_disk_chunks, Q_chunk, missing_chunk_index):
    c = Q_chunk
    for i in range(0,len(all_disk_chunks)):
        if i == missing_chunk_index:
            continue

        c = c ^ shift(all_disk_chunks[i], i)

    return unshift(c, missing_chunk_index)



if (DEBUG):
    TEST_LIST = [0b11111111,0b11010101,0b11110011]
    print(TEST_LIST)

    P = (calculate_P(TEST_LIST))
    print("P",P, type(P))
    Q = (calculate_Q(TEST_LIST))
    print("Q",Q, type(Q))

    print("Recovered:",recover_one_chunk_with_P(TEST_LIST[:-1], P))
    print("Recovered:",recover_one_chunk_with_Q(TEST_LIST, Q, 2))


