import tkinter as tk

class SpotifyGUI:
    width, height = 800, 800

    def __init__(self):
        self.create_ui()
        self.root.mainloop()
    
    def create_ui(self):
        # Window
        self.root = tk.Tk()
        self.root.title('Spotify Playlist Generator')
        self.root.geometry(f'{SpotifyGUI.width}x{SpotifyGUI.height}')
        
        # Title
        title_label = tk.Label(self.root, text='Spotify Playlist Generator', font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)

        # Login
        frame = tk.Frame(self.root)
        frame.pack(pady=10)
        login_label = tk.Label(self.root, text='Playlist JSON from ChatGPT:', font=('Arial', 16, 'bold'))


        # Playlist Prompt
        playlist_prompt_label = tk.Label(self.root, text='Playlist JSON from ChatGPT:', font=('Arial', 16, 'bold'))
        playlist_prompt_label.pack(pady=5)
        self.playlist_prompt_textbox = tk.Text(self.root, width=50, height=5, font=('Arial', 16), wrap=tk.WORD)
        self.playlist_prompt_textbox.pack(pady=5)

        # Frame
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        # Num Songs
        num_songs_label = tk.Label(frame, text='Number of Songs (Default 10):', font=('Arial', 16, 'bold'))
        num_songs_label.grid(row=0, column=0, padx=5, pady=5)
        self.num_songs_textbox = tk.Entry(frame, width=5)
        self.num_songs_textbox.grid(row=0, column=1, padx=5, pady=5)

        '''
        label2 = tk.Label(self.root, text='Last Name:')
        label2.pack(pady=5)
        entry2 = tk.Entry(self.root, width=30)
        entry2.pack(pady=5)

        label3 = tk.Label(self.root, text='Email:')
        label3.pack(pady=5)
        entry3 = tk.Entry(self.root, width=30)
        entry3.pack(pady=5)

        # Create buttons
        submit_button = tk.Button(self.root, text='Submit', width=15)
        submit_button.pack(pady=10)

        cancel_button = tk.Button(self.root, text='Cancel', width=15)
        cancel_button.pack(pady=5)
        '''

        '''
        self.create_scale('Focal Length', 500, 3000, 1, frame = param_frame)
        titles = ['X-Rotation', 'Y-Rotation', 'Z-Rotation']
        self.rotation_scales = []
        for i in range(3):
            _, v = self.create_scale(titles[i], 0, 360, i+2, i, frame = param_frame)
            self.rotation_scales.append([v, 0])
        
        self.img = PhotoImage(file = './images/axes_reference_rh_small.png')
        label = Label(self.window, image = self.img)
        label.place(relx = 1.0, rely = 0.0, anchor = NE)
        '''

SpotifyGUI()