import mysql.connector
import serial
import zmq

def connectToDatabase():
    try:
        database = mysql.connector.connect(
            host = "localhost",
            user = "", #Database User
            password = "", #Database Password
            database = "evereye"
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

def serialFunction(serialPort):
    lockID = 1
    userID = 1
    authenticatedCheck = 0
    keyCheck = False
    lockCheck = False
    logQuery = ""
    
    data = serialPort.readline()
    cleanData = str(data.strip())
    for character in 'b\'':
        cleanData = str.replace(cleanData, character, '')

    # Is User in Database
    logDatabase = connectToDatabase()
    logCursor = createCursor(logDatabase)
    logQuery = "SELECT userID, keyID FROM users WHERE keyID = \"%s\";"
    try:
        logCursor.execute(logQuery % (cleanData,))
        userExistCheck = logCursor.fetchone()
        if (userExistCheck):
            userID = userExistCheck[0]
            keyID = userExistCheck[1]
            keyCheck = True
        else:
            serialPort.write(bytes('b', 'utf-8'))
    except mysql.connector.Error as err:
        serialPort.write(bytes('c', 'utf-8'))
    disconnectFromDatabase(logDatabase, logCursor)

    # Is User Authorized For Lock
    if(keyCheck == True):
        logDatabase = connectToDatabase()
        logCursor = createCursor(logDatabase)
        logQuery = "SELECT * from lockpermissions WHERE userID = %s AND lockID = 1"
        try:
            logCursor.execute(logQuery % (userID,))
            userLockCheck = logCursor.fetchone()
            if (userLockCheck):
                lockCheck = True
                serialPort.write(bytes('a', 'utf-8'))
            else:
                serialPort.write(bytes('g', 'utf-8'))
        except mysql.connector.Error as err:
            serialPort.write(bytes('c', 'utf-8'))

    if(lockCheck == True):
        data = serialPort.readline()
        cleanData = str(data.strip())
        for character in 'b\'':
            cleanData = str.replace(cleanData, character, '')
        
        logDatabase = connectToDatabase()
        logCursor = createCursor(logDatabase)
        logQuery = "Select userID FROM users WHERE keyID = \"%s\" AND userPassword = \"%s\";"
        try:
            logCursor.execute(logQuery % (keyID, cleanData))
            existCheck = logCursor.fetchone()
            if (existCheck):
                authenticatedCheck = 1
                serialPort.write(bytes('d', 'utf-8'))
            else:
                authenticatedCheck = 0
                serialPort.write(bytes('e', 'utf-8'))
        except mysql.connector.Error as err:
            serialPort.write(bytes('f', 'utf-8'))
        disconnectFromDatabase(logDatabase, logCursor)
        
    logDatabase = connectToDatabase()
    logCursor = createCursor(logDatabase)        
    logQuery = "INSERT INTO log(userID, logDate, logTime, lockID, authenticated) VALUES(%s, CURDATE(), CURTIME(), %s, %s);"
    try:
        logCursor.execute(logQuery % (userID, lockID, authenticatedCheck))
    except mysql.connector.Error as err:
        print("Error" + str(err))
    disconnectFromDatabase(logDatabase, logCursor)

    logQuery = ""
    authenticatedCheck = 0
    userID = 1
    keyCheck = False
    lockCheck = False

if __name__ == '__main__':
    serialDevice = serial.Serial(port='COM4', baudrate=9600)
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    while True:
        if(serialDevice.in_waiting > 0):
            serialFunction(serialDevice)
        if(socket.poll(timeout = 1) != 0):
            message = socket.recv()
            if str(message) == "b\'1\'":
                serialDevice.write(bytes('1', 'utf-8'))
                serialData = serialDevice.readline()
                cleanSerialData = str(serialData.strip())
                for serialCharacter in 'b\'':
                    cleanSerialData = str.replace(cleanSerialData, serialCharacter, '')
                socket.send_string(cleanSerialData)
            elif str(message) == "b\'2\'":
                serialDevice.write(bytes('2', 'utf-8'))
                serialData = serialDevice.readline()
                cleanSerialData = str(serialData.strip())
                for serialCharacter in 'b\'':
                    cleanSerialData = str.replace(cleanSerialData, serialCharacter, '')
                socket.send_string(cleanSerialData)
            elif str(message) == "b\'3\'":
                serialDevice.write(bytes('3', 'utf-8'))
                socket.send_string("Confirm")