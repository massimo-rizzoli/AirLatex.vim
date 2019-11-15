import pynvim
import sys
from airlatex.sidebar import SideBar
from airlatex.session import AirLatexSession
from airlatex.documentbuffer import DocumentBuffer
from threading import Thread

@pynvim.plugin
class AirLatex:
    def __init__(self, nvim):
        self.nvim = nvim
        self.servername = self.nvim.eval("v:servername")
        self.sidebar = False
        self.session = False

    @pynvim.command('AirLatex', nargs=0, sync=True)
    def openSidebar(self):
        if not self.sidebar:
            self.sidebar = SideBar(self.nvim, self)
            self.sidebar.initGUI()
        else:
            self.sidebar.initGUI()

        # ensure session to exist
        if not self.session:
            DOMAIN = self.nvim.eval("g:airlatex_domain")
            def initSession(self):
                nvim = pynvim.attach("socket",path=self.servername)
                try:
                    self.session = AirLatexSession(DOMAIN, self.servername, self.sidebar)
                    self.session.login(nvim)
                except Exception as e:
                    nvim.out_write(str(e)+"\n")
            self.session_thread = Thread(target=initSession,args=(self,), daemon=True)
            self.session_thread.start()

    @pynvim.function('AirLatex_SidebarRefresh', sync=False)
    def sidebarRefresh(self, args):
        self.sidebar.triggerRefresh()

    @pynvim.function('AirLatex_SidebarUpdateStatus', sync=True)
    def sidebarStatus(self, args):
        self.sidebar.updateStatus()

    @pynvim.function('AirLatex_ProjectEnter', sync=True)
    def projectEnter(self, args):
        self.sidebar.cursorAction()

    # @pynvim.command('AirLatex_UpdatePos', nargs=0, sync=True)
    # def projectEnter(self):
    #     plugin.updateProject()

    @pynvim.function('AirLatex_Close', sync=True)
    def sidebarClose(self, args):
        self.sidebar.cleanup()
        self.sidebar = None

    @pynvim.function('AirLatex_WriteBuffer', sync=True)
    def writeBuffer(self, args):
        buffer = self.nvim.current.buffer
        if buffer in DocumentBuffer.allBuffers:
            DocumentBuffer.allBuffers[buffer].writeBuffer()


