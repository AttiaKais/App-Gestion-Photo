import os
import json
from tkinter import LEFT, Tk, Toplevel, messagebox, filedialog, Listbox
from tkinter.ttk import Frame, Button, Label
from PIL import Image, ImageTk
import shutil

class PhotoAlbumApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestionnaire d'Albums Photo")
        self.albums = []
        self.selected_album_index = -1
        self.photo_listbox_index = -1
        self.original_photo_path = None
        self.new_photo_path = None
        self.config_file = "config.json"
        self.load_config()
        self.create_widgets()

    def create_widgets(self):
        # Frame pour les albums
        album_frame = Frame(self.root)
        album_frame.pack(side=LEFT, fill='y')

        self.album_listbox = Listbox(album_frame, selectmode='single')
        self.album_listbox.pack(fill='both', expand=True)
        self.album_listbox.bind('<<ListboxSelect>>', self.on_select_album)

        # Frame pour les photos
        photo_frame = Frame(self.root)
        photo_frame.pack(side=LEFT, fill='both', expand=True)

        self.photo_listbox = Listbox(photo_frame, selectmode='single')
        self.photo_listbox.pack(fill='both', expand=True)
        self.photo_listbox.bind('<<ListboxSelect>>', self.on_select_photo)

        # Frame pour les boutons
        button_frame = Frame(self.root)
        button_frame.pack(side=LEFT, fill='y')

        add_album_button = Button(button_frame, text="Ajouter Album", command=self.add_album)
        add_album_button.pack(fill='x')

        delete_album_button = Button(button_frame, text="Supprimer Album", command=self.delete_album)
        delete_album_button.pack(fill='x')

        add_photo_button = Button(button_frame, text="Ajouter Photo", command=self.add_photo)
        add_photo_button.pack(fill='x')

        self.cancel_move_button = Button(button_frame, text="Annuler Déplacement", command=self.cancel_move_photo, state='disabled')
        self.cancel_move_button.pack(fill='x')

        # Frame pour la prévisualisation
        preview_frame = Frame(self.root)
        preview_frame.pack(side=LEFT, fill='both', expand=True)

        self.image_label = Label(preview_frame)
        self.image_label.pack(expand=True)

    def add_album(self):
        album_name = filedialog.askdirectory(title="Sélectionnez un dossier d'album")
        if album_name:
            self.albums.append(album_name)
            self.load_albums()
            messagebox.showinfo("Album ajouté", f"Album '{os.path.basename(album_name)}' ajouté.")

    def delete_album(self):
        if self.selected_album_index >= 0:
            selected_album = self.albums[self.selected_album_index]
            self.albums.pop(self.selected_album_index)
            self.load_albums()
            messagebox.showinfo("Album supprimé", f"Album '{os.path.basename(selected_album)}' supprimé.")
        else:
            messagebox.showwarning("Aucun album sélectionné", "Veuillez sélectionner un album à supprimer.")

    def add_photo(self):
        photo_path = filedialog.askopenfilename(title="Sélectionnez une photo",
                                                filetypes=(("Fichiers image", "*.png *.jpg *.jpeg *.gif"), ("Tous les fichiers", "*.*")))
        if photo_path:
            self.original_photo_path = photo_path
            self.show_confirmation_dialog(photo_path)

    def show_confirmation_dialog(self, photo_path):
        confirm_dialog = Toplevel(self.root)
        confirm_dialog.title("Confirmation de déplacement")
        confirm_dialog.geometry("400x300")

        # Prévisualisation de la photo
        try:
            image = Image.open(photo_path).resize((200, 200), Image.LANCZOS)  # Utilisation de LANCZOS à la place d'ANTIALIAS
            photo = ImageTk.PhotoImage(image)
            image_label = Label(confirm_dialog, image=photo)
            image_label.image = photo
            image_label.pack(pady=10)

            # Boutons de confirmation
            confirm_button = Button(confirm_dialog, text="Déplacer", command=lambda: self.confirm_move_photo(photo_path, confirm_dialog))
            confirm_button.pack(pady=10)

            cancel_button = Button(confirm_dialog, text="Annuler", command=confirm_dialog.destroy)
            cancel_button.pack(pady=10)
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def confirm_move_photo(self, photo_path, dialog):
        if self.selected_album_index >= 0:
            selected_album = self.albums[self.selected_album_index]
            destination_path = os.path.join(selected_album, os.path.basename(photo_path))
            try:
                shutil.move(photo_path, destination_path)
                messagebox.showinfo("Photo déplacée", f"Photo déplacée vers '{destination_path}'.")
                self.new_photo_path = destination_path
                self.load_photos()
                dialog.destroy()
                self.cancel_move_button.config(state='normal')
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
        else:
            messagebox.showwarning("Aucun album sélectionné", "Veuillez sélectionner un album de destination.")

    def cancel_move_photo(self):
        if self.new_photo_path and os.path.exists(self.new_photo_path):
            try:
                shutil.move(self.new_photo_path, self.original_photo_path)
                messagebox.showinfo("Déplacement annulé", f"Photo redéplacée vers '{self.original_photo_path}'.")
                self.load_photos()
                self.cancel_move_button.config(state='disabled')
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def on_select_album(self, event):
        if self.album_listbox.curselection():
            self.selected_album_index = self.album_listbox.curselection()[0]
            self.load_photos()
            self.photo_listbox.selection_clear(0, 'end')

    def on_select_photo(self, event):
        if self.photo_listbox.curselection():
            self.photo_listbox_index = self.photo_listbox.curselection()[0]
            selected_album = self.albums[self.selected_album_index]
            selected_photo = self.photo_listbox.get(self.photo_listbox_index)
            dest_path = os.path.join(selected_album, selected_photo)
            try:
                image = Image.open(dest_path).resize((200, 200), Image.LANCZOS)  # Utilisation de LANCZOS à la place d'ANTIALIAS
                photo = ImageTk.PhotoImage(image)
                self.image_label.config(image=photo)
                self.image_label.image = photo
                self.original_photo_path = dest_path
                self.cancel_move_button.config(state='normal')
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

    def load_albums(self):
        self.album_listbox.delete(0, 'end')
        for album in self.albums:
            self.album_listbox.insert('end', os.path.basename(album))
        if 0 <= self.selected_album_index < len(self.albums):
            self.album_listbox.selection_set(self.selected_album_index)

    def load_photos(self):
        self.photo_listbox.delete(0, 'end')
        if 0 <= self.selected_album_index < len(self.albums):
            selected_album = self.albums[self.selected_album_index]
            photos = [f for f in os.listdir(selected_album) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            for photo in photos:
                self.photo_listbox.insert('end', photo)
        if 0 <= self.photo_listbox_index < len(photos):
            self.photo_listbox.selection_set(self.photo_listbox_index)

    def save_config(self):
        config = {
            'albums': self.albums,
            'selected_album_index': self.selected_album_index,
            'photo_listbox_index': self.photo_listbox_index
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f)

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.albums = config.get('albums', [])
                self.selected_album_index = config.get('selected_album_index', -1)
                self.photo_listbox_index = config.get('photo_listbox_index', -1)

if __name__ == "__main__":
    root = Tk()
    app = PhotoAlbumApp(root)
    root.mainloop()
