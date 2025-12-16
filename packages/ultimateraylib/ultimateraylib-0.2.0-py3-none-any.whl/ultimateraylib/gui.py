from ._classes import *
# gui

# int GuiButton(Rectangle bounds, const char *text)
lib.GuiButton.argtypes = [Rectangle, c_char_p]
lib.GuiButton.restype = ctypes.c_int
def gui_button(bounds: Rectangle, text:str):
    return bool(lib.GuiButton(bounds, text.encode()))

# int GuiMessageBox(Rectangle bounds, const char *title, const char *message, const char *buttons)
makeconnect("GuiMessageBox", [Rectangle, c_char_p, c_char_p, c_char_p], c_int)
def gui_message_box(bounds, title, message, buttons):
    return lib.GuiMessageBox(bounds, title, message, buttons)

'''
RAYGUIAPI int GuiDropdownBox(Rectangle bounds, const char *text, int *active, bool editMode);          // Dropdown Box control


RAYGUIAPI int GuiSpinner(Rectangle bounds, const char *text, int *value, int minValue, int maxValue, bool editMode); // Spinner control

RAYGUIAPI int GuiValueBox(Rectangle bounds, const char *text, int *value, int minValue, int maxValue, bool editMode); // Value Box control, updates input text with numbers

RAYGUIAPI int GuiValueBoxFloat(Rectangle bounds, const char *text, char *textValue, float *value, bool editMode); // Value box control for float values

RAYGUIAPI int GuiTextBox(Rectangle bounds, char *text, int textSize, bool editMode);                   // Text Box control, updates input text

RAYGUIAPI int GuiSlider(Rectangle bounds, const char *textLeft, const char *textRight, float *value, float minValue, float maxValue); // Slider control
RAYGUIAPI int GuiSliderBar(Rectangle bounds, const char *textLeft, const char *textRight, float *value, float minValue, float maxValue); // Slider Bar control
RAYGUIAPI int GuiProgressBar(Rectangle bounds, const char *textLeft, const char *textRight, float *value, float minValue, float maxValue); // Progress Bar control
RAYGUIAPI int GuiStatusBar(Rectangle bounds, const char *text);                                        // Status Bar control, shows info text
RAYGUIAPI int GuiDummyRec(Rectangle bounds, const char *text);                                         // Dummy control for placeholders
RAYGUIAPI int GuiGrid(Rectangle bounds, const char *text, float spacing, int subdivs, Vector2 *mouseCell); // Grid control
'''

makeconnect("GuiDropdownBox", [Rectangle, c_char_p, POINTER(c_int), c_bool], c_int)
def gui_dropdown_box(bounds: Rectangle, text: str, active: int, edit_mode: bool):
    dad = c_int(active)
    lib.GuiDropdownBox(bounds, text, byref(dad), edit_mode)
    return dad.value

makeconnect("GuiSpinner", [Rectangle, c_char_p, POINTER(c_int), c_int, c_int, c_bool], c_int)
def gui_spinner(bounds, text, value: int, min_value, max_value, edit_mode):
    dad = c_int(value)
    lib.GuiSpinner(bounds, text, byref(dad), min_value, max_value, edit_mode)
    return dad.value

makeconnect("GuiValueBox", [Rectangle, c_char_p, POINTER(c_int), c_int, c_int, c_bool], c_int)
def gui_value_box(bounds: Rectangle, text: str, value: int, min_value: int, max_value: int, edit_mode: bool):
    dad = c_int(value)
    lib.GuiValueBox(bounds, text, byref(dad), min_value, max_value, edit_mode)
    return dad.value

makeconnect("GuiValueBoxFloat", [Rectangle, c_char_p, c_char_p, POINTER(c_float), c_bool], c_int)
def gui_value_box_float(bounds: Rectangle, text: str, text_value: str, value: float, edit_mode: bool):
    dad = c_float(value)
    lib.GuiValueBoxFloat(bounds, text, text_value, byref(dad), edit_mode)
    return dad.value

makeconnect("GuiTextBox", [Rectangle, c_char_p, c_int, c_bool], c_int)
def gui_text_box(bounds: Rectangle, text: str, text_size: int, edit_mode: bool):
    # Create a buffer of the right size
    buf = create_string_buffer(text.encode(), text_size)
    caret = lib.GuiTextBox(bounds, buf, text_size, edit_mode)
    return caret, buf.value.decode()  # Return caret and updated string

makeconnect("GuiSlider", [Rectangle, c_char_p, c_char_p, POINTER(c_float), c_float, c_float], c_int)
def gui_slider(bounds: Rectangle, text_left: str, text_right: str, value: float, min_value: float, max_value: float) -> tuple[float, int]:
    skibiidi = c_float(value)
    da = lib.GuiSlider(bounds, text_left.encode(), text_right.encode(), byref(skibiidi), min_value, max_value)
    return skibiidi.value, da

makeconnect("GuiSliderBar", [Rectangle, c_char_p, c_char_p, POINTER(c_float), c_float, c_float], c_int)
def gui_slider_bar(bounds: Rectangle, text_left: str, text_right: str, value: float, min_value: float, max_value: float) -> tuple[float, int]:
    skibiidi = c_float(value)
    da = lib.GuiSliderBar(bounds, text_left.encode(), text_right.encode(), byref(skibiidi), min_value, max_value)
    return skibiidi.value, da

makeconnect("GuiProgressBar", [Rectangle, c_char_p, c_char_p, POINTER(c_float), c_float, c_float], c_int)
def gui_progress_bar(bounds: Rectangle, text_left: str, text_right: str, value: float, min_value: float, max_value: float) -> tuple[float, int]:
    skibiidi = c_float(value)
    da = lib.GuiProgressBar(bounds, text_left.encode(), text_right.encode(), byref(skibiidi), min_value, max_value)
    return skibiidi.value, da

makeconnect("GuiStatusBar", [Rectangle, c_char_p], c_int)
def gui_status_bar(bounds: Rectangle, text: str):
    return lib.GuiStatusBar(bounds, text.encode())

makeconnect("GuiDummyRec", [Rectangle, c_char_p], c_int)
def gui_dummy_rec(bounds: Rectangle, text: str):
    return lib.GuiDummyRec(bounds, text.encode())

