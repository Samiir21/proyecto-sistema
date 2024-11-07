import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime

class Producto:
    def __init__(self, nombre, precio):
        self.nombre = nombre
        self.precio = precio

class PuntoDeVenta:
    def __init__(self, db_name="productos.db"):
        self.db_name = db_name
        self.conectar_db()

    def conectar_db(self):
        """Conecta a la base de datos y crea las tablas si no existen."""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                precio REAL NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                total REAL NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalles_venta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER,
                producto_id INTEGER,
                cantidad INTEGER,
                subtotal REAL,
                FOREIGN KEY(venta_id) REFERENCES ventas(id),
                FOREIGN KEY(producto_id) REFERENCES productos(id)
            )
        ''')
        self.conn.commit()

    def agregar_producto(self, nombre, precio):
        """Agrega un producto al inventario."""
        self.cursor.execute('''
            INSERT INTO productos (nombre, precio)
            VALUES (?, ?)
        ''', (nombre, precio))
        self.conn.commit()

    def obtener_productos(self):
        """Obtiene todos los productos del inventario."""
        self.cursor.execute('SELECT id, nombre, precio FROM productos')
        productos = self.cursor.fetchall()
        return [(producto[0], producto[1], producto[2]) for producto in productos]

    def eliminar_producto(self, id_producto):
        """Elimina un producto del inventario."""
        self.cursor.execute('DELETE FROM productos WHERE id = ?', (id_producto,))
        self.conn.commit()

    def agregar_al_carrito(self, id_producto, cantidad):
        """Agrega un producto al carrito de compras."""
        self.cursor.execute('SELECT nombre, precio FROM productos WHERE id = ?', (id_producto,))
        producto = self.cursor.fetchone()
        if producto:
            nombre, precio = producto
            return Producto(nombre, precio), cantidad
        return None, 0

    def calcular_total(self, carrito):
        """Calcula el total de la compra."""
        return sum([producto.precio * cantidad for producto, cantidad in carrito])

    def generar_recibo(self, carrito):
        """Genera el recibo de compra."""
        recibo = ""
        for producto, cantidad in carrito:
            recibo += f"{producto.nombre} x{cantidad} - ${producto.precio * cantidad:.2f}\n"
        total = self.calcular_total(carrito)
        recibo += f"\nTotal: ${total:.2f}"
        return recibo

    def registrar_venta(self, carrito):
        """Registra una venta en la base de datos."""
        total = self.calcular_total(carrito)
        fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Insertar la venta en la tabla 'ventas'
        self.cursor.execute('''
            INSERT INTO ventas (fecha, total)
            VALUES (?, ?)
        ''', (fecha, total))
        venta_id = self.cursor.lastrowid

        # Insertar los detalles de la venta en la tabla 'detalles_venta'
        for producto, cantidad in carrito:
            subtotal = producto.precio * cantidad
            self.cursor.execute('''
                INSERT INTO detalles_venta (venta_id, producto_id, cantidad, subtotal)
                VALUES (?, ?, ?, ?)
            ''', (venta_id, producto.id, cantidad, subtotal))

        self.conn.commit()

# Función para actualizar la lista de productos en la interfaz
def actualizar_lista_productos():
    for widget in frame_productos.winfo_children():
        widget.destroy()
    
    productos = pos.obtener_productos()
    for index, (id_producto, nombre, precio) in enumerate(productos):
        tk.Label(frame_productos, text=f"{nombre} - ${precio:.2f}").grid(row=index, column=0, sticky="w")
        tk.Button(frame_productos, text="Agregar", command=lambda idx=id_producto: agregar_al_carrito(idx)).grid(row=index, column=1)
        tk.Button(frame_productos, text="Eliminar", command=lambda idx=id_producto: eliminar_producto(idx)).grid(row=index, column=2)

# Función para agregar productos al carrito
def agregar_al_carrito(id_producto):
    cantidad = int(entry_cantidad.get())
    if cantidad > 0:
        producto, cantidad = pos.agregar_al_carrito(id_producto, cantidad)
        if producto:
            carrito.append((producto, cantidad))
            messagebox.showinfo("Producto Agregado", f"Se han agregado {cantidad} unidades al carrito.")
        else:
            messagebox.showwarning("Producto No Encontrado", "El producto no existe.")
    else:
        messagebox.showwarning("Cantidad Inválida", "Por favor, ingrese una cantidad mayor a 0.")
    entry_cantidad.delete(0, tk.END)

# Función para eliminar productos
def eliminar_producto(id_producto):
    pos.eliminar_producto(id_producto)
    messagebox.showinfo("Producto Eliminado", "El producto ha sido eliminado del inventario.")
    actualizar_lista_productos()

# Función para realizar la venta y registrar la transacción
def realizar_venta():
    if not carrito:
        messagebox.showwarning("Carrito Vacío", "El carrito está vacío. Agregue productos antes de realizar la venta.")
        return

    # Registrar la venta en la base de datos
    pos.registrar_venta(carrito)

    # Mostrar recibo
    total = pos.calcular_total(carrito)
    recibo = pos.generar_recibo(carrito)
    messagebox.showinfo("Venta Realizada", f"Venta realizada con éxito.\n\n{recibo}")

    # Limpiar carrito
    carrito.clear()
    lbl_total.config(text="Total: $0.00")
    actualizar_lista_productos()

# Función para mostrar el total y el recibo
def mostrar_recibo():
    total = pos.calcular_total(carrito)
    recibo = pos.generar_recibo(carrito)
    messagebox.showinfo("Recibo", recibo)
    lbl_total.config(text=f"Total: ${total:.2f}")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Punto de Venta")

# Crear el objeto de PuntoDeVenta
pos = PuntoDeVenta()

# Crear una lista de carrito (productos agregados al carrito de compras)
carrito = []

# Agregar algunos productos al inventario (solo se agrega si no están previamente en la base de datos)
productos_iniciales = [
    ("Camiseta", 15.99),
    ("Pantalón", 25.50),
    ("Zapatos", 50.75),
    ("Gorra", 10.00),
    ("Chaqueta", 35.80)
]

for nombre, precio in productos_iniciales:
    pos.agregar_producto(nombre, precio)

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

# Botón para generar el recibo
btn_recibo = tk.Button(ventana, text="Generar Recibo", command=mostrar_recibo)
btn_recibo.pack(pady=10)

# Botón para realizar la venta
btn_venta = tk.Button(ventana, text="Realizar Venta", command=realizar_venta)
btn_venta.pack(pady=10)

# Actualizar la lista de productos
actualizar_lista_productos()

# Iniciar el bucle principal de la ventana
ventana.mainloop()
