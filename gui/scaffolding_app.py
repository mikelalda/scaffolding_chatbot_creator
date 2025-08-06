# --- START OF FILE scaffolding_app.py ---

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from backend.chatbot_logic import ChatbotLogic
from backend.persistence import load_bot, save_bot
from gui.chat_panel import ChatPanel
import unicodedata
import re

class ScaffoldingApp(tb.Window):
    def __init__(self):
        super().__init__(themename="cosmo")  # Cambia el tema por defecto
        
        self.bot_data = {
            "tema": "",
            "publico": "",
            "faq": [],
            "resolucion": [],
            "feedback_positivo": []
        }
        
        self.is_editing = False 
        self.editing_faq_index = None
        self.editing_step_index = None

        self.create_widgets()

    # --- MODIFICADO: init_chat_panel ---
    def init_chat_panel(self, loaded_config=False):
        if self.chat_panel: self.chat_panel.destroy()
        
        welcome_message = ""
        initial_bot_message = ""
        
        tema = self.bot_data.get("tema")
        if tema:
            welcome_message = f"Configuración sobre '{tema}' cargada."
            if loaded_config:
                # --- LÓGICA PARA EL EJEMPLO DINÁMICO ---
                example_question_text = "ej: '¿qué es...?'" # Fallback por si no hay FAQs
                faqs = self.bot_data.get("faq", [])
                if faqs:
                    # Si hay al menos una FAQ, usa la primera como ejemplo
                    first_question = faqs[0].get("pregunta", "¿...?")
                    example_question_text = f"ej: '{first_question}'"
                # --- FIN DE LA LÓGICA ---

                initial_bot_message = (
                    f"¡Hola! Estoy listo para ayudarte con '{tema}'.\n\n"
                    "¿Qué te gustaría hacer?\n"
                    "  - Escribe 'practicar' para empezar un ejercicio.\n"
                    f"  - O simplemente hazme una pregunta ({example_question_text})."
                )
        else:
            initial_bot_message = "Por favor, carga una configuración o créala en la pestaña 'Edición' y haz clic en 'Guardar' para activar el bot."

        logic = ChatbotLogic(self.bot_data)
        self.chat_panel = ChatPanel(self.tab_chat, logic, welcome_message)
        self.chat_panel.pack(fill="both", expand=True)

        if initial_bot_message:
            self.after(100, lambda: self.chat_panel.append(initial_bot_message, "bot"))
            
    # --- El resto del código no necesita cambios, se pega para completitud ---
    
    def normalize_text_for_pattern(self, text: str) -> str:
        text_lower = text.lower().strip()
        if text_lower.startswith('¿'):
            text_lower = text_lower[1:]
        if text_lower.endswith('?'):
            text_lower = text_lower[:-1]
        replacements = {'a': '[aá]', 'e': '[eé]', 'i': '[ií]', 'o': '[oó]', 'u': '[uú]'}
        for original, replacement in replacements.items():
            text_lower = text_lower.replace(original, replacement)
        cleaned_text = re.sub(r'[^a-z0-9\s\[\]]', '', text_lower).strip()
        return f".*{cleaned_text}.*"
        
    def move_step_up(self):
        selected_indices = self.steps_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Sin selección", "Por favor, selecciona un paso para mover.")
            return
        idx = selected_indices[0]
        if idx == 0: return
        step = self.bot_data["resolucion"].pop(idx)
        self.bot_data["resolucion"].insert(idx - 1, step)
        text = self.steps_listbox.get(idx)
        self.steps_listbox.delete(idx)
        self.steps_listbox.insert(idx - 1, text)
        self.renumber_steps_listbox()
        self.steps_listbox.selection_set(idx - 1)

    def move_step_down(self):
        selected_indices = self.steps_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Sin selección", "Por favor, selecciona un paso para mover.")
            return
        idx = selected_indices[0]
        if idx == self.steps_listbox.size() - 1: return
        step = self.bot_data["resolucion"].pop(idx)
        self.bot_data["resolucion"].insert(idx + 1, step)
        text = self.steps_listbox.get(idx)
        self.steps_listbox.delete(idx)
        self.steps_listbox.insert(idx + 1, text)
        self.renumber_steps_listbox()
        self.steps_listbox.selection_set(idx + 1)

    def create_widgets(self):
        # --- MODERNIZA: Aplica colores y fuentes ---
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        tab_control = ttk.Notebook(main_frame)
        self.tab_edit = ttk.Frame(tab_control)
        self.tab_chat = ttk.Frame(tab_control)
        tab_control.add(self.tab_edit, text="Edición del Chatbot")
        tab_control.add(self.tab_chat, text="Chat con Bot")
        tab_control.pack(expand=1, fill="both")

        file_frame = ttk.Frame(self.tab_edit)
        file_frame.pack(fill='x', pady=5)
        ttk.Button(file_frame, text="Guardar Configuración", command=self.save).pack(side='left', padx=5)
        ttk.Button(file_frame, text="Cargar Configuración", command=self.load).pack(side='left', padx=5)

        general_frame = ttk.LabelFrame(self.tab_edit, text="Información General")
        general_frame.pack(fill='x', expand=True, padx=5, pady=5)
        ttk.Label(general_frame, text="Tema:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.tema_entry = ttk.Entry(general_frame, width=80)
        self.tema_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(general_frame, text="Público objetivo:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.publico_entry = ttk.Entry(general_frame, width=80)
        self.publico_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        general_frame.columnconfigure(1, weight=1)

        faq_frame = ttk.LabelFrame(self.tab_edit, text="Preguntas Frecuentes (FAQs)")
        faq_frame.pack(fill='x', expand=True, padx=5, pady=5)
        ttk.Label(faq_frame, text="Pregunta del usuario:").grid(row=0, column=0, sticky='w', padx=5)
        self.faq_pregunta_entry = ttk.Entry(faq_frame, width=50)
        self.faq_pregunta_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(faq_frame, text="Respuesta del bot:").grid(row=1, column=0, sticky='w', padx=5)
        self.faq_respuesta_entry = ttk.Entry(faq_frame, width=50)
        self.faq_respuesta_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        self.faq_buttons_frame = ttk.Frame(faq_frame)
        self.faq_buttons_frame.grid(row=0, column=2, rowspan=2, padx=10, sticky='ns')
        self.faq_add_button = ttk.Button(self.faq_buttons_frame, text="Añadir FAQ", command=self.add_faq)
        self.faq_add_button.pack()
        self.faq_listbox = tk.Listbox(faq_frame, height=5)
        self.faq_listbox.grid(row=2, column=0, columnspan=3, sticky='ew', padx=5, pady=5)
        self.faq_listbox.bind("<Double-1>", self.edit_faq)
        faq_manage_frame = ttk.Frame(faq_frame)
        faq_manage_frame.grid(row=3, column=0, columnspan=3, pady=5)
        self.faq_modify_button = ttk.Button(faq_manage_frame, text="Modificar Seleccionada", command=self.edit_faq)
        self.faq_modify_button.pack(side='left', padx=5)
        self.faq_delete_button = ttk.Button(faq_manage_frame, text="Eliminar Seleccionada", command=self.delete_faq)
        self.faq_delete_button.pack(side='left', padx=5)
        faq_frame.columnconfigure(1, weight=1)

        steps_frame = ttk.LabelFrame(self.tab_edit, text="Pasos de Resolución de Problemas")
        steps_frame.pack(fill='both', expand=True, padx=5, pady=5)
        ttk.Label(steps_frame, text="Instrucción/Pregunta del bot:").grid(row=0, column=0, sticky='w', padx=5)
        self.step_instruccion_entry = ttk.Entry(steps_frame)
        self.step_instruccion_entry.grid(row=0, column=1, padx=5, pady=2, sticky='ew')
        ttk.Label(steps_frame, text="Respuesta esperada (Patrón Regex):").grid(row=1, column=0, sticky='w', padx=5)
        self.step_pattern_entry = ttk.Entry(steps_frame)
        self.step_pattern_entry.grid(row=1, column=1, padx=5, pady=2, sticky='ew')
        ttk.Label(steps_frame, text="Feedback de éxito del bot:").grid(row=2, column=0, sticky='w', padx=5)
        self.step_respuesta_entry = ttk.Entry(steps_frame)
        self.step_respuesta_entry.grid(row=2, column=1, padx=5, pady=2, sticky='ew')
        ttk.Label(steps_frame, text="Pista en caso de error:").grid(row=3, column=0, sticky='w', padx=5)
        self.step_pista_entry = ttk.Entry(steps_frame)
        self.step_pista_entry.grid(row=3, column=1, padx=5, pady=2, sticky='ew')
        self.step_buttons_frame = ttk.Frame(steps_frame)
        self.step_buttons_frame.grid(row=1, column=2, rowspan=2, padx=10, sticky='ns')
        self.step_add_button = ttk.Button(self.step_buttons_frame, text="Añadir Paso", command=self.add_step)
        self.step_add_button.pack()
        self.steps_listbox = tk.Listbox(steps_frame, height=8)
        self.steps_listbox.grid(row=4, column=0, columnspan=3, sticky='nsew', padx=5, pady=5)
        self.steps_listbox.bind("<Double-1>", self.edit_step)
        steps_manage_frame = ttk.Frame(steps_frame)
        steps_manage_frame.grid(row=5, column=0, columnspan=3, pady=5)
        self.step_move_up_button = ttk.Button(steps_manage_frame, text="Subir", command=self.move_step_up)
        self.step_move_up_button.pack(side='left', padx=5)
        self.step_move_down_button = ttk.Button(steps_manage_frame, text="Bajar", command=self.move_step_down)
        self.step_move_down_button.pack(side='left', padx=5)
        self.step_modify_button = ttk.Button(steps_manage_frame, text="Modificar Seleccionado", command=self.edit_step)
        self.step_modify_button.pack(side='left', padx=20)
        self.step_delete_button = ttk.Button(steps_manage_frame, text="Eliminar Seleccionado", command=self.delete_step)
        self.step_delete_button.pack(side='left', padx=5)
        steps_frame.columnconfigure(1, weight=1)
        steps_frame.rowconfigure(4, weight=1)
        self.chat_panel = None
        self.init_chat_panel()

        # --- Botón de configuración de tema ---
        ttk.Button(file_frame, text="Configuración de Tema", command=self.open_theme_selector).pack(side='right', padx=5)

    def load(self, *args):
        if self.is_editing:
            messagebox.showwarning("Edición en curso", "No puedes cargar un nuevo archivo mientras modificas un elemento. Guarda o cancela los cambios primero.")
            return
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            self.bot_data = load_bot(path)
            self.populate_ui_from_data()
            self.init_chat_panel(loaded_config=True) 
            messagebox.showinfo("Cargado", f"Chatbot sobre '{self.bot_data.get('tema')}' cargado. Ve a la pestaña 'Chat con Bot' para empezar.")

    def save(self, *args):
        if self.is_editing:
            messagebox.showwarning("Edición en curso", "No puedes guardar el archivo mientras modificas un elemento. Guarda o cancela los cambios primero.")
            return
        self.bot_data["tema"] = self.tema_entry.get()
        self.bot_data["publico"] = self.publico_entry.get()
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            save_bot(self.bot_data, path)
            messagebox.showinfo("Guardado", "Chatbot guardado exitosamente.")
            self.init_chat_panel(loaded_config=False)
            self.chat_panel.append("Configuración guardada y actualizada. ¿En qué te puedo ayudar?", "bot")

    def set_editing_mode(self, is_editing):
        self.is_editing = is_editing
        state = 'disabled' if is_editing else 'normal'
        self.step_modify_button.config(state=state if self.editing_faq_index is not None else 'normal')
        self.step_delete_button.config(state=state if self.editing_faq_index is not None else 'normal')
        self.step_add_button.config(state=state)
        self.step_move_up_button.config(state=state)
        self.step_move_down_button.config(state=state)
        self.faq_modify_button.config(state=state if self.editing_step_index is not None else 'normal')
        self.faq_delete_button.config(state=state if self.editing_step_index is not None else 'normal')
        self.faq_add_button.config(state=state)

    def edit_faq(self, event=None):
        if self.is_editing:
            messagebox.showwarning("Edición en curso", "Ya estás modificando otro elemento. Por favor, guarda o cancela los cambios actuales primero.")
            return
        selected_indices = self.faq_listbox.curselection()
        if not selected_indices: return
        self.editing_faq_index = selected_indices[0]
        self.set_editing_mode(True)
        faq_item = self.bot_data["faq"][self.editing_faq_index]
        self.faq_pregunta_entry.delete(0, tk.END)
        self.faq_pregunta_entry.insert(0, faq_item["pregunta"])
        self.faq_respuesta_entry.delete(0, tk.END)
        self.faq_respuesta_entry.insert(0, faq_item["respuesta"])
        self.faq_add_button.pack_forget()
        self.faq_save_edit_button = ttk.Button(self.faq_buttons_frame, text="Guardar Cambios", command=self.save_edited_faq)
        self.faq_save_edit_button.pack(side='top', pady=2)
        self.faq_cancel_edit_button = ttk.Button(self.faq_buttons_frame, text="Cancelar", command=self.cancel_edit_faq)
        self.faq_cancel_edit_button.pack(side='top', pady=2)

    def cancel_edit_faq(self):
        self.editing_faq_index = None
        self.set_editing_mode(False)
        self.faq_pregunta_entry.delete(0, tk.END)
        self.faq_respuesta_entry.delete(0, tk.END)
        self.faq_save_edit_button.destroy()
        self.faq_cancel_edit_button.destroy()
        self.faq_add_button.pack()
    
    def save_edited_faq(self):
        if self.editing_faq_index is None: return
        pregunta = self.faq_pregunta_entry.get().strip()
        respuesta = self.faq_respuesta_entry.get().strip()
        if not pregunta or not respuesta:
            messagebox.showwarning("Campos vacíos", "La pregunta y la respuesta no pueden estar vacías.")
            return
        faq_item = {"pattern": self.normalize_text_for_pattern(pregunta), "pregunta": pregunta, "respuesta": respuesta}
        self.bot_data["faq"][self.editing_faq_index] = faq_item
        self.faq_listbox.delete(self.editing_faq_index)
        self.faq_listbox.insert(self.editing_faq_index, f"P: {pregunta} -> R: {respuesta}")
        self.cancel_edit_faq()

    def edit_step(self, event=None):
        if self.is_editing:
            messagebox.showwarning("Edición en curso", "Ya estás modificando otro elemento. Por favor, guarda o cancela los cambios actuales primero.")
            return
        selected_indices = self.steps_listbox.curselection()
        if not selected_indices: return
        self.editing_step_index = selected_indices[0]
        self.set_editing_mode(True)
        step_item = self.bot_data["resolucion"][self.editing_step_index]
        self.clear_step_entries()
        self.step_instruccion_entry.insert(0, step_item.get("instruccion", ""))
        self.step_pattern_entry.insert(0, step_item.get("pattern", ""))
        self.step_respuesta_entry.insert(0, step_item.get("respuesta", ""))
        self.step_pista_entry.insert(0, step_item.get("pista", ""))
        self.step_add_button.pack_forget()
        self.step_save_edit_button = ttk.Button(self.step_buttons_frame, text="Guardar Cambios", command=self.save_edited_step)
        self.step_save_edit_button.pack(side='top', pady=2)
        self.step_cancel_edit_button = ttk.Button(self.step_buttons_frame, text="Cancelar", command=self.cancel_edit_step)
        self.step_cancel_edit_button.pack(side='top', pady=2)

    def cancel_edit_step(self):
        self.editing_step_index = None
        self.set_editing_mode(False)
        self.clear_step_entries()
        self.step_save_edit_button.destroy()
        self.step_cancel_edit_button.destroy()
        self.step_add_button.pack()

    def save_edited_step(self):
        if self.editing_step_index is None: return
        step_item = {
            "instruccion": self.step_instruccion_entry.get().strip(),
            "pattern": self.step_pattern_entry.get().strip(),
            "respuesta": self.step_respuesta_entry.get().strip(),
            "pista": self.step_pista_entry.get().strip()
        }
        if not step_item["instruccion"] or not step_item["pattern"]:
            messagebox.showwarning("Campos requeridos", "La 'Instrucción' y el 'Patrón' son obligatorios.")
            return
        self.bot_data["resolucion"][self.editing_step_index] = step_item
        self.steps_listbox.delete(self.editing_step_index)
        self.steps_listbox.insert(self.editing_step_index, f"Paso {self.editing_step_index + 1}: {step_item['instruccion']}")
        self.cancel_edit_step()

    def add_faq(self, *args):
        pregunta = self.faq_pregunta_entry.get().strip()
        respuesta = self.faq_respuesta_entry.get().strip()
        if not pregunta or not respuesta:
            messagebox.showwarning("Campos vacíos", "Por favor, completa la pregunta y la respuesta de la FAQ.")
            return
        faq_item = {"pattern": self.normalize_text_for_pattern(pregunta), "pregunta": pregunta, "respuesta": respuesta}
        self.bot_data["faq"].append(faq_item)
        self.faq_listbox.insert(tk.END, f"P: {pregunta} -> R: {respuesta}")
        self.faq_pregunta_entry.delete(0, tk.END)
        self.faq_respuesta_entry.delete(0, tk.END)

    def delete_faq(self, *args):
        selected_indices = self.faq_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Sin selección", "Por favor, selecciona una FAQ de la lista para eliminar.")
            return
        for i in sorted(selected_indices, reverse=True):
            self.faq_listbox.delete(i)
            del self.bot_data["faq"][i]
            
    def add_step(self, *args):
        step_item = {
            "instruccion": self.step_instruccion_entry.get().strip(),
            "pattern": self.step_pattern_entry.get().strip(),
            "respuesta": self.step_respuesta_entry.get().strip(),
            "pista": self.step_pista_entry.get().strip()
        }
        if not step_item["instruccion"] or not step_item["pattern"]:
            messagebox.showwarning("Campos requeridos", "La 'Instrucción' y el 'Patrón' son obligatorios.")
            return
        self.bot_data["resolucion"].append(step_item)
        self.steps_listbox.insert(tk.END, f"Paso {self.steps_listbox.size()}: {step_item['instruccion']}")
        self.clear_step_entries()

    def delete_step(self, *args):
        selected_indices = self.steps_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Sin selección", "Por favor, selecciona un paso de la lista para eliminar.")
            return
        for i in sorted(selected_indices, reverse=True):
            self.steps_listbox.delete(i)
            del self.bot_data["resolucion"][i]
        self.renumber_steps_listbox()
        
    def renumber_steps_listbox(self, *args):
        items = self.steps_listbox.get(0, tk.END)
        self.steps_listbox.delete(0, tk.END)
        for i, item_text in enumerate(items):
            try:
                desc = item_text.split(": ", 1)[1]
                self.steps_listbox.insert(tk.END, f"Paso {i + 1}: {desc}")
            except IndexError:
                self.steps_listbox.insert(tk.END, item_text)
            
    def clear_step_entries(self, *args):
        self.step_instruccion_entry.delete(0, tk.END)
        self.step_pattern_entry.delete(0, tk.END)
        self.step_respuesta_entry.delete(0, tk.END)
        self.step_pista_entry.delete(0, tk.END)

    def populate_ui_from_data(self, *args):
        if self.is_editing:
            if self.editing_faq_index is not None: self.cancel_edit_faq()
            if self.editing_step_index is not None: self.cancel_edit_step()
        self.tema_entry.delete(0, tk.END)
        self.publico_entry.delete(0, tk.END)
        self.faq_listbox.delete(0, tk.END)
        self.steps_listbox.delete(0, tk.END)
        self.tema_entry.insert(0, self.bot_data.get("tema", ""))
        self.publico_entry.insert(0, self.bot_data.get("publico", ""))
        for faq in self.bot_data.get("faq", []):
            self.faq_listbox.insert(tk.END, f"P: {faq['pregunta']} -> R: {faq['respuesta']}")
        for i, step in enumerate(self.bot_data.get("resolucion", [])):
            self.steps_listbox.insert(tk.END, f"Paso {i + 1}: {step['instruccion']}")

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

# --- END OF FILE ---