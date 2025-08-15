#!/usr/bin/env python3
"""
综合压力测试脚本
支持多种测试场景和详细的性能监控
"""

import os
import sys
import time
import json
import argparse
import subprocess
import threading
from datetime import datetime
import psutil
import matplotlib.pyplot as plt
import pandas as pd
from config import PROXY_CONFIG, TEST_SCENARIOS, MONITORING_CONFIG, REPORT_CONFIG


class ClashMetaStressTester:
    """Clash-Meta 综合压力测试器"""
    
    def __init__(self):
        self.monitoring = False
        self.stats = []
        self.test_results = {}
        self.start_time = None
        
    def run_test_scenario(self, scenario_name, custom_params=None):
        """运行指定的测试场景"""
        if scenario_name not in TEST_SCENARIOS and not custom_params:
            print(f"未知的测试场景: {scenario_name}")
            return False
            
        params = custom_params or TEST_SCENARIOS[scenario_name]
        
        print(f"\n=== 开始执行 {scenario_name} 测试场景 ===")
        print(f"用户数: {params['users']}")
        print(f"启动速率: {params['spawn_rate']}/秒")
        print(f"持续时间: {params['duration']}")
        
        # 构建locust命令
        cmd = [
            'locust',
            '-f', 'locustfile.py',
            '--host', 'http://localhost',
            '--users', str(params['users']),
            '--spawn-rate', str(params['spawn_rate']),
            '--run-time', params['duration'],
            '--headless',
            '--csv', f'results_{scenario_name}',
            '--html', f'report_{scenario_name}.html'
        ]
        
        # 启动监控
        self.start_monitoring()
        self.start_time = datetime.now()
        
        try:
            # 运行locust测试
            result = subprocess.run(cmd, capture_output=True, text=True, cwd='.')
            
            if result.returncode == 0:
                print(f"✅ {scenario_name} 测试完成")
                self.parse_test_results(scenario_name)
            else:
                print(f"❌ {scenario_name} 测试失败")
                print(f"错误输出: {result.stderr}")
                
        except Exception as e:
            print(f"执行测试时出错: {e}")
        finally:
            self.stop_monitoring()
            
        return True
    
    def start_monitoring(self):
        """启动系统监控"""
        self.monitoring = True
        self.stats = []
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print("📊 系统监控已启动")
    
    def stop_monitoring(self):
        """停止系统监控"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()
        print("📊 系统监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                # 系统资源
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # 网络统计
                net_io = psutil.net_io_counters()
                
                # 查找clash-meta进程
                clash_processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'connections']):
                    try:
                        if any(name in proc.info['name'].lower() for name in MONITORING_CONFIG['process_names']):
                            proc_info = proc.info.copy()
                            proc_info['memory_mb'] = proc.info['memory_info'].rss / 1024 / 1024
                            proc_info['connections_count'] = len(proc.connections()) if proc.connections() else 0
                            clash_processes.append(proc_info)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                stat = {
                    'timestamp': datetime.now().isoformat(),
                    'elapsed_seconds': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0,
                    'system': {
                        'cpu_percent': cpu_percent,
                        'memory_percent': memory.percent,
                        'memory_used_mb': memory.used / 1024 / 1024,
                        'memory_available_mb': memory.available / 1024 / 1024,
                        'disk_percent': disk.percent,
                        'network_bytes_sent': net_io.bytes_sent,
                        'network_bytes_recv': net_io.bytes_recv
                    },
                    'clash_processes': clash_processes
                }
                
                self.stats.append(stat)
                
            except Exception as e:
                print(f"监控错误: {e}")
            
            time.sleep(MONITORING_CONFIG['interval'])
    
    def parse_test_results(self, scenario_name):
        """解析测试结果"""
        try:
            # 读取CSV结果文件
            stats_file = f'results_{scenario_name}_stats.csv'
            if os.path.exists(stats_file):
                df = pd.read_csv(stats_file)
                
                self.test_results[scenario_name] = {
                    'total_requests': df['Request Count'].sum(),
                    'total_failures': df['Failure Count'].sum(),
                    'avg_response_time': df['Average Response Time'].mean(),
                    'max_response_time': df['Max Response Time'].max(),
                    'requests_per_second': df['Requests/s'].mean(),
                    'failure_rate': (df['Failure Count'].sum() / df['Request Count'].sum()) * 100 if df['Request Count'].sum() > 0 else 0
                }
                
                print(f"📈 {scenario_name} 测试结果:")
                print(f"  总请求数: {self.test_results[scenario_name]['total_requests']}")
                print(f"  失败请求数: {self.test_results[scenario_name]['total_failures']}")
                print(f"  平均响应时间: {self.test_results[scenario_name]['avg_response_time']:.2f}ms")
                print(f"  最大响应时间: {self.test_results[scenario_name]['max_response_time']}ms")
                print(f"  平均RPS: {self.test_results[scenario_name]['requests_per_second']:.2f}")
                print(f"  失败率: {self.test_results[scenario_name]['failure_rate']:.2f}%")
                
        except Exception as e:
            print(f"解析测试结果时出错: {e}")
    
    def generate_report(self, scenario_name):
        """生成测试报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存监控数据
        stats_file = f'monitoring_stats_{scenario_name}_{timestamp}.json'
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
        
        # 生成图表
        if REPORT_CONFIG['include_charts'] and self.stats:
            self.generate_charts(scenario_name, timestamp)
        
        # 生成综合报告
        report = {
            'scenario': scenario_name,
            'timestamp': timestamp,
            'test_results': self.test_results.get(scenario_name, {}),
            'system_stats_summary': self.get_stats_summary(),
            'files': {
                'monitoring_data': stats_file,
                'html_report': f'report_{scenario_name}.html',
                'csv_stats': f'results_{scenario_name}_stats.csv'
            }
        }
        
        report_file = f'comprehensive_report_{scenario_name}_{timestamp}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📋 综合报告已生成: {report_file}")
        return report_file
    
    def generate_charts(self, scenario_name, timestamp):
        """生成性能图表"""
        if not self.stats:
            return
        
        # 准备数据
        timestamps = [stat['elapsed_seconds'] for stat in self.stats]
        cpu_data = [stat['system']['cpu_percent'] for stat in self.stats]
        memory_data = [stat['system']['memory_percent'] for stat in self.stats]
        
        # 创建图表目录
        chart_dir = f'{scenario_name}_charts'
        os.makedirs(chart_dir, exist_ok=True)
        
        # CPU使用率图表
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, cpu_data, label='CPU使用率 (%)', color='red')
        plt.xlabel('时间 (秒)')
        plt.ylabel('CPU使用率 (%)')
        plt.title(f'{scenario_name} - CPU使用率')
        plt.legend()
        plt.grid(True)
        plt.savefig(f'{chart_dir}/cpu_usage.png')
        plt.close()
        
        # 内存使用率图表
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, memory_data, label='内存使用率 (%)', color='blue')
        plt.xlabel('时间 (秒)')
        plt.ylabel('内存使用率 (%)')
        plt.title(f'{scenario_name} - 内存使用率')
        plt.legend()
        plt.grid(True)
        plt.savefig(f'{chart_dir}/memory_usage.png')
        plt.close()
        
        # 综合资源使用图表
        plt.figure(figsize=(15, 8))
        plt.subplot(2, 1, 1)
        plt.plot(timestamps, cpu_data, label='CPU (%)', color='red')
        plt.ylabel('CPU使用率 (%)')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(2, 1, 2)
        plt.plot(timestamps, memory_data, label='内存 (%)', color='blue')
        plt.xlabel('时间 (秒)')
        plt.ylabel('内存使用率 (%)')
        plt.legend()
        plt.grid(True)
        
        plt.suptitle(f'{scenario_name} - 系统资源使用情况')
        plt.tight_layout()
        plt.savefig(f'{chart_dir}/system_resources.png')
        plt.close()
        
        print(f"📊 图表已生成到目录: {chart_dir}")
    
    def get_stats_summary(self):
        """获取监控数据摘要"""
        if not self.stats:
            return {}
        
        cpu_data = [stat['system']['cpu_percent'] for stat in self.stats]
        memory_data = [stat['system']['memory_percent'] for stat in self.stats]
        
        return {
            'duration_seconds': max([stat['elapsed_seconds'] for stat in self.stats]),
            'cpu': {
                'avg': sum(cpu_data) / len(cpu_data),
                'max': max(cpu_data),
                'min': min(cpu_data)
            },
            'memory': {
                'avg': sum(memory_data) / len(memory_data),
                'max': max(memory_data),
                'min': min(memory_data)
            },
            'clash_processes_detected': len([stat for stat in self.stats if stat['clash_processes']]) > 0
        }


