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


if __name__ == '__main__':
    root = tk.Tk()
    app = CalculusApp(root)
    root.mainloop()
