#!/usr/bin/env python3
# process_tree_flame_generator.py

import argparse
import json
import os
import sys
from pathlib import Path
from collections import defaultdict


class ProcessTrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_process = False
        self.ranks = set()  # 存储经过此节点的所有rank


class ProcessTrie:
    def __init__(self, all_ranks):
        self.root = ProcessTrieNode()
        self.all_ranks = all_ranks

    def insert(self, words, rank):
        node = self.root
        for word in words:
            if word not in node.children:
                node.children[word] = ProcessTrieNode()
            node = node.children[word]
            node.ranks.add(rank)
        node.is_end_of_process = True
        node.ranks.add(rank)

    def _format_rank_str(self, ranks):
        leak_ranks = list(self.all_ranks - set(ranks))
        ranks = list(ranks)

        def _inner_format(ranks):
            """折叠连续的ranks, [0,1,2,5,6,7]->[0-2,5-7]"""
            ranks = sorted(ranks)
            str_buf = []
            low = 0
            high = 0
            total = len(ranks)
            while high < total - 1:
                low_value = ranks[low]
                high_value = ranks[high]
                while high < total - 1 and high_value + 1 == ranks[high + 1]:
                    high += 1
                    high_value = ranks[high]
                low = high + 1
                high += 1
                if low_value != high_value:
                    str_buf.append(f"{low_value}-{high_value}")
                else:
                    str_buf.append(str(low_value))
            if high == total - 1:
                str_buf.append(str(ranks[high]))
            return "/".join(str_buf)

        has_process_ranks = _inner_format(ranks)
        leak_process_ranks = _inner_format(leak_ranks)
        return f"@{'|'.join([has_process_ranks, leak_process_ranks])}"

    def _traverse_with_all_processes(self, node, path):
        for word, child in node.children.items():
            rank_str = self._format_rank_str(child.ranks)
            if child.is_end_of_process:
                yield ";".join(path + [word]) + rank_str
            word += rank_str
            yield from self._traverse_with_all_processes(child, path + [word])

    def __iter__(self):
        yield from self._traverse_with_all_processes(self.root, [])


def load_process_data(dump_path):
    """加载所有进程树数据"""
    child_processes_path = dump_path
    if not os.path.exists(child_processes_path):
        raise FileNotFoundError(f"未找到进程树数据目录: {child_processes_path}")
    
    process_files = list(Path(child_processes_path).glob("*.processdata"))
    process_data = []
    
    for process_file in process_files:
        try:
            with open(process_file, 'r') as f:
                data = json.load(f)
                process_data.append(data)
        except Exception as e:
            print(f"加载文件 {process_file} 时出错: {e}")
    
    return process_data


def process_tree_to_flame_data(process_data, output_path):
    """将进程树数据转换为火焰图数据"""
    if not process_data:
        print("没有找到进程树数据文件")
        return

    # 获取world_size
    first_data = process_data[0]
    world_size = first_data.get('world_size', 1)
    all_ranks = set(range(world_size))

    # 创建trie树
    process_trie = ProcessTrie(all_ranks)

    # 处理每个进程文件
    for data in process_data:
        rank = data['rank']
        
        # 处理进程树数据，构建完整的父子关系链条
        def traverse_process_tree(node, path=[]):
            name = node.get('name', 'unknown')
            state = node.get('state', 'Unknown')
            
            # 构造进程节点标识，只包含进程名和状态，不包含PID以支持聚合
            process_node = f"{name}({state})"
            current_path = path + [process_node]
            
            # 插入到trie树
            process_trie.insert(current_path, rank)
            
            # 递归处理子进程
            for child in node.get('children', []):
                traverse_process_tree(child, current_path)
        
        # 从根进程开始遍历整个进程树（更新数据结构访问方式）
        root_process = data['process_tree']
        traverse_process_tree(root_process)

    # 生成输出文件
    flame_file = os.path.join(output_path, "process_tree_flame.txt")
    try:
        with open(flame_file, 'w') as f:
            count = 0
            for process_line in process_trie:
                if process_line and not process_line.startswith(';'):
                    # 确保每行都以" 1"结尾
                    if not process_line.endswith(" 1"):
                        process_line = process_line + " 1"
                    f.write(f"{process_line}\n")
                    count += 1
            print(f"进程树火焰图数据已保存到: {flame_file} (共{count}行)")
    except Exception as e:
        print(f"保存进程树火焰图数据时出错: {e}")
        
    # 生成火焰图
    svg_file = os.path.join(output_path, "process_tree_flame.svg")
    try:
        os.system(
            "flamegraph.pl --color python --width 1600 --title "
            f"'Process Tree Hierarchy' < {flame_file} "
            f"> {svg_file}"
        )
        print(f"进程树火焰图已保存到: {svg_file}")
    except Exception as e:
        print(f"生成火焰图时出错: {e}")



