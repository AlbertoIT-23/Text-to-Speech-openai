#!/usr/bin/env python3
import logging
import tkinter as tk
from controllers.app_controller import AppController

def main():
    """
    Application entry point. Sets up the root Tkinter window
    and initializes the main controller.
    """
    root = tk.Tk()
    app = AppController(root)
    root.mainloop()

if __name__ == "__main__":
    main()