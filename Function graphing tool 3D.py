
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import tkinter as tk
from tkinter import ttk, messagebox
import re

class Function3DPlotter:
    def __init__(self, root):
        self.root = root
        self.root.title("3D函数绘图器")
        self.root.geometry("1000x700")
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 输入框架
        input_frame = ttk.LabelFrame(main_frame, text="函数设置", padding="10")
        input_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 函数输入
        ttk.Label(input_frame, text="函数 f(x,y) =").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.function_entry = ttk.Entry(input_frame, width=40)
        self.function_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.function_entry.insert(0, "x**2 + y**2")
        
        # 范围输入
        range_frame = ttk.Frame(input_frame)
        range_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(range_frame, text="x范围:").grid(row=0, column=0, sticky=tk.W)
        self.x_min_entry = ttk.Entry(range_frame, width=8)
        self.x_min_entry.grid(row=0, column=1, padx=(5, 0))
        self.x_min_entry.insert(0, "-5")
        ttk.Label(range_frame, text="到").grid(row=0, column=2, padx=(5, 5))
        self.x_max_entry = ttk.Entry(range_frame, width=8)
        self.x_max_entry.grid(row=0, column=3, padx=(0, 10))
        self.x_max_entry.insert(0, "5")
        
        ttk.Label(range_frame, text="y范围:").grid(row=0, column=4, sticky=tk.W, padx=(20, 0))
        self.y_min_entry = ttk.Entry(range_frame, width=8)
        self.y_min_entry.grid(row=0, column=5, padx=(5, 0))
        self.y_min_entry.insert(0, "-5")
        ttk.Label(range_frame, text="到").grid(row=0, column=6, padx=(5, 5))
        self.y_max_entry = ttk.Entry(range_frame, width=8)
        self.y_max_entry.grid(row=0, column=7, padx=(0, 10))
        self.y_max_entry.insert(0, "5")
        
        # 分辨率输入
        ttk.Label(range_frame, text="分辨率:").grid(row=0, column=8, sticky=tk.W, padx=(20, 0))
        self.resolution_entry = ttk.Entry(range_frame, width=8)
        self.resolution_entry.grid(row=0, column=9, padx=(5, 0))
        self.resolution_entry.insert(0, "50")
        
        # 按钮
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(15, 0))
        
        self.plot_button = ttk.Button(button_frame, text="绘制函数", command=self.plot_function)
        self.plot_button.grid(row=0, column=0, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="清除图像", command=self.clear_plot)
        self.clear_button.grid(row=0, column=1, padx=(0, 10))
        
        # 绘图框架
        plot_frame = ttk.Frame(main_frame)
        plot_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建matplotlib图形
        self.fig = plt.Figure(figsize=(10, 6), dpi=100)
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # 创建画布
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # 示例函数列表
        example_frame = ttk.LabelFrame(main_frame, text="示例函数", padding="10")
        example_frame.grid(row=1, column=1, sticky=(tk.N, tk.S), padx=(10, 0))
        
        examples = [
            "x**2 + y**2",
            "np.sin(x) * np.cos(y)",
            "x**3 - y**3",
            "np.exp(-(x**2 + y**2))",
            "np.sqrt(x**2 + y**2)",
            "x * y",
            "np.sin(np.sqrt(x**2 + y**2))",
            "1 / (1 + x**2 + y**2)"
        ]
        
        self.example_listbox = tk.Listbox(example_frame, height=15, width=25)
        for example in examples:
            self.example_listbox.insert(tk.END, example)
        self.example_listbox.pack(fill=tk.BOTH, expand=True)
        self.example_listbox.bind('<<ListboxSelect>>', self.on_example_select)
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
    def on_example_select(self, event):
        selection = self.example_listbox.curselection()
        if selection:
            example = self.example_listbox.get(selection[0])
            self.function_entry.delete(0, tk.END)
            self.function_entry.insert(0, example)
            
    def plot_function(self):
        try:
            # 获取输入参数
            func_str = self.function_entry.get().strip()
            if not func_str:
                messagebox.showerror("错误", "请输入函数表达式")
                return
                
            x_min = float(self.x_min_entry.get())
            x_max = float(self.x_max_entry.get())
            y_min = float(self.y_min_entry.get())
            y_max = float(self.y_max_entry.get())
            resolution = int(self.resolution_entry.get())
            
            if x_min >= x_max or y_min >= y_max:
                messagebox.showerror("错误", "范围设置不正确")
                return
                
            if resolution <= 0 or resolution > 100:
                messagebox.showerror("错误", "分辨率应在1-100之间")
                return
            
            # 创建网格
            x = np.linspace(x_min, x_max, resolution)
            y = np.linspace(y_min, y_max, resolution)
            X, Y = np.meshgrid(x, y)
            
            # 计算函数值
            import math
            z_expr = func_str.replace('x', 'X').replace('y', 'Y')
            Z = eval(z_expr, {"X": X, "Y": Y, "np": np, "math": math, "sin": np.sin, "cos": np.cos, "tan": np.tan, 
                             "exp": np.exp, "log": np.log, "sqrt": np.sqrt, "abs": np.abs, "sinh": np.sinh, "cosh": np.sinh, "tanh": np.tanh})
            
            # 绘制3D图
            self.ax.clear()
            surf = self.ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
            self.ax.set_xlabel('X轴')
            self.ax.set_ylabel('Y轴')
            self.ax.set_zlabel('Z轴')
            self.ax.set_title(f'f(x,y) = {self.function_entry.get()}')
            
            
            
            # 更新画布
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("错误", f"绘图失败: {str(e)}")
            
    def clear_plot(self):
        self.ax.clear()
        self.canvas.draw()

def main():
    root = tk.Tk()
    app = Function3DPlotter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
