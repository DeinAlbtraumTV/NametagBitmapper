import copy
import json
import pathlib
from os import mkdir
from os.path import exists
import sys
import tkinter as tk
from PIL import Image
import tkinter.filedialog

working_dir = pathlib.Path().resolve()
storage_dir = working_dir.joinpath("bmps")

class BMPCreator(tk.Frame):
    def toggle_pxl(self, x, y):
        self.frames[self.frame][x][y] = not self.frames[self.frame][x][y]
        self.buttons[x][y].config(bg=("white" if self.frames[self.frame][x][y] else "black"),
                                  fg=("black" if self.frames[self.frame][x][y] else "white"))

    def clone_frame(self):
        if len(self.frames) < 123:
            self.frames.append(copy.deepcopy(self.frames[self.frame]))
            self.frame = len(self.frames) - 1
            self.redraw()

    def clear_frame(self):
        for i, buttons in enumerate(self.buttons):
            for j, button in enumerate(buttons):
                self.frames[self.frame][i][j] = False
                button.config(bg=("white" if self.frames[self.frame][i][j] else "black"),
                              fg=("black" if self.frames[self.frame][i][j] else "white"))

    def create_frame(self):
        if len(self.frames) < 123:
            self.frames.append(copy.deepcopy(self.frames[self.frame]))
            self.frame = self.frame + 1
            self.frame_counter.config(text=f"{self.frame + 1}/{len(self.frames)}")
            for i, buttons in enumerate(self.buttons):
                for j, button in enumerate(buttons):
                    self.frames[self.frame][i][j] = False
                    button.config(bg=("white" if self.frames[self.frame][i][j] else "black"),
                                  fg=("black" if self.frames[self.frame][i][j] else "white"))

    def incr_frame(self):
        self.frame = (self.frame + 1) % len(self.frames)
        self.redraw()

    def decr_frame(self):
        self.frame = (self.frame - 1) % len(self.frames)
        self.redraw()

    def del_frame(self):
        if len(self.frames) > 1:
            self.frame -= 1
            self.frames.pop()
            self.redraw()

    def redraw(self):
        self.frame_counter.config(text=f"{self.frame + 1}/{len(self.frames)}") #spalte / zeile
        for i, buttons in enumerate(self.buttons):
            for j, button in enumerate(buttons):
                button.config(bg=("white" if self.frames[self.frame][i][j] else "black"),
                              fg=("black" if self.frames[self.frame][i][j] else "white"))
                
    def load(self):
        with open(storage_dir.joinpath(self.filename)) as f:
            self.frames = json.load(f)

    def save(self):
        img = Image.new('RGB', (48*len(self.frames), 11), "black")  # Create a new black image
        pixels = img.load()  # Create the pixel map
        for frame in range(len(self.frames)):
            for i in range(44):
                for j in range(11):
                    if self.frames[frame][i][j]:
                        pixels[frame * 48 + i, j] = (255, 255, 255)

        with open(storage_dir.joinpath(self.filename), "w") as f:
            json.dump(self.frames, f)

        img.save(working_dir.joinpath(self.filename.replace(".json", ".bmp")))

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.save_button = None
        self.frame_counter = None
        self.decr_button = None
        self.incr_button = None
        self.clone_button = None
        self.clear_button = None
        self.create_button = None
        self.img = tk.PhotoImage(width=1, height=1)
        self.buttons = None
        self.frame = 0
        self.frames = []
        if not exists(storage_dir):
            mkdir(storage_dir)
            
        # skip the filename input if a filename is passed as argument
        if len(args) > 0:
            self.filename = args[0]
        else:
            self.filename = input("Filename: ")

        if not self.filename.endswith(".json"):
            self.filename += ".json"

        if exists(storage_dir.joinpath(self.filename)):
            print(f"Loading {self.filename}")
            self.load()
        else:
            self.setup_frame()

        self.create_buttons()

    def create_buttons(self):
        # creating buttons:
        self.buttons = []
        for i in range(44):
            self.buttons.append([])
            for j in range(11):
                self.buttons[i].append(tk.Button(self, width=37, height=37, text=f"{i+1}/{j+1}", borderwidth=1, highlightthickness=0, padx=0, pady=0, image=self.img, compound="center", command=(lambda x=i, y=j: self.toggle_pxl(x, y)), bg=("white" if self.frames[self.frame][i][j] else "black"), fg=("black" if self.frames[self.frame][i][j] else "white")))
                self.buttons[i][j].grid(row=j+1, column=i)
        self.clone_button = tk.Button(self, text="Duplicate frame to end", command=self.clone_frame)
        self.clone_button.grid(row=45, column=36, columnspan=8, sticky="news")
        
        self.clear_button = tk.Button(self, text="Clear frame", command=self.clear_frame)
        self.clear_button.grid(row=45, column=20, columnspan=4, sticky="news")
        
        self.clear_button = tk.Button(self, text="Delete frame", command=self.del_frame)
        self.clear_button.grid(row=45, column=24, columnspan=4, sticky="news")
        
        self.create_button = tk.Button(self, text="Create new frame", command=self.create_frame)
        self.create_button.grid(row=45, column=28, columnspan=8, sticky="news")
        
        self.incr_button = tk.Button(self, text="++", command=self.incr_frame)
        self.incr_button.grid(row=45, column=12, columnspan=8, sticky="news")
        
        self.decr_button = tk.Button(self, text="--", command=self.decr_frame)
        self.decr_button.grid(row=45, column=4, columnspan=8, sticky="news")
        
        #ToDo add an Disclaimer that this overwrites the current frame
        self.import_button = tk.Button(self, text="Import from BMP", command=(lambda: self.load_frame_from_bmp(tk.filedialog.askopenfilename())))
        self.import_button.grid(row=45, column=0, columnspan=4, sticky="news")
        
        self.shift_frame_left = tk.Button(self, text="⇦ (h)", command=self.shift_frame_left) #h
        self.shift_frame_left.grid(row=46, column=0, columnspan=4, sticky="news")
        
        self.shift_frame_down = tk.Button(self, text="⇩ (j)", command=self.shift_frame_down) # j
        self.shift_frame_down.grid(row=46, column=4, columnspan=4, sticky="news")
        
        self.shift_frame_up = tk.Button(self, text="⇧ (k)", command=self.shift_frame_up) #k
        self.shift_frame_up.grid(row=46, column=8, columnspan=4, sticky="news")
        
        self.shift_frame_right = tk.Button(self, text="⇨ (l)", command=self.shift_frame_right) #l
        self.shift_frame_right.grid(row=46, column=12, columnspan=4, sticky="news")
        
        self.frame_counter = tk.Label(self, text=f"{self.frame + 1}/{len(self.frames)}", bg="black", fg="white")
        self.frame_counter.grid(row=46, column=16, columnspan=40-12, sticky="news") #todo columspan
        
        self.save_button = tk.Button(self, text="Save", command=self.save)
        self.save_button.grid(row=46, column=40, columnspan=4, sticky="news")
        
        self.close_button = tk.Button(self, text="Close", command=self.quit, bg="red", fg="white")
        self.close_button.grid(row=0, column=42, columnspan=3, sticky="news")        
        

    def setup_frame(self):
        self.frames.append([])
        for i in range(44):
            self.frames[self.frame].append([])
            for j in range(11):
                self.frames[self.frame][i].append(False)
                
    def load_frame_from_bmp(self, filename):
        # Load the bmp into the current editor
        img = Image.open(filename)
        img = img.convert("RGB")    
        img = img.resize((44, 11))
        img = img.convert("1")
        pixels = img.load()
        for i in range(44):
            for j in range(11):
                self.frames[self.frame][i][j] = pixels[i, j] == 255
        self.redraw()
        
    def shift_frame_left(self):
        self.frames[self.frame] = self.frames[self.frame][1:] + [self.frames[self.frame][0]]
        self.redraw()
        
    def shift_frame_right(self):
        self.frames[self.frame] = [self.frames[self.frame][-1]] + self.frames[self.frame][:-1]
        self.redraw()
        
    def shift_frame_up(self):
        self.frames[self.frame] = [row[1:] + [False] for row in self.frames[self.frame]]
        self.redraw()
        
    def shift_frame_down(self):
        self.frames[self.frame] = [[False] + row[:-1] for row in self.frames[self.frame]]
        self.redraw()
    
        
        

if __name__ == "__main__":
    args = sys.argv[1:]
    root = tk.Tk()
    window = BMPCreator(root)
    window.pack(fill="both", expand=True)
    
    root.mainloop()
