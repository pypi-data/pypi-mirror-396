import socket
import universe
import os
import random
import json
import zlib
import torch
import time

def random_sample_split(r_u32):
    r0_u32 = random_gen()
    r1_u32 = universe.sub(r_u32, r0_u32)
    return r0_u32, r1_u32

def random_gen():
    seed = f"{random.getrandbits(128):032x}"
    return universe.convert(bytes.fromhex(seed))

def Gen_DCF(alpha_u32, beta_u32):
    #beta_u32 = universe.float2fix(beta)
    #alpha_u32 = universe.float2fix(alpha)
    alpha_binary_representation = universe.u32_to_binary_list(alpha_u32)
    #hyperparameter
    n = 32
    cw = []
    # Line-2
    s_0 = [f"{random.getrandbits(128):032x}"]
    s_1 = [f"{random.getrandbits(128):032x}"]
    # Line-3
    V_alpha = universe.float2fix(0)
    t_0 = [0]
    t_1 = [1]
    # Line-4
    for i in range(1,n+1):
        # Line-5 & 6
        s_0L, v_0L, t_0L, s_0R, v_0R, t_0R = universe.split_dcf(universe.pnrg_dcf(bytes.fromhex(s_0[i-1])).hex())
        s_1L, v_1L, t_1L, s_1R, v_1R, t_1R = universe.split_dcf(universe.pnrg_dcf(bytes.fromhex(s_1[i-1])).hex())
        t_0L = int(t_0L, 16) % 2
        t_0R = int(t_0R, 16) % 2
        t_1L = int(t_1L, 16) % 2
        t_1R = int(t_1R, 16) % 2
        # Line - 7 & 8 & 9
        if alpha_binary_representation[i-1] == 0:
            s_0Keep, v_0Keep, t_0Keep, s_0Lose, v_0Lose, t_0Lose = s_0L, v_0L, t_0L, s_0R, v_0R, t_0R
            s_1Keep, v_1Keep, t_1Keep, s_1Lose, v_1Lose, t_1Lose = s_1L, v_1L, t_1L, s_1R, v_1R, t_1R
        else:
            s_0Lose, v_0Lose, t_0Lose, s_0Keep, v_0Keep, t_0Keep = s_0L, v_0L, t_0L, s_0R, v_0R, t_0R
            s_1Lose, v_1Lose, t_1Lose, s_1Keep, v_1Keep, t_1Keep = s_1L, v_1L, t_1L, s_1R, v_1R, t_1R
        # Line 10
        s_cw = universe.strhex_xor(s_0Lose,s_1Lose)
        # Line 11, line_11_result=V_CW
        convert_v_0Lose = universe.convert(bytes.fromhex(v_0Lose))
        convert_v_1Lose = universe.convert(bytes.fromhex(v_1Lose))
        line_11_result = universe.sub(convert_v_1Lose, convert_v_0Lose)
        line_11_result = universe.sub(line_11_result, V_alpha)
        if t_1[i-1] == 1:
            line_11_result = universe.neg(line_11_result)
        else:
            pass
        V_cw = line_11_result
        # Line 12 & 13
        if alpha_binary_representation[i-1] == 0: #Lose = R
            pass
        else: #Lose = L
            # beta_u32
            if t_1[i-1] == 1:
                V_cw = universe.sub(V_cw, beta_u32)
            else:
                V_cw = universe.add(V_cw, beta_u32)
        # Line 14
        V_alpha = universe.sub(V_alpha, universe.convert(bytes.fromhex(v_1Keep)))
        V_alpha = universe.add(V_alpha, universe.convert(bytes.fromhex(v_0Keep)))
        if t_1[i-1] == 1:
            V_alpha = universe.sub(V_alpha, V_cw)
        else:
            V_alpha = universe.add(V_alpha, V_cw)
        # Line 15
        #print(t_0L, t_1L, x_binary_representation[i-1])
        t_cwL = t_0L ^ t_1L ^ int(alpha_binary_representation[i-1]) ^ 1
        t_cwR = t_0R ^ t_1R ^ int(alpha_binary_representation[i-1]) ^ 0
        # Line 16
        cw.append([s_cw,V_cw,t_cwL,t_cwR])
        # Line 17
        if t_0[i-1] == 0: # correction not happened
            s_0.append(s_0Keep)
        else: # correction happened
            s_0.append(universe.strhex_xor(s_0Keep,s_cw))
        if t_1[i-1] == 0: # correction not happened
            s_1.append(s_1Keep)
        else: # correction happened
            s_1.append(universe.strhex_xor(s_1Keep,s_cw))
        # Line 18
        if alpha_binary_representation[i-1] == 0:
            #Keep = L
            t_cwKeep = t_cwL
        else:
            #Keep = R
            t_cwKeep = t_cwR
        if t_0[i-1] == 1: # correction happened
            t_0.append(t_0Keep ^ t_cwKeep)
        else: # correction not happened
            t_0.append(t_0Keep)
        if t_1[i-1] == 1: # correction happened
            t_1.append(t_1Keep ^ t_cwKeep)
        else: # correction not happened
            t_1.append(t_1Keep ^ 0)
    # Line 20
    line_20_result = universe.sub(universe.convert(bytes.fromhex(s_1[n])), universe.convert(bytes.fromhex(s_0[n])))
    line_20_result = universe.sub(line_20_result, V_alpha)
    if t_1[n] == 1:
        line_20_result = universe.neg(line_20_result)
    else:
        pass
    cw.append(line_20_result) #cw has the length of 33
    k0 = (0, s_0[0], cw)
    k1 = (1, s_1[0], cw)
    return k0, k1

