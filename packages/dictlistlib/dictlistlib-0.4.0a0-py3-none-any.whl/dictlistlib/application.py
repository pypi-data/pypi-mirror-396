"""Module containing the logic for the dictlistlib."""

import platform

from dictlistlib.utils import Text

try:
    import tkinter as tk
except ModuleNotFoundError as ex:
    from dictlistlib.utils import Printer
    import sys
    lst = ["Failed to launch dictlistlib application because",
           "Python{} binary doesn't have tkinter module".format(platform.python_version()),
           "Please install tkinter module and try it again"]
    Printer.print(lst)
    sys.exit(1)
except Exception as ex:
    raise ex

from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.font import Font

from os import path
from pprint import pformat
import webbrowser

from dictlistlib import create_from_csv_data
from dictlistlib import create_from_json_data
from dictlistlib import create_from_yaml_data

from dictlistlib.utils import Tabular

from dictlistlib.config import Data


def get_relative_center_location(parent, width, height):
    """get relative a center location of parent window.

    Parameters
    ----------
    parent (tkinter): tkinter component instance.
    width (int): a width of a child window.
    height (int): a height of a child window.

    Returns
    -------
    tuple: x, y location.
    """
    pwh, px, py = parent.winfo_geometry().split('+')
    px, py = int(px), int(py)
    pw, ph = [int(i) for i in pwh.split('x')]

    x = int(px + (pw - width) / 2)
    y = int(py + (ph - height) / 2)
    return x, y


def create_msgbox(title=None, error=None, warning=None, info=None,
                  question=None, okcancel=None, retrycancel=None,
                  yesno=None, yesnocancel=None, **options):
    """create tkinter.messagebox
    Parameters
    ----------
    title (str): a title of messagebox.  Default is None.
    error (str): an error message.  Default is None.
    warning (str): a warning message. Default is None.
    info (str): an information message.  Default is None.
    question (str): a question message.  Default is None.
    okcancel (str): an ok or cancel message.  Default is None.
    retrycancel (str): a retry or cancel message.  Default is None.
    yesno (str): a yes or no message.  Default is None.
    yesnocancel (str): a yes, no, or cancel message.  Default is None.
    options (dict): options for messagebox.

    Returns
    -------
    any: a string or boolean result
    """
    if error:
        # a return result is an "ok" string
        result = messagebox.showerror(title=title, message=error, **options)
    elif warning:
        # a return result is an "ok" string
        result = messagebox.showwarning(title=title, message=warning, **options)
    elif info:
        # a return result is an "ok" string
        result = messagebox.showinfo(title=title, message=info, **options)
    elif question:
        # a return result is a "yes" or "no" string
        result = messagebox.askquestion(title=title, message=question, **options)
    elif okcancel:
        # a return result is boolean
        result = messagebox.askokcancel(title=title, message=okcancel, **options)
    elif retrycancel:
        # a return result is boolean
        result = messagebox.askretrycancel(title=title, message=retrycancel, **options)
    elif yesno:
        # a return result is boolean
        result = messagebox.askyesno(title=title, message=yesno, **options)
    elif yesnocancel:
        # a return result is boolean or None
        result = messagebox.askyesnocancel(title=title, message=yesnocancel, **options)
    else:
        # a return result is an "ok" string
        result = messagebox.showinfo(title=title, message=info, **options)

    return result


def set_modal_dialog(dialog):
    """set dialog to become a modal dialog

    Parameters
    ----------
    dialog (tkinter.TK): a dialog or window application.
    """
    dialog.transient(dialog.master)
    dialog.wait_visibility()
    dialog.grab_set()
    dialog.wait_window()


