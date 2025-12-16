import socket
import json
import universe
import torch
import zlib
import gzip
import time
import pickle

def Eval_mult(key, masked_x, masked_y):
    b, rxb_u32, ryb_u32, rxyb_u32 = key
    return universe.sub(universe.add(b*universe.mult(masked_x,masked_y),rxyb_u32),universe.add(universe.mult(masked_x,ryb_u32),universe.mult(masked_y,rxb_u32)))

def Eval_DPF(key, input_u32):
    n = 32
    # Line 1
    b, s_b_0, cw = key
    party_s_b = [s_b_0]
    input_binary_representation = universe.u32_to_binary_list(input_u32)
    party_t_b = [b]
    # Line 2
    for i in range(1,n+1):
        # Line 3
        s_cw, t_cwL, t_cwR = cw[i-1]
        # Line 4 & 5
        s_hatL, t_hatL, s_hatR, t_hatR = universe.split_dpf(universe.pnrg_dpf(bytes.fromhex(party_s_b[i-1])).hex())
        t_hatL = int(t_hatL, 16) % 2
        t_hatR = int(t_hatR, 16) % 2
        if party_t_b[i-1] == 1:
            s_L = universe.strhex_xor(s_hatL, s_cw)
            t_L = t_hatL ^ t_cwL
            s_R = universe.strhex_xor(s_hatR, s_cw)
            t_R = t_hatR ^ t_cwR
        else:
            s_L = s_hatL
            t_L = t_hatL
            s_R = s_hatR
            t_R = t_hatR
        # Line 6 & 7
        if input_binary_representation[i-1] == 0:
            party_s_b.append(s_L)
            party_t_b.append(t_L)
        else:
            party_s_b.append(s_R)
            party_t_b.append(t_R)
    # Line 10
    if party_t_b[n] == 1:
        party_share_b = universe.add(universe.convert(bytes.fromhex(party_s_b[n])), cw[n])
    else:
        party_share_b = universe.convert(bytes.fromhex(party_s_b[n]))
    if b == 1:
        party_share_b = universe.neg(party_share_b)
    return party_share_b

def Eval_DCF(key, input_u32):
    n = 32
    # Line 1
    b, s_b_0, cw = key
    party_s_b = [s_b_0]
    #input_u32 = universe.float2fix(input)
    input_binary_representation = universe.u32_to_binary_list(input_u32)
    party_V = 0
    party_t_b = [b]

    # Line 2
    for i in range(1,n+1):
        # Line 3
        s_cw,V_cw,t_cwL,t_cwR = cw[i-1]
        # Line 4
        s_hatL, v_hatL, t_hatL, s_hatR, v_hatR, t_hatR = universe.split_dcf(universe.pnrg_dcf(bytes.fromhex(party_s_b[i-1])).hex())
        t_hatL = int(t_hatL, 16) % 2
        t_hatR = int(t_hatR, 16) % 2
        # Line 5 & 6
        if party_t_b[i-1] == 1:
            s_L = universe.strhex_xor(s_hatL, s_cw)
            t_L = t_hatL ^ t_cwL
            s_R = universe.strhex_xor(s_hatR, s_cw)
            t_R = t_hatR ^ t_cwR
        else:
            s_L = s_hatL
            t_L = t_hatL
            s_R = s_hatR
            t_R = t_hatR
        # Line 7 & 8 & 9 & 10
        if input_binary_representation[i-1] == 0:
            line_7_result = universe.convert(bytes.fromhex(v_hatL))
            party_s_b.append(s_L)
            party_t_b.append(t_L)
        else:
            line_7_result = universe.convert(bytes.fromhex(v_hatR))
            party_s_b.append(s_R)
            party_t_b.append(t_R)
        if party_t_b[i-1] == 1:
            line_7_result = universe.add(line_7_result, V_cw)
        line_7_result = universe.add(line_7_result, party_t_b[i-1]*V_cw)
        if b == 0:
            party_V = universe.add(party_V, line_7_result)
        else:
            party_V = universe.sub(party_V, line_7_result)
    # Line 13
    line_13_result = universe.convert(bytes.fromhex(party_s_b[n]))
    if party_t_b[n]:
        line_13_result = universe.add(line_13_result, cw[n])
    if b == 0:
        party_V = universe.add(party_V, line_13_result)
    else:
        party_V = universe.sub(party_V, line_13_result)
    return party_V

def Eval_DDCF(key, input_u32):
    key_b, S_b = key
    result = Eval_DCF(key=key_b, input_u32=input_u32)
    return universe.add(result, S_b)

def Eval_SC(key, input_u32):
    z0_u32 = universe.u32_mod_31(input_u32)
    a = (2**31)-1
    m_32 = Eval_DDCF(key, universe.sub(a, z0_u32))
    b = key[0][0] # key -> Eval_DDCF's key -> Eval_DCF's key
    result = b * universe.u32_msb(input_u32)
    result = universe.add(result, m_32)
    result = universe.sub(result, (2*universe.u32_msb(input_u32)*m_32)%(2**32))
    return universe.sub(b, result)

def reliable_connect(host, port, retries=5, delay=0.1):
    for attempt in range(retries):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            return sock
        except socket.error as e:
            #print(f"连接失败({attempt+1}/{retries})，原因: {e}")
            time.sleep(delay)
    raise Exception("无法连接服务器，尝试次数超过限制")

