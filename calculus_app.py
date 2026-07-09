import os
import sys
import ctypes

_lib_path = os.path.expanduser('~/.local/lib')
_py_path = os.path.expanduser('~/.local/python3.12')
_ctk = os.path.join(_lib_path, 'libtk8.6.so')
_cblt = os.path.join(_lib_path, 'libBLT.2.5.so.8.6')
if os.path.exists(_ctk):
    ctypes.CDLL(_ctk, mode=ctypes.RTLD_GLOBAL)
if os.path.exists(_cblt):
    try:
        ctypes.CDLL(_cblt, mode=ctypes.RTLD_GLOBAL)
    except:
        pass
if os.path.exists(_py_path):
    sys.path.insert(0, _py_path)

_tk_scripts = os.path.expanduser('~/.local/share/tcltk/tk8.6')
if os.path.exists(_tk_scripts):
    os.environ['TK_LIBRARY'] = _tk_scripts

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import sympy as sp

class CalculusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Complex Calculus Toolkit")
        self.root.geometry("1100x750")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

        self._build_derivative_tab()
        self._build_integral_tab()
        self._build_complex_tab()
        self._build_problems_tab()

    def _safe_func(self, expr_str):
        x = sp.Symbol('x')
        try:
            return sp.sympify(expr_str)
        except:
            return None

    def _expr_to_numpy(self, expr_str):
        x = sp.Symbol('x')
        try:
            f = sp.lambdify(x, sp.sympify(expr_str), 'numpy')
            return f
        except:
            return None

    def _build_derivative_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Derivatives')

        ctrl = ttk.Frame(tab)
        ctrl.pack(fill='x', padx=10, pady=5)

        ttk.Label(ctrl, text='f(x) =').grid(row=0, column=0, sticky='w', padx=5)
        self.deriv_expr = ttk.Entry(ctrl, width=40)
        self.deriv_expr.grid(row=0, column=1, padx=5, pady=2)
        self.deriv_expr.insert(0, 'x**3 - 2*x**2 + x')

        ttk.Label(ctrl, text='Tangent at x =').grid(row=0, column=2, sticky='w', padx=5)
        self.deriv_tangent = ttk.Entry(ctrl, width=8)
        self.deriv_tangent.grid(row=0, column=3, padx=5, pady=2)
        self.deriv_tangent.insert(0, '1')

        ttk.Label(ctrl, text='x range:').grid(row=1, column=0, sticky='w', padx=5)
        self.deriv_xmin = ttk.Entry(ctrl, width=8)
        self.deriv_xmin.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        self.deriv_xmin.insert(0, '-3')

        ttk.Label(ctrl, text='to').grid(row=1, column=1, padx=55)
        self.deriv_xmax = ttk.Entry(ctrl, width=8)
        self.deriv_xmax.grid(row=1, column=1, padx=80, pady=2)
        self.deriv_xmax.insert(0, '3')

        ttk.Button(ctrl, text='Plot', command=self._plot_derivative).grid(row=1, column=2, padx=5)
        ttk.Button(ctrl, text='Clear', command=lambda: self._clear_plot(self.deriv_fig, self.deriv_canvas)).grid(row=1, column=3, padx=5)

        self.deriv_fig = Figure(figsize=(8, 5))
        self.deriv_ax = self.deriv_fig.add_subplot(111)
        self.deriv_canvas = FigureCanvasTkAgg(self.deriv_fig, master=tab)
        self.deriv_canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=5)
        toolbar = NavigationToolbar2Tk(self.deriv_canvas, tab)
        toolbar.pack()

    def _plot_derivative(self):
        self.deriv_ax.clear()
        expr_str = self.deriv_expr.get().strip()
        try:
            xmin = float(self.deriv_xmin.get())
            xmax = float(self.deriv_xmax.get())
            tangent_x = float(self.deriv_tangent.get())
        except ValueError:
            messagebox.showerror('Error', 'Invalid numeric input')
            return

        f_expr = self._safe_func(expr_str)
        if f_expr is None:
            messagebox.showerror('Error', 'Invalid function expression')
            return

        x = sp.Symbol('x')
        f_prime_expr = sp.diff(f_expr, x)
        f_np = sp.lambdify(x, f_expr, 'numpy')
        f_prime_np = sp.lambdify(x, f_prime_expr, 'numpy')

        xs = np.linspace(xmin, xmax, 400)
        try:
            ys = f_np(xs)
            y_prime = f_prime_np(xs)
        except Exception as e:
            messagebox.showerror('Error', f'Evaluation error: {e}')
            return

        self.deriv_ax.plot(xs, ys, 'b-', linewidth=2, label=f'f(x) = {sp.latex(f_expr)}')
        self.deriv_ax.plot(xs, y_prime, 'r--', linewidth=2, label=f"f'(x) = {sp.latex(f_prime_expr)}")

        try:
            y_tang = f_np(tangent_x)
            slope = f_prime_np(tangent_x)
            tangent_ys = slope * (xs - tangent_x) + y_tang
            self.deriv_ax.plot(xs, tangent_ys, 'g-.', linewidth=1.5, label=f'Tangent at x={tangent_x}')
            self.deriv_ax.plot(tangent_x, y_tang, 'go', markersize=8)
        except:
            pass

        self.deriv_ax.axhline(0, color='gray', linewidth=0.5)
        self.deriv_ax.axvline(0, color='gray', linewidth=0.5)
        self.deriv_ax.grid(True, alpha=0.3)
        self.deriv_ax.legend(fontsize=9)
        self.deriv_ax.set_xlabel('x')
        self.deriv_canvas.draw()

    def _build_integral_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Integrals')

        ctrl = ttk.Frame(tab)
        ctrl.pack(fill='x', padx=10, pady=5)

        ttk.Label(ctrl, text='f(x) =').grid(row=0, column=0, sticky='w', padx=5)
        self.int_expr = ttk.Entry(ctrl, width=40)
        self.int_expr.grid(row=0, column=1, padx=5, pady=2)
        self.int_expr.insert(0, 'sin(x)')

        ttk.Label(ctrl, text='From').grid(row=1, column=0, sticky='w', padx=5)
        self.int_a = ttk.Entry(ctrl, width=8)
        self.int_a.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        self.int_a.insert(0, '0')

        ttk.Label(ctrl, text='To').grid(row=1, column=1, padx=55)
        self.int_b = ttk.Entry(ctrl, width=8)
        self.int_b.grid(row=1, column=1, padx=80, pady=2)
        self.int_b.insert(0, 'pi')

        self.int_riemann_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(ctrl, text='Show Riemann sum', variable=self.int_riemann_var).grid(row=2, column=0, columnspan=2, sticky='w', padx=5)

        ttk.Label(ctrl, text='Riemann rectangles:').grid(row=2, column=2, sticky='w', padx=5)
        self.int_n = ttk.Spinbox(ctrl, from_=2, to=100, width=5)
        self.int_n.grid(row=2, column=3, sticky='w', padx=5, pady=2)
        self.int_n.set(10)

        ttk.Button(ctrl, text='Plot', command=self._plot_integral).grid(row=3, column=0, padx=5, pady=5)
        ttk.Button(ctrl, text='Clear', command=lambda: self._clear_plot(self.int_fig, self.int_canvas)).grid(row=3, column=1, padx=5, pady=5)

        self.int_result_var = tk.StringVar()
        ttk.Label(ctrl, textvariable=self.int_result_var, foreground='blue').grid(row=3, column=2, columnspan=2, sticky='w', padx=5)

        self.int_fig = Figure(figsize=(8, 5))
        self.int_ax = self.int_fig.add_subplot(111)
        self.int_canvas = FigureCanvasTkAgg(self.int_fig, master=tab)
        self.int_canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=5)
        toolbar = NavigationToolbar2Tk(self.int_canvas, tab)
        toolbar.pack()

    def _plot_integral(self):
        self.int_ax.clear()
        expr_str = self.int_expr.get().strip()
        a_str = self.int_a.get().strip()
        b_str = self.int_b.get().strip()

        x = sp.Symbol('x')
        f_expr = self._safe_func(expr_str)
        if f_expr is None:
            messagebox.showerror('Error', 'Invalid function')
            return

        try:
            a = float(sp.N(sp.sympify(a_str)))
            b = float(sp.N(sp.sympify(b_str)))
        except:
            messagebox.showerror('Error', 'Invalid integration bounds')
            return

        if a >= b:
            messagebox.showerror('Error', 'Lower bound must be less than upper bound')
            return

        f_np = sp.lambdify(x, f_expr, 'numpy')
        padding = (b - a) * 0.2
        xs = np.linspace(a - padding, b + padding, 400)
        ys = f_np(xs)

        xs_fill = np.linspace(a, b, 400)
        ys_fill = f_np(xs_fill)
        self.int_ax.fill_between(xs_fill, ys_fill, alpha=0.3, color='skyblue', label='Area')

        self.int_ax.plot(xs, ys, 'b-', linewidth=2, label=f'f(x) = {sp.latex(f_expr)}')
        self.int_ax.axvline(a, color='red', linestyle='--', linewidth=1)
        self.int_ax.axvline(b, color='red', linestyle='--', linewidth=1)

        if self.int_riemann_var.get():
            n = int(self.int_n.get())
            riemann_xs = np.linspace(a, b, n + 1)
            dx = (b - a) / n
            for i in range(n):
                x_mid = (riemann_xs[i] + riemann_xs[i+1]) / 2
                y_mid = f_np(x_mid)
                self.int_ax.add_patch(
                    matplotlib.patches.Rectangle(
                        (riemann_xs[i], 0), dx, y_mid,
                        alpha=0.2, color='orange', linewidth=0.5, edgecolor='red'
                    )
                )
            self.int_ax.plot([], [], color='orange', alpha=0.6, linewidth=4, label=f'Riemann sum (n={n})')

        try:
            F = sp.integrate(f_expr, x)
            definite = sp.integrate(f_expr, (x, a, b))
            result_str = f'∫ f(x) dx from {a:.3f} to {b:.3f} = {float(definite):.6f}'
            self.int_result_var.set(result_str)
        except:
            self.int_result_var.set('Could not compute symbolic integral')

        self.int_ax.axhline(0, color='gray', linewidth=0.5)
        self.int_ax.grid(True, alpha=0.3)
        self.int_ax.legend(fontsize=9)
        self.int_ax.set_xlabel('x')
        self.int_canvas.draw()

    def _build_complex_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Complex Analysis')

        ctrl = ttk.Frame(tab)
        ctrl.pack(fill='x', padx=10, pady=5)

        ttk.Label(ctrl, text='f(z) =').grid(row=0, column=0, sticky='w', padx=5)
        self.complex_expr = ttk.Entry(ctrl, width=40)
        self.complex_expr.grid(row=0, column=1, padx=5, pady=2)
        self.complex_expr.insert(0, 'z**2')

        ttk.Label(ctrl, text='Range:').grid(row=1, column=0, sticky='w', padx=5)
        self.complex_range = ttk.Entry(ctrl, width=8)
        self.complex_range.grid(row=1, column=1, sticky='w', padx=5, pady=2)
        self.complex_range.insert(0, '2')

        self.complex_plot_type = tk.StringVar(value='phase')
        ttk.Radiobutton(ctrl, text='Phase Plot', variable=self.complex_plot_type, value='phase').grid(row=2, column=0, padx=5)
        ttk.Radiobutton(ctrl, text='Modulus', variable=self.complex_plot_type, value='modulus').grid(row=2, column=1, sticky='w', padx=5)
        ttk.Radiobutton(ctrl, text='Real Part', variable=self.complex_plot_type, value='real').grid(row=2, column=2, sticky='w', padx=5)
        ttk.Radiobutton(ctrl, text='Imag Part', variable=self.complex_plot_type, value='imag').grid(row=2, column=3, sticky='w', padx=5)

        ttk.Button(ctrl, text='Plot', command=self._plot_complex).grid(row=3, column=0, padx=5, pady=5)
        ttk.Button(ctrl, text='Clear', command=lambda: self._clear_plot(self.complex_fig, self.complex_canvas)).grid(row=3, column=1, padx=5, pady=5)

        self.complex_fig = Figure(figsize=(8, 6))
        self.complex_canvas = FigureCanvasTkAgg(self.complex_fig, master=tab)
        self.complex_canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=5)
        toolbar = NavigationToolbar2Tk(self.complex_canvas, tab)
        toolbar.pack()

    def _complex_func(self, expr_str, z):
        local_vars = {'z': z, 'np': np}
        allowed = {'sin': np.sin, 'cos': np.cos, 'exp': np.exp, 'log': np.log,
                   'abs': np.abs, 'sqrt': np.sqrt, 'tan': np.tan, 'pi': np.pi,
                   'e': np.e, '1j': 1j, 'conj': np.conj, 'angle': np.angle,
                   'real': np.real, 'imag': np.imag}
        local_vars.update(allowed)
        expr = expr_str.replace('^', '**')
        try:
            return eval(expr, {'__builtins__': {}}, local_vars)
        except:
            return None

    def _plot_complex(self):
        self.complex_fig.clear()
        expr_str = self.complex_expr.get().strip()
        try:
            r = float(self.complex_range.get())
        except ValueError:
            messagebox.showerror('Error', 'Invalid range')
            return

        plot_type = self.complex_plot_type.get()
        n = 400
        x = np.linspace(-r, r, n)
        y = np.linspace(-r, r, n)
        X, Y = np.meshgrid(x, y)
        Z = X + 1j * Y

        try:
            FZ = self._complex_func(expr_str, Z)
        except:
            FZ = None

        if FZ is None:
            messagebox.showerror('Error', 'Could not evaluate complex function')
            return

        ax = self.complex_fig.add_subplot(111)

        if plot_type == 'phase':
            phase = np.angle(FZ)
            ax.imshow(phase, extent=[-r, r, -r, r], cmap='hsv', origin='lower', aspect='auto')
            ax.set_title(f'Phase plot of f(z) = {expr_str}')
            cbar = self.complex_fig.colorbar(ax.images[0], ax=ax, fraction=0.046, pad=0.04)
            cbar.set_label('Argument (rad)')
        elif plot_type == 'modulus':
            mod = np.abs(FZ)
            mod = np.clip(mod, 1e-10, np.percentile(mod[~np.isnan(mod)], 95))
            cs = ax.contourf(X, Y, mod, levels=30, cmap='viridis')
            ax.set_title(f'|f(z)| for f(z) = {expr_str}')
            self.complex_fig.colorbar(cs, ax=ax, fraction=0.046, pad=0.04, label='|f(z)|')
        elif plot_type == 'real':
            real_part = np.real(FZ)
            real_part = np.clip(real_part, np.percentile(real_part[~np.isnan(real_part)], 1),
                                np.percentile(real_part[~np.isnan(real_part)], 99))
            cs = ax.contourf(X, Y, real_part, levels=30, cmap='RdBu_r')
            ax.set_title(f'Re[f(z)] for f(z) = {expr_str}')
            self.complex_fig.colorbar(cs, ax=ax, fraction=0.046, pad=0.04, label='Re')
        elif plot_type == 'imag':
            imag_part = np.imag(FZ)
            imag_part = np.clip(imag_part, np.percentile(imag_part[~np.isnan(imag_part)], 1),
                                np.percentile(imag_part[~np.isnan(imag_part)], 99))
            cs = ax.contourf(X, Y, imag_part, levels=30, cmap='RdBu_r')
            ax.set_title(f'Im[f(z)] for f(z) = {expr_str}')
            self.complex_fig.colorbar(cs, ax=ax, fraction=0.046, pad=0.04, label='Im')

        ax.set_xlabel('Re(z)')
        ax.set_ylabel('Im(z)')
        ax.grid(True, alpha=0.2)
        self.complex_canvas.draw()

    def _clear_plot(self, fig, canvas):
        fig.clear()
        fig.add_subplot(111)
        canvas.draw()


    def _build_problems_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text='Practice Problems')

        self.problems = [
            {
                'title': 'Derivative of a cubic',
                'question': 'Find the derivative of f(x) = x³ - 3x² + 2x - 5.\nThen find f\'(0) and f\'(2).',
                'steps': [
                    'f\'(x) = d/dx (x³ - 3x² + 2x - 5)',
                    'Using the power rule: d/dx(xⁿ) = n·xⁿ⁻¹',
                    'f\'(x) = 3x² - 6x + 2',
                    'f\'(0) = 3(0)² - 6(0) + 2 = 2',
                    'f\'(2) = 3(4) - 6(2) + 2 = 12 - 12 + 2 = 2',
                ],
                'answer': 'f\'(x) = 3x² - 6x + 2, f\'(0) = 2, f\'(2) = 2',
                'plot': {
                    'type': 'derivative',
                    'func': 'x**3 - 3*x**2 + 2*x - 5',
                    'xmin': -2, 'xmax': 4,
                }
            },
            {
                'title': 'Tangent line to sin(x)',
                'question': 'Find the equation of the tangent line to\nf(x) = sin(x) at x = π/4.',
                'steps': [
                    'f(x) = sin(x), f\'(x) = cos(x)',
                    'At x = π/4: f(π/4) = sin(π/4) = √2/2',
                    'f\'(π/4) = cos(π/4) = √2/2',
                    'Tangent line: y - y₀ = m(x - x₀)',
                    'y - √2/2 = (√2/2)(x - π/4)',
                    'y = (√2/2)x + (√2/2)(1 - π/4)',
                ],
                'answer': 'y = (√2/2)(x - π/4) + √2/2',
                'plot': {
                    'type': 'tangent',
                    'func': 'sin(x)',
                    'at': 0.7854,
                    'xmin': 0, 'xmax': 1.57,
                }
            },
            {
                'title': 'Critical points of a cubic',
                'question': 'Find the critical points of f(x) = x³ - 3x² + 2\nand determine if they are maxima or minima.',
                'steps': [
                    'f(x) = x³ - 3x² + 2',
                    'f\'(x) = 3x² - 6x = 3x(x - 2)',
                    'Set f\'(x) = 0: x = 0 or x = 2',
                    'f\'\'(x) = 6x - 6',
                    'At x = 0: f\'\'(0) = -6 < 0 → Local maximum',
                    'At x = 2: f\'\'(2) = 6 > 0 → Local minimum',
                    'f(0) = 2, f(2) = 8 - 12 + 2 = -2',
                ],
                'answer': 'Local max at (0, 2), Local min at (2, -2)',
                'plot': {
                    'type': 'derivative',
                    'func': 'x**3 - 3*x**2 + 2',
                    'xmin': -1.5, 'xmax': 3.5,
                }
            },
            {
                'title': 'Definite integral of a quadratic',
                'question': 'Evaluate ∫₀¹ (x² - 2x + 1) dx',
                'steps': [
                    '∫ (x² - 2x + 1) dx = x³/3 - x² + x + C',
                    'F(1) = 1/3 - 1 + 1 = 1/3',
                    'F(0) = 0 - 0 + 0 = 0',
                    '∫₀¹ = F(1) - F(0) = 1/3',
                ],
                'answer': '1/3',
                'plot': {
                    'type': 'integral',
                    'func': 'x**2 - 2*x + 1',
                    'a': 0, 'b': 1,
                }
            },
            {
                'title': 'Area between curves',
                'question': 'Find the area between y = x² and y = x\nfrom x = 0 to x = 1.',
                'steps': [
                    'Area = ∫₀¹ (upper - lower) dx',
                    'On [0,1]: x ≥ x², so upper = x, lower = x²',
                    'Area = ∫₀¹ (x - x²) dx',
                    '= [x²/2 - x³/3]₀¹',
                    '= (1/2 - 1/3) - (0 - 0)',
                    '= 1/6',
                ],
                'answer': 'Area = 1/6',
                'plot': {
                    'type': 'area_between',
                    'func1': 'x',
                    'func2': 'x**2',
                    'a': 0, 'b': 1,
                }
            },
            {
                'title': 'Integral of sin(x)',
                'question': 'Evaluate ∫₀^π sin(x) dx',
                'steps': [
                    '∫ sin(x) dx = -cos(x) + C',
                    'F(π) = -cos(π) = -(-1) = 1',
                    'F(0) = -cos(0) = -1',
                    '∫₀^π = F(π) - F(0) = 1 - (-1) = 2',
                ],
                'answer': '2',
                'plot': {
                    'type': 'integral',
                    'func': 'sin(x)',
                    'a': 0, 'b': 3.14159,
                }
            },
            {
                'title': 'Phase plot of z²',
                'question': 'Plot the phase portrait of f(z) = z².\nWhat happens to the argument near the origin?',
                'steps': [
                    'f(z) = z² = r²e^(i2θ)',
                    'The argument doubles: arg(f(z)) = 2·arg(z)',
                    'Near the origin (z=0): f(z) ≈ 0',
                    'The phase shows 2 full color cycles around origin',
                    'This is because winding number = 2',
                ],
                'answer': 'f(z) = z² doubles the argument, creating 2 color cycles around the origin',
                'plot': {
                    'type': 'complex_phase',
                    'func': 'z**2',
                    'range': 2,
                }
            },
            {
                'title': 'Modulus of exp(z)',
                'question': 'Plot |exp(z)| in the complex plane.\nDescribe the pattern.',
                'steps': [
                    'f(z) = eᶻ = e^(x+iy) = eˣ·e^(iy)',
                    '|eᶻ| = eˣ (depends only on real part)',
                    'arg(eᶻ) = y (depends only on imaginary part)',
                    'The modulus increases exponentially along x-axis',
                    'The argument varies linearly along y-axis',
                ],
                'answer': '|eᶻ| = eˣ — exponential growth along real axis, constant along imaginary axis',
                'plot': {
                    'type': 'complex_modulus',
                    'func': 'exp(z)',
                    'range': 2,
                }
            },
        ]

        left = ttk.Frame(tab, width=300)
        left.pack(side='left', fill='y', padx=5, pady=5)
        left.pack_propagate(False)

        ttk.Label(left, text='Select a problem:', font=('', 10, 'bold')).pack(anchor='w', padx=5, pady=2)

        self.problem_listbox = tk.Listbox(left, width=40, height=12)
        self.problem_listbox.pack(fill='both', expand=True, padx=5, pady=2)
        for i, p in enumerate(self.problems):
            self.problem_listbox.insert(i, p['title'])
        self.problem_listbox.bind('<<ListboxSelect>>', self._on_problem_select)

        sep = ttk.Separator(left, orient='horizontal')
        sep.pack(fill='x', padx=5, pady=5)

        ttk.Label(left, text='Your own problem:', font=('', 10, 'bold')).pack(anchor='w', padx=5, pady=2)

        self.c = ttk.Frame(left)
        self.c.pack(fill='x', padx=5, pady=2)

        ttk.Label(self.c, text='Type:').grid(row=0, column=0, sticky='w')
        self.custom_type = ttk.Combobox(self.c, values=['Derivative', 'Integral', 'Tangent', 'Area Between', 'Complex Phase', 'Complex Modulus'], width=18, state='readonly')
        self.custom_type.grid(row=0, column=1, pady=1)
        self.custom_type.set('Derivative')
        self.custom_type.bind('<<ComboboxSelected>>', self._on_custom_type_change)

        ttk.Label(self.c, text='f(x) =').grid(row=1, column=0, sticky='w')
        self.custom_func = ttk.Entry(self.c, width=22)
        self.custom_func.grid(row=1, column=1, pady=1)
        self.custom_func.insert(0, 'x**2')

        ttk.Label(self.c, text='f2(x) =').grid(row=2, column=0, sticky='w')
        self.custom_func2 = ttk.Entry(self.c, width=22)
        self.custom_func2.grid(row=2, column=1, pady=1)
        self.custom_func2.insert(0, 'x')

        ttk.Label(self.c, text='From:').grid(row=3, column=0, sticky='w')
        self.custom_a = ttk.Entry(self.c, width=10)
        self.custom_a.grid(row=3, column=1, sticky='w', pady=1)
        self.custom_a.insert(0, '0')

        ttk.Label(self.c, text='To:').grid(row=3, column=1, padx=55)
        self.custom_b = ttk.Entry(self.c, width=10)
        self.custom_b.grid(row=3, column=1, padx=80, pady=1)
        self.custom_b.insert(0, '1')

        self.custom_at_label = ttk.Label(self.c, text='At x =')
        self.custom_at_label.grid(row=4, column=0, sticky='w')
        self.custom_at = ttk.Entry(self.c, width=10)
        self.custom_at.grid(row=4, column=1, sticky='w', pady=1)
        self.custom_at.insert(0, '0.5')
        self.custom_range_label = ttk.Label(self.c, text='Range:')
        self.custom_range = ttk.Entry(self.c, width=10)
        self.custom_range.grid(row=4, column=1, padx=80, pady=1)
        self.custom_range.insert(0, '2')

        self._update_custom_fields()

        btn_c = ttk.Frame(left)
        btn_c.pack(fill='x', padx=5, pady=3)
        ttk.Button(btn_c, text='Solve', command=self._solve_custom).pack(side='left', padx=2)
        ttk.Button(btn_c, text='Plot', command=self._plot_custom).pack(side='left', padx=2)
        ttk.Button(btn_c, text='Add to List', command=self._add_custom_to_list).pack(side='left', padx=2)

        right = ttk.Frame(tab)
        right.pack(side='right', fill='both', expand=True, padx=5, pady=5)

        self.prob_question = tk.Text(right, height=4, width=60, wrap='word', font=('', 10))
        self.prob_question.pack(fill='x', padx=5, pady=2)
        self.prob_question.insert('1.0', 'Select a problem from the list.')
        self.prob_question.config(state='disabled')

        self.prob_steps = tk.Text(right, height=12, width=60, wrap='word', font=('', 10))
        self.prob_steps.pack(fill='x', padx=5, pady=2)
        self.prob_steps.config(state='disabled')

        btn_frame = ttk.Frame(right)
        btn_frame.pack(fill='x', padx=5, pady=2)

        self.show_solution_btn = ttk.Button(btn_frame, text='Show Solution', command=self._show_problem_solution)
        self.show_solution_btn.pack(side='left', padx=5)

        self.plot_problem_btn = ttk.Button(btn_frame, text='Visualize', command=self._plot_problem)
        self.plot_problem_btn.pack(side='left', padx=5)

        self.current_problem = None
        self.prob_fig = Figure(figsize=(6, 4))
        self.prob_ax = self.prob_fig.add_subplot(111)
        self.prob_canvas = FigureCanvasTkAgg(self.prob_fig, master=right)
        self.prob_canvas.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)

    def _on_problem_select(self, event):
        sel = self.problem_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        self.current_problem = self.problems[idx]
        self.prob_question.config(state='normal')
        self.prob_question.delete('1.0', 'end')
        self.prob_question.insert('1.0', self.current_problem['question'])
        self.prob_question.config(state='disabled')
        self.prob_steps.config(state='normal')
        self.prob_steps.delete('1.0', 'end')
        self.prob_steps.insert('1.0', 'Click "Show Solution" to see the step-by-step solution.')
        self.prob_steps.config(state='disabled')
        self.prob_ax.clear()
        self.prob_canvas.draw()

    def _show_problem_solution(self):
        if not self.current_problem:
            return
        steps = '\n\n'.join(f'{i+1}. {s}' for i, s in enumerate(self.current_problem['steps']))
        steps += f'\n\nAnswer: {self.current_problem["answer"]}'
        self.prob_steps.config(state='normal')
        self.prob_steps.delete('1.0', 'end')
        self.prob_steps.insert('1.0', steps)
        self.prob_steps.config(state='disabled')

    def _plot_problem(self):
        if not self.current_problem:
            return
        cfg = self.current_problem.get('plot')
        if not cfg:
            return
        self.prob_ax.clear()
        t = cfg['type']
        x = sp.Symbol('x')

        if t == 'derivative':
            f = sp.sympify(cfg['func'])
            fp = sp.diff(f, x)
            fn = sp.lambdify(x, f, 'numpy')
            fpn = sp.lambdify(x, fp, 'numpy')
            xs = np.linspace(cfg['xmin'], cfg['xmax'], 400)
            self.prob_ax.plot(xs, fn(xs), 'b-', linewidth=2, label=f'f(x)')
            self.prob_ax.plot(xs, fpn(xs), 'r--', linewidth=2, label=f"f'(x)")
            self.prob_ax.axhline(0, color='gray', linewidth=0.5)
            self.prob_ax.legend(fontsize=9)
            self.prob_ax.grid(True, alpha=0.3)
            self.prob_ax.set_xlabel('x')

        elif t == 'tangent':
            f = sp.sympify(cfg['func'])
            fp = sp.diff(f, x)
            fn = sp.lambdify(x, f, 'numpy')
            fpn = sp.lambdify(x, fp, 'numpy')
            at = cfg['at']
            xs = np.linspace(cfg['xmin'], cfg['xmax'], 400)
            y0 = fn(at)
            m = fpn(at)
            self.prob_ax.plot(xs, fn(xs), 'b-', linewidth=2, label=f'f(x)')
            self.prob_ax.plot(xs, m * (xs - at) + y0, 'g--', linewidth=2, label='Tangent')
            self.prob_ax.plot(at, y0, 'ro', markersize=8)
            self.prob_ax.axhline(0, color='gray', linewidth=0.5)
            self.prob_ax.legend(fontsize=9)
            self.prob_ax.grid(True, alpha=0.3)

        elif t == 'integral':
            f = sp.sympify(cfg['func'])
            fn = sp.lambdify(x, f, 'numpy')
            a, b = cfg['a'], cfg['b']
            pad = (b - a) * 0.2
            xs = np.linspace(a - pad, b + pad, 400)
            ys = fn(xs)
            self.prob_ax.plot(xs, ys, 'b-', linewidth=2)
            xf = np.linspace(a, b, 400)
            yf = fn(xf)
            self.prob_ax.fill_between(xf, yf, alpha=0.3, color='skyblue')
            self.prob_ax.axvline(a, color='red', linestyle='--')
            self.prob_ax.axvline(b, color='red', linestyle='--')
            self.prob_ax.grid(True, alpha=0.3)
            self.prob_ax.set_xlabel('x')

        elif t == 'area_between':
            f1 = sp.sympify(cfg['func1'])
            f2 = sp.sympify(cfg['func2'])
            fn1 = sp.lambdify(x, f1, 'numpy')
            fn2 = sp.lambdify(x, f2, 'numpy')
            a, b = cfg['a'], cfg['b']
            pad = (b - a) * 0.2
            xs = np.linspace(a - pad, b + pad, 400)
            self.prob_ax.plot(xs, fn1(xs), 'b-', linewidth=2, label='y = x')
            self.prob_ax.plot(xs, fn2(xs), 'r-', linewidth=2, label='y = x²')
            xf = np.linspace(a, b, 400)
            self.prob_ax.fill_between(xf, fn1(xf), fn2(xf), alpha=0.3, color='green')
            self.prob_ax.axhline(0, color='gray', linewidth=0.5)
            self.prob_ax.legend(fontsize=9)
            self.prob_ax.grid(True, alpha=0.3)

        elif t == 'complex_phase':
            r = cfg['range']
            n = 300
            xx = np.linspace(-r, r, n)
            yy = np.linspace(-r, r, n)
            XX, YY = np.meshgrid(xx, yy)
            ZZ = XX + 1j * YY
            local_vars = {'z': ZZ, 'np': np, 'sin': np.sin, 'cos': np.cos, 'exp': np.exp,
                          'log': np.log, 'abs': np.abs, 'sqrt': np.sqrt, 'tan': np.tan,
                          'pi': np.pi, 'e': np.e, '1j': 1j}
            FZ = eval(cfg['func'].replace('^', '**'), {'__builtins__': {}}, local_vars)
            phase = np.angle(FZ)
            self.prob_ax.imshow(phase, extent=[-r, r, -r, r], cmap='hsv', origin='lower', aspect='auto')
            self.prob_ax.set_xlabel('Re(z)')
            self.prob_ax.set_ylabel('Im(z)')

        elif t == 'complex_modulus':
            r = cfg['range']
            n = 300
            xx = np.linspace(-r, r, n)
            yy = np.linspace(-r, r, n)
            XX, YY = np.meshgrid(xx, yy)
            ZZ = XX + 1j * YY
            local_vars = {'z': ZZ, 'np': np, 'sin': np.sin, 'cos': np.cos, 'exp': np.exp,
                          'log': np.log, 'abs': np.abs, 'sqrt': np.sqrt, 'tan': np.tan,
                          'pi': np.pi, 'e': np.e, '1j': 1j}
            FZ = eval(cfg['func'].replace('^', '**'), {'__builtins__': {}}, local_vars)
            mod = np.abs(FZ)
            mod = np.clip(mod, 1e-10, np.percentile(mod[~np.isnan(mod)], 95))
            cs = self.prob_ax.contourf(XX, YY, mod, levels=30, cmap='viridis')
            self.prob_fig.colorbar(cs, ax=self.prob_ax, fraction=0.046, pad=0.04)
            self.prob_ax.set_xlabel('Re(z)')
            self.prob_ax.set_ylabel('Im(z)')

        self.prob_ax.set_title(self.current_problem['title'])
        self.prob_canvas.draw()


    def _on_custom_type_change(self, event=None):
        self._update_custom_fields()

    def _update_custom_fields(self):
        t = self.custom_type.get()
        show_f2 = t == 'Area Between'
        show_bounds = t in ('Integral', 'Area Between')
        show_at = t == 'Tangent'
        show_range = t in ('Complex Phase', 'Complex Modulus')

        self.custom_func2.grid()
        self.custom_func2.grid_remove()
        self.custom_a.grid()
        self.custom_a.grid_remove()
        self.custom_b.grid()
        self.custom_b.grid_remove()
        self.custom_at.grid()
        self.custom_at.grid_remove()
        self.custom_range.grid()
        self.custom_range.grid_remove()
        self.custom_at_label.grid()
        self.custom_at_label.grid_remove()
        self.custom_range_label.grid()
        self.custom_range_label.grid_remove()

        if show_f2:
            self.custom_func2.grid()
        if show_bounds:
            self.custom_a.grid()
            self.custom_b.grid()
        if show_at:
            self.custom_at_label.grid()
            self.custom_at.grid()
        if show_range:
            self.custom_range_label.grid()
            self.custom_range.grid()

    def _solve_custom(self):
        t = self.custom_type.get()
        func_str = self.custom_func.get().strip()
        x = sp.Symbol('x')
        steps = []
        answer = ''

        try:
            if t == 'Derivative':
                f = sp.sympify(func_str)
                fp = sp.diff(f, x)
                steps.append(f'f(x) = {sp.latex(f)}')
                steps.append(f"f'(x) = {sp.latex(fp)}")
                a_str = self.custom_a.get().strip()
                b_str = self.custom_b.get().strip()
                if a_str:
                    a = float(sp.N(sp.sympify(a_str)))
                    steps.append(f"f'({a}) = {float(fp.subs(x, a)):.4f}")
                if b_str:
                    b = float(sp.N(sp.sympify(b_str)))
                    steps.append(f"f'({b}) = {float(fp.subs(x, b)):.4f}")
                answer = sp.latex(fp)
            elif t == 'Integral':
                f = sp.sympify(func_str)
                F = sp.integrate(f, x)
                steps.append(f'∫ f(x) dx = {sp.latex(F)} + C')
                a = float(sp.N(sp.sympify(self.custom_a.get())))
                b = float(sp.N(sp.sympify(self.custom_b.get())))
                definite = sp.integrate(f, (x, a, b))
                steps.append(f'∫ from {a:.4f} to {b:.4f}')
                steps.append(f'= {float(definite):.6f}')
                answer = f'{float(definite):.6f}'
            elif t == 'Tangent':
                f = sp.sympify(func_str)
                fp = sp.diff(f, x)
                at = float(self.custom_at.get())
                y0 = float(f.subs(x, at))
                m = float(fp.subs(x, at))
                steps.append(f'f(x) = {sp.latex(f)}')
                steps.append(f"f'(x) = {sp.latex(fp)}")
                steps.append(f'At x = {at}:')
                steps.append(f'  f({at}) = {y0:.4f}')
                steps.append(f"  f'({at}) = {m:.4f}")
                steps.append(f'Tangent: y = {m:.4f}(x - {at}) + {y0:.4f}')
                answer = f'y = {m:.4f}(x - {at}) + {y0:.4f}'
            elif t == 'Area Between':
                f1 = sp.sympify(func_str)
                f2 = sp.sympify(self.custom_func2.get().strip())
                a = float(sp.N(sp.sympify(self.custom_a.get())))
                b = float(sp.N(sp.sympify(self.custom_b.get())))
                area = sp.integrate(sp.Abs(f1 - f2), (x, a, b))
                steps.append(f'f1(x) = {sp.latex(f1)}')
                steps.append(f'f2(x) = {sp.latex(f2)}')
                steps.append(f'Area = ∫ |f1 - f2| dx from {a} to {b}')
                steps.append(f'= {float(area):.6f}')
                answer = f'{float(area):.6f}'
            elif t in ('Complex Phase', 'Complex Modulus'):
                steps.append(f'f(z) = {func_str}')
                steps.append('Visualizing in the complex plane...')
                answer = 'See the plot for visualization.'
        except Exception as e:
            steps.append(f'Error: {e}')
            answer = 'Could not solve'

        self.prob_question.config(state='normal')
        self.prob_question.delete('1.0', 'end')
        self.prob_question.insert('1.0', f'Solving: {t}\nf(x) = {func_str}')
        self.prob_question.config(state='disabled')
        text = '\n\n'.join(f'{i+1}. {s}' for i, s in enumerate(steps))
        text += f'\n\nAnswer: {answer}'
        self.prob_steps.config(state='normal')
        self.prob_steps.delete('1.0', 'end')
        self.prob_steps.insert('1.0', text)
        self.prob_steps.config(state='disabled')

    def _plot_custom(self):
        t = self.custom_type.get()
        func_str = self.custom_func.get().strip()
        self.prob_ax.clear()
        x = sp.Symbol('x')

        try:
            if t == 'Derivative':
                f = sp.sympify(func_str)
                fp = sp.diff(f, x)
                fn = sp.lambdify(x, f, 'numpy')
                fpn = sp.lambdify(x, fp, 'numpy')
                a = float(sp.N(sp.sympify(self.custom_a.get() or '-2')))
                b = float(sp.N(sp.sympify(self.custom_b.get() or '2')))
                if a >= b: a, b = -2, 2
                xs = np.linspace(a, b, 400)
                self.prob_ax.plot(xs, fn(xs), 'b-', linewidth=2, label='f(x)')
                self.prob_ax.plot(xs, fpn(xs), 'r--', linewidth=2, label="f'(x)")
                self.prob_ax.axhline(0, color='gray', linewidth=0.5)
                self.prob_ax.legend(fontsize=9)
                self.prob_ax.grid(True, alpha=0.3)
            elif t == 'Integral':
                f = sp.sympify(func_str)
                fn = sp.lambdify(x, f, 'numpy')
                a = float(sp.N(sp.sympify(self.custom_a.get())))
                b = float(sp.N(sp.sympify(self.custom_b.get())))
                pad = (b - a) * 0.2
                xs = np.linspace(a - pad, b + pad, 400)
                self.prob_ax.plot(xs, fn(xs), 'b-', linewidth=2)
                xf = np.linspace(a, b, 400)
                self.prob_ax.fill_between(xf, fn(xf), alpha=0.3, color='skyblue')
                self.prob_ax.axvline(a, color='red', linestyle='--')
                self.prob_ax.axvline(b, color='red', linestyle='--')
                self.prob_ax.grid(True, alpha=0.3)
            elif t == 'Tangent':
                f = sp.sympify(func_str)
                fp = sp.diff(f, x)
                fn = sp.lambdify(x, f, 'numpy')
                fpn = sp.lambdify(x, fp, 'numpy')
                at = float(self.custom_at.get())
                a = float(sp.N(sp.sympify(self.custom_a.get() or str(at - 2))))
                b = float(sp.N(sp.sympify(self.custom_b.get() or str(at + 2))))
                xs = np.linspace(a, b, 400)
                y0 = fn(at)
                m = fpn(at)
                self.prob_ax.plot(xs, fn(xs), 'b-', linewidth=2, label='f(x)')
                self.prob_ax.plot(xs, m * (xs - at) + y0, 'g--', linewidth=2, label='Tangent')
                self.prob_ax.plot(at, y0, 'ro', markersize=8)
                self.prob_ax.axhline(0, color='gray', linewidth=0.5)
                self.prob_ax.legend(fontsize=9)
                self.prob_ax.grid(True, alpha=0.3)
            elif t == 'Area Between':
                f1 = sp.sympify(func_str)
                f2 = sp.sympify(self.custom_func2.get().strip())
                fn1 = sp.lambdify(x, f1, 'numpy')
                fn2 = sp.lambdify(x, f2, 'numpy')
                a = float(sp.N(sp.sympify(self.custom_a.get())))
                b = float(sp.N(sp.sympify(self.custom_b.get())))
                pad = (b - a) * 0.2
                xs = np.linspace(a - pad, b + pad, 400)
                self.prob_ax.plot(xs, fn1(xs), 'b-', linewidth=2, label='f1(x)')
                self.prob_ax.plot(xs, fn2(xs), 'r-', linewidth=2, label='f2(x)')
                xf = np.linspace(a, b, 400)
                y1 = fn1(xf); y2 = fn2(xf)
                self.prob_ax.fill_between(xf, y1, y2, alpha=0.3, color='green')
                self.prob_ax.axhline(0, color='gray', linewidth=0.5)
                self.prob_ax.legend(fontsize=9)
                self.prob_ax.grid(True, alpha=0.3)
            elif t == 'Complex Phase':
                r = float(self.custom_range.get())
                n = 300
                xx = np.linspace(-r, r, n)
                yy = np.linspace(-r, r, n)
                XX, YY = np.meshgrid(xx, yy)
                ZZ = XX + 1j * YY
                lv = {'z': ZZ, 'np': np, 'sin': np.sin, 'cos': np.cos, 'exp': np.exp,
                      'log': np.log, 'abs': np.abs, 'sqrt': np.sqrt, 'tan': np.tan,
                      'pi': np.pi, 'e': np.e, '1j': 1j}
                FZ = eval(func_str.replace('^', '**'), {'__builtins__': {}}, lv)
                phase = np.angle(FZ)
                self.prob_ax.imshow(phase, extent=[-r, r, -r, r], cmap='hsv', origin='lower', aspect='auto')
                self.prob_ax.set_xlabel('Re(z)')
                self.prob_ax.set_ylabel('Im(z)')
            elif t == 'Complex Modulus':
                r = float(self.custom_range.get())
                n = 300
                xx = np.linspace(-r, r, n)
                yy = np.linspace(-r, r, n)
                XX, YY = np.meshgrid(xx, yy)
                ZZ = XX + 1j * YY
                lv = {'z': ZZ, 'np': np, 'sin': np.sin, 'cos': np.cos, 'exp': np.exp,
                      'log': np.log, 'abs': np.abs, 'sqrt': np.sqrt, 'tan': np.tan,
                      'pi': np.pi, 'e': np.e, '1j': 1j}
                FZ = eval(func_str.replace('^', '**'), {'__builtins__': {}}, lv)
                mod = np.abs(FZ)
                mod = np.clip(mod, 1e-10, np.percentile(mod[~np.isnan(mod)], 95))
                cs = self.prob_ax.contourf(XX, YY, mod, levels=30, cmap='viridis')
                self.prob_fig.colorbar(cs, ax=self.prob_ax, fraction=0.046, pad=0.04)
                self.prob_ax.set_xlabel('Re(z)')
                self.prob_ax.set_ylabel('Im(z)')

            self.prob_ax.set_title(f'{t}: {func_str}')
        except Exception as e:
            self.prob_ax.text(0.5, 0.5, f'Error: {e}', ha='center', va='center', transform=self.prob_ax.transAxes)
        self.prob_canvas.draw()

    def _add_custom_to_list(self):
        t = self.custom_type.get()
        func_str = self.custom_func.get().strip()
        title = f'Custom: {t} of {func_str}'
        if len(title) > 45:
            title = title[:42] + '...'
        q = f'Solve the {t.lower()} of f(x) = {func_str}'
        steps = ['Custom problem — click Show Solution or Visualize.']
        answer = 'Use Solve and Plot buttons.'
        p = {'title': title, 'question': q, 'steps': steps, 'answer': answer}
        if t == 'Tangent':
            p['plot'] = {'type': 'tangent', 'func': func_str, 'at': float(self.custom_at.get()),
                          'xmin': float(self.custom_a.get() or '-2'), 'xmax': float(self.custom_b.get() or '2')}
        elif t == 'Integral':
            p['plot'] = {'type': 'integral', 'func': func_str,
                          'a': float(sp.N(sp.sympify(self.custom_a.get()))),
                          'b': float(sp.N(sp.sympify(self.custom_b.get())))}
        elif t == 'Area Between':
            p['title'] = f'Custom: Area between {func_str} and {self.custom_func2.get()}'
            p['plot'] = {'type': 'area_between', 'func1': func_str, 'func2': self.custom_func2.get().strip(),
                          'a': float(sp.N(sp.sympify(self.custom_a.get()))),
                          'b': float(sp.N(sp.sympify(self.custom_b.get())))}
        elif t == 'Derivative':
            p['plot'] = {'type': 'derivative', 'func': func_str, 'xmin': -3, 'xmax': 3}
        elif t in ('Complex Phase', 'Complex Modulus'):
            pt = 'complex_phase' if t == 'Complex Phase' else 'complex_modulus'
            p['plot'] = {'type': pt, 'func': func_str, 'range': float(self.custom_range.get())}
        self.problems.append(p)
        self.problem_listbox.insert('end', title)
        self.problem_listbox.select_clear(0, 'end')
        self.problem_listbox.select_set('end')
        self._on_problem_select(None)


if __name__ == '__main__':
    root = tk.Tk()
    app = CalculusApp(root)
    root.mainloop()
