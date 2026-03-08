import sys
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
import re
from scipy.optimize import minimize_scalar
import warnings
warnings.filterwarnings('ignore')

class FunctionPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title("函数绘图工具")
        self.root.geometry("1000x800")
        
        # 创建界面
        self.create_widgets()
        
        # 初始化图形
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 鼠标悬停相关变量
        self.annotation = None
        self.canvas.mpl_connect('motion_notify_event', self.on_hover)
        
    def create_widgets(self):
        # 输入框架
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10, padx=10, fill=tk.X)
        
        # 函数输入
        ttk.Label(input_frame, text="函数表达式:").grid(row=0, column=0, sticky=tk.W)
        self.function_entry = ttk.Entry(input_frame, width=50)
        self.function_entry.grid(row=0, column=1, padx=5)
        self.function_entry.insert(0, "x**2 - 4*x + 3")
        
        # X范围输入
        ttk.Label(input_frame, text="X范围:").grid(row=1, column=0, sticky=tk.W)
        range_frame = ttk.Frame(input_frame)
        range_frame.grid(row=1, column=1, sticky=tk.W)
        
        # 替换原x_min_entry和x_max_entry的布局代码
        self.x_min_entry = ttk.Entry(range_frame, width=10)
        self.x_min_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5)
        self.x_min_entry.insert(0, "-5")

        self.x_max_entry = ttk.Entry(range_frame, width=10)
        self.x_max_entry.grid(row=0, column=3, sticky=tk.W+tk.E, padx=5)
        self.x_max_entry.insert(0, "5")
        
        # 控制按钮
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=2, column=1, pady=10)
        
        ttk.Button(button_frame, text="绘制", command=self.plot_function).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空", command=self.clear_plot).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="查找极值", command=self.find_extrema).pack(side=tk.LEFT, padx=5)
        
        # 示例按钮
        examples_frame = ttk.Frame(input_frame)
        examples_frame.grid(row=3, column=1, pady=5)
        
        ttk.Label(examples_frame, text="示例:").pack(side=tk.LEFT)
        examples = ["x**2 - 4*x + 3", "np.sin(x)", "x**3 - 3*x**2 + 2", "np.exp(-x**2)*np.cos(5*x)"]
        for example in examples:
            btn = ttk.Button(examples_frame, text=example, 
                           command=lambda ex=example: self.function_entry.delete(0, tk.END) or self.function_entry.insert(0, ex))
            btn.pack(side=tk.LEFT, padx=2)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(self.root, text="极值分析结果", padding=10)
        result_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.result_text = tk.Text(result_frame, height=6, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绘图区域
        self.plot_frame = ttk.Frame(self.root)
        self.plot_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
    def safe_eval(self, expression, x):
        """安全地计算数学表达式"""
        # 允许的安全函数和常量
        allowed_names = {
            "np": np,
            "sin": np.sin,
            "cos": np.cos,
            "tan": np.tan,
            "arcsin": np.arcsin,
            "arccos": np.arccos,
            "arctan": np.arctan,
            "exp": np.exp,
            "log": np.log,
            "log10": np.log10,
            "sqrt": np.sqrt,
            "abs": np.abs,
            "sign": np.sign,
            "floor": np.floor,
            "ceil": np.ceil,
            "round": np.round,
            "pi": np.pi,
            "e": np.e,
            "x": x
        }
        
        # 清理表达式
        expression = expression.replace("^", "**")  # 替换幂运算符
        
        try:
            # 使用eval计算表达式，只允许预定义的变量和函数
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            return result
        except Exception as e:
            raise ValueError(f"表达式计算错误: {str(e)}")
            
    def find_local_extrema(self, x, y):
        """查找局部极值点"""
        extrema_points = []
        
        # 查找局部极大值和极小值
        for i in range(1, len(y)-1):
            # 局部极大值条件
            if y[i] > y[i-1] and y[i] > y[i+1]:
                extrema_points.append((x[i], y[i], "局部极大值"))
            # 局部极小值条件
            elif y[i] < y[i-1] and y[i] < y[i+1]:
                extrema_points.append((x[i], y[i], "局部极小值"))
                
        return extrema_points
    
    def find_global_extrema(self, x, y):
        """查找全局极值点"""
        max_idx = np.argmax(y)
        min_idx = np.argmin(y)
        
        global_max = (x[max_idx], y[max_idx], "全局极大值")
        global_min = (x[min_idx], y[min_idx], "全局极小值")
        
        return global_max, global_min
    
    def plot_function(self):
        try:
            # 获取输入参数
            function_str = self.function_entry.get().strip()
            if not function_str:
                messagebox.showerror("错误", "请输入函数表达式")
                return
                
            x_min = float(self.x_min_entry.get())
            x_max = float(self.x_max_entry.get())
            
            if x_min >= x_max:
                messagebox.showerror("错误", "X最小值必须小于最大值")
                return
            
            # 生成X值
            x = np.linspace(x_min, x_max, 1000)
            
            # 计算Y值
            y = self.safe_eval(function_str, x)
            
            # 绘制图形
            self.ax.clear()
            self.line, = self.ax.plot(x, y, linewidth=2, color='#2563eb', label=f'y = {function_str}')
            self.ax.set_xlabel('x', fontsize=12)
            self.ax.set_ylabel('y', fontsize=12)
            self.ax.set_title(f'函数: {function_str}', fontsize=14)
            self.ax.grid(True, alpha=0.3)
            self.ax.legend()
            
            # 更新画布
            self.canvas.draw()
            
            # 自动查找并显示极值
            self.find_extrema(auto_mode=True)
            
        except ValueError as ve:
            messagebox.showerror("输入错误", str(ve))
        except Exception as e:
            messagebox.showerror("绘图错误", f"绘图失败: {str(e)}")
            
    def find_extrema(self, auto_mode=False):
        try:
            function_str = self.function_entry.get().strip()
            if not function_str:
                if not auto_mode:
                    messagebox.showerror("错误", "请输入函数表达式")
                return
                
            x_min = float(self.x_min_entry.get())
            x_max = float(self.x_max_entry.get())
            
            if x_min >= x_max:
                if not auto_mode:
                    messagebox.showerror("错误", "X最小值必须小于最大值")
                return
            
            # 生成X值
            x = np.linspace(x_min, x_max, 1000)
            
            # 计算Y值
            y = self.safe_eval(function_str, x)
            
            # 查找极值点
            local_extrema = self.find_local_extrema(x, y)
            global_max, global_min = self.find_global_extrema(x, y)
            
            # 在图上标记极值点
            # 标记全局极值
            self.ax.plot(global_max[0], global_max[1], 'ro', markersize=8, 
                        label=f'全局最大值 ({global_max[0]:.3f}, {global_max[1]:.3f})')
            self.ax.plot(global_min[0], global_min[1], 'go', markersize=8, 
                        label=f'全局最小值 ({global_min[0]:.3f}, {global_min[1]:.3f})')
            
            # 标记局部极值（排除与全局极值重合的点）
            plotted_points = [(global_max[0], global_max[1]), (global_min[0], global_min[1])]
            local_count = 0
            for point in local_extrema:
                # 检查是否与已标记点重合
                is_duplicate = False
                for plotted in plotted_points:
                    if abs(point[0] - plotted[0]) < 1e-3 and abs(point[1] - plotted[1]) < 1e-3:
                        is_duplicate = True
                        break
                
                if not is_duplicate and local_count < 5:  # 最多标记5个局部极值
                    color = 'orange' if '大' in point[2] else 'purple'
                    marker = '^' if '大' in point[2] else 'v'
                    self.ax.plot(point[0], point[1], marker, color=color, markersize=6,
                                label=f'{point[2]} ({point[0]:.3f}, {point[1]:.3f})')
                    plotted_points.append((point[0], point[1]))
                    local_count += 1
            
            # 更新图例
            self.ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # 更新画布
            self.canvas.draw()
            
            # 显示结果文本
            result_text = f"函数: {function_str}\n"
            result_text += f"定义域: [{x_min}, {x_max}]\n\n"
            result_text += f"全局最大值: ({global_max[0]:.6f}, {global_max[1]:.6f})\n"
            result_text += f"全局最小值: ({global_min[0]:.6f}, {global_min[1]:.6f})\n\n"
            
            if local_extrema:
                result_text += "局部极值点:\n"
                for i, point in enumerate(local_extrema[:10]):  # 最多显示10个
                    result_text += f"  {i+1}. {point[2]}: ({point[0]:.6f}, {point[1]:.6f})\n"
            else:
                result_text += "未检测到明显的局部极值点\n"
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result_text)
            
        except ValueError as ve:
            if not auto_mode:
                messagebox.showerror("输入错误", str(ve))
        except Exception as e:
            if not auto_mode:
                messagebox.showerror("计算错误", f"极值计算失败: {str(e)}")
    
    def on_hover(self, event):
        """鼠标悬停事件处理"""
        if event.inaxes == self.ax:
            # 获取当前鼠标位置的坐标
            x, y = event.xdata, event.ydata
            
            # 如果已有注释框，先移除
            if self.annotation:
                self.annotation.remove()
            
            # 创建新的注释框
            self.annotation = self.ax.annotate(
                f'x: {x:.3f}\ny: {y:.3f}',
                xy=(x, y),
                xytext=(10, 10),
                textcoords='offset points',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0')
            )
            
            # 刷新画布
            self.canvas.draw()
        else:
            # 鼠标移出绘图区域时移除注释
            if self.annotation:
                self.annotation.remove()
                self.annotation = None
                self.canvas.draw()
    
    def clear_plot(self):
        self.ax.clear()
        self.ax.set_xlim(-5, 5)
        self.ax.set_ylim(-5, 5)
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()
        self.result_text.delete(1.0, tk.END)
        if self.annotation:
            self.annotation.remove()
            self.annotation = None

def main():
    root = tk.Tk()
    app = FunctionPlotter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