def parties_comm(message_to_party_0, comm_host, comm_port, idx):
    chunk_size = 1024*4
    #p1_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #p1_socket.connect((comm_host, comm_port))
    p1_socket = reliable_connect(comm_host, comm_port)
    message_from_party_0_length = int.from_bytes(p1_socket.recv(4), 'big')
#     message_from_party_0 = p1_socket.recv(message_from_party_0_length).decode()
    message_from_party_0 = receive_all(p1_socket, message_from_party_0_length, chunk_size)
#     message_from_party_0 = json.loads(message_from_party_0)
    message_from_party_0 = json.loads(message_from_party_0.decode())

    message_to_party_0 = json.dumps(message_to_party_0).encode()
    message_to_party_0_length = len(message_to_party_0).to_bytes(4, 'big')
    print(f"{idx}-th communication, online comm, party1 sends to party0: {int.from_bytes(message_to_party_0_length, byteorder='big')} bytes")
    #time.sleep(0.02) #20ms latency
    #time.sleep(0.2) #200ms latency
    #time.sleep(int.from_bytes(message_to_party_0_length, byteorder='big') / (100*1000000)) # 100 Mbps
    #p1_socket.send(message_to_party_0_length + message_to_party_0) #message_to_party_0.encode()
    p1_socket.send(message_to_party_0_length)
    for i in range(0, len(message_to_party_0), chunk_size):
        p1_socket.send(message_to_party_0[i:i + chunk_size])
    p1_socket.close()
    return message_from_party_0

def receive_all(sock, length, chunk_size = 4096):
    data = b''
    while len(data) < length:
        packet = sock.recv(min(length - len(data), chunk_size))  # Receive up to 4KB at a time
        if not packet:
            raise ValueError("Socket connection broken or incomplete data")
        data += packet
    return data

if __name__ == "__main__":
    #hyperparameter
    buffer_size = 1048576 * 10  # 10MB
    p_length = 400
    E = [(i, j) for i in range(0, p_length) for j in range(i+1, p_length)]

    # Offline, set up party socket
    client_host, client_port = '127.0.0.1', 12345
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buffer_size)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)
    client_socket.connect((client_host, client_port))
    message_length = int.from_bytes(client_socket.recv(4), 'big')
    message = receive_all(client_socket, message_length, chunk_size=16384)
    message = json.loads(zlib.decompress(message).decode('utf-8'))
    client_socket.close()
    random_values_sorting, keys_list_sorting, random_values_routing, keys_list_routing, masked_q_mult, keys_list_mult = message

    # Online-1, reveal and mask
    # 1. Initialize share of confidence vectors
    random_values, keys_list = random_values_sorting, keys_list_sorting
    p_1 = torch.zeros_like(torch.rand(1,p_length))
    p_1 = p_1.tolist()[0]
    start_time = time.time()
    # 2. mask locally
    for i in range(p_length):
        p_1[i] = random_values[i]
    # 3. transmit the message
    p_0 = parties_comm(message_to_party_0 = p_1, comm_host='127.0.0.1', comm_port=54321, idx=1)
    # 4. reveal the masked value
    p_hat = []
    for i in range(p_length):
        p_hat.append(universe.add(p_0[i], p_1[i]))

    # Online-2, SHAMP-sorting
    rank = [0 for _ in range(p_length)]
    for k in range(len(E)):
        i,j = E[k]
        p1_result = Eval_SC(key=keys_list[k], input_u32=universe.sub(p_hat[i], p_hat[j]))
        rank[i] = universe.add(rank[i], p1_result)
        rank[j] = universe.add(rank[j], universe.sub(1, p1_result))
    #print(rank)
    #end_time = time.time()
    #print(f"online sorting running time: {end_time - start_time:.6f} seconds")

    # Online-3, DPF routing
    #start_time = time.time()
    random_values, keys_list = random_values_routing, keys_list_routing
    p_1 = rank
    for i in range(p_length):
        r_u32 = random_values[i]
        p_1[i] = universe.add(p_1[i], r_u32)
    p_0 = parties_comm(message_to_party_0 = p_1, comm_host='127.0.0.1', comm_port=54321, idx=2)
    rank_hat = []
    for i in range(p_length):
        rank_hat.append(universe.add(p_0[i], p_1[i]))

    m_ij_1_list = []
    for i in range(p_length):
        for j in range(p_length):
            m_ij = Eval_DPF(key=keys_list[i], input_u32=universe.sub(rank_hat[i],j))
            #print(i,j,m_ij)
            sel_idex = i*p_length + j
            masked_m_ij_1 = universe.add(keys_list_mult[sel_idex][1],m_ij)
            m_ij_1_list.append(masked_m_ij_1)
    m_ij_0_list = parties_comm(message_to_party_0 = m_ij_1_list, comm_host='127.0.0.1', comm_port=54321, idx=3)

    q_prime = []
    for i in range(p_length):
        q_prime.append(0)
        for j in range(p_length):
            sel_idex = i*p_length + j
            masked_m_ij = universe.add(m_ij_0_list[sel_idex],m_ij_1_list[sel_idex])
            masked_q_j = masked_q_mult[sel_idex]
            # Evaluate Mult
            q_prime_ij = Eval_mult(key=keys_list_mult[sel_idex],masked_x=masked_m_ij,masked_y=masked_q_j)
            q_prime[i] = universe.add(q_prime[i],q_prime_ij)
    #end_time = time.time()
    #print(f"online selecting running time: {end_time - start_time:.6f} seconds")
    #print(q_prime)
    end_time = time.time()
    print(f"online 1 running time: {end_time - start_time:.6f} seconds")
    print('party1 ends')