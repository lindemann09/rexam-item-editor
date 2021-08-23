from os import getcwd, path
from math import floor
import PySimpleGUI as sg
from markdown import markdown

from .. import __version__, APPNAME, consts
from .json_settings import JSONSettings
from .dialogs import top_label, ask_save
from ..rexam import exam

sg.theme_add_new("mytheme", consts.SG_COLOR_THEME)
sg.theme("mytheme")


class ExamCompiler(object):
    SHOW_HASHES = True

    def __init__(self, settings=None):

        if not isinstance(settings, JSONSettings):
            self.settings = JSONSettings(
                         appname=APPNAME.replace(" ", "_").lower(),
                         settings_file_name="settings.json",
                         defaults= {"recent_dirs": []},
                         reset=False)
        else:
            self.settings = settings

        self.exam = exam.Exam()
        self.exam.item_database_folder = getcwd()

        self.txt_base_directory = sg.Text(self.exam.item_database_folder, size=(60, 1),
                                          background_color=consts.COLOR_BKG_ACTIVE_INFO)
        self.it_exam = sg.InputText("", size=(20, 1),
                                    enable_events=True,
                                    background_color=consts.COLOR_BKG_ACTIVE_INFO,
                                    key="change_name")

        self.gui_db = GUIItemTable(show_l2=False,
                                   n_row=8,
                                   show_hash=False,
                                   short_hashes=True,
                                   key='database',
                                   tooltip='Item Database')
        self.gui_exam = GUIItemTable(show_l2=self.gui_db.show_l2,
                                     n_row=8,
                                     show_hash=False,
                                     short_hashes=self.gui_db.short_hashes,
                                     key='exam',
                                     tooltip='Exam Items')
        self.cb_language2 = sg.Checkbox('Second language', key="cb_l2", enable_events=True)

        self.layout = [
            [top_label([self.txt_base_directory,
                        sg.Button("change", size=(6, 1),
                                  key="change_directory")],
                       label="Database Directory", border_width=2),
             top_label([self.it_exam,
                        sg.Button("save", size=(12, 1), key="save_exam"),
                        sg.Button("load", size=(4, 1), key="load_exam"),
                        sg.Button("new", size=(4, 1), key="load_exam")
                        ],
                        label="Exam", border_width=2),
             self.cb_language2
             ],
            [top_label([self.gui_db.table, self.gui_db.multiline], label="Database",  border_width=2)],
            [
             sg.Button("add", size=(30, 2),
                       button_color= consts.COLOR_GREEN_BTN,
                       key="add_to_exam"),
            sg.Button("remove", size=(30, 2),
                      button_color=consts.COLOR_RED_BTN,
                      key="remove_from_exam"),
            sg.Button("up", size=(10, 2), key="move_up"),
            sg.Button("down", size=(10, 2), key="move_down")
            ],
            [sg.Frame("Exam", layout=[[self.gui_exam.table, self.gui_exam.multiline]])]
        ]

        self._selected_row_tab_db = None
        self.generate_html = True # TODO in gui


    @property
    def exam_file(self):
        return self.it_exam.get()

    @exam_file.setter
    def exam_file(self, v):
        self.it_exam.update(value=v)

    def _tmp_html_file(self):
        flname = self.exam_file.replace(".json", "")
        if len(flname):
            return path.abspath(flname) + ".tmp.html"
        else:
            return ""

    def update_tables(self, exam_tab_select_row=None):
        """table with item_id, name, short question l1 ,
           short question l2"""

        self.txt_base_directory.update(value=self.exam.item_database_folder)
        # exam
        if self.exam.item_db is not None:
            db_ids = self.exam.get_database_ids(rm_nones=False)
        else:
            db_ids = []

        tmp = []
        for quest, idx in zip(self.exam.questions, db_ids):

            if idx is None:
                tmp.append(exam.EntryNotFound(quest, use_l2=True))
            else:
                tmp.append(self.exam.item_db.entries[idx])
        self.gui_exam.set_items(items=tmp)
        if exam_tab_select_row is not None:
            self.gui_exam.set_selected(exam_tab_select_row)

        # markdown and html
        md = self.exam.markdown(use_l2=self.gui_exam.show_l2)
        self.gui_exam.multiline.update(value=md)

        # save to .tmp.md file
        if self.generate_html:
            flname = self._tmp_html_file()
            if len(flname):
                with open(flname, "w", encoding=consts.FILE_ENCODING) as fl:
                    fl.write(markdown(md))

        # not in exam --> show in database
        if self.exam.item_db is not None:
            tmp = [x for x in self.exam.item_db.selected_entries \
                                if x.id not in db_ids]
        else:
            tmp = []
        self.gui_db.set_items(items=tmp)

    @property
    def selected_db_row(self):
        return self._selected_row_tab_db

    @selected_db_row.setter
    def selected_db_row(self, v):
        if v != self._selected_row_tab_db:
            self._selected_row_tab_db = v
            if v is not None:
                cnt_selected = self.gui_db.get_row(v)[0]
                tmp = self.exam.item_db.entries[cnt_selected]

                if self.gui_db.show_l2:
                    tmp = tmp.item_l2
                else:
                    tmp = tmp.item_l1

                txt = "File {}\nHash {}\n\n".format(tmp.full_path, tmp.hash())
                txt += str(tmp)
                self.gui_db.multiline.update(value=txt)

    def load_exam(self, json_filename):
        self.save_exam(ask=True)
        try:
            self.exam.load(json_filename)
        except Exception as e:
            return e

        print(self.exam.item_db)
        self.exam_file = json_filename
        self.update_tables()
        return True

    def save_exam(self, ask=True):
        if len(self.exam_file)>0 and exam.Exam(self.exam.json_filename).as_dict_list() != self.exam.as_dict_list():
            # changes
            if ask: # something has changed
                if not ask_save(item_name=self.exam.json_filename):
                    return
            self.exam.save(self.exam_file)

    def reset_gui(self):
        self.update_tables()

    def run(self):

        win = sg.Window("{} ({})".format("Exam Compiler", __version__),
                        self.layout, finalize=True,
                        return_keyboard_events=True,
                        enable_close_attempted_event=True)

        self.reset_gui()
        self.load_exam("demo.json") #FIXME

        while True:
            win.refresh()
            event, values = win.read(timeout=5000)

            if event == sg.WINDOW_CLOSE_ATTEMPTED_EVENT or \
                    event == "Close" or event is None:
                self.save_exam(ask=True)
                break

            elif event == "change_directory":
                fld = sg.PopupGetFolder(message="", no_window=True)
                if len(fld):
                    self.exam.item_database_folder = fld
                self.reset_gui()

            elif event=="save_exam":
                self.save_exam(ask=False)

            elif event=="load_exam":
                pass # TODO

            elif event=="new_exam":
                pass # TODO

            elif event==self.gui_db.key_tab:

                try:
                    self.selected_db_row = values[event][0]
                except:
                    old = self.selected_db_row
                    self.selected_db_row = None
                    self.gui_db.set_selected(old)

            #elif event==self.gui_exam.key_tab:
            #    selected_entry = self.gui_exam.get_row()
            #    #TODO

            elif event == "cb_l2":
                self.gui_db.show_l2 = values[event]
                self.gui_exam.show_l2 = values[event]
                self.update_tables()

            elif event=="add_to_exam":
                try:
                    selected_entry = self.gui_db.get_row(values[self.gui_db.key_tab][0])
                except:
                    continue # nothing selected
                self.add_to_exam(selected_entry[0])

            elif event=="remove_from_exam":
                try:
                    selected_entry = self.gui_exam.get_row(values[self.gui_exam.key_tab][0])
                except:
                    continue # nothing selected
                self.remove_from_exam(selected_entry[0])

            elif event=="move_up":
                try:
                    selected_entry = values[self.gui_exam.key_tab][0]
                except:
                    continue # nothing selected
                self.exam.replace(selected_entry, selected_entry-1)
                self.update_tables(exam_tab_select_row=selected_entry - 1)

            elif event=="move_down":
                try:
                    selected_entry = values[self.gui_exam.key_tab][0]
                except:
                    continue # nothing selected
                self.exam.replace(selected_entry, selected_entry+1)
                self.update_tables(exam_tab_select_row=selected_entry + 1)

            elif event=="change_name":
                pass #' TODO'

            else:
                pass#   print(event)

        win.close()
        self.settings.save()

    def add_to_exam(self, selected_entry):
        item = self.exam.item_db.entries[selected_entry]
        self.exam.add_database_item(item)
        self.update_tables()

    def remove_from_exam(self, selected_entry):
        item = self.exam.item_db.entries[selected_entry]
        self.exam.remove_item(item)
        self.update_tables()


