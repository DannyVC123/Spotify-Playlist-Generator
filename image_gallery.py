import tkinter as tk
from tkinter import PhotoImage

from track import Track

class ImageGallery:
    def __init__(self, tab, tracks):
        self.tab = tab
        self.tracks = tracks
        self.index = 0
        self.images_per_page = 5

        # Create a frame to hold the images and navigation buttons
        self.frame = tk.Frame(tab)
        self.frame.pack(pady=10)

        # Create left and right arrows
        self.left_arrow = tk.Button(self.frame, text="←", command=self.scroll_left)
        self.left_arrow.grid(row=0, column=0, rowspan=2)

        self.right_arrow = tk.Button(self.frame, text="→", command=self.scroll_right)
        self.right_arrow.grid(row=0, column=6)

        # Create a frame for displaying images
        self.image_frame = tk.Frame(self.frame)
        self.image_frame.grid(row=0, column=1, columnspan=5)

        # Display the first set of images
        self.display_images()

    def display_images(self):
        # Clear the previous images
        for widget in self.image_frame.winfo_children():
            widget.destroy()

        # Get the current 5 images
        start = self.index
        end = min(self.index + self.images_per_page, len(self.tracks))
        images_to_show = self.tracks[start:end]

        # Add images to the frame
        for i, track in enumerate(images_to_show):
            label = tk.Label(self.image_frame, image=track.album_cover)
            label.image = track.album_cover
            label.grid(row=0, column=i, padx=5)

            name_label = tk.Label(self.image_frame, text=track.name, wraplength=120)
            name_label.grid(row=1, column=i, padx=5)

    def scroll_left(self):
        if self.index - self.images_per_page < 0:
            self.index = (len(self.tracks) - 1) // self.images_per_page * self.images_per_page
        else:
            self.index -= self.images_per_page
        
        self.display_images()

    def scroll_right(self):
        if self.index + self.images_per_page >= len(self.tracks):
            self.index = 0
        else:
            self.index += self.images_per_page
        
        self.display_images()