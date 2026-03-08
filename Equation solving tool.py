
import tkinter as tk
from tkinter import ttk, scrolledtext
from sympy import symbols, Eq, solve, pretty, latex, simplify, expand
from sympy.parsing.sympy_parser import parse_expr
from sympy.printing.pretty import pretty_print
import sympy as sp

class EquationSolver:
    def __init__(self, root):
        self.root = root
        self.root.title("高级方程求解器 - SymPy")
        self.root.geometry("900x800")
        self.root.configure(bg='#f8f9fa')
        
        # 创建变量
        self.x = symbols('x')
        self.create_widgets()
        
    def create_widgets(self):
        # 标题
        title_label = tk.Label(
            self.root, 
            text="SymPy 高级方程求解器", 
            font=("Arial", 22, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        title_label.pack(pady=15)
        
        # 输入框架
        input_frame = tk.Frame(self.root, bg='#f8f9fa')
        input_frame.pack(pady=10, padx=20, fill='x')
        
        input_label = tk.Label(
            input_frame, 
            text="请输入方程或表达式:", 
            font=("Arial", 12),
            bg='#f8f9fa'
        )
        input_label.pack(anchor='w')
        
        self.entry = tk.Entry(
            input_frame, 
            width=80, 
            font=("Consolas", 12),
            bd=2,
            relief='solid'
        )
        self.entry.pack(pady=5, fill='x')
        self.entry.bind('<Return>', lambda event: self.solve_equation())
        
        # 按钮框架
        button_frame = tk.Frame(self.root, bg='#f8f9fa')
        button_frame.pack(pady=10)
        
        solve_button = tk.Button(
            button_frame, 
            text="求解方程", 
            command=self.solve_equation,
            bg='#3498db',
            fg='white',
            font=("Arial", 10, "bold"),
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2'
        )
        solve_button.pack(side='left', padx=5)
        
        clear_button = tk.Button(
            button_frame, 
            text="清空结果", 
            command=self.clear_results,
            bg='#e74c3c',
            fg='white',
            font=("Arial", 10, "bold"),
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2'
        )
        clear_button.pack(side='left', padx=5)
        
        example_button = tk.Button(
            button_frame, 
            text="示例", 
            command=self.show_examples,
            bg='#2ecc71',
            fg='white',
            font=("Arial", 10, "bold"),
            padx=20,
            pady=8,
            relief='flat',
            cursor='hand2'
        )
        example_button.pack(side='left', padx=5)
        
        # 示例文本
        example_frame = tk.Frame(self.root, bg='#f8f9fa')
        example_frame.pack(pady=5, padx=20, fill='x')
        
        example_text = tk.Label(
            example_frame,
            text="示例: x**2 - 4 = 0, sin(x) + cos(x) = 1, x**3 - 6*x**2 + 11*x - 6",
            font=("Arial", 9),
            bg='#f8f9fa',
            fg='#7f8c8d'
        )
        example_text.pack(anchor='w')
        
        # 结果框架
        result_frame = tk.LabelFrame(
            self.root, 
            text="求解结果", 
            font=("Arial", 12, "bold"),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        result_frame.pack(pady=15, padx=20, fill='both', expand=True)
        
        # 创建文本框和滚动条
        text_frame = tk.Frame(result_frame, bg='#f8f9fa')
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.result_text = scrolledtext.ScrolledText(
            text_frame,
            width=90,
            height=18,
            font=("Consolas", 11),
            bg='white',
            fg='#2c3e50',
            wrap=tk.NONE,
            bd=1,
            relief='solid'
        )
        self.result_text.pack(side='left', fill='both', expand=True)
        
        # 添加水平滚动条
        h_scrollbar = tk.Scrollbar(text_frame, orient='horizontal', command=self.result_text.xview)
        h_scrollbar.pack(side='bottom', fill='x')
        self.result_text.config(xscrollcommand=h_scrollbar.set)
        
    def solve_equation(self):
        try:
            expr_input = self.entry.get().strip()
            if not expr_input:
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "请输入一个方程或表达式")
                return
                
            # 解析输入
            if '=' in expr_input:
                left, right = map(str.strip, expr_input.split('=', 1))
                equation = Eq(parse_expr(left), parse_expr(right))
                solutions = solve(equation, self.x)
                equation_str = f"{left} = {right}"
            else:
                expression = parse_expr(expr_input)
                solutions = solve(expression, self.x)
                equation_str = expr_input
            
            # 显示结果
            self.result_text.delete(1.0, tk.END)
            
            # 原方程美化显示
            self.result_text.insert(tk.END, "原方程:\n", "title")
            self.result_text.insert(tk.END, "=" * 60 + "\n", "separator")
            
            # 使用SymPy美化原方程显示
            if '=' in expr_input:
                left_expr = parse_expr(left)
                right_expr = parse_expr(right)
                self.result_text.insert(tk.END, pretty(left_expr) + " = " + pretty(right_expr) + "\n\n")
            else:
                expr_parsed = parse_expr(expr_input)
                self.result_text.insert(tk.END, pretty(expr_parsed) + " = 0\n\n")
            
            # 解的美化显示
            if solutions:
                self.result_text.insert(tk.END, "解:\n", "title")
                self.result_text.insert(tk.END, "=" * 60 + "\n", "separator")
                
                for i, sol in enumerate(solutions, 1):
                    self.result_text.insert(tk.END, f"解 {i}:\n", "subtitle")
                    pretty_result = pretty(sol, use_unicode=True)
                    # 确保美化输出正确显示
                    self.result_text.insert(tk.END, pretty_result + "\n")
                    self.result_text.insert(tk.END, "\n")
                
                # 数值近似值
                self.result_text.insert(tk.END, "数值近似值:\n", "title")
                self.result_text.insert(tk.END, "=" * 60 + "\n", "separator")
                for i, sol in enumerate(solutions, 1):
                    try:
                        numeric_val = float(sol.evalf())
                        self.result_text.insert(tk.END, f"解 {i}: {numeric_val:.8f}\n")
                    except:
                        self.result_text.insert(tk.END, f"解 {i}: {sol.evalf()}\n")
                self.result_text.insert(tk.END, "\n")
                
                
                
            # 添加样式标签
            self.result_text.tag_config("title", font=("Arial", 12, "bold"), foreground="#2c3e50")
            self.result_text.tag_config("subtitle", font=("Arial", 11, "bold"), foreground="#3498db")
            self.result_text.tag_config("separator", foreground="#bdc3c7")
                
        except Exception as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"错误: {str(e)}\n", "error")
            self.result_text.insert(tk.END, "请检查输入格式是否正确\n", "error")
            self.result_text.insert(tk.END, "示例格式: x**2 - 4 = 0 或 x**2 - 4\n", "error")
            self.result_text.tag_config("error", foreground="#e74c3c", font=("Arial", 10, "bold"))
    
    def clear_results(self):
        self.result_text.delete(1.0, tk.END)
        self.entry.delete(0, tk.END)
        
    def show_examples(self):
        examples = [
            "x**2 - 4 = 0",
            "x**3 - 6*x**2 + 11*x - 6 = 0",
            "sin(x) + cos(x) = 1",
            "x**2 + 2*x + 1",
            "exp(x) - 5 = 0",
            "log(x, 10) = 2",
            "x**4 - 5*x**2 + 4 = 0"
        ]
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "示例方程:\n\n", "title")
        self.result_text.tag_config("title", font=("Arial", 12, "bold"), foreground="#2c3e50")
        for i, example in enumerate(examples, 1):
            self.result_text.insert(tk.END, f"{i}. {example}\n")
        self.result_text.insert(tk.END, "\n点击'求解方程'按钮可尝试求解这些示例")

def main():
    root = tk.Tk()
    app = EquationSolver(root)
    root.mainloop()

if __name__ == "__main__":
    main()
