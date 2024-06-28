import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox, filedialog
import threading

class MetroTravelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Metro Travel Route Finder")
        self.create_widgets()
        
    def create_widgets(self):
        tk.Label(self.root, text="Aeropuerto de Origen:").grid(row=0, column=0)
        self.origin_entry = tk.Entry(self.root)
        self.origin_entry.grid(row=0, column=1)

        tk.Label(self.root, text="Aeropuerto de Destino:").grid(row=1, column=0)
        self.destination_entry = tk.Entry(self.root)
        self.destination_entry.grid(row=1, column=1)

        self.visa_var = tk.BooleanVar()
        tk.Checkbutton(self.root, text="¿Tiene visa?", variable=self.visa_var).grid(row=2, columnspan=2)

        self.route_option = tk.StringVar(value="Cheapest")
        tk.Radiobutton(self.root, text="Ruta más barata", variable=self.route_option, value="Cheapest").grid(row=3, column=0)
        tk.Radiobutton(self.root, text="Menos escalas", variable=self.route_option, value="Fewest Stops").grid(row=3, column=1)

        tk.Button(self.root, text="Cargar Datos", command=self.load_data).grid(row=4, columnspan=2)
        tk.Button(self.root, text="Encontrar Ruta", command=self.find_route).grid(row=5, columnspan=2)
        tk.Button(self.root, text="Mostrar Grafo", command=self.show_graph).grid(row=6, columnspan=2)

    def load_data(self):
        print("Cargar Datos")
        file_path = filedialog.askopenfilename()
        if file_path:
            try:
                # Ejecutar la carga de datos en un hilo separado
                threading.Thread(target=self.load_data_worker, args=(file_path,)).start()
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar los datos: {e}")
        else:
            messagebox.showerror("Error", "No se seleccionó ningún archivo.")
    
    def load_data_worker(self, file_path):
        try:
            self.data = pd.read_csv(file_path)
            self.create_graph()
            messagebox.showinfo("Datos Cargados", "Datos cargados exitosamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar los datos: {e}")

    def create_graph(self):
        self.G = nx.Graph()
        for index, row in self.data.iterrows():
            self.G.add_edge(row['Origen'], row['Destino'], weight=row['Precio'], visa=row['Requiere_Visa'])
        print("Gráfico creado")

    def find_route(self):
        print("Encontrar Ruta")
        origin = self.origin_entry.get().strip()
        destination = self.destination_entry.get().strip()
        has_visa = self.visa_var.get()
        route_option = self.route_option.get()
        
        if not origin or not destination:
            messagebox.showerror("Error", "Debe ingresar tanto el origen como el destino.")
            return
        
        try:
            if has_visa:
                if route_option == "Cheapest":
                    path = nx.shortest_path(self.G, source=origin, target=destination, weight='weight')
                    cost = nx.shortest_path_length(self.G, source=origin, target=destination, weight='weight')
                    messagebox.showinfo("Ruta encontrada", f"La ruta más barata de {origin} a {destination} es: {' -> '.join(path)} con un costo de ${cost:.2f}")
                elif route_option == "Fewest Stops":
                    path = nx.shortest_path(self.G, source=origin, target=destination)
                    messagebox.showinfo("Ruta encontrada", f"La ruta con menos escalas de {origin} a {destination} es: {' -> '.join(path)} con {len(path) - 1} escalas")
            else:
                # Filtrar nodos que no requieren visa
                visa_free_nodes = [node for node in self.G.nodes if node == origin or all(self.G[node][neighbor]['visa'] == 0 for neighbor in self.G[node])]
                G_filtered = self.G.subgraph(visa_free_nodes)
                
                if route_option == "Cheapest":
                    path = nx.shortest_path(G_filtered, source=origin, target=destination, weight='weight')
                    cost = nx.shortest_path_length(G_filtered, source=origin, target=destination, weight='weight')
                    messagebox.showinfo("Ruta encontrada", f"La ruta más barata de {origin} a {destination} es: {' -> '.join(path)} con un costo de ${cost:.2f}")
                elif route_option == "Fewest Stops":
                    path = nx.shortest_path(G_filtered, source=origin, target=destination)
                    messagebox.showinfo("Ruta encontrada", f"La ruta con menos escalas de {origin} a {destination} es: {' -> '.join(path)} con {len(path) - 1} escalas")
                    
        except nx.NetworkXNoPath:
            messagebox.showerror("Error", "No hay ruta disponible entre los destinos seleccionados.")
        except nx.NodeNotFound:
            messagebox.showerror("Error", "Uno de los nodos seleccionados no existe en la red de nodos filtrados por los requisitos de visa.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al encontrar la ruta: {e}")
    
    def show_graph(self):
        print("Mostrar Grafo")
        try:
            pos = nx.spring_layout(self.G)
            nx.draw(self.G, pos, with_labels=True, node_color='skyblue', node_size=2000, font_size=10, font_weight='bold')
            labels = nx.get_edge_attributes(self.G, 'weight')
            nx.draw_networkx_edge_labels(self.G, pos, edge_labels=labels)
            plt.show()
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al mostrar el grafo: {e}")

# Crear la ventana principal
if __name__ == "__main__":
    root = tk.Tk()
    app = MetroTravelApp(root)
    root.mainloop()
