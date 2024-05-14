import customtkinter as ctk
from PIL import ImageTk
from PIL import Image
from tkinter import Menu
import time 
import connect
from tkinter import simpledialog
from tkinter import messagebox


ctk.set_appearance_mode("dark")        
ctk.set_default_color_theme("blue")    
appWidth, appHeight = 600, 600



class Music_player(ctk.CTk):
    def __init__(self, filename, **kwargs):
        super().__init__(**kwargs)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.is_playing = False
        self.title("Music Player")    
        self.geometry(f"{appWidth}x{appHeight}")
        
        self.filename = filename
        self.canvas = ctk.CTkCanvas(self, width=600, height=800, bg="#2d2d2d")
        self.canvas.pack()
        
        
        self.image = Image.open(self.filename)
        self.image = self.image.resize((250, 250))#, Image.Resampling.LANCZOS)
        self.tkimage = None
        self.canvas_obj = None
        
        
        # Play/Pause Button
        self.play_pause_button = ctk.CTkButton(self, text="▶", font=ctk.CTkFont(size=20), command= self.toggle_playback, width=50, height=50)
        self.play_pause_button.place(relx=0.5, rely=0.75, anchor=ctk.CENTER)
        
        self.angle = 0
        self.after(100, self.update)
        
        self.mouse_over_button = False
        self.mouse_over_slider = False

         # Tempo 
        self.tempo_label = ctk.CTkLabel(self, text="Tempo: 120 BPM")
        self.tempo_label.place(relx=0.42, rely=0.9)

        self.tempo_slider = ctk.CTkSlider(self, from_=60, to=180, command=self.change_tempo)
        self.tempo_slider.place(relx=0.34, rely=0.95)
        self.tempo_slider.set(120)

        self.angle = 0
        self.after(100, self.update)

        self.mouse_over_button = False
        self.mouse_over_slider = False
        
        
        # Speaker Button with Text Symbol
        self.speaker_button = ctk.CTkButton(self, text="🔊", font=ctk.CTkFont(size=25), width=50, height=50, command=self.toggle_mute)
        self.speaker_button.place(relx=0.2, rely=0.71)
        self.speaker_button.bind("<Enter>", self.on_enter_button)
        self.speaker_button.bind("<Leave>", self.on_leave_button)

        # Volume Slider - initially hidden
        self.volume_slider = ctk.CTkSlider(self, from_=0, to=100, command=self.on_volume_change)
        self.volume_slider.place(relx=0.25, rely=0.83, anchor="center")
        self.volume_slider.set(50)  # Default volume level
        self.volume_slider.place_forget()  # Hide slider initially

        # Bind events for volume slider
        self.volume_slider.bind("<Enter>", self.on_enter_slider)
        self.volume_slider.bind("<Leave>", self.on_leave_slider)
        
        
        self.repeat_music = False  # Repeat music state, False means don't repeat, True means repeat
        
        # Repeat Button
        self.repeat_button = ctk.CTkButton(self, text="⟳", font=ctk.CTkFont(size=20), command=self.toggle_repeat, width=50, height=50)
        self.repeat_button.place(relx=0.7, rely=0.71) 

        # Timer label
        self.timer_label = ctk.CTkLabel(self, text="00:00", width=100, height=50)
        self.timer_label.place(relx=0.5, rely=0.1, anchor="center")

        # Start time and elapsed time
        self.start_time = None
        self.elapsed_time = 0
        
        # Record Button
        self.record_button = ctk.CTkButton(self, text="REC",font=ctk.CTkFont(size=20), command=self.start_recording, width=50, height=50)
        self.record_button.place(relx=0.1, rely=0.1, anchor="center")
        # Create a button with "≡" symbol
        self.menu_button = ctk.CTkButton(self, text="≡",font=ctk.CTkFont(size=30), width=50, height=50)
        self.menu_button.place(relx=0.9, rely=0.1,anchor="center")

        # Bind the hover event to the button
        self.menu_button.bind("<Enter>", self.show_menu)

        # Prepare the dropdown menu (not visible until hovered)
        self.prepare_menu()
        self.connect = connect.Connect()
        
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.connect.quit()
            self.destroy()

    def prepare_menu(self):
        menubar = Menu(self)
        self.config(menu=menubar)
        
        # Dropdown menu
        self.dropdown_menu = Menu(menubar, tearoff=0)
        
        self.dropdown_menu.add_command(label="Instru Droite guitare", command=lambda: self.set_instru(1, 25))
        self.dropdown_menu.add_command(label="Instru Sdm guitare", command=lambda: self.set_instru(2, 25))
        self.dropdown_menu.add_command(label="Instru Gauche guitare", command=lambda: self.set_instru(0, 25))
        self.dropdown_menu.add_command(label="Instru Droite piano", command=lambda: self.set_instru(1, 0))
        self.dropdown_menu.add_command(label="Instru Gauche piano", command=lambda: self.set_instru(0, 0))
        self.dropdown_menu.add_command(label="Instru Sdm piano", command=lambda: self.set_instru(2, 0))
        self.dropdown_menu.add_separator()
        
    

        # Add an input option
        self.dropdown_menu.add_command(label="Instrument main droite", command=self.set_instru_input_1)
        self.dropdown_menu.add_command(label="Instrument main gauche", command=self.set_instru_input_0)
        self.dropdown_menu.add_command(label="Instrument voix sdm", command=self.set_instru_input_2)
        self.dropdown_menu.add_separator()

        self.dropdown_menu.add_command(label="Proba fausse note", command=self.fausse_note)

    def change_tempo(self, tempo):
            tempo = self.tempo_slider.get()
            tempo = int(tempo)
            self.tempo_label.configure(text=f"Tempo: {tempo} BPM")
            self.connect.update_tempo(tempo)

    def fausse_note(self):
        proba = simpledialog.askfloat("Proba fausse note", "Choisir la probabilité de fausse note (0-1):", parent=self)
        if proba is not None:
            print(f"The user inputted: {proba}")
            self.connect.proba_fausse_note (proba)

    def set_instru_input(self,voix):
        if voix == 0:
            nom = "main gauche"
        elif voix == 1:
            nom = "main droite"
        else:
            nom = "voix sdm"        
        number = simpledialog.askinteger("Sélection d'instrument",
                f"Choisir un instrument pour la {nom} (0-127) ou -1 pour retirer cette voix:",
                parent=self)

        if number is not None:
            print(f"The user inputted: {number}")
            self.set_instru(voix, number)
    
    def set_instru_input_0(self):
        self.set_instru_input(0)

    def set_instru_input_1(self):
        self.set_instru_input(1)
    
    def set_instru_input_2(self):
        self.set_instru_input(2)
    def show_menu(self, event):
        try:
            self.dropdown_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.dropdown_menu.grab_release()

    

    def set_instru(self, voix = None, instrument=0):
        if voix is not None:
            self.connect.set_instrument(voix, instrument)
        
    def on_volume_change(self, event=None):
        current_volume = self.volume_slider.get()  
        self.connect.adjust_volume(current_volume)
 
    def start_recording(self):
        print("Recording started...") 
        
    def update_timer(self):
        if self.is_playing:
            # Calculate elapsed time
            current_time = time.time()
            self.elapsed_time = int(current_time - self.start_time)
            mins, secs = divmod(self.elapsed_time, 60)
            self.timer_label.configure(text=f'{mins:02d}:{secs:02d}')
            self.after(1000, self.update_timer)
        
    def toggle_repeat(self):
        self.is_playing = False
        self.play_pause_button.configure(text="▶")
        self.start_time = None
        self.elapsed_time = 0
        self.timer_label.configure(text="00:00")
        if self.canvas_obj is not None:
            self.canvas.delete(self.canvas_obj)
            self.canvas_obj = None
            self.tkimage = None
        self.connect.restart_music()  
        print("Music restarted")

    def on_enter_button(self, event):
        self.mouse_over_button = True
        self.show_volume_slider()

    def on_leave_button(self, event):
        self.mouse_over_button = False
        self.check_mouse_leave()

    def on_enter_slider(self, event):
        self.mouse_over_slider = True

    def on_leave_slider(self, event):
        self.mouse_over_slider = False
        self.check_mouse_leave()

    def show_volume_slider(self):
        self.volume_slider.place(relx=0.25, rely=0.83, anchor="center")

    def check_mouse_leave(self):
        # If mouse is not over either button or slider, hide the slider after a short delay
        if not self.mouse_over_button and not self.mouse_over_slider:
            self.after(500, self.hide_volume_slider)

    def hide_volume_slider(self):
        if not self.mouse_over_button and not self.mouse_over_slider:
            self.volume_slider.place_forget()

    def toggle_mute(self):
        print("Toggle mute functionality not implemented")
        
        
        
        
    def update(self):
        if self.is_playing:
            self.angle += 20
            self.angle %= 360
            self.tkimage = ImageTk.PhotoImage(self.image.rotate(self.angle))
            if self.canvas_obj is None:
                self.canvas_obj = self.canvas.create_image(300, 250, image=self.tkimage)
            else:
                self.canvas.itemconfig(self.canvas_obj, image=self.tkimage)
            # This is necessary because ImageTk.PhotoImage doesn't hold a reference.
            self.canvas.image = self.tkimage  
            self.after(100, self.update)
        elif self.canvas_obj is not None:
            self.canvas.delete(self.canvas_obj)
            self.canvas_obj = None
            self.tkimage = None
        
            
            
    def toggle_playback(self):
        self.is_playing = not self.is_playing
        self.connect.play_music(self.is_playing)
        if self.is_playing:
            if not self.start_time:
                self.start_time = time.time() - self.elapsed_time
            self.update_timer()
            self.play_pause_button.configure(text="⏸")
            self.update()  # Start or continue rotation
        else:
            self.start_time = None
            self.play_pause_button.configure(text="▶")
            # Rotation will automatically stop due to update logic

        print("Toggle play/pause")

 
 
if __name__ == "__main__":
    mp = Music_player('discc.png')
    mp.mainloop()   
    
    
    
    
    