def Gen_DDCF(alpha_u32, beta1_u32, beta2_u32):
    beta_u32 = universe.sub(beta1_u32, beta2_u32)
    #this is nive implementation
    S_0 = random_gen()
    S_1 = universe.sub(beta2_u32, S_0)
    k0, k1 = Gen_DCF(alpha_u32, beta_u32)
    return (k0, S_0), (k1, S_1)

def Gen_SC(randmask_u32):
    # Line 1
    y_u32 = universe.neg(randmask_u32)
    # Line 2
    z1_u32 = universe.u32_mod_31(y_u32)
    # Line 3
    y_msb_u32 = universe.u32_msb(y_u32)
    # The values of beta1_u32, beta1_u32 are either 1: u32 or 0: u32
    beta1_u32 = 1 ^ y_msb_u32 #universe.float2fix(1 ^ y_msb_u32)
    beta2_u32 = 0 ^ y_msb_u32 #universe.float2fix(0 ^ y_msb_u32)
    # Line 4
    k0, k1 = Gen_DDCF(alpha_u32=z1_u32, beta1_u32=beta1_u32, beta2_u32=beta2_u32)
    return k0, k1

def Gen_DPF(alpha_u32, beta_u32):
    #hyperparameter
    n = 32
    cw = []
    alpha_binary_representation = universe.u32_to_binary_list(alpha_u32)
    # Line - 2
    s_0 = [f"{random.getrandbits(128):032x}"]
    s_1 = [f"{random.getrandbits(128):032x}"]
    # Line - 3
    t_0 = [0]
    t_1 = [1]
    # Line-4
    for i in range(1,n+1):
        # Line - 5
        s_0L, t_0L, s_0R, t_0R = universe.split_dpf(universe.pnrg_dpf(bytes.fromhex(s_0[i-1])).hex())
        s_1L, t_1L, s_1R, t_1R = universe.split_dpf(universe.pnrg_dpf(bytes.fromhex(s_1[i-1])).hex())
        t_0L = int(t_0L, 16) % 2
        t_0R = int(t_0R, 16) % 2
        t_1L = int(t_1L, 16) % 2
        t_1R = int(t_1R, 16) % 2
        # Line - 6 & 7 & 8
        if alpha_binary_representation[i-1] == 0:
            s_0Keep, t_0Keep, s_0Lose, t_0Lose = s_0L, t_0L, s_0R, t_0R
            s_1Keep, t_1Keep, s_1Lose, t_1Lose = s_1L, t_1L, s_1R, t_1R
        else:
            s_0Lose, t_0Lose, s_0Keep, t_0Keep = s_0L, t_0L, s_0R, t_0R
            s_1Lose, t_1Lose, s_1Keep, t_1Keep = s_1L, t_1L, s_1R, t_1R
        # Line 9
        s_cw = universe.strhex_xor(s_0Lose,s_1Lose)
        # Line 10
        t_cwL = t_0L ^ t_1L ^ int(alpha_binary_representation[i-1]) ^ 1
        t_cwR = t_0R ^ t_1R ^ int(alpha_binary_representation[i-1])
        # Line 11
        cw.append([s_cw, t_cwL, t_cwR])
        # Line 12
        if t_0[i-1] == 0: # correction not happened
            s_0.append(s_0Keep)
        else:
            s_0.append(universe.strhex_xor(s_0Keep,s_cw))
        if t_1[i-1] == 0: # correction not happened
            s_1.append(s_1Keep)
        else: # correction happened
            s_1.append(universe.strhex_xor(s_1Keep,s_cw))
        # Line 13
        # first, let's generate variable t_cwKeep
        if alpha_binary_representation[i-1] == 0:
            #Keep = L
            t_cwKeep = t_cwL
        else:
            #Keep = R
            t_cwKeep = t_cwR
        if t_0[i-1] == 1: # correction happened
            t_0.append(t_0Keep ^ t_cwKeep)
        else: # correction not happened
            t_0.append(t_0Keep)
        if t_1[i-1] == 1: # correction happened
            t_1.append(t_1Keep ^ t_cwKeep)
        else: # correction not happened
            t_1.append(t_1Keep)
        # Line 14, end
    line_15_result = universe.sub(beta_u32, universe.convert(bytes.fromhex(s_0[n])))
    line_15_result = universe.add(line_15_result, universe.convert(bytes.fromhex(s_1[n])))
    if t_1[n] == 1:
        line_15_result = universe.neg(line_15_result)
    else:
        pass
    cw.append(line_15_result) #cw has the length of 33
    k0 = (0, s_0[0], cw)
    k1 = (1, s_1[0], cw)
    return k0, k1

