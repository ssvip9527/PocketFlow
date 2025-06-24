from pocketflow import AsyncNode, AsyncFlow
import asyncio


# 定义支付节点
class ValidatePayment(AsyncNode):
    async def exec_async(self, prep_res):
        print("1.1.正在验证支付...")
        return "支付验证成功"

    async def post_async(self, shared, prep_res, exec_res):
        shared["payment_status"] = exec_res
        return "default"


class ProcessPayment(AsyncNode):
    async def exec_async(self, prep_res):
        print("1.2.正在处理支付...")
        return "支付处理成功"

    async def post_async(self, shared, prep_res, exec_res):
        shared["payment_result"] = exec_res
        return "default"


class PaymentConfirmation(AsyncNode):
    async def exec_async(self, prep_res):
        print("1.3.正在确认支付...")
        return "支付已确认"

    async def post_async(self, shared, prep_res, exec_res):
        shared["payment_confirmation"] = exec_res
        return "default"


# 定义库存节点
class CheckStock(AsyncNode):
    async def exec_async(self, prep_res):
        print("2.1.正在检查库存...")
        return "库存可用"

    async def post_async(self, shared, prep_res, exec_res):
        shared["stock_status"] = exec_res
        return "default"


class ReserveItems(AsyncNode):
    async def exec_async(self, prep_res):
        print("2.2.正在预留商品...")
        return "商品已预留"

    async def post_async(self, shared, prep_res, exec_res):
        shared["reservation_status"] = exec_res
        return "default"


class UpdateInventory(AsyncNode):
    async def exec_async(self, prep_res):
        print("2.3. 正在更新库存...")
        return "库存已更新"

    async def post_async(self, shared, prep_res, exec_res):
        shared["inventory_update"] = exec_res
        return "default"


# 定义发货节点
class CreateLabel(AsyncNode):
    async def exec_async(self, prep_res):
        print("3.1 正在创建发货标签...")
        return "发货标签已创建"

    async def post_async(self, shared, prep_res, exec_res):
        shared["shipping_label"] = exec_res
        return "default"


class AssignCarrier(AsyncNode):
    async def exec_async(self, prep_res):
        print("3.2 正在分配承运商...")
        return "承运商已分配"

    async def post_async(self, shared, prep_res, exec_res):
        shared["carrier"] = exec_res
        return "default"


class SchedulePickup(AsyncNode):
    async def exec_async(self, prep_res):
        print("3.3 正在安排取件...")
        return "取件已安排"

    async def post_async(self, shared, prep_res, exec_res):
        shared["pickup_status"] = exec_res
        return "default"


# 创建节点实例
validate_payment = ValidatePayment()
process_payment = ProcessPayment()
payment_confirmation = PaymentConfirmation()

check_stock = CheckStock()
reserve_items = ReserveItems()
update_inventory = UpdateInventory()

create_label = CreateLabel()
assign_carrier = AssignCarrier()
schedule_pickup = SchedulePickup()

# 支付处理子流程
validate_payment >> process_payment >> payment_confirmation
payment_flow = AsyncFlow(start=validate_payment)

# 库存子流程
check_stock >> reserve_items >> update_inventory
inventory_flow = AsyncFlow(start=check_stock)

# 发货子流程
create_label >> assign_carrier >> schedule_pickup
shipping_flow = AsyncFlow(start=create_label)

# 将子流程连接到主订单管道
payment_flow >> inventory_flow >> shipping_flow
# payment_flow >> inventory_flow >> create_label
# payment_flow >> inventory_flow >> assign_carrier


# 创建主流程
class OrderFlow(AsyncFlow):
    pass


order_pipeline = OrderFlow(start=payment_flow)

# 创建共享数据结构
shared_data = {
    "order_id": "ORD-12345",
    "customer": "John Doe",
    "items": [
        {"id": "ITEM-001", "name": "智能手机", "price": 999.99, "quantity": 1},
        {"id": "ITEM-002", "name": "手机壳", "price": 29.99, "quantity": 1},
    ],
    "shipping_address": {
        "street": "主街123号",
        "city": "任意镇",
        "state": "加利福尼亚州",
        "zip": "12345",
    },
}


# 异步运行整个管道
async def main():
    await order_pipeline.run_async(shared_data)

    # 打印最终状态
    print("\n订单处理完成！")
    print(f"支付: {shared_data.get('payment_confirmation')}")
    print(f"库存: {shared_data.get('inventory_update')}")
    print(f"发货: {shared_data.get('pickup_status')}")


if __name__ == "__main__":
    asyncio.run(main())
