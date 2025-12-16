# distributed_coordinator.py
import argparse
import json
import os
import time
from datetime import datetime
import socket
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse

class CoordinatorServer(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.coordinator = kwargs.pop('coordinator', None)
        super().__init__(*args, **kwargs)
    
    # distributed_coordinator.py
    def do_POST(self):
        if self.path == '/register':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            node_id = data.get('node_id')
            ip = self.client_address[0]
            port = data.get('port')
            
            if node_id and port:
                self.coordinator.register_node(node_id, ip, port)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'status': 'registered', 'node_id': node_id}
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(400)
                self.end_headers()
        
        elif self.path == '/upload':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            node_id = data.get('node_id')
            file_name = data.get('file_name')
            stack_data = data.get('stack_data')
            
            if node_id and file_name and stack_data:
                self.coordinator.save_stack_data(node_id, file_name, stack_data)
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'status': 'saved', 'node_id': node_id, 'file_name': file_name}
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(400)
                self.end_headers()
                
        elif self.path == '/stop-all':
            # 通知所有已注册的节点停止服务
            results = self.coordinator.stop_all_nodes()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'stop_command_sent', 'results': results}
            self.wfile.write(json.dumps(response).encode())
    
    def do_GET(self):
        if self.path == '/trigger':
            # 触发所有节点采集
            self.coordinator.trigger_collection()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'status': 'triggered'}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/nodes':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'nodes': list(self.coordinator.nodes.keys())}
            self.wfile.write(json.dumps(response).encode())

class DistributedCoordinator:
    def __init__(self, host='0.0.0.0', port=8080, dump_path='/tmp/stack_data'):
        self.host = host
        self.port = port
        self.dump_path = Path(dump_path)
        self.dump_path.mkdir(parents=True, exist_ok=True)
        self.nodes = {}  # node_id -> {ip, port}
        self.server = None
        self.collection_id = None
        
    def register_node(self, node_id, ip, port):
        """注册节点，支持重复注册并检查是否所有节点都已注册"""
        # 检查节点是否已经注册
        if node_id in self.nodes:
            old_info = self.nodes[node_id]
            print(f"节点 {node_id} 已经注册过，旧信息: {old_info['ip']}:{old_info['port']}，"
              f"新信息: {ip}:{port}")
        
            # 如果IP或端口不同，通知旧节点停止服务
            if old_info['ip'] != ip or old_info['port'] != port:
                try:
                    # 向旧节点发送停止命令
                    stop_url = f"http://{old_info['ip']}:{old_info['port']}/stop-local"
                    data = json.dumps({}).encode()
                    req = urllib.request.Request(stop_url, data=data, 
                                            headers={'Content-Type': 'application/json'})
                    urllib.request.urlopen(req, timeout=10)
                    print(f"已通知旧节点 {node_id} ({old_info['ip']}:{old_info['port']}) 停止服务")
                except Exception as e:
                    print(f"通知旧节点 {node_id} 停止服务失败: {e}")
            
            print(f"新信息将覆盖旧信息")
        else:
            print(f"新节点 {node_id} 注册: {ip}:{port}")
        
        # 更新或添加节点信息
        self.nodes[node_id] = {'ip': ip, 'port': port}
        print(f"节点 {node_id} 注册成功: {ip}:{port}")
        
        # 检查是否所有节点都已经注册
        world_size = os.environ.get("WORLD_SIZE")
        if world_size:
            try:
                world_size = int(world_size)
                if len(self.nodes) == world_size:
                    print(f"所有节点均已注册成功，总共 {world_size} 个节点")
                elif len(self.nodes) > world_size:
                    print(f"警告: 注册的节点数 {len(self.nodes)} 超过了 WORLD_SIZE {world_size}")
            except ValueError:
                # WORLD_SIZE 不是有效整数
                pass
        
    # distributed_coordinator.py
    def save_stack_data(self, node_id, file_name, stack_data):
        """保存节点堆栈数据（保持原有文件结构）"""
        # 如果有 collection_id，则创建带有 ID 的目录
        if self.collection_id:
            node_dir = self.dump_path / f"collection_{self.collection_id}"
        else:
            # 兼容没有 collection_id 的情况
            node_dir = self.dump_path
            
        node_dir.mkdir(parents=True, exist_ok=True)
        
        # 使用原始文件名保存
        filepath = node_dir / file_name
        
        with open(filepath, 'w') as f:
            json.dump(stack_data, f, indent=2)
        
        print(f"节点 {node_id} 的堆栈数据已保存到 {filepath}")
        
    def trigger_collection(self):
        """触发所有节点进行堆栈采集"""
        self.collection_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"触发所有节点采集，ID: {self.collection_id}")
        
        for node_id, node_info in self.nodes.items():
            try:
                url = f"http://{node_info['ip']}:{node_info['port']}/collect"
                data = json.dumps({'collection_id': self.collection_id}).encode()
                req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
                urllib.request.urlopen(req, timeout=30)
                print(f"已通知节点 {node_id} 开始采集")
            except Exception as e:
                print(f"通知节点 {node_id} 失败: {e}")
    def stop_all_nodes(self):
        """通知所有节点停止服务"""
        results = {}
        
        print("正在通知所有节点停止服务...")
        
        for node_id, node_info in self.nodes.items():
            try:
                url = f"http://{node_info['ip']}:{node_info['port']}/stop-local"
                data = json.dumps({}).encode()
                req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
                urllib.request.urlopen(req, timeout=10)
                results[node_id] = 'success'
                print(f"已通知节点 {node_id} 停止服务")
            except Exception as e:
                results[node_id] = f'failed: {str(e)}'
                print(f"通知节点 {node_id} 停止服务失败: {e}")
        
        return results            
    def start_server(self):
        """启动协调服务"""
        def handler_factory(*args, **kwargs):
            return CoordinatorServer(*args, coordinator=self, **kwargs)
            
        self.server = HTTPServer((self.host, self.port), handler_factory)
        print(f"协调服务启动在 {self.host}:{self.port}")
        self.server.serve_forever()
        
    def stop_server(self):
        """停止协调服务"""
        if self.server:
            self.server.shutdown()

def main():
    parser = argparse.ArgumentParser(description="分布式堆栈采集协调服务")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    parser.add_argument("--port", type=int, default=8080, help="监听端口")
    parser.add_argument("--dump-path", default="/tmp/stack_data", help="数据保存路径")
    
    args = parser.parse_args()
    
    coordinator = DistributedCoordinator(args.host, args.port, args.dump_path)
    try:
        coordinator.start_server()
    except KeyboardInterrupt:
        print("协调服务已停止")
        coordinator.stop_server()

if __name__ == "__main__":
    main()