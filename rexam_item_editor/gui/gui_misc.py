import PySimpleGUI as sg

from .. import consts
from ..rexam.git_info import GitInfo


class GUIBaseDirectory(object):

    def __init__(self, database_folder, label="Base Directory",
                 size=(60, 1), key="change_directory"):

        self.label = label
        self.text = sg.Text(database_folder, size=size,
                                background_color=consts.COLOR_BKG_ACTIVE_INFO)
        self.frame = sg.Frame(title=label, layout=[[self.text,
                      sg.Button("change", size=(6, 1), key=key)]], border_width=2)

    def update_folder(self, folder):
        self.text.update(value=folder)
        txt = self.label
        head = GitInfo(folder).head
        if len(head):
            txt += ": git head {}".format(head[:7])
        self.frame.update(value=txt)
