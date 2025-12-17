"""
验证 ws-robot 包是否正确构建和安装的脚本
"""

import sys
import importlib


def print_success(msg):
    print(f"✓ {msg}")


def print_error(msg):
    print(f"✗ {msg}")


def print_info(msg):
    print(f"ℹ {msg}")


def check_import(module_name, class_name=None):
    """检查模块是否可以导入"""
    try:
        module = importlib.import_module(module_name)
        if class_name:
            if hasattr(module, class_name):
                print_success(f"Can import {class_name} from {module_name}")
                return True
            else:
                print_error(f"Cannot find {class_name} in {module_name}")
                return False
        else:
            print_success(f"Can import {module_name}")
            return True
    except ImportError as e:
        print_error(f"Cannot import {module_name}: {e}")
        return False


def main():
    print("=" * 60)
    print("WS-Robot Package Verification")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # 检查主包
    print_info("Checking main package...")
    if not check_import("ws_robot"):
        all_passed = False
        print_error("Main package import failed!")
        return 1
    
    print()
    
    # 检查各个模块
    print_info("Checking submodules...")
    modules = [
        ("ws_robot", "WebSocketMessage"),
        ("ws_robot", "WebSocketOperation"),
        ("ws_robot", "WebSocketConstants"),
        ("ws_robot", "WebSocketRobotClient"),
        ("ws_robot", "WebSocketRobotManager"),
        ("ws_robot", "WebSocketRobotInstance"),
        ("ws_robot", "RobotAPIBody"),
    ]
    
    for module_name, class_name in modules:
        if not check_import(module_name, class_name):
            all_passed = False
    
    print()
    
    # 检查版本
    print_info("Checking version...")
    try:
        import ws_robot
        version = getattr(ws_robot, "__version__", "unknown")
        print_success(f"Package version: {version}")
    except Exception as e:
        print_error(f"Cannot get version: {e}")
        all_passed = False
    
    print()
    
    # 检查依赖
    print_info("Checking dependencies...")
    try:
        import websocket
        print_success("websocket-client is installed")
    except ImportError:
        print_error("websocket-client is not installed")
        all_passed = False
    
    print()
    
    # 检查基本功能
    print_info("Checking basic functionality...")
    try:
        from ws_robot import (
            WebSocketMessage,
            WebSocketOperation,
            RobotAPIBody
        )
        
        # 创建一个消息
        msg = WebSocketMessage.create_request(
            WebSocketOperation.GET_STATUS,
            "test_request_id",
            {"test": "data"}
        )
        if msg.operation == "GET_STATUS" and msg.requestId == "test_request_id":
            print_success("WebSocketMessage works correctly")
        else:
            print_error("WebSocketMessage not working as expected")
            all_passed = False
        
        # 创建一个 API body
        api_body = RobotAPIBody()
        data = api_body.gen_create_data(
            appId="test_app",
            cname="test_channel",
            user="test_user",
            uid=12345
        )
        if data["appId"] == "test_app" and data["uid"] == 12345:
            print_success("RobotAPIBody works correctly")
        else:
            print_error("RobotAPIBody not working as expected")
            all_passed = False
            
    except Exception as e:
        print_error(f"Basic functionality check failed: {e}")
        all_passed = False
    
    print()
    print("=" * 60)
    
    if all_passed:
        print_success("All checks passed! Package is ready to use.")
        print()
        print_info("Quick start:")
        print("  from ws_robot import WebSocketRobotClient, WebSocketRobotManager")
        print("  # See example.py for more details")
        return 0
    else:
        print_error("Some checks failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

