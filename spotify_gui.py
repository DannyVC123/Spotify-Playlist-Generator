import tkinter as tk

class SpotifyGUI:
    width, height = 800, 800

    def __init__(self):
        self.create_ui()
        self.root.mainloop()
    
    def create_ui(self):
        self.root = tk.Tk()
        self.root.title("Spofy Playlist Generator")
        self.root.geometry(f'{SpotifyGUI.width}x{SpotifyGUI.height}')
        
        # Create a label for the title
        title_label = tk.Label(self.root, text="Spotify Playlist Generator", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)  # Add padding at the top for spacing

        # Create textboxes with labels
        label1 = tk.Label(self.root, text="First Name:")
        label1.pack(pady=5)
        entry1 = tk.Entry(self.root, width=30)
        entry1.pack(pady=5)

        label2 = tk.Label(self.root, text="Last Name:")
        label2.pack(pady=5)
        entry2 = tk.Entry(self.root, width=30)
        entry2.pack(pady=5)

        label3 = tk.Label(self.root, text="Email:")
        label3.pack(pady=5)
        entry3 = tk.Entry(self.root, width=30)
        entry3.pack(pady=5)

        # Create buttons
        submit_button = tk.Button(self.root, text="Submit", width=15)
        submit_button.pack(pady=10)

        cancel_button = tk.Button(self.root, text="Cancel", width=15)
        cancel_button.pack(pady=5)

        '''
        self.create_scale('Focal Length', 500, 3000, 1, frame = param_frame)
        titles = ['X-Rotation', 'Y-Rotation', 'Z-Rotation']
        self.rotation_scales = []
        for i in range(3):
            _, v = self.create_scale(titles[i], 0, 360, i+2, i, frame = param_frame)
            self.rotation_scales.append([v, 0])
        
        self.img = PhotoImage(file = "./images/axes_reference_rh_small.png")
        label = Label(self.window, image = self.img)
        label.place(relx = 1.0, rely = 0.0, anchor = NE)
        '''

SpotifyGUI()