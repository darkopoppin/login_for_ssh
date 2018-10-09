import curses
from curses.textpad import Textbox, rectangle
from pexpect import pxssh
import subprocess
import re

class LoginPage (object):
    

    def __init__(self):
        self.init_curse()
        self.PAD_HEIGHT, self.PAD_WIDTH = self.stdscr.getmaxyx()
        self.inputs = [None, None]
        self.login = True

    def run(self):
        self.create_pad()
        boxes, input_box = self.text_box() 
        while self.login == False or self.inputs[0] == None or self.inputs[1] == None:
            inputs = self.select(boxes, input_box)
            self.pad.refresh(0,0, 0,0, self.PAD_HEIGHT, self.PAD_WIDTH)

    def init_curse(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.stdscr.refresh()

    def create_pad(self):
        self.pad = curses.newpad(self.PAD_HEIGHT,self.PAD_WIDTH)
        self.pad.box()

    def text_box(self):
        boxes = []
        input_box = []
        height = self.PAD_HEIGHT//2
        width = self.PAD_WIDTH//2

        #Text above the boxes
        self.pad.addstr(height-7, width-11, 'Username:')
        self.pad.addstr(height-2, width-11, 'Password:')

        for x in range(1,-1,-1):#Creates the boxes for input
            boxes.append(self.pad.derwin(1,20, height-x*5, width-10))
            input_box.append(curses.newwin(1,20, height-x*5, width-10))
            #rectangle(self.win, height-1-x*5,width-11, height+1-x*5, width+11)

        #Log in button
        button = self.pad.derwin(3,10, height+3, width-5)
        button.box()
        button.addstr(1,2,'Log in')
        boxes.append(button)
        
    
        return boxes, input_box
    
    def select(self, boxes, input_box=None):
        selected = 0
        last = 1
        while True:
            boxes[selected].bkgd(curses.color_pair(1))
            boxes[last].bkgd(curses.color_pair(2))
            self.pad.refresh(0,0, 0,0, self.PAD_HEIGHT, self.PAD_WIDTH)

            c = self.stdscr.getch()
            if c == curses.KEY_DOWN:
                last = selected
                if selected == len(boxes)-1:
                    selected = 0
                else:
                    selected += 1
            elif c == curses.KEY_UP:
                last = selected
                if selected == 0:
                    selected = len(boxes)-1
                else:
                    selected -= 1
            elif c == 10 and boxes.index(boxes[selected]) == 2 and self.login == False:
                boxes[2].bkgd(curses.color_pair(2))
                self.login = True
                break
            elif c == 10:
                if self.login == False:#enables input mode on the login page
					if selected == 1:
						curses.echo()
                    input_box[selected].refresh()
                    box = Textbox(input_box[selected])
                    text = box.edit()
                    self.inputs[selected] = text[:-1]
                    boxes[selected].addstr(0,0, self.inputs[selected])
					curses.noecho()
                else:#returns the directory that we want to go to
                    return selected
            elif c == ord('q'):
                break
        return
           
    def end_curses(self):
        curses.echo()
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.endwin()

class FileExplorer(LoginPage):
    
    def __init__(self,s):
        super().__init__()
        self.s = s
        self.create_pad()
        self.login = True

    def run(self):
        self.moving()
        self.pad.refresh(0,0, 0,0, self.PAD_HEIGHT, self.PAD_WIDTH)
        self.stdscr.getch()
        self.end_curses()
        self.s.logout()
    
    def moving(self):
        i = 0
        direc = None
        while True:
            files = self.list_files(direc)
            self.pad.addstr(10,10,''.join(files))
            self.pad.refresh(0,0, 0,0, self.PAD_HEIGHT, self.PAD_WIDTH)
            widgets = self.widgets(files,i)
            direc_index = self.select(widgets)
            direc = files[direc_index]
            i += 1

    def list_files(self, direc=None):
        if direc != None:
            self.s.sendline('cd ' + direc)
            self.s.prompt
        self.s.sendline('ls')
        self.s.prompt()
        output_list = self.s.before.decode().split()
        output_str = ''.join(output_list)
        regex = re.compile(r'm[a-z.A-Z]*')
        files = [match.lstrip('m') for match in re.findall(regex, output_str) if len(match) > 1]
        return files
    
    def widgets(self, files,i):
        widgets=[]
        for f in files:
            widget = self.pad.derwin(1,len(f)+1, int(files.index(f))+1,i*10)
            widget.addstr(f)
            widgets.append(widget)
        return widgets

def main():
    login = LoginPage()
    login.run()
    s = pxssh.pxssh()
    ssh = s.login("127.0.0.1",  'sabahob2', 'zrritlct')
    files = FileExplorer(s)
    files.run()

if __name__ == '__main__':
    main()
