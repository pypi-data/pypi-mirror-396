import zmq
import time
import torch
from tensordict import TensorDict
from transfer_queue.utils.zmq_utils import ZMQMessage, ZMQRequestType
from tensordict.tensorclass import NonTensorData
import random
import multiprocessing



# -------------------------- Server（ROUTER Socket） --------------------------
def router_server():
    context = zmq.Context()
    router_socket = context.socket(zmq.ROUTER)
    router_socket.bind("tcp://127.0.0.1:5555")
    print("ROUTER Server is ready, binding：tcp://127.0.0.1:5555")


    print("\n=== start communication（send_multipart/recv_multipart）===")
    messages = router_socket.recv_multipart()
    id = messages.pop(0)
    response_msg = ZMQMessage.deserialize(messages)
    print(response_msg)

    # Try to do in-place modification to see if it's allowed
    td = response_msg.body['data']
    print(f"Server解析数据::\n{td['strided']},\n{td['jagged']},\n{td['empty_tensor']},\n{td['nested']},\n{td['non_contiguous']}")
    print(f"Server连续性：{td['non_contiguous'].is_contiguous()}")
    # it's safe to do in-place modification even we set
    # arr = torch.frombuffer(buffer, dtype=torch.uint8)

    print(f"Server指针{td['strided'].data_ptr()}, {td['jagged'].data_ptr()}, {td['empty_tensor'].data_ptr()}, "
          f"{td['nested'].data_ptr()}, {td['non_contiguous'].data_ptr()}")
    router_socket.send_multipart([
        id,
        b"ack",
    ])


    time.sleep(1)
    router_socket.close()
    context.term()

# -------------------------- Client（DEALER Socket） --------------------------
def dealer_client():
    context = zmq.Context()
    dealer_socket = context.socket(zmq.DEALER)
    # set client identity
    dealer_socket.setsockopt_string(zmq.IDENTITY, "client_001")
    dealer_socket.connect("tcp://127.0.0.1:5555")
    print("DEALER Client is ready, connecting：tcp://127.0.0.1:5555")
    time.sleep(0.5)

    base = torch.randn(2, 10)
    non_contiguous = base[:, ::2]
    print(f"Client非连续张量连续性：{non_contiguous.is_contiguous()}")

    # Create TensorDict with different layouts
    td = TensorDict(
        {
            "strided": torch.randn(2, 5, 3),
            "jagged": torch.nested.as_nested_tensor([torch.randn(3, 4), torch.randn(2, 4)], layout=torch.jagged),
            "empty_tensor": torch.empty(2, 0),
            "nested": torch.nested.as_nested_tensor([torch.randn(4, 3), torch.randn(2, 4)], layout=torch.strided),
            "non_contiguous": non_contiguous,
        },
        batch_size=2,
    )
    print(f"Client原始数据:\n{td['strided']},\n{td['jagged']},\n{td['empty_tensor']},\n{td['nested']},\n{td['non_contiguous']}")
    print(f"Client连续性：{td['non_contiguous'].is_contiguous()}")
    # 打印原始数据的指针位置

    print(f"Client指针{td['strided'].data_ptr()}, {td['jagged'].data_ptr()}, {td['empty_tensor'].data_ptr()}, "
          f"{td['nested'].data_ptr()}, {td['non_contiguous'].data_ptr()}")


    request_msg = ZMQMessage.create(
        request_type=ZMQRequestType.PUT_DATA,
        sender_id='123',
        receiver_id='456',
        body={"data":td},
    )


    dealer_socket.send_multipart(request_msg.serialize(),copy=False)


    response_frames = dealer_socket.recv_multipart()
    response_frame1 = response_frames[0]
    print(f"DEALER Receive → Frame: {response_frame1}")

    dealer_socket.close()
    context.term()

# -------------------------- Start all processes --------------------------
if __name__ == "__main__":
    # Start server process
    server_process = multiprocessing.Process(target=router_server)
    server_process.start()
    time.sleep(0.5)

    # Start client process
    client_process = multiprocessing.Process(target=dealer_client)
    client_process.start()


    server_process.join()
    client_process.join()
    print("Test Finish！")