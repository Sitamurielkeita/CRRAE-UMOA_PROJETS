import os
import psycopg2
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import database_logic as db



# ==============================================================================
# CLASSE PRINCIPALE DE L'APPLICATION (UI)
# ==============================================================================

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Configuration de la fenêtre principale ---
        self.title("Gestionnaire de Comptes Moderne")
        self.geometry("1000x500")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # --- Configuration de la grille principale (1x2) ---
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Création des widgets ---
        self._create_sidebar_frame()
        self._create_treeview_frame()

        # --- Initialisation et chargement des données ---
        db.init_db()
        self.load_accounts()

    def _create_sidebar_frame(self):
        sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=10)
        sidebar_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        sidebar_frame.grid_rowconfigure(4, weight=1)

        title_label = ctk.CTkLabel(sidebar_frame, text="Gérer un Compte", font=ctk.CTkFont(size=20, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10))

        self.entry_name = ctk.CTkEntry(sidebar_frame, placeholder_text="Nom")
        self.entry_name.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

        self.entry_email = ctk.CTkEntry(sidebar_frame, placeholder_text="Email")
        self.entry_email.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

        self.entry_balance = ctk.CTkEntry(sidebar_frame, placeholder_text="Solde")
        self.entry_balance.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

        btn_add = ctk.CTkButton(sidebar_frame, text="Ajouter", command=self.add_account)
        btn_add.grid(row=4, column=0, padx=(20, 10), pady=10, sticky="ew")

        btn_update = ctk.CTkButton(sidebar_frame, text="Mettre à jour", command=self.update_account)
        btn_update.grid(row=4, column=1, padx=(10, 20), pady=10, sticky="ew")

        btn_delete = ctk.CTkButton(sidebar_frame, text="Supprimer", fg_color="#D32F2F", hover_color="#B71C1C",
                                   command=self.delete_account)
        btn_delete.grid(row=5, column=0, padx=(20, 10), pady=10, sticky="ew")

        btn_clear = ctk.CTkButton(sidebar_frame, text="Nettoyer", fg_color="gray50", hover_color="gray30",
                                  command=self.clear_form)
        btn_clear.grid(row=5, column=1, padx=(10, 20), pady=10, sticky="ew")

    def _create_treeview_frame(self):
        """Crée le panneau de droite pour le tableau."""
        treeview_frame = ctk.CTkFrame(self, corner_radius=10)
        treeview_frame.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        treeview_frame.grid_columnconfigure(0, weight=1)
        treeview_frame.grid_rowconfigure(0, weight=1)

        # Style pour le Treeview
        style = ttk.Style()
        style.theme_use("clam")

        bg_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        text_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        header_bg = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"])
        selected_color = self._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["hover_color"])

        style.configure("Treeview", background=bg_color, foreground=text_color, fieldbackground=bg_color, borderwidth=0,
                        rowheight=25)
        style.configure("Treeview.Heading", background=header_bg, foreground=text_color, relief="flat")
        style.map('Treeview', background=[('selected', selected_color)], foreground=[('selected', text_color)])

        columns = ("ID", "Nom", "Email", "Solde")
        self.tree = ttk.Treeview(treeview_frame, columns=columns, show="headings", style="Treeview")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")

        self.tree.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.tree.bind("<ButtonRelease-1>", self.handle_tree_click)

        btn_reload = ctk.CTkButton(treeview_frame, text="Rafraîchir", command=self.load_accounts)
        btn_reload.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="e")

    def handle_tree_click(self, event):
        """Gère le clic de la souris sur le Treeview."""
        # Identifie la ligne sur laquelle l'utilisateur a cliqué
        item_id = self.tree.identify_row(event.y)

        if item_id:
            # Si une ligne est identifiée, on la sélectionne manuellement
            self.tree.selection_set(item_id)
            # Puis on appelle notre fonction logique originale
            self.on_tree_select(event)

    # =========================================================

    # --- Méthodes de l'interface (logique) ---

    def load_accounts(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            accounts = db.load_accounts_db()
            for row in accounts:
                self.tree.insert("", "end", values=row)
        except Exception as e:
            messagebox.showerror("Erreur de Connexion", f"Impossible de charger les comptes.\n{e}")


    def add_account(self):
        name = self.entry_name.get()
        email = self.entry_email.get()
        balance = self.entry_balance.get()

        if not name or not email:
            messagebox.showwarning("Champs requis", "Le nom et l'email sont obligatoires.")
            return

        try:
            db.add_account_db(name, email, balance)
            self.load_accounts()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Erreur d'insertion", f"Impossible d'ajouter le compte.\n{e}")


    def update_account(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un compte à mettre à jour.")
            return

        item = self.tree.item(selected[0])
        account_id = item["values"][0]

        name = self.entry_name.get()
        email = self.entry_email.get()
        balance = self.entry_balance.get()

        if not name or not email:
            messagebox.showwarning("Champs requis", "Le nom et l'email sont obligatoires.")
            return

        try:
            db.update_account_db(account_id, name, email, balance)
            self.load_accounts()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Erreur de mise à jour", f"Impossible de mettre à jour le compte.\n{e}")


    def delete_account(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un compte à supprimer.")
            return

        if not messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer ce compte ?"):
            return

        item = self.tree.item(selected[0])
        account_id = item["values"][0]

        try:
            db.delete_account_db(account_id)
            self.load_accounts()
            self.clear_form()
        except Exception as e:
            messagebox.showerror("Erreur de suppression", f"Impossible de supprimer le compte.\n{e}")

    def clear_form(self):
        self.entry_name.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_balance.delete(0, tk.END)
        # Petite amélioration pour désélectionner visuellement
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        values = item["values"]

        # On efface les champs avant de les remplir
        self.entry_name.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_balance.delete(0, tk.END)

        self.entry_name.insert(0, values[1])  # Nom
        self.entry_email.insert(0, values[2])  # Email
        self.entry_balance.insert(0, f"{values[3]}")  # Solde (converti en str)


if __name__ == "__main__":
    app = App()
    app.mainloop()
