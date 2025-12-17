# Andrea Diamantini
# UDP GUI Client


import asyncio
import socket
import sys

import wx
import wxasync


class ChatWindow(wx.Frame):
    def __init__(self, name, clientAddress, serverAddress):
        super().__init__(None, title="Async UDP Client Chat")

        # member variables
        self.name = name
        self.clientAddress = clientAddress
        self.serverAddress = serverAddress

        # The NETWORK SOCKET async part --------
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind(clientAddress)
        self.udp_socket.setblocking(False)

        self.loop = asyncio.get_running_loop()

        self.udp_socket.sendto(("CONNECT " + self.name).encode(), self.serverAddress)

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

        # And now start receiving...
        wxasync.StartCoroutine(self.recvMessage, self)

    async def sendMessage(self, evt):
        msg = self.tc1.Value.strip()

        if msg:
            # Send it!
            self.udp_socket.sendto(msg.encode(), self.serverAddress)
            self.msgList.Append(f"[IO] {msg}")

        self.tc1.Clear()
        return

    async def recvMessage(self):
        while True:
            data = await self.loop.sock_recv(self.udp_socket, 1024)
            msg = data.decode()
            self.msgList.Append(msg)

        return


# ---------------------------------------------------------------------------------


async def runGuiClient(server_port):
    # THE App...
    app = wxasync.WxAsyncApp()

    diag1 = wx.TextEntryDialog(None, "Server host or IP: ")
    if diag1.ShowModal() != wx.ID_OK:
        sys.exit(0)
    server_host = diag1.GetValue()

    diag2 = wx.TextEntryDialog(None, "Set Name: ")
    if diag2.ShowModal() != wx.ID_OK:
        sys.exit(0)
    name = diag2.GetValue()

    serverAddress = (server_host, server_port)

    # client address
    import random

    client_host = socket.gethostname()
    client_ip = socket.gethostbyname(client_host)
    client_port = random.randint(22223, 55555)
    clientAddress = (client_ip, client_port)

    window = ChatWindow(name, clientAddress, serverAddress)
    window.Show()

    app.SetTopWindow(window)
    await app.MainLoop()


# ---------------------------------------------------------------------------------

if __name__ == "__main__":
    server_port = 22222

    try:
        asyncio.run(runGuiClient(server_port))

    # close on CTRL + C
    except KeyboardInterrupt:
        print("[INFO] Closing GUI client")
