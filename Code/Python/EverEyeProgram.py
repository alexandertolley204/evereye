import csv
import mysql.connector
import serial
import tkinter
import zmq
import tkcalendar
import datetime
from PIL import Image, ImageTk
import pathlib

class databaseConnection():
    def connectToDatabase():
        try:
            database = mysql.connector.connect(
                host="localhost",
                user = "", #Database User
                password = "", #Database Password
                database="evereye"
            )
        except mysql.connector.Error as err:
            exit("Cannot connect to Database" + str(err))
        return database

    def createCursor(database):
        cursor = database.cursor(buffered = True)
        return cursor

    def disconnectFromDatabase(database, cursor):
        cursor.close()
        database.commit()
        database.close()

class everEyeApp(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.title('EverEye')
        self.geometry('500x300')
        self.resizable(False, False)
        self._frame = None
        self.switchFrame(logInPage)
        self.editUserFullName = tkinter.StringVar()
        self.editFlag = 0
        self.deleteFlag = 0
        self.logFlag = 0
        self.logSelectData = tkinter.StringVar()

    def switchFrame(self, frameClass):
        newFrame = frameClass(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = newFrame
        self._frame.pack()

    def establishSerialConnection(self):
        self.serialDevice = serial.Serial(
            port = 'COM5',
            baudrate = 9600
        )

    def disconnectSerialConnection(self):
        self.serialDevice.close()
    
    def establishSocketConnection(self):
        self.context1 = zmq.Context()
        self.socket1 = self.context1.socket(zmq.REQ)
        self.socket1.connect("tcp://localhost:5555")
        self.context2 = zmq.Context()
        self.socket2 = self.context2.socket(zmq.REQ)
        self.socket2.connect("tcp://localhost:5556")
        
    def serialCommand(self, command):
        self.serialDevice.write(bytes(command, 'utf-8'))
        self.serialData = self.serialDevice.readline()
        self.cleanSerialData = str(self.serialData.strip())
        for self.serialCharacter in 'b\'':
            self.cleanSerialData = str.replace(
                self.cleanSerialData,
                self.serialCharacter,
                ''
            )
        return self.cleanSerialData

    def socketCommunication(self, command, socketNumber):
        if socketNumber == 1:
            self.socket1.send_string(command)
            self.socketData = str(self.socket1.recv())
        if socketNumber == 2:
            self.socket2.send_string(command)
            self.socketData = str(self.socket2.recv())
        for self.serialCharacter in 'b\'':
            self.socketData = str.replace(
                self.socketData,
                self.serialCharacter,
                ''
            )
        return self.socketData

    def setEditFlag(self, flag):
        self.editFlag = flag

    def setDeleteFlag(self, flag):
        self.deleteFlag = flag

class logInPage(tkinter.Frame):
    def __init__(self, master):
        tkinter.Frame.__init__(
            self,
            master,
            height = 300,
            width = 500
        )
        self.master = master
        self.password = tkinter.StringVar()

        self.master.bind("<Return>", self.passwordCheck)
        self.mainLogo()
        self.passwordEntry()
        self.passwordSubmit()
        self.acknowledgement()

    def mainLogo(self):
        self.logo = tkinter.Label(
            text = "EverEye",
            font = ("Bahnschrift SemiBold SemiConden", 32),
            foreground = 'Red'
        )
        self.logo.place(
            x = 173,
            y = 25
        )

    def acknowledgement(self):
        self.madeBy = tkinter.Label(
            text = "Made by A.J. Tolley\nIcons created by Freepik - Flaticon\nhttps://www.flaticon.com/authors/freepik"
        )
        self.madeBy.place(
            x = 135,
            y = 240
        )

    def passwordCheck(self, event):
        self.master.unbind("<Return>")
        if self.password.get() == "Dolphins":
            self.master.switchFrame(mainMenu)
        else:
            self.wrongPasswordWindow = tkinter.Toplevel(self)
            self.wrongPasswordWindow.geometry('250x100')
            self.wrongPasswordWindow.title("Error")
            self.wrongPasswordWindow.grab_set()

            self.wrongPasswordWindowLabel = tkinter.Label(
                self.wrongPasswordWindow,
                text = "Incorrect Password",
                font = ('Helvetica', 12)
            )
            self.wrongPasswordWindowLabel.pack(
                ipady = 10
            )

            self.wrongPasswordWindowButton = tkinter.Button(
                self.wrongPasswordWindow,
                text = "Confirm",
                width = 10,
                height = 1
            )
            self.wrongPasswordWindowButton.pack()
            self.wrongPasswordWindowButton['command'] = lambda: [
                self.wrongPasswordWindow.destroy(),
                self.master.bind("<Return>", self.passwordCheck),
                self.passwordEntryBox.delete(
                    0,
                    tkinter.END
                )
            ]

    def passwordEntry(self):
        self.passwordLabel = tkinter.Label(
            self,
            text = "Password",
            font = ("Helvetica", 10)
        )
        self.passwordLabel.place(
            x = 210,
            y = 100
        )
        self.passwordEntryBox = tkinter.Entry(
            self,
            textvariable = self.password,
            show = "*"
        )
        self.passwordEntryBox.place(
            x = 180,
            y = 120
        )
        self.passwordEntryBox.focus()

    def passwordSubmit(self):
        self.submitButton = tkinter.Button(
            self,
            text = "Submit",
            width = 10,
            height = 2
        )
        self.submitButton.place(
            x = 200,
            y = 150
        )
        self.submitButton['command'] = lambda: self.passwordCheck(None)

class mainMenu(tkinter.Frame):
    def __init__(self, master):
        tkinter.Frame.__init__(
            self,
            master,
            height = 300,
            width = 500
        )
        self.master = master

        self.getPath()
        self.menuButtons()
        self.logPeek()

    def getPath(self):
        self.currentDirectory = pathlib.Path(__file__).parents[2]
        self.iconDirectory = self.currentDirectory / 'Icons'

    def createUser(self):
        self.createIconPath = self.iconDirectory / 'add-user.png'
        self.createRawIcon = Image.open(self.createIconPath)
        self.createResizedIcon = self.createRawIcon.resize((25, 25))
        self.createRawIcon.close()
        self.createUserIcon  = ImageTk.PhotoImage(self.createResizedIcon)
        self.createResizedIcon.close()
        self.createUserButton = tkinter.Button(
            self,
            image = self.createUserIcon,
            text = "Create User",
            compound = tkinter.LEFT,
            width = 100,
            height = 40
        )
        self.createUserButton.place(
            x = 80,
            y = 150
        )
        self.createUserButton['command'] = lambda: [
            self.master.setEditFlag(0),
            self.master.switchFrame(createAndEditUser)
        ]

    def editUser(self):
        self.editIconPath = self.iconDirectory / 'designer.png'
        self.editRawIcon = Image.open(self.editIconPath)
        self.editResizedIcon = self.editRawIcon.resize((25, 25))
        self.editRawIcon.close()
        self.editUserIcon = ImageTk.PhotoImage(self.editResizedIcon)
        self.editResizedIcon.close()
        self.editUserButton = tkinter.Button(
            self,
            image = self.editUserIcon,
            text = "Edit User",
            compound = tkinter.LEFT,
            width = 100,
            height = 40
        )
        self.editUserButton.place(
            x = 200,
            y = 150
        )
        self.editUserButton['command'] = lambda: [
            self.master.setDeleteFlag(0),
            self.master.switchFrame(selectUser)
        ]

    def deleteUser(self):
        self.deleteIconPath = self.iconDirectory / 'remove-user.png'
        self.deleteRawIcon = Image.open(self.deleteIconPath)
        self.deleteResizedIcon = self.deleteRawIcon.resize((25, 25))
        self.deleteRawIcon.close()
        self.deleteUserIcon = ImageTk.PhotoImage(self.deleteResizedIcon)
        self.deleteResizedIcon.close()
        self.deleteUserButton = tkinter.Button(
            self,
            image = self.deleteUserIcon,
            text = "Delete User",
            compound = tkinter.LEFT,
            width = 100, 
            height = 40
        )
        self.deleteUserButton.place(
            x = 320,
            y = 150
        )
        self.deleteUserButton['command'] = lambda: [
            self.master.setDeleteFlag(1),
            self.master.switchFrame(selectUser)
        ]

    def accessLogs(self):
        self.logsIconPath = self.iconDirectory / 'file.png'
        self.logsRawIcon = Image.open(self.logsIconPath)
        self.logsResizeIcon = self.logsRawIcon.resize((25, 25))
        self.logsRawIcon.close()
        self.accessLogsIcon = ImageTk.PhotoImage(self.logsResizeIcon)
        self.logsResizeIcon.close()
        self.accessLogsButton = tkinter.Button(
            self,
            image = self.accessLogsIcon,
            text="Access Logs",
            compound = tkinter.LEFT,
            width = 100,
            height = 40
        )
        self.accessLogsButton.place(
            x = 80,
            y = 220
        )
        self.accessLogsButton['command'] = lambda: self.master.switchFrame(accessLogs)

    def openLock(self):
        self.lockIconPath = self.iconDirectory / 'open-lock.png'
        self.lockRawIcon = Image.open(self.lockIconPath)
        self.lockResizeIcon = self.lockRawIcon.resize((25, 25))
        self.lockRawIcon.close()
        self.openLockIcon = ImageTk.PhotoImage(self.lockResizeIcon)
        self.lockResizeIcon.close()
        self.openLockButton = tkinter.Button(
            self,
            image = self.openLockIcon,
            text = "Open Lock",
            compound = tkinter.LEFT,
            width = 100,
            height = 40
        )
        self.openLockButton.place(
            x = 200,
            y = 220
        )
        self.openLockButton['command'] = lambda: self.master.switchFrame(openLock)

    def logOff(self):
        self.exitIconPath = self.iconDirectory / 'exit.png'
        self.exitRawIcon = Image.open(self.exitIconPath)
        self.exitResizeIcon = self.exitRawIcon.resize((25, 25))
        self.exitRawIcon.close()
        self.logOffIcon = ImageTk.PhotoImage(self.exitResizeIcon)
        self.exitResizeIcon.close()
        self.logOffButton = tkinter.Button(
            self,
            image = self.logOffIcon,
            text = "Log Off",
            compound = tkinter.LEFT,
            width = 100,
            height = 40
        )
        self.logOffButton.place(
            x = 320,
            y = 220
        )
        self.logOffButton['command'] = lambda: self.master.switchFrame(logInPage)

    def menuButtons(self):
        self.createUser()
        self.editUser()
        self.deleteUser()
        self.accessLogs()
        self.openLock()
        self.logOff()
    
    def logPeek(self):
        self.logTable = tkinter.ttk.Treeview(
            self,
            height = 5,
            selectmode = 'none'
        )
        self.logTable.place(
            x = 25,
            y = 10
        )
        self.logTable['columns'] = (
            'id',
            'name',
            'date',
            'time',
            'lock',
            'valid'
        )

        style = tkinter.ttk.Style()
        style.configure(
            "Treeview.Heading",
            font = ('TKDefaultFont', 9)
        )
        style.configure(
            "Treeview",
            font = ('TKDefaultFont', 9)
        )

        self.logTable.column(
            "#0",
            width = 0,
            stretch = tkinter.NO
        )
        self.logTable.column(
            "id",
            anchor = tkinter.CENTER,
            width = 60
        )
        self.logTable.column(
            "name",
            anchor = tkinter.CENTER,
            width = 130
        )
        self.logTable.column(
            "date",
            anchor = tkinter.CENTER,
            width = 80
        )
        self.logTable.column(
            "time",
            anchor = tkinter.CENTER,
            width = 60
        )
        self.logTable.column(
            "lock",
            anchor = tkinter.CENTER,
            width = 70
        )
        self.logTable.column(
            "valid",
            anchor = tkinter.CENTER,
            width = 50
        )

        self.logTable.heading(
            "#0",
            text = "",
            anchor = tkinter.CENTER
        )
        self.logTable.heading(
            "id",
            text = "Log ID",
            anchor = tkinter.CENTER
        )
        self.logTable.heading(
            "name",
            text = "Name",
            anchor = tkinter.CENTER
        )
        self.logTable.heading(
            "date",
            text = "Date",
            anchor = tkinter.CENTER
        )
        self.logTable.heading(
            "time",
            text = "Time",
            anchor = tkinter.CENTER
        )
        self.logTable.heading(
            "lock",
            text = "Lock",
            anchor = tkinter.CENTER
        )
        self.logTable.heading(
            "valid",
            text = "Valid",
            anchor = tkinter.CENTER
        )

        self.logDatabase = databaseConnection.connectToDatabase()
        self.logCursor = databaseConnection.createCursor(self.logDatabase)
        self.logQuery = "SELECT * FROM logview WHERE logID > (SELECT COUNT(*) FROM logview) - 5 ORDER BY logID DESC;"
        try:
            self.logCursor.execute(self.logQuery)
            logResult = self.logCursor.fetchall()
            self.tableID = 0
            for x in logResult:
                if x[6] == 1:
                    self.logTable.insert(
                        parent = '',
                        index = 'end',
                        id = self.tableID,
                        text = '',
                        values = (x[0], x[1] + " " + x[2], x[3], x[4], x[5], "Yes")
                    )
                else:
                    self.logTable.insert(
                        parent = '',
                        index = 'end',
                        id = self.tableID,
                        text = '',
                        values = (x[0], x[1] + " " + x[2], x[3], x[4], x[5], "No")
                    )
                self.tableID = self.tableID + 1
        except mysql.connector.Error as err:
            print("Error " + str(err))
        databaseConnection.disconnectFromDatabase(self.logDatabase, self.logCursor)

class createAndEditUser(tkinter.Frame):
    def __init__(self, master):
        tkinter.Frame.__init__(self, master, height = 300, width = 500)
        self.master = master
        self.lockArray  = list(("Lock 1", "Lock 2",  "Lock 3", "Lock 4"))

        if self.master.editFlag == 0:
            self.userFirstName = tkinter.StringVar()
            self.userLastName = tkinter.StringVar()
            self.keyID = ""
            self.userPassword = ""
            self.userLock1Authorization = tkinter.IntVar()
            self.userLock2Authorization = tkinter.IntVar()
        else:
            self.extractFromDatabase(self.master.editUserFullName)
            self.master.editUserFullName = ""
            self.keyID = self.selectResult[1]
            self.userFirstName = tkinter.StringVar(self, self.selectResult[2])
            self.userLastName = tkinter.StringVar(self, self.selectResult[3])
            self.userPassword = self.selectResult[4]
            self.userLock1Authorization = tkinter.IntVar()
            self.userLock2Authorization = tkinter.IntVar()
            self.userLock1Default = 0
            self.userLock2Default = 0

            self.extractLockPermissions(self.selectResult[0])
            for x in self.lockPermissions:
                if x[1] == 1:
                    self.userLock1Authorization.set(1)
                    self.userLock1Default = 1
                elif x[1] == 2:
                    self.userLock2Authorization.set(1)
                    self.userLock2Default = 1
            
        self.keyIDEntry()
        self.userFirstNameEntry()
        self.userLastNameEntry()
        self.userPasswordEntry()
        self.userVerifiedLocks()
        self.userSubmitButton()
        self.backToMenuButton()

    def addLockPermission(self, lockID):
        self.userQuerry = "SELECT * FROM users WHERE keyID = \"%s\";"
        try:
            self.userCursor.execute(self.userQuerry % (self.keyID,))
        except mysql.connector.Error as err:
            print("Error" + str(err))
        self.selectResult = self.userCursor.fetchone()
        self.userQuerry = "INSERT INTO lockpermissions(userID, lockID) VALUES(\"%s\", \"%s\");"
        try:
            self.userCursor.execute(self.userQuerry % (self.selectResult[0], lockID))
        except mysql.connector.Error as err:
            print("Error", + str(err))

    def removeLockPermission(self, lockID):
        self.userQuerry = "DELETE FROM lockpermissions WHERE userID = %s AND lockID = %s"
        try:
            self.userCursor.execute(self.userQuerry % (self.selectResult[0], lockID))
        except mysql.connector.Error as err:
            print("Error" + str(err))

    def extractFromDatabase(self, nameArray):
        self.userQuerry = "SELECT * FROM users WHERE firstName = \"%s\" AND lastName = \"%s\";"
        self.userDatabase = databaseConnection.connectToDatabase()
        self.userCursor = databaseConnection.createCursor(self.userDatabase)
        try:
            self.userCursor.execute(self.userQuerry % (nameArray[0], nameArray[1]))
            self.selectResult = self.userCursor.fetchone()
        except mysql.connector.Error as err:
            print("Error" + str(err))
        databaseConnection.disconnectFromDatabase(self.userDatabase, self.userCursor)
        return self.selectResult

    def extractLockPermissions(self, userID):
        self.lockPermissions = list(())
        self.userDatabase = databaseConnection.connectToDatabase()
        self.userCursor = databaseConnection.createCursor(self.userDatabase)
        self.userQuerry = "SELECT * FROM lockpermissions where userID = %s;"
        try:
            self.userCursor.execute(self.userQuerry % (userID,))
            self.lockResult = self.userCursor.fetchall()
            for x in self.lockResult:
                self.lockPermissions.append(x)
        except mysql.connector.Error as err:
            print("Error" + str(err))
        databaseConnection.disconnectFromDatabase(self.userDatabase, self.userCursor)

    def checkDataBeforeSubmission(self):
        if self.userPassword != "" and self.keyID != "" and self.userFirstName.get() != "" and self.userLastName.get() != "": 
            self.submitToDatabase()
        elif self.keyID == "":
            self.submitErrorWindow = tkinter.Toplevel(self)
            self.submitErrorWindow.geometry('250x100')
            self.submitErrorWindow.title("Error")
            self.submitErrorWindow.grab_set()

            self.submitErrorWindowLabel = tkinter.Label(
                self.submitErrorWindow,
                text = "No KeyID\nPlease scan a RFID tag",
                font = ("Helvetica", 12),
                anchor = tkinter.CENTER
            )
            self.submitErrorWindowLabel.pack(
                ipady = 10
            )

            self.submitErrorWindowButton = tkinter.Button(
                self.submitErrorWindow,
                text = "Confirm",
                width = 10,
                height = 1
            )
            self.submitErrorWindowButton.pack()
            self.submitErrorWindowButton['command'] = lambda: self.submitErrorWindow.destroy()

        elif self.userPassword == "":
            self.submitErrorWindow = tkinter.Toplevel(self)
            self.submitErrorWindow.geometry('250x100')
            self.submitErrorWindow.title("Error")
            self.submitErrorWindow.grab_set()

            self.submitErrorWindowLabel = tkinter.Label(
                self.submitErrorWindow,
                text = "No Password\nPlease enter a valid Password",
                font = ("Helvetica", 12)
            )
            self.submitErrorWindowLabel.pack(
                ipady = 10
            )

            self.submitErrorWindowButton = tkinter.Button(
                self.submitErrorWindow,
                text = "Confirm",
                width = 10,
                height = 1
            )
            self.submitErrorWindowButton.pack()
            self.submitErrorWindowButton['command'] = lambda: self.submitErrorWindow.destroy()

        elif self.userFirstName.get() == "":            
            self.submitErrorWindow = tkinter.Toplevel(self)
            self.submitErrorWindow.geometry('250x100')
            self.submitErrorWindow.title("Error")
            self.submitErrorWindow.grab_set()

            self.submitErrorWindowLabel = tkinter.Label(
                self.submitErrorWindow,
                text = "No First Name\nPlease enter a First Name",
                font = ("Helvetica", 12)
            )
            self.submitErrorWindowLabel.pack(
                ipady = 10
            )
            

            self.submitErrorWindowButton = tkinter.Button(
                self.submitErrorWindow,
                text = "Confirm",
                width = 10,
                height = 1
            )
            self.submitErrorWindowButton.pack()
            self.submitErrorWindowButton['command'] = lambda: self.submitErrorWindow.destroy()

        elif self.userLastName.get() == "":
            self.submitErrorWindow = tkinter.Toplevel(self)
            self.submitErrorWindow.geometry('250x100')
            self.submitErrorWindow.title("Error")
            self.submitErrorWindow.grab_set()

            self.submitErrorWindowLabel = tkinter.Label(
                self.submitErrorWindow,
                text = "No Last Name\nPlease enter a Last Name",
                font = ("Helvetica", 12)
            )
            self.submitErrorWindowLabel.pack(
                ipady = 10
            )
            

            self.submitErrorWindowButton = tkinter.Button(
                self.submitErrorWindow,
                text = "Confirm",
                width = 10,
                height = 1
            )
            self.submitErrorWindowButton.pack()
            self.submitErrorWindowButton['command'] = lambda: self.submitErrorWindow.destroy()
        
    def databaseErrorExistingKeyID(self):
        self.errorWindowKeyID = tkinter.Toplevel(self)
        self.errorWindowKeyID.geometry('250x100')
        self.errorWindowKeyID.title("Error")
        self.errorWindowKeyID.grab_set()

        self.errorWindowKeyIDLabel = tkinter.Label(
            self.errorWindowKeyID,
            text = "KeyID is already assigned to an existing user\nPlease scan a different RFID tag",
            font = ('Helvetica', 12)
        )
        self.errorWindowKeyIDLabel.pack(
            ipady = 10
        )

        self.errorWindowKeyIDButton = tkinter.Button(
            self.errorWindowKeyID,
            text = "Confirm",
            width = 10,
            height = 1
        )
        self.errorWindowKeyIDButton.pack()
        self.errorWindowKeyIDButton['command'] = lambda: self.errorWindowKeyID.destroy()

    def submitToDatabase(self):
        self.userDatabase = databaseConnection.connectToDatabase()
        self.userCursor = databaseConnection.createCursor(self.userDatabase)

        if self.master.editFlag == 0:
            self.userQuerry = "INSERT INTO users(keyID, firstName, lastName, userPassword) VALUES(\"%s\", \"%s\", \"%s\", \"%s\");"
            try:
                self.userCursor.execute(self.userQuerry % (self.keyID, self.userFirstName.get(), self.userLastName.get(), self.userPassword))
                if self.userLock1Authorization.get() == 1:
                    self.addLockPermission(1)
                if self.userLock2Authorization.get() == 1:
                    self.addLockPermission(2)
            except mysql.connector.Error as err:
                if err.errno == 1062:
                    self.databaseErrorExistingKeyID()
                    print("Error " + str(err.errno))
                else:
                    print("Error " + str(err))
        else:
            self.userQuerry = "UPDATE users SET keyID = \"%s\", firstName = \"%s\", lastName = \"%s\", userPassword = \"%s\" WHERE userID = %s;"
            try:
                self.userCursor.execute(self.userQuerry % (self.keyID, self.userFirstName.get(), self.userLastName.get(), self.userPassword, self.selectResult[0]))
                if self.userLock1Authorization.get() != self.userLock1Default:
                    if self.userLock1Authorization.get() == 1:
                        self.addLockPermission(1)
                    else:
                        self.removeLockPermission(1)
                if self.userLock2Authorization.get() != self.userLock2Default:
                    if self.userLock2Authorization.get() == 1:
                        self.addLockPermission(2)
                    else:
                        self.removeLockPermission(2)
            except mysql.connector.Error as err:
                if err.errno == 1062:
                    self.databaseErrorExistingKeyID()
                else:
                    print("Error " + str(err))

        databaseConnection.disconnectFromDatabase(self.userDatabase, self.userCursor)

        self.userConfirmWindow = tkinter.Toplevel(self)
        self.userConfirmWindow.geometry('250x100')
        self.userConfirmWindow.title("Success")
        self.userConfirmWindow.grab_set()

        if self.master.editFlag == 0:
            self.userConfirmWindowLabel = tkinter.Label(
                self.userConfirmWindow,
                text = "User " + self.userFirstName.get() + " " + self.userLastName.get() + "\nsuccessfully created",
                font = ('Helvetica', 12)
            )
            self.userConfirmWindowLabel.pack(
                ipady = 10
            )
        else:
            self.userConfirmWindowLabel = tkinter.Label(
                self.userConfirmWindow,
                text = "User " + self.userFirstName.get() + " " + self.userLastName.get() + "\nsuccessfully edited",
                font = ('Helvetica', 12)
            )
            self.userConfirmWindowLabel.pack(
                ipady = 10
            )

        self.userConfirmWindowButton = tkinter.Button(
            self.userConfirmWindow,
            text = "Confirm",
            width = 10,
            height = 1
        )
        self.userConfirmWindowButton.pack()
        self.userConfirmWindowButton['command'] = lambda: self.master.switchFrame(mainMenu)  

    def keyIDSubmit(self):
        self.keyID = self.master.socketCommunication('1', 1)
        self.keyIDValidLabel.destroy()
        self.keyIDEntry()

    def passwordSubmit(self):
        self.userPassword = self.master.socketCommunication('2', 1)
        if len(self.userPassword) < 6:
            self.userPassword = ""

            self.errorPasswordWindow = tkinter.Toplevel(self)
            self.errorPasswordWindow.geometry('250x100')
            self.errorPasswordWindow.title("Error")
            self.errorPasswordWindow.grab_set()

            self.errorPasswordWindowLabel = tkinter.Label(
                self.errorPasswordWindow,
                text = "Password must be at least\n6 characters in length",
                font = ('Helvetica', 12)
            )
            self.errorPasswordWindowLabel.pack(
                ipady = 10
            )

            self.errorPasswordWindowButton = tkinter.Button(
                self.errorPasswordWindow,
                text = "Confirm",
                width = 10,
                height = 1
            )
            self.errorPasswordWindowButton.pack()
            self.errorPasswordWindowButton['command'] = lambda: self.errorPasswordWindow.destroy()

        self.passwordValidLabel.destroy()
        self.userPasswordEntry()

    def keyIDEntry(self):
        self.keyIDLabel = tkinter.Label(
            self,
            text = "Key ID:",
            font = ("Helvetica", 14)
        )
        self.keyIDLabel.place(
            x = 50,
            y = 30
        )

        self.keyIDButton = tkinter.Button(
            self,
            text="Scan RFID Tag",
            width = 12,
            height = 2
        )
        self.keyIDButton.place(
            x = 380,
            y = 25
        )
        self.keyIDButton['command'] = lambda: self.keyIDSubmit()
        
        self.keyIDValidLabel = tkinter.Label(
            self,
            font = ("Helvetica", 14),
            width = 17
        )
        if self.keyID == "":
            self.keyIDValidLabel['text']  = "No KeyID"
            self.keyIDValidLabel['background'] = 'red'
        else:
            self.keyIDValidLabel['text'] = 'KeyID Scanned'
            self.keyIDValidLabel['background'] = 'green'
        self.keyIDValidLabel.place(
            x = 160,
            y = 30
        )
    
    def userFirstNameEntry(self):
        self.userLabelFirstName = tkinter.Label(
            self,
            text = "First Name:",
            font = ("Helvetica", 14)
        )
        self.userLabelFirstName.place(
            x = 50,
            y = 70
        )

        self.userEntryFirstName = tkinter.Entry(
            self,
            textvariable = self.userFirstName,
            font = ("Helvetica", 14),
            width = 17
        )
        self.userEntryFirstName.place(
            x = 160,
            y = 70
        )
        self.userEntryFirstName.focus()

    def userLastNameEntry(self):
        self.userLabelLastName = tkinter.Label(
            self,
            text = "Last Name:",
            font = ("Helvetica", 14)
        )
        self.userLabelLastName.place(
            x = 50,
            y = 110
        )

        self.userEntryLastName = tkinter.Entry(
            self,
            textvariable = self.userLastName,
            font = ("Helvetica", 14),
            width = 17
        )
        self.userEntryLastName.place(
            x = 160,
            y = 110
        )

    def userPasswordEntry(self):
        self.userLabelPassword = tkinter.Label(
            self,
            text = "Password:",
            font = ("Helvetica", 14)
        )
        self.userLabelPassword.place(
            x = 50,
            y = 150
        )

        self.userPasswordButton = tkinter.Button(
            self,
            text = "Enter Password",
            width = 12,
            height = 2
        )
        self.userPasswordButton.place(
            x = 380,
            y = 145
        )
        self.userPasswordButton['command'] = lambda: self.passwordSubmit()

        self.passwordValidLabel = tkinter.Label(
            self,
            font = ("Helvetica", 14),
            width = 17
        )
        if self.userPassword == "":
            self.passwordValidLabel['text']  = "No Password"
            self.passwordValidLabel['background'] = 'red'
        else:
            self.passwordValidLabel['text'] = 'Password Entered'
            self.passwordValidLabel['background'] = 'green'
        self.passwordValidLabel.place(
            x = 160,
            y = 150
        )

    def userVerifiedLocks(self):
        self.userLabelLocks =  tkinter.Label(
            self,
            text = "Locks:",
            font = ("Helvetica", 14)
        )
        self.userLabelLocks.place(
            x = 50,
            y = 190
        )

        self.lockDatabase = databaseConnection.connectToDatabase()
        self.lockCursor = databaseConnection.createCursor(self.lockDatabase)
        self.lockQuerry = "SELECT * FROM locks;"
        try:
            self.lockCursor.execute(self.lockQuerry)
            self.databaseArray = self.lockCursor.fetchall()
            self.lockNumber = 0
            for x in self.databaseArray:
                self.lockArray[self.lockNumber] = x[1]
                self.lockNumber += 1
        except mysql.connector.Error as err:
            print("Error " + str(err))
        databaseConnection.disconnectFromDatabase(self.lockDatabase, self.lockCursor)

        self.userLock1Check = tkinter.Checkbutton(
            self,
            text = self.lockArray[0],
            variable = self.userLock1Authorization,
            onvalue = 1,
            offvalue = 0
        )
        self.userLock1Check.place(
            x = 160,
            y = 190
        )

        self.userLock2Check = tkinter.Checkbutton(
            self,
            text = self.lockArray[1],
            variable = self.userLock2Authorization,
            onvalue = 1,
            offvalue = 0
        )
        self.userLock2Check.place(
            x = 250,
            y = 190
        )

        self.userLock3Check = tkinter.Checkbutton(
            self,
            text = self.lockArray[2],
            onvalue = 1,
            offvalue = 0,
            state = tkinter.DISABLED
        )
        self.userLock3Check.place(
            x = 160,
            y = 210
        )

        self.userLock4Check = tkinter.Checkbutton(
            self,
            text = self.lockArray[3],
            onvalue = 1,
            offvalue = 0,
            state = tkinter.DISABLED
        )
        self.userLock4Check.place(
            x = 250,
            y = 210
        )

    def userSubmitButton(self):
        self.userSubmit = tkinter.Button(
            self,
            text = "Submit",
            width = 12,
            height = 2
        )
        self.userSubmit.place(
            x = 380,
            y = 235
        )
        self.userSubmit['command'] = lambda: self.checkDataBeforeSubmission()

    def backToMenuButton(self):
        self.backToMenu = tkinter.Button(
            self,
            text="Back To Menu",
            height = 2,
            width = 12
        )
        self.backToMenu.place(
            x = 25,
            y = 235
        )
        self.backToMenu['command'] = lambda: self.master.switchFrame(mainMenu)

class selectUser(tkinter.Frame):
    def __init__(self, master):
        tkinter.Frame.__init__(
            self,
            master,
            height = 300,
            width = 500
        )
        self.master = master
        self.userFullName = tkinter.StringVar()

        self.userSelection()
        self.selectionButton()
        self.backToMenuButton()

    def processSelection(self):
        self.selectionIndex = self.userSelectList.curselection()
        self.selectionValue = self.userSelectList.get(self.selectionIndex)
        self.userFullName = self.selectionValue
        self.userFullNameArray = self.userFullName.split()

        #Blank Entry Check
        if len(self.userFullNameArray) == 0:
            self.userFullNameArray = ["", ""]
        elif len(self.userFullNameArray) == 1:
            self.userFullNameArray = ["", ""]
        
        if self.master.deleteFlag == 1:
            self.deleteConfirm()
        else:
            self.editSelection()

    def editSelection(self):
        self.master.editUserFullName = self.userFullNameArray
        self.master.setEditFlag(1)
        self.master.switchFrame(createAndEditUser)

    def deleteConfirm(self):
        self.deleteWindow = tkinter.Toplevel(self)
        self.deleteWindow.geometry('250x100')
        self.deleteWindow.title("Confirm Delete")
        self.deleteWindow.grab_set()
        
        self.deleteWindowLabel = tkinter.Label(
            self.deleteWindow,
            text = "Are you sure you want to delete\n" + self.userFullNameArray[0] + " " + self.userFullNameArray[1] + "?",
            font = ("Helvetica", 12)
        )
        self.deleteWindowLabel.pack(
            ipady = 10
        )

        self.deleteWindowYesButton = tkinter.Button(
            self.deleteWindow,
            text = "Yes",
            width = 10,
            height = 1
        )
        self.deleteWindowYesButton.pack(
            side = tkinter.LEFT,
            padx = 10
        )
        self.deleteWindowYesButton['command'] = lambda: self.deleteSelection()

        self.deleteWindowNoButton = tkinter.Button(
            self.deleteWindow,
            text = "No",
            width = 10,
            height = 1
        )
        self.deleteWindowNoButton.pack(
            side = tkinter.RIGHT,
            padx = 10
        )
        self.deleteWindowNoButton['command'] = lambda: self.deleteWindow.destroy()

    def deleteSelection(self):
        self.userDatabase = databaseConnection.connectToDatabase()
        self.userCursor = databaseConnection.createCursor(self.userDatabase)
        self.userQuery = "SELECT * FROM users WHERE firstName = \"%s\" AND lastName = \"%s\";"
        self.userCursor.execute(self.userQuery % (self.userFullNameArray[0], self.userFullNameArray[1]))
        self.deleteUserID = self.userCursor.fetchone()
        self.userQuery = "UPDATE log SET userID = 2 WHERE userID = %s;"
        self.userCursor.execute(self.userQuery % (self.deleteUserID[0],))
        self.userQuery = "DELETE FROM lockpermissions WHERE userID = %s"
        self.userCursor.execute(self.userQuery % (self.deleteUserID[0],))
        self.userQuery = "DELETE FROM users WHERE userID = \"%s\";"
        self.userCursor.execute(self.userQuery % (self.deleteUserID[0]))
        databaseConnection.disconnectFromDatabase(self.userDatabase, self.userCursor)

        self.deleteSuccessWindow = tkinter.Toplevel(self)
        self.deleteSuccessWindow.geometry('250x100')
        self.deleteSuccessWindow.title("Delete Successful")
        self.deleteSuccessWindow.grab_set()
        
        self.deleteSuccessWindowLabel = tkinter.Label(
            self.deleteSuccessWindow,
            text = self.userFullNameArray[0] + " " + self.userFullNameArray[1]+"\nsuccessfully deleted",
            font = ("Helvetica", 12)
        )
        self.deleteSuccessWindowLabel.pack(
            ipady = 10
        )

        self.deleteSuccessWindowButton = tkinter.Button(
            self.deleteSuccessWindow,
            text = "Confirm",
            width = 10,
            height = 1
        )
        self.deleteSuccessWindowButton.pack()
        self.deleteSuccessWindowButton['command'] = lambda: self.master.switchFrame(mainMenu)

    def userSelection(self):
        if self.master.deleteFlag == 1:
            self.userLabel = tkinter.Label(
                self,
                text = "Select User to Delete",
                font = ('Helvetica', 14)
            )
        else:
            self.userLabel = tkinter.Label(
                self,
                text = "Select User to Update",
                font = ('Helvetica', 14)
            )
        self.userLabel.place(
            x = 150,
            y = 10
        )

        self.userDatabase = databaseConnection.connectToDatabase()
        self.userCursor = databaseConnection.createCursor(self.userDatabase)
        self.userQuery = "SELECT * FROM users WHERE userID > 2;"
        try:
            self.userCursor.execute(self.userQuery)
            self.userResult = self.userCursor.fetchall()
            self.junkVariable = tkinter.StringVar()
            self.userSelectList = tkinter.Listbox(
                self,
                font = ('Helvetica', 14),
                height = 7,
                relief = tkinter.SOLID
            )
            self.userSelectList.place(
                x = 135,
                y = 40
            )
            for self.x in self.userResult:
                self.userFullName = self.x[2] + " " + self.x[3]
                self.userSelectList.insert(tkinter.END, self.userFullName)
        except mysql.connector.Error as err:
            self.errorText = tkinter.Text(
                self,
                width = 60,
                height = 5
            )
            self.errorText.place(
                x = 8,
                y = 20
            )
            self.errorText.insert(tkinter.INSERT, err)
            self.errorText['state'] = tkinter.DISABLED
        databaseConnection.disconnectFromDatabase(self.userDatabase, self.userCursor)

        self.userSelectScrollBar = tkinter.Scrollbar(
            self,
            orient = tkinter.VERTICAL
        )
        self.userSelectScrollBar.place(
            x = 358,
            y = 40,
            height = 165
        )
        self.userSelectList.config(yscrollcommand = self.userSelectScrollBar.set)
        self.userSelectScrollBar.config(command = self.userSelectList.yview)
    
    def selectionButton(self):
        if self.master.deleteFlag == 1:
            self.userSelectButtonText = "Delete User"
        else:
            self.userSelectButtonText = "Edit User"
        self.userSelectButton = tkinter.Button(
            self,
            text = self.userSelectButtonText,
            height = 2,
            width = 12
        )
        self.userSelectButton.place(
            x = 380,
            y = 235
        )
        self.userSelectButton['command'] = lambda: self.processSelection()

    def backToMenuButton(self):
        self.backToMenu = tkinter.Button(
            self,
            text="Back To Menu",
            height = 2,
            width = 12
        )
        self.backToMenu.place(
            x = 25,
            y = 235
        )
        self.backToMenu['command'] = lambda: self.master.switchFrame(mainMenu)

class accessLogs(tkinter.Frame):
    def __init__(self, master):
        tkinter.Frame.__init__(
            self,
            master,
            height = 300,
            width = 500
        )
        self.master = master
        self.dataSelect = tkinter.Listbox(self)
        self.confirmSelectButton = tkinter.Button(self)
        self.dataSelectScrollBar = tkinter.Scrollbar(self)

        self.sortByUserButton()
        self.sortByLockButton()
        self.sortByTimeButton()
        self.backToMenuButton()

    def processSelectionWithList(self):
        self.selectIndex = self.dataSelect.curselection()
        self.selectValue = self.dataSelect.get(self.selectIndex)
        self.master.logSelectData = self.selectValue
        self.master.switchFrame(logDisplay)

    def processSelectionWithCalendar(self):
        self.selectValue = self.dataSelect.get_date()
        self.dateTimeConversion = datetime.datetime.strptime(str(self.selectValue), '%m/%d/%y')
        self.selectValue = self.dateTimeConversion.strftime("%Y-%m-%d")
        self.master.logSelectData = self.selectValue
        self.master.switchFrame(logDisplay)

    def selectUserLog(self):
        self.dataSelect.destroy()
        self.dataSelectScrollBar.destroy()
        self.confirmSelectButton.destroy()

        self.logDatabase = databaseConnection.connectToDatabase()
        self.logCursor = databaseConnection.createCursor(self.logDatabase)
        self.logQuery = "SELECT * FROM users;"
        try:
            self.logCursor.execute(self.logQuery)
            self.logResult = self.logCursor.fetchall()
            self.dataSelect = tkinter.Listbox(
                self,
                font = ('Helvetica', 14),
                height = 8,
                relief = tkinter.SOLID
            )
            self.dataSelect.place(
                x = 150,
                y = 20
            )
            for self.x in self.logResult:
                self.userFullName = self.x[2] + " " + self.x[3]
                self.dataSelect.insert(
                    tkinter.END,
                    self.userFullName
                )
        except mysql.connector.Error as err:
            self.errorText = tkinter.Text(
                self,
                width = 60,
                height = 5
            )
            self.errorText.place(
                x = 8,
                y = 20
            )
            self.errorText.insert(
                tkinter.INSERT,
                err
            )
            self.errorText['state'] = tkinter.DISABLED
        databaseConnection.disconnectFromDatabase(self.logDatabase, self.logCursor)

        self.dataSelectScrollBar = tkinter.Scrollbar(
            self,
            orient = tkinter.VERTICAL
        )
        self.dataSelectScrollBar.place(
            x = 374,
            y = 21,
            height = 186
        )
        self.dataSelect.config(yscrollcommand = self.dataSelectScrollBar.set)
        self.dataSelectScrollBar.config(command = self.dataSelect.yview)

        self.confirmSelectButton = tkinter.Button(
            self,
            text = "Show Logs",
            width = 12,
            height = 2
        )
        self.confirmSelectButton.place(
            x = 380,
            y = 235
        )
        self.master.logFlag = 0
        self.confirmSelectButton['command'] = lambda: self.processSelectionWithList()

    def selectLockLog(self):
        self.dataSelect.destroy()
        self.dataSelectScrollBar.destroy()
        self.confirmSelectButton.destroy()

        self.logDatabase = databaseConnection.connectToDatabase()
        self.logCursor = databaseConnection.createCursor(self.logDatabase)
        self.logQuery = "SELECT * FROM locks;"
        try:
            self.logCursor.execute(self.logQuery)
            self.logResult = self.logCursor.fetchall()
            self.dataSelect = tkinter.Listbox(
                self,
                font = ('Helvetica', 14),
                height = 8,
                relief = tkinter.SOLID
            )
            self.dataSelect.place(
                x = 150,
                y = 20
            )
            for self.x in self.logResult:
                self.userFullName = self.x[1]
                self.dataSelect.insert(
                    tkinter.END,
                    self.userFullName
                )
        except mysql.connector.Error as err:
            self.errorText = tkinter.Text(
                self,
                width = 60,
                height = 5
            )
            self.errorText.place(
                x = 8,
                y = 20
            )
            self.errorText.insert(
                tkinter.INSERT,
                err
            )
            self.errorText['state'] = tkinter.DISABLED

        self.dataSelectScrollBar = tkinter.Scrollbar(
            self,
            orient = tkinter.VERTICAL
        )
        self.dataSelectScrollBar.place(
            x = 374,
            y = 21,
            height = 186
        )
        self.dataSelect.config(yscrollcommand = self.dataSelectScrollBar.set)
        self.dataSelectScrollBar.config(command = self.dataSelect.yview)

        self.confirmSelectButton = tkinter.Button(
            self,
            text = "Show Logs",
            width = 12,
            height = 2
        )
        self.confirmSelectButton.place(
            x = 380,
            y = 235
        )
        self.master.logFlag = 1
        self.confirmSelectButton['command'] = lambda: self.processSelectionWithList()

    def selectDateLog(self):
        self.dataSelect.destroy()
        self.dataSelectScrollBar.destroy()
        self.confirmSelectButton.destroy()

        self.dataSelectScrollBar = tkinter.Scrollbar(self)

        self.currentDate = datetime.datetime.now()
        self.dataSelect = tkcalendar.Calendar(
            self,
            selectmode = 'day',
            year = self.currentDate.year,
            month = self.currentDate.month,
            day = self.currentDate.day,
            maxdate = self.currentDate
        )
        self.dataSelect.place(
            x = 150,
            y = 20
        )

        self.confirmSelectButton = tkinter.Button(
            self,
            text = "Show Logs",
            width = 12,
            height = 2
        )
        self.confirmSelectButton.place(
            x = 380,
            y = 235
        )
        self.master.logFlag = 2
        self.confirmSelectButton['command'] = lambda: self.processSelectionWithCalendar()

    def sortByUserButton(self):
        self.userButton = tkinter.Button(
            self,
            text = "Sort by User",
            width = 12,
            height = 2
        )
        self.userButton.place(
            x = 25,
            y = 40
        )
        self.userButton['command'] = lambda: self.selectUserLog()

    def sortByLockButton(self):
        self.lockButton = tkinter.Button(
            self,
            text = "Sort by Lock",
            width = 12,
            height = 2
        )
        self.lockButton.place(
            x = 25,
            y = 100
        )
        self.lockButton['command'] = lambda: self.selectLockLog()

    def sortByTimeButton(self):
        self.timeButton = tkinter.Button(
            self,
            text = "Sort by Date",
            width = 12,
            height = 2
        )
        self.timeButton.place(
            x = 25,
            y = 160
        )
        self.timeButton['command'] = lambda: self.selectDateLog()

    def backToMenuButton(self):
        self.backToMenu = tkinter.Button(
            self,
            text="Back To Menu",
            width = 12,
            height = 2
        )
        self.backToMenu.place(
            x = 25,
            y = 235
        )
        self.backToMenu['command'] = lambda: self.master.switchFrame(mainMenu)

class logDisplay(tkinter.Frame):
    def __init__(self, master):
        tkinter.Frame.__init__(
            self,
            master,
            height = 300,
            width = 500
        )
        self.master = master
        self.selectData = self.master.logSelectData
        self.exportFileName = tkinter.StringVar()

        if self.master.logFlag == 0:
            self.logListingsUser()
        elif self.master.logFlag == 1:
            self.logListingsLock()
        else:
            self.logListingsDate()
        self.exportDataButton()
        self.backToAccessLogs()

    def confirmExport(self):
        self.exportWindow = tkinter.Toplevel(self)
        self.exportWindow.geometry('250x150')
        self.exportWindow.title("Confirm Export")
        self.exportWindow.grab_set()
        
        self.exportWindowLabel = tkinter.Label(
            self.exportWindow,
            text = "Enter name of file\n to export logs to",
            font = ("Helvetica", 12),
        )
        self.exportWindowLabel.pack(
            ipady = 10
        )

        self.exportEntry = tkinter.Entry(
            self.exportWindow,
            textvariable = self.exportFileName,
            font = ("Helvetica", 12),
            width = 17
        )
        self.exportEntry.pack(
            pady = 10
        )
        self.exportEntry.focus()

        self.exportWindowButton = tkinter.Button(
            self.exportWindow,
            text = "Export",
            width = 10,
            height = 1
        )
        self.exportWindowButton.pack(
            padx = 10,
            pady = 10,
            side = tkinter.LEFT
        )
        self.exportWindowButton['command'] = lambda: self.exportLogCSV()

        self.exportWindowClose = tkinter.Button(
            self.exportWindow,
            text = "Close",
            width = 10,
            height = 1
        )
        self.exportWindowClose.pack(
            padx = 10,
            pady = 10,
            side = tkinter.RIGHT
        )
        self.exportWindowClose['command'] = lambda: self.exportWindow.destroy()

    def exportLogCSV(self):
        self.currentDirectory = pathlib.Path(__file__).parents[2]
        self.logsDirectory = self.currentDirectory / 'Logs'
        self.logsFile = self.logsDirectory / (self.exportFileName.get() + '.csv')

        with open(self.logsFile, mode = 'w', newline = '\n') as self.testFile:
            self.logQuery = self.logCursor.statement
            self.testWriter = csv.writer(
                self.testFile,
                delimiter = ",",
                quotechar = '"',
                quoting = csv.QUOTE_MINIMAL
            )
            self.logDatabase = databaseConnection.connectToDatabase()
            self.logCursor = databaseConnection.createCursor(self.logDatabase)
            try:
                self.logCursor.execute(self.logQuery)
                self.logResult = self.logCursor.fetchall()
                self.fieldNames = list(())
                for x in self.logCursor.description:
                    self.fieldNames.append(x[0])
                self.testWriter.writerow(self.fieldNames)
                for x in self.logResult:
                    self.testWriter.writerow([x[0], x[1], x[2], x[3], x[4], x[5], x[6]])
            except mysql.connector.Error as err:
                print("Error" + str(err))
            databaseConnection.disconnectFromDatabase(self.logDatabase, self.logCursor)

        self.exportSuccessWindow = tkinter.Toplevel(self)
        self.exportSuccessWindow.geometry('250x100')
        self.exportSuccessWindow.title("Log Exported")
        self.exportSuccessWindow.grab_set()

        self.exportWindowSuccessLabel = tkinter.Label(
            self.exportSuccessWindow,
            text = "Logs successfully exported to\n%s.csv" % (self.exportFileName.get()),
            font = ("Helvetica", 12)
        )
        self.exportWindowSuccessLabel.pack(
            ipady = 10
        )

        self.exportSuccessWindowButton = tkinter.Button(
            self.exportSuccessWindow,
            text = "Close",
            width = 10,
            height = 1
        )
        self.exportSuccessWindowButton.pack(
            pady = 10
        )
        self.exportSuccessWindowButton['command'] = lambda:[
            self.exportSuccessWindow.destroy(),
            self.exportWindow.destroy()
        ]

    def logListingsUser(self):
        self.logTable = tkinter.ttk.Treeview(
            self,
            height = 6,
            selectmode = 'none'
        )
        self.logTable.place(
            x = 55,
            y = 50
        )
        self.logTable['columns'] = (
            'id', 
            'date',
            'time',
            'lock',
            'valid'
        )

        style = tkinter.ttk.Style()
        style.configure(
            "Treeview.Heading",
            font = ('TKDefaultFont', 12)
        )
        style.configure(
            "Treeview",
            font = ('TKDefaultFont', 12)
        )

        self.logTable.column(
            "#0",
            width = 0,
            stretch = tkinter.NO
        )
        self.logTable.column(
            "id",
            anchor = tkinter.CENTER,
            width = 60
        )
        self.logTable.column(
            'date',
            anchor = tkinter.CENTER,
            width = 90
        )
        self.logTable.column(
            'time',
            anchor = tkinter.CENTER,
            width = 80
        )
        self.logTable.column(
            'lock',
            anchor = tkinter.CENTER,
            width = 85
        )
        self.logTable.column(
            'valid',
            anchor = tkinter.CENTER,
            width = 60
        )

        self.logTable.heading(
            "#0",
            text = "",
            anchor = tkinter.CENTER
        )
        self.logTable.heading(
            "id",
            text = "Log ID",
            anchor = tkinter.CENTER
        )
        self.logTable.heading(
            'date',
            text = "Date",
            anchor = tkinter.CENTER
        )
        self.logTable.heading(
            'time',
            text = "Time",
            anchor = tkinter.CENTER
        )
        self.logTable.heading(
            'lock',
            text = "Lock",
            anchor = tkinter.CENTER
        )
        self.logTable.heading(
            'valid',
            text = "Valid",
            anchor = tkinter.CENTER
        )

        self.fullNameArray = self.selectData.split()

        self.nameLabel = tkinter.Label(
            text = self.selectData,
            font = ('Helvetica', 14)
        )
        self.nameLabel.place(
            x = 160,
            y = 10
        )

        self.logTreeScrollBar = tkinter.Scrollbar(
            self,
            orient = tkinter.VERTICAL
        )
        self.logTreeScrollBar.place(
            x = 432,
            y = 50,
            height = 146
        )
        self.logTable.config(yscrollcommand = self.logTreeScrollBar.set)
        self.logTreeScrollBar.config(command = self.logTable.yview)

        self.logDatabase = databaseConnection.connectToDatabase()
        self.logCursor = databaseConnection.createCursor(self.logDatabase)
        self.logQuery = "SELECT * FROM logview WHERE firstName = \"%s\" AND lastName = \"%s\" ORDER BY logID DESC;"
        try:
            self.logCursor.execute(self.logQuery % (self.fullNameArray[0], self.fullNameArray[1]))
            logResult = self.logCursor.fetchall()
            self.tableID = 0
            for x in logResult:
                if x[6] == 1:
                    self.logTable.insert(
                        parent = '',
                        index = 'end',
                        id = self.tableID,
                        text = '',
                        values = (x[0], x[3], x[4], x[5], "Yes")
                    )
                else:
                    self.logTable.insert(
                        parent = '',
                        index = 'end',
                        id = self.tableID,
                        text = '',
                        values = (x[0], x[3], x[4], x[5], "No")
                    )
                self.tableID = self.tableID + 1
        except mysql.connector.Error as err:
            print("Error" + str(err))
        databaseConnection.disconnectFromDatabase(self.logDatabase, self.logCursor)

    def logListingsLock(self):
        self.logTable = tkinter.ttk.Treeview(
            self,
            height = 6,
            selectmode = 'none'
        )
        self.logTable.place(
            x = 25,
            y = 50
        )
        self.logTable['columns'] = (
            'id',
            'name',
            'date',
            'time',
            'valid'
        )

        style = tkinter.ttk.Style()
        style.configure(
            "Treeview.Heading",
            font = ('TKDefaultFont', 12)
        )
        style.configure(
            "Treeview",
            font = ('TKDefaultFont', 12)
        )

        self.logTable.column(
            "#0",
            width = 0,
            stretch = tkinter.NO
        )
        self.logTable.column(
            "id",
            anchor = tkinter.CENTER,
            width = 60
        )
        self.logTable.column(
            "name",
            anchor = tkinter.CENTER,
            width = 150
        )
        self.logTable.column(
            'date',
            anchor = tkinter.CENTER,
            width = 90
        )
        self.logTable.column(
            'time',
            anchor = tkinter.CENTER,
            width = 80
        )
        self.logTable.column(
            'valid',
            anchor = tkinter.CENTER,
            width = 60
        )

        self.logTable.heading(
            "#0",
            text = "",
            anchor = tkinter.CENTER
        )
        self.logTable.heading(
            "id",
            text = "Log ID",
            anchor = tkinter.CENTER
        )
        self.logTable.heading(
            'name',
            text = "Name",
            anchor = tkinter.CENTER
        )
        self.logTable.heading(
            'date',
            text = "Date",
            anchor = tkinter.CENTER
        )
        self.logTable.heading(
            'time',
            text = "Time",
            anchor = tkinter.CENTER
        )
        self.logTable.heading(
            'valid',
            text = "Valid",
            anchor = tkinter.CENTER
        )

        self.lockLabel = tkinter.Label(
            text = self.selectData,
            font = ('Helvetica', 14)
        )
        self.lockLabel.place(
            x = 200,
            y = 10
        )

        self.logTreeScrollBar = tkinter.Scrollbar(
            self,
            orient = tkinter.VERTICAL
        )
        self.logTreeScrollBar.place(
            x = 467,
            y = 50,
            height = 146
        )
        self.logTable.config(yscrollcommand = self.logTreeScrollBar.set)
        self.logTreeScrollBar.config(command = self.logTable.yview)

        self.logDatabase = databaseConnection.connectToDatabase()
        self.logCursor = databaseConnection.createCursor(self.logDatabase)
        self.logQuery = "SELECT * FROM logview WHERE lockName = \"%s\" ORDER BY logID DESC;"
        try:
            self.logCursor.execute(self.logQuery % (self.selectData,))
            self.logResult = self.logCursor.fetchall()
            self.tableID = 0
            for x in self.logResult:
                if x[6] == 1:
                    self.logTable.insert(
                        parent = '',
                        index = 'end',
                        id = self.tableID,
                        text = '',
                        values = (x[0], x[1] + " " + x[2], x[3], x[4], "Yes")
                    )
                else:
                    self.logTable.insert(
                        parent = '',
                        index = 'end',
                        id = self.tableID,
                        text = '',
                        values = (x[0], x[1] + " " + x[2], x[3], x[4], "No")
                    )
                self.tableID = self.tableID + 1
        except mysql.connector.Error as err:
            print("Error" + str(err))
        databaseConnection.disconnectFromDatabase(self.logDatabase, self.logCursor)

    def logListingsDate(self):
        self.logTable = tkinter.ttk.Treeview(
            self,
            height = 6,
            selectmode = 'none'
        )
        self.logTable.place(
            x = 25,
            y = 50
        )
        self.logTable['columns'] = (
            'id',
            'name',
            'time',
            'lock',
            'valid'
        )

        style = tkinter.ttk.Style()
        style.configure(
            "Treeview.Heading",
            font = ('TKDefaultFont', 12)
        )
        style.configure(
            "Treeview",
            font = ('TKDefaultFont', 12)
        )

        self.logTable.column(
            "#0",
            width = 0,
            stretch = tkinter.NO
        )
        self.logTable.column(
            "id",
            anchor = tkinter.CENTER,
            width = 60
        )
        self.logTable.column(
            "name",
            anchor = tkinter.CENTER,
            width = 150
        )
        self.logTable.column(
            'time',
            anchor = tkinter.CENTER,
            width = 80
        )
        self.logTable.column(
            'lock',
            anchor = tkinter.CENTER,
            width = 85
        )
        self.logTable.column(
            'valid',
            anchor = tkinter.CENTER,
            width = 60
        )

        self.logTable.heading(
            "#0",
            text = "",
            anchor = tkinter.CENTER
        )
        self.logTable.heading(
            "id",
            text = "Log ID",
            anchor = tkinter.CENTER
        )
        self.logTable.heading(
            'name',
            text = "Name",
            anchor = tkinter.CENTER
        )
        self.logTable.heading(
            'time',
            text = "Time",
            anchor = tkinter.CENTER
        )
        self.logTable.heading(
            'lock',
            text = "Lock",
            anchor = tkinter.CENTER
        )
        self.logTable.heading(
            'valid',
            text = "Valid",
            anchor = tkinter.CENTER
        )

        self.dateLabel = tkinter.Label(
            text = self.selectData,
            font = ('Helvetica', 14)
        )
        self.dateLabel.place(
            x = 200,
            y = 10
        )

        self.logTreeScrollBar = tkinter.Scrollbar(
            self,
            orient = tkinter.VERTICAL
        )
        self.logTreeScrollBar.place(
            x = 463,
            y = 50,
            height = 146
        )
        self.logTable.config(yscrollcommand = self.logTreeScrollBar.set)
        self.logTreeScrollBar.config(command = self.logTable.yview)

        self.logDatabase = databaseConnection.connectToDatabase()
        self.logCursor = databaseConnection.createCursor(self.logDatabase)
        self.logQuery = "SELECT * FROM logview WHERE logDate = \"%s\" ORDER BY logID DESC"
        try:
            self.logCursor.execute(self.logQuery % (self.selectData,))
            logResult = self.logCursor.fetchall()
            self.tableID = 0
            for x in logResult:
                if x[6] == 1:
                    self.logTable.insert(
                        parent = '',
                        index = 'end',
                        id = self.tableID,
                        text = '',
                        values = (x[0], x[1] + " " + x[2], x[4], x[5], "Yes")
                    )
                else:
                    self.logTable.insert(
                        parent = '',
                        index = 'end',
                        id = self.tableID,
                        text = '',
                        values = (x[0], x[1] + " " + x[2], x[4], x[5], "No")
                    )
                self.tableID = self.tableID + 1
        except mysql.connector.Error as err:
            print("Error" + str(err))
        databaseConnection.disconnectFromDatabase(self.logDatabase, self.logCursor)

    def exportDataButton(self):
        self.exportButton = tkinter.Button(
            self,
            text="Export Logs (.csv)",
            width = 20,
            height = 2
        )
        self.exportButton.place(
            x = 320,
            y = 235
        )
        self.exportButton['command'] = lambda: self.confirmExport()

    def backToAccessLogs(self):
        self.backToAccessLogsButton = tkinter.Button(
            self,
            text="Back To Log Select",
            height = 2
        )
        self.backToAccessLogsButton.place(
            x = 25,
            y = 235
        )
        self.backToAccessLogsButton['command'] = lambda: self.master.switchFrame(accessLogs)

class openLock(tkinter.Frame):
    def __init__(self, master):
        tkinter.Frame.__init__(
            self,
            master,
            height = 300,
            width = 500
        )
        self.master = master
        self.lockArray = list(("Lock 1", "Lock 2", "Lock 3", "Lock 4"))
        self.obtainLockArray()
        self.openLockLabel()
        self.openLock1()
        self.openLock2()
        self.openLock3()
        self.openLock4()
        self.backToMenu()

    def obtainLockArray(self):
        self.lockDatabase = databaseConnection.connectToDatabase()
        self.lockCursor = databaseConnection.createCursor(self.lockDatabase)
        self.lockQuery = "SELECT * FROM locks;"
        try:
            self.lockCursor.execute(self.lockQuery)
            self.logResult = self.lockCursor.fetchall()
            self.listNumber = 0
            for x in self.logResult:
                self.lockArray[self.listNumber] = x[1]
                self.listNumber = self.listNumber + 1
        except mysql.connector.Error as err:
                print("Error" + str(err))

    def openLockLabel(self):
        self.lockLabel = tkinter.Label(
            text = "Select Lock to Open",
            font = ("Helvetica", 14)
        )

        self.lockLabel.place(
            x = 150,
            y = 25
        )

    def openLock1(self):
        self.openLock1Button = tkinter.Button(
            self,
            width = 10,
            height = 2
        )
        self.openLock1Button['text'] = self.lockArray[0]
        self.openLock1Button.place(
            x = 135,
            y = 90
        )
        self.openLock1Button['command'] = lambda: self.master.socketCommunication('3', 1)

    def openLock2(self):
        self.openLock2Button = tkinter.Button(
            self,
            width = 10,
            height = 2
        )
        self.openLock2Button['text'] = self.lockArray[1]
        self.openLock2Button.place(
            x = 265,
            y = 90
        )
        self.openLock2Button['command'] = lambda: self.master.socketCommunication('3', 2)

    def openLock3(self):
        self.openLock3Button = tkinter.Button(
            self,
            width = 10,
            height = 2,
            state = tkinter.DISABLED
        )
        self.openLock3Button['text'] = self.lockArray[2]
        self.openLock3Button.place(
            x = 135,
            y = 165
        )

    def openLock4(self):
        self.openLock4Button = tkinter.Button(
            self,
            width = 10,
            height = 2,
            state = tkinter.DISABLED
        )
        self.openLock4Button['text'] = self.lockArray[3]
        self.openLock4Button.place(
            x = 265,
            y = 165
        )

    def backToMenu(self):
        self.backToMenu = tkinter.Button(
            self,
            text="Back To Menu",
            height = 2
        )
        self.backToMenu.place(
            x = 25,
            y = 235
        )
        self.backToMenu['command'] = lambda: self.master.switchFrame(mainMenu)

if __name__ == "__main__":
    app = everEyeApp()
    app.establishSocketConnection()
    app.mainloop()