class GUIItemTable(object):
    LANGUAGES = ("Dutch", "English")

    def __init__(self, n_row, key, tooltip, max_lines = 1, font='Courier', font_size = 10,
                 show_l2 = False, show_hash=True, short_hashes=True):
        self.max_lines = max_lines
        self.show_hash = show_hash
        self.short_hashes = short_hashes
        self.show_l2 = show_l2
        headings, width = self.get_headings()
        row_height = 30
        self.key_tab = key+"_tab"

        self.table = sg.Table(values=[[""] * len(headings)],
                              col_widths=width,
                              headings=[str(x) for x in range(len(headings))],
                              max_col_width=500,
                              background_color='white',
                              auto_size_columns=False,
                              display_row_numbers=False,
                              select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                              justification='left',
                              num_rows=n_row,
                              enable_events=True,
                              bind_return_key=True,
                              # alternating_row_color='lightyellow',
                              key=self.key_tab,
                              row_height=row_height,
                              font='{} {}'.format(font, font_size),
                              vertical_scroll_only=False,
                              tooltip=tooltip)
        h = floor(row_height * n_row/(1.4*font_size))
        self.multiline = sg.Multiline(size=(80, h),  font='{} {}'.format(font, font_size),)


    def update_headings(self):
        w = self.table.Widget
        if w is not None:
            for idx, txt in zip(self.table.ColumnHeadings, self.get_headings()[0]):
                w.heading(idx, text=txt)

    def get_headings(self):
        headings = ["Cnt", "Name",
                    GUIItemTable.LANGUAGES[int(self.show_l2)]]
        width = [5, 10, 70]
        if self.show_hash:
            headings.append("Hash")
            width.append(10)
        return headings, width

    def get_row(self, row_num):
        return self.table.get()[row_num]

    def set_items(self, items):
        values = []
        for x in items:
            d = [x.id]
            d.extend(x.short_repr(self.max_lines,
                                  use_l2=self.show_l2,
                                  add_versions=self.show_hash,
                                  short_version=self.short_hashes)) # TODO short hashes
            values.append(d)
        self.table.update(values=values)
        self.update_headings()

    def set_selected(self, selected):
        if not isinstance(selected, (list, tuple)):
            selected = [selected]
        self.table.update(select_rows=selected)