def main():
    parser = argparse.ArgumentParser(description='Clash-Meta 综合压力测试')
    parser.add_argument('--scenario', choices=list(TEST_SCENARIOS.keys()), 
                       default='light', help='测试场景')
    parser.add_argument('--users', type=int, help='自定义用户数')
    parser.add_argument('--spawn-rate', type=int, help='自定义启动速率')
    parser.add_argument('--duration', help='自定义持续时间 (如: 5m, 300s)')
    parser.add_argument('--no-charts', action='store_true', help='不生成图表')
    parser.add_argument('--all-scenarios', action='store_true', help='运行所有测试场景')
    
    args = parser.parse_args()
    
    # 检查依赖
    try:
        import locust
        import matplotlib
        import pandas
    except ImportError as e:
        print(f"缺少依赖包: {e}")
        print("请安装: pip install locust matplotlib pandas psutil")
        return
    
    tester = ClashMetaStressTester()
    
    # 禁用图表生成
    if args.no_charts:
        REPORT_CONFIG['include_charts'] = False
    
    if args.all_scenarios:
        # 运行所有场景
        for scenario in TEST_SCENARIOS.keys():
            tester.run_test_scenario(scenario)
            tester.generate_report(scenario)
            time.sleep(30)  # 场景间休息30秒
    else:
        # 运行单个场景
        if args.users or args.spawn_rate or args.duration:
            # 自定义参数
            custom_params = {
                'users': args.users or TEST_SCENARIOS[args.scenario]['users'],
                'spawn_rate': args.spawn_rate or TEST_SCENARIOS[args.scenario]['spawn_rate'],
                'duration': args.duration or TEST_SCENARIOS[args.scenario]['duration']
            }
            tester.run_test_scenario('custom', custom_params)
            tester.generate_report('custom')
        else:
            # 使用预定义场景
            tester.run_test_scenario(args.scenario)
            tester.generate_report(args.scenario)
    
    print("\n🎉 所有测试完成!")


if __name__ == "__main__":
    main()