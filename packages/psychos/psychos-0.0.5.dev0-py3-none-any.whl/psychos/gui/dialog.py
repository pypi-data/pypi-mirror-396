import tkinter as tk
from tkinter import ttk

class Dialog:
    """A versatile dialog form using Tkinter.

    This dialog can contain:
      - Interactive fields (Entry or Combobox).
      - Static labels (added via `add_label`).
      - OK and/or Cancel buttons.

    When displayed (via `.show()`):
      - Returns a dictionary of field values + {"accepted": True} if the user
        presses OK.
      - Returns None if the user presses Cancel or closes the dialog window.

    Args:
        title (str, optional): Title of the dialog window. Defaults to "" (no title).
        ok_text (str, optional): Label for the OK button. Defaults to "OK".
        cancel_text (str, optional): Label for the Cancel button. Defaults to "Cancel".
        ok_button (bool, optional): Whether to display the OK button. Defaults to True.
        cancel_button (bool, optional): Whether to display the Cancel button. Defaults to True.
        theme (str, optional): The ttk theme to use. Defaults to "clam".
        main_padding (int, optional): Padding around the main container. Defaults to 20.
        button_padding (int, optional): Padding around the button area. Defaults to 5.
        wraplength (int, optional): Maximum label width in pixels (wraps text). Defaults to 300.
    """

    def __init__(
        self,
        title="",
        ok_text="OK",
        cancel_text="Cancel",
        ok_button=True,
        cancel_button=True,
        theme="clam",
        main_padding=20,
        button_padding=5,
        wraplength=300
    ):
        self.title = title
        self.ok_text = ok_text
        self.cancel_text = cancel_text
        self.ok_button = ok_button
        self.cancel_button = cancel_button
        self.theme = theme
        self.main_padding = main_padding
        self.button_padding = button_padding
        self.wraplength = wraplength

        # List to store field definitions (order matters).
        # Each item is either:
        #   {"widget_type": "label", "text": "..."}
        # or {"widget_type": "field", "name": ..., "default": ..., "label": ..., "format": ..., "choices": ...}
        self.fields = []

        # Dictionary to store references to interactive widgets (fields).
        # Key = field name, Value = {"widget": widget, "format": format_fn}
        self._widgets = {}

        # Final result. Will be None if canceled, or a dict if accepted.
        self._data = None

    # -------------------------------------------------------------------------
    # Public Methods
    # -------------------------------------------------------------------------

    def add_field(self, name, default=None, label=None, format=str, choices=None):
        """Add an interactive field (Entry or Combobox) to the form.

        Args:
            name (str):
                Name (key) of the field in the returned data.
            default (Any, optional):
                Default value for the field. For a text entry, this is inserted
                as the initial text. For a combo box, it sets the initial selection.
                Defaults to None.
            label (str, optional):
                Label to display next to the field. If None, uses `name`. Defaults to None.
            format (Callable, optional):
                A function to format/parse the returned value (e.g., `int`). Defaults to `str`.
            choices (list, optional):
                If provided, creates a combo box with these choices instead of a text entry.
                Defaults to None.
        """
        self.fields.append({
            "widget_type": "field",
            "name": name,
            "default": default,
            "label": label or name,
            "format": format,
            "choices": choices
        })

    def add_label(self, text):
        """Add a static label to the form (useful for headers, instructions, or separators).

        Args:
            text (str): The text to display in the label.
        """
        self.fields.append({
            "widget_type": "label",
            "text": text
        })

    def show(self):
        """Display the dialog form and block until the user responds.

        Returns:
            dict or None:
                - A dictionary containing all field values plus {"accepted": True} if OK is pressed.
                - None if Cancel is pressed or the dialog is closed.
        """
        # Create and hide the root window
        self.root = tk.Tk()
        self.root.withdraw()

        # Set up the Toplevel dialog window
        main_frame = self._setup_tinker()

        # Add widgets (labels/fields) in order
        self._add_widgets(main_frame)

        # Add OK/Cancel buttons
        self._add_buttons(main_frame)

        # Center and display
        self._center_dialog()
        self.dialog_window.grab_set()
        self.root.mainloop()

        return self._data

    # -------------------------------------------------------------------------
    # Internal Helper Methods
    # -------------------------------------------------------------------------

    def _setup_tinker(self):
        """Initialize the Toplevel dialog window with styling and padding.

        Returns:
            ttk.Frame: The main frame inside the dialog window.
        """
        self.dialog_window = tk.Toplevel(self.root)
        if self.title:
            self.dialog_window.title(self.title)
        self.dialog_window.protocol("WM_DELETE_WINDOW", self._on_close)

        # Apply the chosen theme
        style = ttk.Style(self.dialog_window)
        style.theme_use(self.theme)

        # Create a main frame with padding
        main_frame = ttk.Frame(
            self.dialog_window,
            padding=(self.main_padding, self.main_padding)
        )
        main_frame.pack(fill="both", expand=True)

        return main_frame

    def _add_widgets(self, parent):
        """Add label/field widgets to the given parent frame."""
        for idx, field in enumerate(self.fields):
            if field["widget_type"] == "label":
                self._create_label_widget(parent, field, idx)
            else:
                self._create_field_widget(parent, field, idx)

    def _create_label_widget(self, parent, field, row_idx):
        """Create a label widget spanning two columns."""
        lbl = ttk.Label(parent, text=field["text"], wraplength=self.wraplength)
        lbl.grid(row=row_idx, column=0, columnspan=2, padx=5, pady=5, sticky="w")

    def _create_field_widget(self, parent, field, row_idx):
        """Create a label and either an Entry or Combobox widget."""
        # Create label
        label_widget = ttk.Label(parent, text=field["label"], wraplength=self.wraplength)
        label_widget.grid(row=row_idx, column=0, sticky="e", padx=5, pady=5)

        # Create input widget
        if field["choices"] is not None:
            widget = ttk.Combobox(parent, values=field["choices"], state="readonly")
            # Set default if valid; otherwise pick the first choice
            if field["default"] is not None and field["default"] in field["choices"]:
                widget.set(field["default"])
            else:
                widget.current(0)
        else:
            widget = ttk.Entry(parent)
            if field["default"] is not None:
                widget.insert(0, str(field["default"]))

        widget.grid(row=row_idx, column=1, padx=5, pady=5, sticky="w")

        # Store the widget and its formatting function
        self._widgets[field["name"]] = {
            "widget": widget,
            "format": field["format"]
        }

    def _add_buttons(self, parent):
        """Create and place the OK/Cancel buttons."""
        button_frame = ttk.Frame(parent, padding=(self.button_padding, self.button_padding))
        button_frame.grid(row=len(self.fields), column=0, columnspan=2, pady=(10, 0))

        if self.ok_button:
            ok_btn = ttk.Button(button_frame, text=self.ok_text, command=self._on_ok)
            ok_btn.pack(side="left", padx=5)

        if self.cancel_button:
            cancel_btn = ttk.Button(button_frame, text=self.cancel_text, command=self._on_cancel)
            cancel_btn.pack(side="right", padx=5)

    def _center_dialog(self):
        """Center the dialog on the user's screen."""
        self.dialog_window.update_idletasks()  # Ensure geometry is accurate
        width = self.dialog_window.winfo_width()
        height = self.dialog_window.winfo_height()
        screen_width = self.dialog_window.winfo_screenwidth()
        screen_height = self.dialog_window.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.dialog_window.geometry(f"+{x}+{y}")

    def _on_ok(self):
        """Gather field values, mark as accepted, and close the dialog."""
        data = {}
        for name, info in self._widgets.items():
            widget = info["widget"]
            format_fn = info["format"]
            raw_value = widget.get()
            try:
                data[name] = format_fn(raw_value)
            except Exception:
                # If formatting fails, store the raw string
                data[name] = raw_value

        data["accepted"] = True
        self._data = data
        self._close_dialog()

    def _on_cancel(self):
        """User canceled the dialog."""
        self._data = None
        self._close_dialog()

    def _on_close(self):
        """Window close button behaves like cancel."""
        self._data = None
        self._close_dialog()

    def _close_dialog(self):
        """Destroy the dialog and stop the event loop."""
        self.dialog_window.destroy()
        self.root.quit()