class Content:
    """Content class

    Attributes
    ----------
    data (str): a text.


    """
    def __init__(self, data='', filename='', filetype=''):
        self.case = 'file' if filename else 'data' if data else 'unknown'
        self.data = data
        self.filename = filename
        self.filetype = filetype
        self.ready = False
        self.query_obj = None
        self.process()

    @property
    def is_csv(self):
        """Check if filename or content is in csv format."""
        return self.filetype == 'csv'

    @property
    def is_json(self):
        """Check if filename or content is in json format."""
        return self.filetype == 'json'

    @property
    def is_yaml(self):
        """Check if filename or content is in yaml format."""
        return self.filetype in ['yaml', 'yml']

    @property
    def is_ready(self):
        """Check if content is ready to use."""
        return self.ready

    def process_filename(self):
        if self.filename:
            _, ext = path.splitext(self.filename)
            extension = ext[1:]
            ext = ext.lower()[1:]
            if ext in ['csv', 'json', 'yml', 'yaml']:
                ext = 'yaml' if ext in ['yml', 'yaml'] else ext
                self.filetype = ext
            else:
                if not ext:
                    message = ('Make sure to select file with '
                               'extension json, yaml, yml, or csv.')
                else:
                    fmt = ('Selecting file extension is {}.  Make sure it is '
                           'in form of json, yaml, yml, or csv.')
                    message = fmt.format(extension)

                title = 'File Extension'
                create_msgbox(title=title, warning=message)

            with open(self.filename, newline='') as stream:
                self.data = stream.read().strip()

                if not self.data:
                    message = 'This {} file is empty.'.format(self.filename)
                    title = 'File Extension'
                    create_msgbox(title=title, warnig=message)

    def process_data(self):
        if not self.data:
            if self.case != 'file':
                title = 'Empty Data'
                message = 'data is empty.'
                create_msgbox(title=title, warning=message)

            return

        if not self.filetype:
            if self.case != 'file':
                title = 'Unselecting File Extension'
                message = ('Need to check filetype radio button '
                           'such as json, yaml, or csv.')
                create_msgbox(title=title, warning=message)
                return

        if self.is_yaml:
            try:
                self.query_obj = create_from_yaml_data(self.data)
                self.ready = True
            except Exception as exc:
                create_msgbox(title='Processing YAML Data', error=Text(exc))
        elif self.is_json:
            try:
                self.query_obj = create_from_json_data(self.data)
                self.ready = True
            except Exception as exc:
                create_msgbox(title='Processing JSON data', error=Text(exc))
        elif self.is_csv:
            try:
                self.query_obj = create_from_csv_data(self.data)
                self.ready = True
            except Exception as exc:
                create_msgbox(title='Processing CSV Data', error=Text(exc))

    def process(self):
        """Analyze `self.filename` or `self.data` and
        assign equivalent `self.filetype`"""
        self.process_filename()
        self.process_data()


