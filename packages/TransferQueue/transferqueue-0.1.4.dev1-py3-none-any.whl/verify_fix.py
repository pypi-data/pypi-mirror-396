#!/usr/bin/env python
"""
验证脚本：测试单元素nested tensor的序列化/反序列化修复

此脚本验证了在TQ_ZERO_COPY_SERIALIZATION=True时，
序列化只有1个tensor的nested tensor能够正确区分于普通tensor。
"""

import os
import torch
from tensordict import TensorDict

# 启用零拷贝序列化
os.environ["TQ_ZERO_COPY_SERIALIZATION"] = "True"

from transfer_queue.utils.zmq_utils import ZMQMessage, ZMQRequestType

def test_single_nested_tensor_fix():
    """验证单元素nested tensor修复"""
    print("=" * 80)
    print("测试：单元素nested tensor序列化/反序列化修复")
    print("=" * 80)

    # 创建单元素nested tensor和普通tensor
    single_nested = torch.nested.as_nested_tensor([torch.randn(4, 3)], layout=torch.strided)
    normal_tensor = torch.randn(1, 4, 3)

    print("\n1. 创建测试数据：")
    print(f"   - 单元素nested tensor: {single_nested.shape}, is_nested={single_nested.is_nested}")
    print(f"   - 普通tensor: {normal_tensor.shape}, is_nested={normal_tensor.is_nested}")

    # 创建TensorDict
    td = TensorDict(
        {
            "single_nested_tensor": single_nested,
            "normal_tensor": normal_tensor,
        },
        batch_size=1,
    )

    print("\n2. 创建ZMQMessage并序列化：")
    msg = ZMQMessage(
        request_type=ZMQRequestType.PUT_DATA,
        sender_id="test_sender",
        receiver_id="test_receiver",
        body={"data": td},
    )

    # 序列化
    serialized_data = msg.serialize()
    print(f"   - 序列化完成，数据列表长度: {len(serialized_data)}")

    # 反序列化
    print("\n3. 反序列化数据：")
    decoded_msg = ZMQMessage.deserialize(serialized_data)

    print(f"   - 反序列化完成")
    print(f"   - decoded_msg.body['data']['single_nested_tensor'].is_nested = {decoded_msg.body['data']['single_nested_tensor'].is_nested}")
    print(f"   - decoded_msg.body['data']['normal_tensor'].is_nested = {decoded_msg.body['data']['normal_tensor'].is_nested}")

    # 验证结果
    print("\n4. 验证结果：")
    success = True

    # 检查单元素nested tensor
    if decoded_msg.body["data"]["single_nested_tensor"].is_nested:
        print("   ✓ 单元素nested tensor正确保持为nested类型")
    else:
        print("   ✗ 单元素nested tensor错误地变成了普通tensor类型")
        success = False

    # 检查普通tensor
    if not decoded_msg.body["data"]["normal_tensor"].is_nested:
        print("   ✓ 普通tensor正确保持为普通tensor类型")
    else:
        print("   ✗ 普通tensor错误地变成了nested类型")
        success = False

    # 检查数据内容
    import torch
    if torch.allclose(
        decoded_msg.body["data"]["single_nested_tensor"][0],
        single_nested[0]
    ):
        print("   ✓ 单元素nested tensor数据内容正确")
    else:
        print("   ✗ 单元素nested tensor数据内容不正确")
        success = False

    if torch.allclose(
        decoded_msg.body["data"]["normal_tensor"],
        normal_tensor
    ):
        print("   ✓ 普通tensor数据内容正确")
    else:
        print("   ✗ 普通tensor数据内容不正确")
        success = False

    print("\n" + "=" * 80)
    if success:
        print("✓ 所有测试通过！修复有效。")
    else:
        print("✗ 测试失败！修复可能存在问题。")
    print("=" * 80)

    return success

if __name__ == "__main__":
    test_single_nested_tensor_fix()
