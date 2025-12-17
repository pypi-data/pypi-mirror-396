# Andrea Diamantini
# TCP GUI Client

import asyncio
import socket
import sys

import wx
import wxasync


class TCPChatWindow(wx.Frame):
    def __init__(self, name, serverAddress):
        super().__init__(None, title="Async TCP Client Chat")

        # member variables
        self.name = name
        self.serverAddress = serverAddress

        # The NETWORK SOCKET async part --------
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setblocking(False)

        self.loop = asyncio.get_running_loop()

        # The GUI part -------------------------
        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        self.msgList = wx.ListBox(panel)
        hbox1.Add(self.msgList, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)
        vbox.Add(hbox1, proportion=1, flag=wx.ALL | wx.EXPAND, border=5)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        self.tc1 = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER)
        sendButton = wx.Button(panel, label="SEND")

        # AsyncBind (instead of usual Bind)
        wxasync.AsyncBind(wx.EVT_TEXT_ENTER, self.sendMessage, self.tc1)
        wxasync.AsyncBind(wx.EVT_BUTTON, self.sendMessage, sendButton)

        hbox2.Add(self.tc1, proportion=1, flag=wx.ALL, border=5)
        hbox2.Add(sendButton, proportion=0, flag=wx.ALL, border=5)
        vbox.Add(hbox2, proportion=0, flag=wx.ALL | wx.EXPAND, border=5)

        self.SetMinSize((200, 300))
        panel.SetSizer(vbox)
        self.Centre()

        # Start Connection!
        wxasync.StartCoroutine(self.manageConnection, self)

    async def manageConnection(self):
        await self.loop.sock_connect(self.tcp_socket, self.serverAddress)
        print(f"[INFO] Connected to {self.serverAddress}...")

        # async execution
        wxasync.StartCoroutine(self.recvMessage, self)

    async def sendMessage(self, evt):
        msg = self.tc1.Value.strip()

        if msg:
            # Send message
            sendMsg = self.name + ": " + msg
            self.tcp_socket.sendall(sendMsg.encode())
            self.msgList.Append(f"[ME] {msg}")

        self.tc1.Clear()
        return

    async def recvMessage(self):
        print("receiving data...")
        while True:
            data = await self.loop.sock_recv(self.tcp_socket, 1024)
            msg = data.decode()
            self.msgList.Append(msg)

        print("NO MORE receiving...")
        return


# ---------------------------------------------------------------------------------


async def runGuiClient(server_port):
    # THE App...
    app = wxasync.WxAsyncApp()

    # user name
    diag1 = wx.TextEntryDialog(None, "Name: ")
    if diag1.ShowModal() != wx.ID_OK:
        sys.exit(0)

    name = diag1.GetValue()

    # host choice
    diag2 = wx.TextEntryDialog(None, "Server PC Name or IP address: ")
    if diag2.ShowModal() != wx.ID_OK:
        sys.exit(0)

    host = diag2.GetValue()
    s_addr = (host, server_port)

    # The Main Window
    window = TCPChatWindow(name, s_addr)
    window.Show()

    app.SetTopWindow(window)
    await app.MainLoop()


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    server_port = 33333

    try:
        asyncio.run(runGuiClient(server_port))

    # Close on CTRL + C
    except KeyboardInterrupt:
        print("[INFO] Closing GUI client")
