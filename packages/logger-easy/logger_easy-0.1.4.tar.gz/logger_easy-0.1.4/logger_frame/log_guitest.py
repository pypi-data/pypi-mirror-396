from tkinter import *
from tkinter import ttk
import logger

lgr = logger.Logger("log_wind",filing=False)



root = Tk()

root.title("log_test")

etr = Entry(root)
etr.bind("<Return>", lambda e: hand())

cmb = ttk.Combobox(root, values=["DEBUG", "INFO", "WARN", "ERROR"],state="readonly")
cmb.current(0)

bv = BooleanVar(value=False)
cb = Checkbutton(root, text="debug",onvalue=True,offvalue=False,variable=bv)

def hand():
    lgr.debugflag = bv.get()
    ev = etr.get()
    etr.delete(0,END)
    match cmb.get():
        case "DEBUG":
            lgr.debug(ev)
        case "INFO":
            lgr(ev)
        case "WARN":
            lgr.warn(ev)
        case "ERROR":
            lgr.error(ev)
        case _:
            pass

btn = Button(root, text="log!", command=hand)

ex = Button(root,text="quit",command=root.destroy)

etr.grid(column=1,row=1,pady=5,padx=7)

cb.grid(column=1,row=2)

cmb.grid(column=2,row=2,padx=7)

btn.grid(column=1,row=3)

ex.grid(column=2,row=3,pady=10)
 
root.mainloop()