def Gen_mult(rx_u32, ry_u32):
    # Line 1
    rx0_u32, rx1_u32 = random_sample_split(rx_u32)
    # Line 2
    ry0_u32, ry1_u32 = random_sample_split(ry_u32)
    # Line 3
    rxy_u32 = universe.mult(rx_u32, ry_u32)
    rxy0_u32, rxy1_u32 = random_sample_split(rxy_u32)
    return (0, rx0_u32, ry0_u32, rxy0_u32), (1, rx1_u32, ry1_u32, rxy1_u32)

def dealer_transfer(dealer_socket, message_to_p0, message_to_p1):
    chunk_size = 16384  # 4KB

    #send to party-0
    conn, addr = dealer_socket.accept()
    compressed_message_k0 = zlib.compress(json.dumps(message_to_p0).encode('utf-8'))
    message_length_k0 = len(compressed_message_k0).to_bytes(4, 'big')
    print(f"offline comm sends to party0: {int.from_bytes(message_length_k0, byteorder='big')} bytes")
    #time.sleep(0.02) #20ms latency
    #time.sleep(0.2) #200ms latency
    #time.sleep(int.from_bytes(message_length_k0, byteorder='big') / (100*1000000)) # 100 Mbps
    conn.send(message_length_k0)
    for i in range(0, len(compressed_message_k0), chunk_size):
        conn.send(compressed_message_k0[i:i + chunk_size])
    conn.close()

    #send to party-1
    conn, addr = dealer_socket.accept()
    compressed_message_k1 = zlib.compress(json.dumps(message_to_p1).encode('utf-8'))
    message_length_k1 = len(compressed_message_k1).to_bytes(4, 'big')
    print(f"offline comm sends to party1: {int.from_bytes(message_length_k1, byteorder='big')} bytes")
    #time.sleep(0.02) #20ms latency
    #time.sleep(0.2) #200ms latency
    #time.sleep(int.from_bytes(message_length_k1, byteorder='big') / (100*1000000)) # 100 Mbps
    conn.send(message_length_k1)
    for i in range(0, len(compressed_message_k1), chunk_size):
        conn.send(compressed_message_k1[i:i + chunk_size])
    conn.close()

if __name__ == "__main__":
    start_time = time.time()
    #hyperparameter
    buffer_size = 1048576 * 10  # 10MB
    p_length = 400
    E = [(i, j) for i in range(0, p_length) for j in range(i+1, p_length)]

    # Set up dealer socket
    dealer_host, dealer_port = '127.0.0.1', 12345
    dealer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dealer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buffer_size)
    dealer_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)
    dealer_socket.bind((dealer_host, dealer_port))
    dealer_socket.listen(2)

    message_to_p0, message_to_p1 = [[],[], [],[], [],[]], [[],[], [],[], [],[]]
    random_values = []
    #start_time = time.time()
    for _ in range(p_length):
        r_u32 = random_gen()
        r0_u32 = random_gen()
        r1_u32 = universe.sub(r_u32, r0_u32)
        message_to_p0[0].append(r0_u32)
        message_to_p1[0].append(r1_u32)
        random_values.append(r_u32)
    for e in E:
        i,j = e
        k0, k1 = Gen_SC(randmask_u32=universe.sub(random_values[i],random_values[j]))
        message_to_p0[1].append(k0)
        message_to_p1[1].append(k1)

    for i in range(p_length):
        r_u32 = random_gen()
        #print('mask',r_u32)
        r0_u32 = random_gen()
        r1_u32 = universe.sub(r_u32, r0_u32)
        k0, k1 = Gen_DPF(alpha_u32=r_u32, beta_u32=int(1))
        message_to_p0[2].append(r0_u32)
        message_to_p1[2].append(r1_u32)
        message_to_p0[3].append(k0)
        message_to_p1[3].append(k1)
    #end_time = time.time()
    #print(f"offline running time of sort: {end_time - start_time:.6f} seconds")

    q = torch.nn.Softmax(dim=1)(torch.rand(1,p_length))
    q = sorted(q.tolist()[0])
    #print('dealer computed', q)
    #start_time = time.time()
    for i in range(p_length):
        for j in range(p_length):
            rx_u32, ry_u32 = random_gen(), random_gen()
            k0, k1 = Gen_mult(rx_u32=rx_u32, ry_u32=ry_u32)
            # already masked value
            masked_q_j = universe.add(ry_u32,universe.float2fix(q[j]))
            message_to_p0[4].append(masked_q_j)
            message_to_p1[4].append(masked_q_j)
            # save mult keys
            message_to_p0[5].append(k0)
            message_to_p1[5].append(k1)

    #end_time = time.time()
    #print(f"offline running time of selection: {end_time - start_time:.6f} seconds")

    dealer_transfer(dealer_socket=dealer_socket,
                    message_to_p0=message_to_p0,
                    message_to_p1=message_to_p1)

    dealer_socket.close()
    end_time = time.time()
    print(f"offline running time: {end_time - start_time:.6f} seconds")