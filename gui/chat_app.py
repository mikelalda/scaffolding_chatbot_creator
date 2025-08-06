import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import os # Para operaciones de ruta y listar directorio

# Asumiendo que backend.chatbot_logic y backend.persistence existen y están correctamente implementados
from backend.chatbot_logic import ChatbotLogic
from backend.persistence import load_bot 
from gui.chat_panel import ChatPanel

class ScaffoldingApp(tb.Window):
    def __init__(self):
        super().__init__(themename="cosmo")
        self.title("Chatbot Integrado") 

        # Lista para almacenar todas las configuraciones de bot cargadas
        self.all_bot_configs = []
        # El índice de la configuración actualmente activa en all_bot_configs
        self.active_config_index = -1 
        
        # Inicializa bot_data con estructuras vacías por defecto, se actualizará al cargar configs
        self.bot_data = {
            "tema": "Información General", 
            "publico": "Usuarios",        
            "faq": [],
            "resolucion": [],
            "feedback_positivo": [] 
        }
        
        self.chat_panel = None 
        self.theme_selector_combobox = None # Referencia para el Combobox del selector de tema

        # Carga todas las configuraciones de la carpeta 'configs'
        self.load_all_configs_from_folder("configs")
        
        # Crea los widgets, incluyendo el selector de tema y el panel de chat
        self.create_widgets()
        
        self.minsize(600, 450)
        self.geometry("800x600")

        # Selecciona el primer tema por defecto si hay alguno
        if self.all_bot_configs:
            self.theme_selector_combobox.set(self.all_bot_configs[0]["name"])
            self.switch_conversation_theme(0) # Carga el primer tema al inicio
        else:
            # Si no hay configuraciones cargadas, inicializa el chat panel con los datos por defecto
            self.init_chat_panel()

    def load_all_configs_from_folder(self, folder_name):
        """
        Carga y almacena todas los archivos de configuración JSON de la carpeta especificada.
        La carpeta se espera en el mismo directorio donde se ejecuta el script.
        """
        # La ruta de la carpeta 'configs' se obtiene relativa al directorio de ejecución actual
        full_folder_path = os.path.join(os.getcwd(), folder_name)

        # Crea la carpeta 'configs' si no existe
        if not os.path.exists(full_folder_path):
            os.makedirs(full_folder_path)
            messagebox.showinfo("Configuración", 
                                f"La carpeta '{full_folder_path}' no existía y ha sido creada en:\n{full_folder_path}\n"
                                "Por favor, coloca tus archivos .json de configuración aquí.")
            return

        json_files = [f for f in os.listdir(full_folder_path) if f.endswith('.json')]

        if not json_files:
            messagebox.showwarning("Sin Configuraciones", 
                                   f"No se encontraron archivos .json en la carpeta '{full_folder_path}'. "
                                   "El bot iniciará con una configuración vacía o por defecto.")
            return

        # Vaciar la lista de configuraciones previas si se vuelve a cargar
        self.all_bot_configs = []

        # Itera sobre cada archivo JSON y carga su contenido
        for filename in json_files:
            filepath = os.path.join(full_folder_path, filename)
            try:
                config = load_bot(filepath)
                if isinstance(config, dict): 
                    # Almacena la configuración completa junto con su nombre (tema)
                    config_name = config.get("tema", os.path.splitext(filename)[0]) # Usa el tema o el nombre del archivo
                    self.all_bot_configs.append({"name": config_name, "data": config})
            except Exception as e:
                print(f"Error cargando {filename}: {e}")
                
        if json_files:
            messagebox.showinfo("Configuraciones Cargadas", 
                                f"Se cargaron {len(self.all_bot_configs)} configuraciones válidas de la carpeta '{folder_name}'.")

    def switch_conversation_theme(self, event=None):
        """
        Cambia el tema de conversación del chatbot según la selección del Combobox.
        """
        if self.theme_selector_combobox:
            selected_name = self.theme_selector_combobox.get()
            for i, config_entry in enumerate(self.all_bot_configs):
                if config_entry["name"] == selected_name:
                    self.active_config_index = i
                    self.bot_data = config_entry["data"] # Actualiza self.bot_data con la configuración seleccionada
                    self.init_chat_panel() # Reinicia el panel de chat con la nueva configuración
                    return
            # Si no se encuentra el tema seleccionado (podría pasar si se elimina un archivo o error)
            messagebox.showwarning("Tema no encontrado", f"El tema '{selected_name}' no pudo ser cargado.")
            # Si no se encuentra, vuelve a cargar la configuración por defecto
            self.bot_data = {
                "tema": "Información General",
                "publico": "Usuarios",
                "faq": [],
                "resolucion": [],
                "feedback_positivo": []
            }
            self.init_chat_panel()


    def init_chat_panel(self):
        """
        Inicializa y muestra el ChatPanel, cargando contenido basado en bot_data.
        """
        if self.chat_panel:
            self.chat_panel.destroy()

        welcome_message = ""
        initial_bot_message = ""

        tema = self.bot_data.get("tema")
        # Verifica si hay contenido real en la configuración cargada (FAQs o pasos de resolución)
        if self.bot_data.get("faq") or self.bot_data.get("resolucion"):
            welcome_message = f"Configuración sobre '{tema}' cargada."
            example_question_text = "ej: '¿qué es...?'" 
            faqs = self.bot_data.get("faq", [])
            if faqs:
                first_question = faqs[0].get("pregunta", "¿...?")
                example_question_text = f"ej: '{first_question}'"

            initial_bot_message = (
                f"¡Hola! Estoy listo para ayudarte con '{tema}'.\n\n"
                "¿Qué te gustaría hacer?\n"
                "  - Escribe 'practicar' para empezar un ejercicio.\n"
                f"  - O simplemente hazme una pregunta ({example_question_text})."
            )
        else:
            initial_bot_message = (
                "No se encontraron configuraciones válidas o están vacías para este tema.\n"
                "El bot está operando con una configuración por defecto/vacía. "
                "Por favor, selecciona otro tema o verifica tus archivos JSON en la subcarpeta 'configs'."
            )

        logic = ChatbotLogic(self.bot_data)
        
        # El panel de chat se empaqueta en la ventana principal (self)
        self.chat_panel = ChatPanel(self, logic, welcome_message)
        self.chat_panel.pack(fill="both", expand=True)

        if initial_bot_message:
            self.after(100, lambda: self.chat_panel.append(initial_bot_message, "bot"))

    def create_widgets(self):
        """
        Configura el selector de tema y el panel de chat.
        """
        # Frame para el selector de tema en la parte superior
        theme_selector_frame = ttk.Frame(self)
        theme_selector_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(theme_selector_frame, text="Seleccionar tema de conversación:").pack(side="left", padx=(0, 10))
        
        theme_names = [config["name"] for config in self.all_bot_configs]
        
        self.theme_selector_combobox = ttk.Combobox(
            theme_selector_frame, 
            values=theme_names, 
            state="readonly", # No permite escribir, solo seleccionar
            width=40
        )
        self.theme_selector_combobox.pack(side="left", fill="x", expand=True)
        # Vincula el evento de selección al método para cambiar el tema
        self.theme_selector_combobox.bind("<<ComboboxSelected>>", self.switch_conversation_theme)

        
        # --- Botón de configuración de tema ---
        ttk.Button(theme_selector_frame, text="Configuración de Tema", command=self.open_theme_selector).pack(side='right', padx=5)

        # El panel de chat se inicializará y empaquetará después, en init_chat_panel
        # Esto asegura que se cargue con el tema inicial o el seleccionado
        # No llamamos init_chat_panel aquí directamente, lo haremos en __init__ después de cargar los temas
    
    def open_theme_selector(self):
        temas = ["sandstone", "cosmo", "minty", "yeti", "pulse", "flatly",
            "morph", "journal", "darkly", "superhero", "solar", "cyborg", "simplex", "united"
        ]
        selector = tk.Toplevel(self)
        selector.title("Selecciona un tema visual")
        selector.geometry("350x150")
        selector.resizable(False, False)

        # Frame horizontal para label y combobox
        frame = ttk.Frame(selector)
        frame.pack(fill="x", padx=10, pady=20)

        ttk.Label(frame, text="Selecciona un tema:").pack(side="left", padx=(0,10))
        tema_var = tk.StringVar(value=self.style.theme.name)
        tema_combo = ttk.Combobox(frame, textvariable=tema_var, values=temas, state="readonly", width=15)
        tema_combo.pack(side="left")

        # Botón debajo, alineado a la derecha
        btn_frame = ttk.Frame(selector)
        btn_frame.pack(fill="x", padx=10)
        ttk.Button(btn_frame, text="Aplicar", command=lambda: [self.style.theme_use(tema_var.get()), selector.destroy()]).pack(side="right", pady=5)
        
# Para ejecutar la aplicación
if __name__ == "__main__":
    app = ScaffoldingApp()
    app.mainloop()