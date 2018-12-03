# View more python learning tutorial on my Youtube and Youku channel!!!

# Youtube video tutorial: https://www.youtube.com/channel/UCdyjiB5H8Pu7aDTNVXTTpcg
# Youku video tutorial: http://i.youku.com/pythontutorial

import tkinter as tk
from PIL import ImageTk, Image
window = tk.Tk()
window.title('my window')
window.geometry('800x550')

canvas = tk.Canvas(window, bg='blue', height=100, width=200)
# image_file = tk.PhotoImage(file='ins.gif')
# image = canvas.create_image(10, 10, anchor='nw', image=image_file)
img = ImageTk.PhotoImage(Image.open("okay/1.jpeg"))
panel = tk.Label(window, image = img)
panel.pack()



window.mainloop()