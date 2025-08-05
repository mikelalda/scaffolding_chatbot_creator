# --- START OF FILE chat_panel.py ---

import tkinter as tk
from tkinter import scrolledtext

class ChatPanel(tk.Frame):
    # --- MODIFICADO: Añadido 'welcome_message' como argumento ---
    def __init__(self, parent, logic, welcome_message: str, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.logic = logic

        # --- Paleta de Colores y Fuentes Atractivas ---
        BG_COLOR = "#F0F0F0"
        TEXT_COLOR = "#1C1C1C"
        BOT_BUBBLE_COLOR = "#EAEAEA"
        USER_BUBBLE_COLOR = "#D1E8FF"
        INPUT_BG_COLOR = "#FFFFFF"
        BUTTON_COLOR = "#0078D4"
        BUTTON_TEXT_COLOR = "#FFFFFF"
        FONT_NORMAL = ("Calibri", 12)
        FONT_BOLD = ("Calibri", 12, "bold")
        
        self.configure(bg=BG_COLOR)

        self.chat_log = scrolledtext.ScrolledText(
            self, 
            state='disabled', 
            wrap=tk.WORD,
            bg=BG_COLOR, 
            fg=TEXT_COLOR,
            font=FONT_NORMAL,
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=10
        )
        self.chat_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.chat_log.tag_configure("bot", background=BOT_BUBBLE_COLOR, foreground=TEXT_COLOR, relief=tk.RAISED, borderwidth=1, font=FONT_NORMAL, spacing3=10, lmargin1=10, lmargin2=10, justify='left')
        self.chat_log.tag_configure("user", background=USER_BUBBLE_COLOR, foreground=TEXT_COLOR, relief=tk.RAISED, borderwidth=1, font=FONT_NORMAL, spacing3=10, lmargin1=60, lmargin2=60, rmargin=10, justify='right')
        self.chat_log.tag_configure("info", foreground="grey", font=("Calibri", 10, "italic"), spacing3=10, justify='center')

        input_frame = tk.Frame(self, bg=BG_COLOR)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.entry = tk.Entry(
            input_frame, 
            width=60, 
            bg=INPUT_BG_COLOR, 
            fg="grey",
            font=FONT_NORMAL, 
            relief=tk.FLAT,
            bd=2,
            insertbackground=TEXT_COLOR
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=5)
        
        self.placeholder = "Escribe tu mensaje aquí..."
        self.entry.insert(0, self.placeholder)
        self.entry.bind("<FocusIn>", self.on_entry_focus_in)
        self.entry.bind("<FocusOut>", self.on_entry_focus_out)
        self.entry.bind("<Return>", self.on_send)

        tk.Button(
            input_frame, 
            text="Enviar", 
            command=self.on_send,
            bg=BUTTON_COLOR,
            fg=BUTTON_TEXT_COLOR,
            font=FONT_BOLD,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            activebackground="#005A9E",
            activeforeground=BUTTON_TEXT_COLOR
        ).pack(side=tk.RIGHT)

        # --- MODIFICADO: Usar el mensaje de bienvenida pasado como argumento ---
        if welcome_message:
            self.append(welcome_message, "info")


    def on_send(self, event=None):
        user_input = self.entry.get().strip()
        if not user_input or user_input == self.placeholder:
            return
            
        self.append(user_input, "user")
        self.entry.delete(0, tk.END)
        
        self.after(500, self.get_bot_response, user_input)

    def get_bot_response(self, user_input):
        bot_response = self.logic.get_response(user_input)
        self.append(bot_response, "bot")

    def append(self, text: str, tag: str):
        self.chat_log.configure(state='normal')
        self.chat_log.insert(tk.END, text + "\n\n", tag)
        self.chat_log.configure(state='disabled')
        self.chat_log.see(tk.END)
        
    def on_entry_focus_in(self, event):
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg='black')

    def on_entry_focus_out(self, event):
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg='grey')