class Application:
    """A dictlistlib application class.

    Attributes
    ----------
    root (tkinter.Tk): a top tkinter app.
    content (Content): a Content instance.

    Methods
    -------
    build_menu() -> None
    run() -> None
    callback_file_open() -> None
    callback_help_documentation() -> None
    callback_help_view_licenses() -> None
    callback_help_about() -> None
    """

    browser = webbrowser

    def __init__(self):
        # support platform: macOS, Linux, and Window
        self.is_macos = platform.system() == 'Darwin'
        self.is_linux = platform.system() == 'Linux'
        self.is_window = platform.system() == 'Windows'

        # standardize tkinter widget for macOS, Linux, and Window operating system
        self.RadioButton = tk.Radiobutton if self.is_linux else ttk.Radiobutton
        self.CheckBox = tk.Checkbutton if self.is_linux else ttk.Checkbutton
        self.Label = ttk.Label
        self.Frame = ttk.Frame
        self.LabelFrame = ttk.LabelFrame
        self.Button = ttk.Button
        self.TextBox = ttk.Entry
        self.TextArea = tk.Text
        self.PanedWindow = ttk.PanedWindow

        self._base_title = 'dictlistlib'
        self.root = tk.Tk()
        self.root.geometry('800x600+100+100')
        self.root.minsize(200, 200)
        self.root.option_add('*tearOff', False)
        self.content = None

        self.paned_window = None
        self.text_frame = None
        self.entry_frame = None
        self.result_frame = None

        self.radio_btn_var = tk.StringVar()
        self.radio_btn_var.set(None)    # noqa
        self.lookup_entry_var = tk.StringVar()
        self.select_entry_var = tk.StringVar()
        self.result = None

        self.input_textarea = None
        self.result_textarea = None
        self.csv_radio_btn = None
        self.json_radio_btn = None
        self.yaml_radio_btn = None

        self.set_title()
        self.build_menu()
        self.build_frame()
        self.build_textarea()
        self.build_entry()
        self.build_result()

    def set_title(self, widget=None, title=''):
        """Set a new title for tkinter widget.

        Parameters
        ----------
        widget (tkinter): a tkinter widget.
        title (str): a title.  Default is empty.
        """
        widget = widget or self.root
        btitle = self._base_title
        title = '{} - {}'.format(title, btitle) if title else btitle
        widget.title(title)

    def create_custom_label(self, parent, text='', link='',
                            increased_size=0, bold=False, underline=False,
                            italic=False):
        """create custom label

        Parameters
        ----------
        parent (tkinter): a parent of widget.
        text (str): a text of widget.
        link (str): a label hyperlink.
        increased_size (int): increased size for font.
        bold (bool): True will set bold font.
        underline (bool): True will set to underline font.
        italic (bool): True will set to italic font.

        Returns
        -------
        tkinter.Label: a label widget.
        """

        def mouse_over(event):
            if 'underline' not in event.widget.font:
                event.widget.configure(
                    font=event.widget.font + ['underline'],
                    cursor='hand2'
                )

        def mouse_out(event):
            event.widget.config(
                font=event.widget.font,
                cursor='arrow'
            )

        def mouse_press(event):
            self.browser.open_new_tab(event.widget.link)

        style = ttk.Style()
        style.configure("Blue.TLabel", foreground="blue")
        if link:
            label = self.Label(parent, text=text, style='Blue.TLabel')
            label.bind('<Enter>', mouse_over)
            label.bind('<Leave>', mouse_out)
            label.bind('<Button-1>', mouse_press)
        else:
            label = self.Label(parent, text=text)
        font = Font(name='TkDefaultFont', exists=True, root=label)
        font = [font.cget('family'), font.cget('size') + increased_size]
        bold and font.append('bold')
        underline and font.append('underline')
        italic and font.append('italic')
        label.configure(font=font)
        label.font = font
        label.link = link
        return label

    def callback_file_open(self):
        """Callback for Menu File > Open."""
        filetypes = [
            ('JSON Files', '*json'),
            ('YAML Files', '*yaml'),
            ('YML Files', '*yml'),
            ('CSV Files', '*csv')
        ]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            content = Content(filename=filename)
            if content.is_ready:
                self.set_title(title=filename)
                self.input_textarea.delete("1.0", "end")
                self.input_textarea.insert(tk.INSERT, content.data)
                self.radio_btn_var.set(content.filetype)

    def callback_help_documentation(self):
        """Callback for Menu Help > Getting Started."""
        self.browser.open_new_tab(Data.documentation_url)

    def callback_help_view_licenses(self):
        """Callback for Menu Help > View Licenses."""
        self.browser.open_new_tab(Data.license_url)

    def callback_help_about(self):
        """Callback for Menu Help > About"""

        about = tk.Toplevel(self.root)
        self.set_title(widget=about, title='About')
        width, height = 460, 460
        x, y = get_relative_center_location(self.root, width, height)
        about.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        about.resizable(False, False)

        top_frame = self.Frame(about)
        top_frame.pack(fill=tk.BOTH, expand=True)

        paned_window = self.PanedWindow(top_frame, orient=tk.VERTICAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=8, pady=12)

        # company
        frame = self.Frame(paned_window, width=450, height=20)
        paned_window.add(frame, weight=4)

        self.create_custom_label(
            frame, text=Data.main_app_text,
            increased_size=2, bold=True
        ).grid(row=0, column=0, columnspan=2, sticky=tk.W)

        # URL
        cell_frame = self.Frame(frame, width=450, height=5)
        cell_frame.grid(row=1, column=0, sticky=tk.W, columnspan=2)

        url = Data.repo_url
        self.Label(cell_frame, text='URL:').pack(side=tk.LEFT)

        self.create_custom_label(
            cell_frame, text=url, link=url
        ).pack(side=tk.LEFT)

        # dependencies
        self.create_custom_label(
            frame, text='Pypi.com Dependencies:', bold=True
        ).grid(row=2, column=0, sticky=tk.W)

        # compare_versions package
        self.create_custom_label(
            frame, text=Data.compare_versions_text,
            link=Data.compare_versions_link
        ).grid(row=3, column=0, padx=(20, 0), sticky=tk.W)

        # python-dateutil package
        self.create_custom_label(
            frame, text=Data.python_dateutil_text,
            link=Data.python_dateutil_link
        ).grid(row=4, column=0, padx=(20, 0), pady=(0, 10), sticky=tk.W)

        # PyYAML package
        self.create_custom_label(
            frame, text=Data.pyyaml_text,
            link=Data.pyyaml_link
        ).grid(row=3, column=1, padx=(20, 0), sticky=tk.W)

        # license textbox
        lframe = self.LabelFrame(
            paned_window, height=200, width=450,
            text=Data.license_name
        )
        paned_window.add(lframe, weight=7)

        width = 58 if self.is_macos else 51
        height = 18 if self.is_macos else 14 if self.is_linux else 15
        txtbox = self.TextArea(lframe, width=width, height=height, wrap='word')
        txtbox.grid(row=0, column=0, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(lframe, orient=tk.VERTICAL, command=txtbox.yview)
        scrollbar.grid(row=0, column=1, sticky='nsew')
        txtbox.config(yscrollcommand=scrollbar.set)
        txtbox.insert(tk.INSERT, Data.license)
        txtbox.config(state=tk.DISABLED)

        # footer - copyright
        frame = self.Frame(paned_window, width=450, height=20)
        paned_window.add(frame, weight=1)

        self.Label(frame, text=Data.copyright_text).pack(side=tk.LEFT, pady=(10, 10))

        self.create_custom_label(
            frame, text=Data.company, link=Data.company_url
        ).pack(side=tk.LEFT, pady=(10, 10))

        self.Label(frame, text='.  All right reserved.').pack(side=tk.LEFT, pady=(10, 10))

        set_modal_dialog(about)

    def build_menu(self):
        """Build menubar for dictlistlib."""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        file = tk.Menu(menu_bar)
        help_ = tk.Menu(menu_bar)

        menu_bar.add_cascade(menu=file, label='File')
        menu_bar.add_cascade(menu=help_, label='Help')

        file.add_command(label='Open', command=lambda: self.callback_file_open())
        file.add_separator()
        file.add_command(label='Quit', command=lambda: self.root.quit())

        help_.add_command(label='Documentation',
                          command=lambda: self.callback_help_documentation())
        help_.add_command(label='View Licenses',
                          command=lambda: self.callback_help_view_licenses())
        help_.add_separator()
        help_.add_command(label='About', command=lambda: self.callback_help_about())

    def build_frame(self):
        """Build layout for dictlistlib."""
        self.paned_window = self.PanedWindow(self.root, orient=tk.VERTICAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        self.text_frame = self.Frame(
            self.paned_window, width=600, height=400, relief=tk.RIDGE
        )
        self.entry_frame = self.Frame(
            self.paned_window, width=600, height=100, relief=tk.RIDGE
        )
        self.result_frame = self.Frame(
            self.paned_window, width=600, height=100, relief=tk.RIDGE
        )
        self.paned_window.add(self.text_frame, weight=7)
        self.paned_window.add(self.entry_frame)
        self.paned_window.add(self.result_frame, weight=2)

    def build_textarea(self):
        """Build input text for dictlistlib."""

        self.text_frame.rowconfigure(0, weight=1)
        self.text_frame.columnconfigure(0, weight=1)
        self.input_textarea = self.TextArea(self.text_frame, width=20, height=5, wrap='none')
        self.input_textarea.grid(row=0, column=0, sticky='nswe')
        vscrollbar = ttk.Scrollbar(
            self.text_frame, orient=tk.VERTICAL, command=self.input_textarea.yview
        )
        vscrollbar.grid(row=0, column=1, sticky='ns')
        hscrollbar = ttk.Scrollbar(
            self.text_frame, orient=tk.HORIZONTAL, command=self.input_textarea.xview
        )
        hscrollbar.grid(row=1, column=0, sticky='ew')
        self.input_textarea.config(
            yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set
        )

    def build_entry(self):
        """Build input entry for dictlistlib."""
        def callback_run_btn():
            data = self.input_textarea.get('1.0', 'end').strip()
            filetype = self.radio_btn_var.get()
            lookup = self.lookup_entry_var.get()
            select = self.select_entry_var.get()

            content = Content(data=data, filetype=filetype)
            if not content.is_ready:
                return

            try:
                result = content.query_obj.find(lookup=lookup, select=select)
                self.result = result
                self.result_textarea.delete("1.0", "end")
                self.result_textarea.insert(tk.INSERT, str(result))

            except Exception as exc:
                create_msgbox(title='Query Problem', error=Text(exc))

        def callback_tabular_btn():
            data = self.input_textarea.get('1.0', 'end').strip()
            filetype = self.radio_btn_var.get()
            lookup = self.lookup_entry_var.get()
            select = self.select_entry_var.get()

            content = Content(data=data, filetype=filetype)
            if not content.is_ready:
                return

            try:
                result = content.query_obj.find(lookup=lookup, select=select)
                self.result = result
                tabular_obj = Tabular(self.result)

                if tabular_obj.is_tabular:
                    text = tabular_obj.get()
                else:
                    fmt = 'CANNOT convert to tabular format because {!r}\n{}\n{}'
                    pretty_text = pformat(self.result)
                    text = fmt.format(tabular_obj.failure, '-' * 40, pretty_text)

                self.result_textarea.delete("1.0", "end")
                self.result_textarea.insert(tk.INSERT, str(text))

            except Exception as exc:
                create_msgbox(title='Query Problem', error=Text(exc))

        def callback_clear_text_btn():
            self.input_textarea.delete("1.0", "end")
            self.result_textarea.delete("1.0", "end")
            self.radio_btn_var.set(None)    # noqa
            self.lookup_entry_var.set('')
            self.select_entry_var.set('')
            self.result = None
            self.set_title()

        def callback_paste_text_btn():
            filetype = self.radio_btn_var.get()
            if filetype == 'None':
                title = 'Unselect CSV/JSON/YAML'
                message = 'Please select CSV, JSON, or YAML.'
                create_msgbox(title=title, warning=message)
                return

            try:
                data = self.root.clipboard_get()
                if data:
                    self.input_textarea.delete("1.0", "end")
                    # filetype = self.radio_btn_var.get()
                    self.content = Content(data=data, filetype=filetype)
                    if self.content.is_ready:
                        self.set_title(title='<<PASTE - Clipboard>>')
                        self.input_textarea.insert(tk.INSERT, data)
                        self.radio_btn_var.set(self.content.filetype)
            except Exception as _ex:        # noqa
                title = 'Empty Clipboard',
                message = 'CAN NOT paste because there is no data in pasteboard.'
                create_msgbox(title=title, warning=message)

        def callback_clear_lookup_entry():
            self.lookup_entry_var.set('')

        def callback_clear_select_entry():
            self.select_entry_var.set('')

        width = 70 if self.is_macos else 79 if self.is_linux else 107
        x1 = 2 if self.is_linux else 0

        # frame for row 0
        frame = self.Frame(self.entry_frame, width=600, height=30)
        frame.grid(row=0, column=0, padx=10, pady=(4, 0), sticky=tk.W)

        # radio buttons
        self.csv_radio_btn = self.RadioButton(
            frame, text='csv', variable=self.radio_btn_var,
            value='csv'
        )
        self.csv_radio_btn.pack(side=tk.LEFT)

        self.json_radio_btn = self.RadioButton(
            frame, text='json', variable=self.radio_btn_var,
            value='json'
        )
        self.json_radio_btn.pack(side=tk.LEFT, padx=(x1, 0))

        self.yaml_radio_btn = self.RadioButton(
            frame, text='yaml', variable=self.radio_btn_var,
            value='yaml'
        )
        self.yaml_radio_btn.pack(side=tk.LEFT, padx=(x1, 0))

        # open button
        open_file_btn = self.Button(frame, text='Open',
                                    command=self.callback_file_open)
        open_file_btn.pack(side=tk.LEFT, padx=(x1, 0))

        # paste button
        paste_text_btn = self.Button(frame, text='Paste',
                                     command=callback_paste_text_btn)
        paste_text_btn.pack(side=tk.LEFT, padx=(x1, 0))

        # clear button
        clear_text_btn = self.Button(frame, text='Clear',
                                     command=callback_clear_text_btn)
        clear_text_btn.pack(side=tk.LEFT, padx=(x1, 0))

        # run button
        run_btn = self.Button(frame, text='Run',
                              command=callback_run_btn)
        run_btn.pack(side=tk.LEFT, padx=(x1, 0))

        # pprint button
        tabular_btn = self.Button(frame, text='Tabular',
                                  command=callback_tabular_btn)
        tabular_btn.pack(side=tk.LEFT, padx=(x1, 0))

        # frame for row 1 & 2
        frame = ttk.Frame(self.entry_frame, width=600, height=30)
        frame.grid(row=1, column=0, padx=10, pady=(0, 4), sticky=tk.W)

        # lookup entry
        lbl = self.Label(frame, text='Lookup')
        lbl.grid(row=0, column=0, padx=(0, 4), pady=0, sticky=tk.W)
        lookup_entry = self.TextBox(frame, width=width,
                                    textvariable=self.lookup_entry_var)
        lookup_entry.grid(row=0, column=1, padx=0, pady=0, sticky=tk.W)
        lookup_entry.bind('<Return>', lambda event: callback_run_btn())

        # clear button
        clear_lookup_btn = self.Button(frame, text='Clear',
                                       command=callback_clear_lookup_entry)
        clear_lookup_btn.grid(row=0, column=2, padx=(x1, 0), pady=0, sticky=tk.W)

        # select statement entry
        lbl = self.Label(frame, text='Select')
        lbl.grid(row=1, column=0, padx=(0, 4), pady=0, sticky=tk.W)
        select_entry = self.TextBox(frame, width=width,
                                    textvariable=self.select_entry_var)
        select_entry.grid(row=1, column=1, padx=0, pady=0, sticky=tk.W)
        select_entry.bind('<Return>', lambda event: callback_run_btn())

        # clear button
        clear_select_btn = self.Button(frame, text='Clear',
                                       command=callback_clear_select_entry)
        clear_select_btn.grid(row=1, column=2, padx=(x1, 0), pady=0, sticky=tk.W)

    def build_result(self):
        """Build result text"""
        self.result_frame.rowconfigure(0, weight=1)
        self.result_frame.columnconfigure(0, weight=1)
        self.result_textarea = self.TextArea(
            self.result_frame, width=20, height=5, wrap='none'
        )
        self.result_textarea.grid(row=0, column=0, sticky='nswe')
        vscrollbar = ttk.Scrollbar(
            self.result_frame, orient=tk.VERTICAL,
            command=self.result_textarea.yview
        )
        vscrollbar.grid(row=0, column=1, sticky='ns')
        hscrollbar = ttk.Scrollbar(
            self.result_frame, orient=tk.HORIZONTAL,
            command=self.result_textarea.xview
        )
        hscrollbar.grid(row=1, column=0, sticky='ew')
        self.result_textarea.config(
            yscrollcommand=vscrollbar.set, xscrollcommand=hscrollbar.set
        )

    def run(self):
        """Launch dictlistlib."""
        self.root.mainloop()


def execute():
    """Launch dictlistlib."""
    app = Application()
    app.run()
