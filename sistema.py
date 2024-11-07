import tkinter as tk
from tkinter import messagebox

class Producto:
    def __init__(self, nombre, precio):
        self.nombre = nombre
        self.precio = precio

class PuntoDeVenta:
    def __init__(self):
        self.productos = []  # Lista de productos disponibles
        self.carrito = []    # Carrito de compras del cliente
    
    def agregar_producto(self, nombre, precio):
        """Agrega un producto al inventario"""
        producto = Producto(nombre, precio)
        self.productos.append(producto)
    
    def obtener_productos(self):
        """Devuelve los productos como una lista de tuplas (nombre, precio)"""
        return [(producto.nombre, producto.precio) for producto in self.productos]
    
    def agregar_al_carrito(self, indice_producto, cantidad):
        """Agrega un producto al carrito de compras"""
        if 0 <= indice_producto < len(self.productos):
            producto = self.productos[indice_producto]
            for _ in range(cantidad):
                self.carrito.append(producto)
    
    def calcular_total(self):
        """Calcula el total de la compra"""
        total = sum([producto.precio for producto in self.carrito])
        return total

    def generar_recibo(self):
        """Genera el recibo de compra"""
        recibo = ""
        for producto in self.carrito:
            recibo += f"{producto.nombre} - ${producto.precio:.2f}\n"
        total = self.calcular_total()
        recibo += f"\nTotal: ${total:.2f}"
        return recibo

# Función para actualizar la lista de productos en la interfaz
def actualizar_lista_productos():
    for widget in frame_productos.winfo_children():
        widget.destroy()
    
    productos = pos.obtener_productos()
    for index, (nombre, precio) in enumerate(productos):
        tk.Label(frame_productos, text=f"{nombre} - ${precio:.2f}").grid(row=index, column=0, sticky="w")
        tk.Button(frame_productos, text="Agregar", command=lambda idx=index: agregar_al_carrito(idx)).grid(row=index, column=1)

# Función para agregar productos al carrito
def agregar_al_carrito(indice_producto):
    cantidad = int(entry_cantidad.get())
    if cantidad > 0:
        pos.agregar_al_carrito(indice_producto, cantidad)
        messagebox.showinfo("Producto Agregado", f"Se han agregado {cantidad} unidades al carrito.")
    else:
        messagebox.showwarning("Cantidad Inválida", "Por favor, ingrese una cantidad mayor a 0.")
    entry_cantidad.delete(0, tk.END)

# Función para mostrar el total y el recibo
def mostrar_recibo():
    total = pos.calcular_total()
    recibo = pos.generar_recibo()
    messagebox.showinfo("Recibo", recibo)
    lbl_total.config(text=f"Total: ${total:.2f}")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Punto de Venta")

# Crear el objeto de PuntoDeVenta
pos = PuntoDeVenta()

# Agregar algunos productos al inventario
pos.agregar_producto("Camiseta", 15.99)
pos.agregar_producto("Pantalón", 25.50)
pos.agregar_producto("Zapatos", 50.75)
pos.agregar_producto("Gorra", 10.00)
pos.agregar_producto("Chaqueta", 35.80)

# Frame para mostrar los productos
frame_productos = tk.Frame(ventana)
frame_productos.pack(pady=10)

# Etiqueta para el total
lbl_total = tk.Label(ventana, text="Total: $0.00", font=("Arial", 16))
lbl_total.pack(pady=10)

# Entrada para la cantidad
entry_cantidad = tk.Entry(ventana)
entry_cantidad.pack(pady=5)
entry_cantidad.insert(0, "1")  # Valor predeterminado de la cantidad

# Botón para mostrar el recibo
btn_recibo = tk.Button(ventana, text="Generar Recibo", command=mostrar_recibo)
btn_recibo.pack(pady=10)

# Actualizar la lista de productos
actualizar_lista_productos()

# Iniciar el bucle principal de la ventana
ventana.mainloop()