def generate_detailed_process_report(process_data, output_path):
    """生成详细的进程报告，展示层次结构"""
    report_file = os.path.join(output_path, "process_tree_detailed_report.txt")
    
    with open(report_file, 'w') as f:
        f.write("详细进程树分析报告\n")
        f.write("=" * 60 + "\n\n")
        
        total_processes = 0
        state_stats = defaultdict(int)
        name_stats = defaultdict(int)
        
        for data in sorted(process_data, key=lambda x: x['rank']):
            rank = data['rank']
            world_size = data['world_size']
            f.write(f"Rank {rank} (World Size: {world_size}):\n")
            
            def report_processes_with_hierarchy(node, level=1):
                nonlocal total_processes
                total_processes += 1
                
                name = node.get('name', 'unknown')
                state = node.get('state', 'Unknown')
                pid = node.get('pid', 'unknown')
                
                state_stats[state] += 1
                name_stats[name] += 1
                
                indent = "  " * level
                f.write(f"{indent}- {name} (PID: {pid}, State: {state})\n")
                
                for child in node.get('children', []):
                    report_processes_with_hierarchy(child, level + 1)
            
            # 更新数据结构访问方式
            root_process = data['process_tree']
            report_processes_with_hierarchy(root_process)
            f.write("\n")
        
        f.write(f"总计进程数: {total_processes}\n\n")
        f.write("进程状态统计:\n")
        f.write("-" * 20 + "\n")
        for state, count in sorted(state_stats.items(), key=lambda x: x[1], reverse=True):
            f.write(f"  {state}: {count}\n")
        
        f.write("\n进程类型统计:\n")
        f.write("-" * 20 + "\n")
        for name, count in sorted(name_stats.items(), key=lambda x: x[1], reverse=True):
            f.write(f"  {name}: {count}\n")
    
    print(f"详细进程树报告已保存到: {report_file}")


def main():
    parser = argparse.ArgumentParser(description="处理进程树数据并生成火焰图")
    parser.add_argument("--dump-path", "-p", type=str, default="/tmp/tt", 
                       help="进程数据路径（默认: /tmp/tt）")
    parser.add_argument("--output-dir", "-o", type=str, 
                       help="输出目录（默认与输入路径相同）")
    
    args = parser.parse_args()
    
    dump_path = Path(args.dump_path)
    if not dump_path.exists():
        print(f"路径 {dump_path} 不存在")
        return 1
    
    # 设置输出目录
    output_dir = args.output_dir if args.output_dir else str(dump_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # 加载进程数据
        print("正在加载进程树数据...")
        process_data = load_process_data(str(dump_path))
        if not process_data:
            print(f"在路径 {dump_path} 中未找到任何.processdata文件")
            return 1
        print(f"成功加载 {len(process_data)} 个进程的数据")
        
        # 生成层次结构火焰图数据
        process_tree_to_flame_data(process_data, str(output_path))

        # 生成详细报告
        generate_detailed_process_report(process_data, str(output_path))
        
    except Exception as e:
        print(f"处理过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())