from flow import create_flow

def main():
    """运行通信示例。"""
    flow = create_flow()
    shared = {}
    flow.run(shared)

if __name__ == "__main__":
    main() 