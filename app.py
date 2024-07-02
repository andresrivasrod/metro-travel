import tkinter as tk
from tkinter import messagebox, Canvas
import math

class MetroTravelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Metro Travel Route Finder")  # Título de la ventana principal

        # Cargar automáticamente los datos al inicio
        try:
            file_path = "data.csv"  # Nombre del archivo CSV con los datos
            self.data = self.load_data(file_path)  # Cargar los datos desde el archivo CSV
            self.create_graph()  # Crear el grafo basado en los datos cargados
            messagebox.showinfo("Datos Cargados", "Datos cargados exitosamente desde 'data.csv'.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar los datos desde 'data.csv': {e}")  # Mostrar mensaje de error si no se pueden cargar los datos

        self.create_widgets()  # Crear todos los elementos de la interfaz gráfica

    def load_data(self, file_path):
        data = []
        with open(file_path, 'r') as file:
            lines = file.readlines()
            headers = lines[0].strip().split(',')  # Obtener los encabezados del archivo CSV
            for line in lines[1:]:
                row = line.strip().split(',')
                data.append({headers[i]: row[i] for i in range(len(headers))})  # Crear diccionarios para cada fila de datos
        return data  # Devolver la lista de diccionarios con los datos cargados

    def create_widgets(self):
        # Crear etiquetas y campos de entrada para origen y destino
        tk.Label(self.root, text="Aeropuerto de Origen:").grid(row=0, column=0)
        self.origin_entry = tk.Entry(self.root)
        self.origin_entry.grid(row=0, column=1)

        tk.Label(self.root, text="Aeropuerto de Destino:").grid(row=1, column=0)
        self.destination_entry = tk.Entry(self.root)
        self.destination_entry.grid(row=1, column=1)

        # Checkbox para seleccionar si tiene visa
        self.visa_var = tk.BooleanVar()
        tk.Checkbutton(self.root, text="¿Tiene visa?", variable=self.visa_var).grid(row=2, columnspan=2)

        # Radio buttons para seleccionar la opción de ruta (más barata o menos escalas)
        self.route_option = tk.StringVar(value="Cheapest")
        tk.Radiobutton(self.root, text="Ruta más barata", variable=self.route_option, value="Cheapest").grid(row=3, column=0)
        tk.Radiobutton(self.root, text="Menos escalas", variable=self.route_option, value="Fewest Stops").grid(row=3, column=1)

        # Botones para encontrar la ruta y mostrar el grafo
        tk.Button(self.root, text="Encontrar Ruta", command=self.find_route).grid(row=4, columnspan=2)
        tk.Button(self.root, text="Mostrar Grafo", command=self.show_graph).grid(row=5, columnspan=2)

    def create_graph(self):
        # Crear un conjunto de nodos únicos (aeropuertos)
        self.nodes = set()
        for row in self.data:
            self.nodes.add(row['Origen'])
            self.nodes.add(row['Destino'])

        self.node_list = list(self.nodes)  # Lista de nodos únicos
        self.node_index = {node: i for i, node in enumerate(self.node_list)}  # Índices de los nodos en la lista

        size = len(self.nodes)
        self.adj_matrix = [[float('inf')] * size for _ in range(size)]  # Matriz de adyacencia para almacenar los costos de vuelo
        self.visa_matrix = [[1] * size for _ in range(size)]  # Matriz de adyacencia para requisitos de visa (1: requiere visa, 0: no requiere visa)

        # Llenar las matrices de adyacencia con los datos cargados
        for row in self.data:
            i = self.node_index[row['Origen']]
            j = self.node_index[row['Destino']]
            self.adj_matrix[i][j] = float(row['Precio'])
            self.adj_matrix[j][i] = float(row['Precio'])  # Grafo no dirigido, mismo costo en ambas direcciones
            self.visa_matrix[i][j] = int(row['Requiere_Visa'])
            self.visa_matrix[j][i] = int(row['Requiere_Visa'])

    def dijkstra_shortest_path(self, start, end, has_visa, weight_matrix):
        import heapq

        size = len(self.node_list)
        distances = [float('inf')] * size  # Distancias iniciales, todas a infinito
        previous_nodes = [None] * size  # Nodos previos en el camino más corto
        distances[self.node_index[start]] = 0  # Distancia al nodo inicial es 0
        priority_queue = [(0, self.node_index[start])]  # Cola de prioridad para explorar nodos

        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)

            if current_distance > distances[current_node]:
                continue

            for neighbor in range(size):
                if weight_matrix[current_node][neighbor] == float('inf'):
                    continue  # Saltar nodos no conectados

                # Si no tiene visa y el vecino requiere visa, saltar este vecino
                if not has_visa and self.visa_matrix[current_node][neighbor] == 1:
                    continue

                distance = current_distance + weight_matrix[current_node][neighbor]
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(priority_queue, (distance, neighbor))

        path = []
        current = self.node_index[end]
        while previous_nodes[current] is not None:
            path.insert(0, self.node_list[current])
            current = previous_nodes[current]
        if path:
            path.insert(0, start)

        return path, distances[self.node_index[end]]

    def bfs_fewest_stops(self, start, end, has_visa):
        from collections import deque

        size = len(self.node_list)
        visited = [False] * size
        previous_nodes = [None] * size
        queue = deque([(start, [])])  # Cola para BFS, cada elemento es (nodo_actual, camino_hasta_el_nodo_actual)

        while queue:
            current_node, path = queue.popleft()

            if current_node == end:
                return path + [current_node]  # Devolver el camino completo cuando se alcanza el nodo de destino

            if visited[self.node_index[current_node]]:
                continue

            visited[self.node_index[current_node]] = True

            for neighbor in self.node_list:
                if self.adj_matrix[self.node_index[current_node]][self.node_index[neighbor]] < float('inf'):
                    if not has_visa and self.visa_matrix[self.node_index[current_node]][self.node_index[neighbor]] == 1:
                        continue  # Saltar vecinos que requieren visa si el usuario no tiene visa
                    queue.append((neighbor, path + [current_node]))  # Agregar vecino a la cola con el camino actualizado

        return []  # Si no se encontró un camino válido

    def find_route(self):
        origin = self.origin_entry.get().strip()  # Obtener el aeropuerto de origen del campo de entrada
        destination = self.destination_entry.get().strip()  # Obtener el aeropuerto de destino del campo de entrada
        has_visa = self.visa_var.get()  # Obtener si el usuario tiene visa o no
        route_option = self.route_option.get()  # Obtener la opción de ruta seleccionada (más barata o menos escalas)

        if not origin or not destination:
            messagebox.showerror("Error", "Debe ingresar tanto el origen como el destino.")
            return

        try:
            if route_option == "Cheapest":
                # Encontrar la ruta más barata utilizando el algoritmo de Dijkstra
                path, cost = self.dijkstra_shortest_path(origin, destination, has_visa, self.adj_matrix)
                if cost == float('inf'):
                    messagebox.showerror("Error", "No hay ruta disponible entre los destinos seleccionados.")
                else:
                    messagebox.showinfo("Ruta encontrada", f"La ruta más barata de {origin} a {destination} es: {' -> '.join(path)} con un costo de ${cost:.2f}")
            elif route_option == "Fewest Stops":
                # Encontrar la ruta con menos escalas utilizando BFS
                path = self.bfs_fewest_stops(origin, destination, has_visa)
                if not path:
                    messagebox.showerror("Error", "No hay ruta disponible entre los destinos seleccionados.")
                else:
                    messagebox.showinfo("Ruta encontrada", f"La ruta con menos escalas de {origin} a {destination} es: {' -> '.join(path)} con {len(path) - 1} escalas")
        except KeyError:
            messagebox.showerror("Error", "Uno de los nodos seleccionados no existe en la red de nodos.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al encontrar la ruta: {e}")

    def show_graph(self):
        try:
            window = tk.Toplevel(self.root)  # Ventana secundaria para mostrar el grafo
            window.title("Graph Visualization")  # Título de la ventana secundaria
            canvas = Canvas(window, width=800, height=600, bg="white")  # Canvas para dibujar el grafo
            canvas.pack()

            positions = self.calculate_positions(len(self.node_list), 350, 300, 250)  # Calcular posiciones de los nodos en el círculo

            # Dibujar los nodos (aeropuertos) y etiquetarlos
            for i, node in enumerate(self.node_list):
                x, y = positions[i]
                canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill="skyblue")  # Dibujar nodo como círculo
                canvas.create_text(x, y, text=node, fill="black")  # Etiquetar nodo con nombre del aeropuerto

            # Dibujar las aristas (conexiones entre nodos) y etiquetarlas con precios
            for i in range(len(self.node_list)):
                for j in range(i+1, len(self.node_list)):
                    if self.adj_matrix[i][j] < float('inf'):
                        x1, y1 = positions[i]
                        x2, y2 = positions[j]
                        canvas.create_line(x1, y1, x2, y2, fill="black")  # Dibujar línea entre nodos
                        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                        canvas.create_text(mid_x, mid_y, text=f"{self.adj_matrix[i][j]:.2f}", fill="black")  # Etiquetar línea con costo

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al mostrar el grafo: {e}")

    def calculate_positions(self, num_nodes, center_x, center_y, radius):
        angle_step = 2 * math.pi / num_nodes  # Paso de ángulo entre cada nodo en el círculo
        positions = []
        for i in range(num_nodes):
            angle = i * angle_step
            x = center_x + radius * math.cos(angle)  # Calcular coordenada x del nodo en el círculo
            y = center_y + radius * math.sin(angle)  # Calcular coordenada y del nodo en el círculo
            positions.append((x, y))  # Agregar posición calculada a la lista
        return positions  # Devolver lista de posiciones calculadas

# Crear la ventana principal
if __name__ == "__main__":
    root = tk.Tk()  # Crear la ventana principal
    app = MetroTravelApp(root)  # Iniciar la aplicación dentro de la ventana principal
    root.mainloop()  # Iniciar el bucle principal de la interfaz gráfica
