import pexpect as pe

import ConfigParser

from twisted.application import service
from twisted.internet import reactor
from twisted.web import server, resource
from twisted.web.static import File
from twisted.web.wsgi import WSGIResource

from flask import Flask, request as req, json, session, make_response

import MySQLdb

import random
import os
import time

class ConfigFile:
    def __init__(self, configfilepath = '/var/PyDALI/server/conf/properties.cfg'):
        self.config = ConfigParser.ConfigParser()
        self.config.read(configfilepath)

    def checkConfigFile(self):
        try:
            self.config.get('Database', 'MYSQL_HOST')
            self.config.get('Database', 'MYSQL_PORT')
            self.config.get('Database', 'MYSQL_USER')
            self.config.get('Database', 'MYSQL_PASSWD')
            self.config.get('Database', 'MYSQL_DB')


            self.config.get('Server', 'RootFiles')
            self.config.get('Server', 'ServerPort')
        except ConfigParser.NoOptionError, e:
            print 'Error in config file:', e
            exit()
        except ConfigParser.NoSectionError, e:
            print 'Error in config file:', e
            exit()

    def get(self, section, key):
        return self.config.get(section, key)

configFile = ConfigFile()
configFile.checkConfigFile()

SECRET_KEY = 'whhasdasdhaat'
ROOT = configFile.get('Server', 'RootFiles')

app = Flask(__name__)
app.config.from_object(__name__)
app.config['DEBUG'] = True

class DataAccess:
    MYSQL_HOST = configFile.get('Database', 'MYSQL_HOST')
    MYSQL_PORT = int(configFile.get('Database', 'MYSQL_PORT'))
    MYSQL_USER = configFile.get('Database', 'MYSQL_USER')
    MYSQL_PASSWD = configFile.get('Database', 'MYSQL_PASSWD')
    MYSQL_DB = configFile.get('Database', 'MYSQL_DB')

    Cursor = None

    # constructor
    def __init__(self, namedb=None):
        if (namedb != None):
            self.MYSQL_DB = namedb
        try:
            self.conn = MySQLdb.Connect(host=self.MYSQL_HOST,
                                        port=self.MYSQL_PORT,
                                        user=self.MYSQL_USER,
                                        passwd=self.MYSQL_PASSWD,
                                        db=self.MYSQL_DB)
            self.Cursor = self.conn.cursor(
                MySQLdb.cursors.DictCursor)  # Permette l'accesso attraverso il nome dei fields

        except MySQLdb.Error, e:
            print "ERRORE MySQL:"
            print "%s" % e.args[1]
            raw_input("Premi INVIO uscire: ")

    def closeConnection(self):
        self.conn.close()


@app.route('/login', methods=['POST'])
def login():
    if 'username' in session:
        return session['user']
    db = DataAccess()
    usr = formGet(req.form['username'])
    pwd = formGet(req.form['password'])
    try:
        query = """ SELECT us.*
                FROM users as us
                WHERE us.username = '%s' AND us.password = '%s'
                """ % (usr, pwd)
        db.Cursor.execute(query)
        result = db.Cursor.fetchone()
        if (result <> None):
            sk = ''.join(random.choice('1gio2giu3') for _ in range(16))
            d = {}
            d['username'] = usr
            d['email'] = result['email']
            d['id'] = result['id']
            d['sk'] = sk
            print sk
            session['username'] = usr
            session['user'] = esitMessage(1, d)
            session['sk'] = sk
            db.closeConnection()
            return esitMessage(1, d)
        else:
            db.closeConnection()
            return esitMessage(0, 'Unregistered User')
    except MySQLdb.Error:
        db.closeConnection()
        return esitMessage(0, 'Problem Server')


@app.route('/register', methods=['POST'])
def register():
    db = DataAccess()
    usr = formGet(req.form['username'])
    pwd = formGet(req.form['password'])
    email = formGet(req.form['email'])
    try:
        query = """ SELECT us.*
                FROM users as us
                WHERE us.username = '%s'
                """ % (usr)
        if (db.Cursor.execute(query) > 0):
            db.closeConnection()
            return esitMessage(2, 'Already a Registered User')
    except MySQLdb.Error:
        db.closeConnection()
        return esitMessage(20, 'Problem server')
    try:
        query = """ INSERT INTO users (username,password,email)
                    VALUE ('%s','%s','%s')
                    """ % (usr, pwd, email)
        if (db.Cursor.execute(query) > 0):
            result = db.Cursor.lastrowid
            sk = ''.join(random.choice('1gio2giu3') for _ in range(16))
            d = {}
            d['username'] = usr
            d['email'] = email
            d['id'] = result
            d['sk'] = sk
            session['username'] = usr
            session['user'] = esitMessage(1, d)
            session['sk'] = sk
            db.conn.commit()
            path = ROOT + '/' + usr
            os.mkdir(path)
            db.closeConnection()
            return esitMessage(1, d)
        else:
            db.closeConnection()
            return esitMessage(0, 'Registration Failed')
    except MySQLdb.Error:
        db.closeConnection()
        return esitMessage(20, 'Problem server')


@app.route('/logout', methods=['POST'])
def logout():
    if checkSecret():
        session.pop('username', None)
        session.pop('sk', None)
        session.pop('user', None)
        return esitMessage(1, 'Successful Logout')
    else:
        return esitMessage(5, 'Server Error')


@app.route('/createproject', methods=['POST'])
def createproject():
    if checkSecret():
        db = DataAccess()
        id = req.form['iduser']
        nome = formGet(req.form['nome'])
        try:
            query = """ SELECT pr.*
                    FROM projects as pr
                    WHERE pr.nome = '%s' AND pr.idUser = %s
                    """ % (nome, id)
            if (db.Cursor.execute(query) > 0):
                db.closeConnection()
                return esitMessage(2, 'Existing Project')
        except MySQLdb.Error:
            db.closeConnection()
            return esitMessage(20, 'Problem server')
        try:
            query = """INSERT INTO projects (nome,idUser)
                     VALUE ('%s',%s)
                  """ % (nome, id)
            if (db.Cursor.execute(query) > 0):
                db.conn.commit()
                query = """ SELECT us.username
                    FROM users as us
                    WHERE us.id = %s
                    """ % (id)
                db.Cursor.execute(query)
                usr = db.Cursor.fetchone()['username']
                path = ROOT + '/' + usr + '/' + nome
                os.mkdir(path)
                db.closeConnection()
                return esitMessage(1, 'Creating Successful')
            else:
                db.closeConnection()
                return esitMessage(0, 'Creating Failed')
        except MySQLdb.Error:
            db.closeConnection()
            return esitMessage(20, 'Problem server')

    else:
        return esitMessage(5, 'Server Error')


@app.route('/getprojects', methods=['POST'])
def getprojects():
    if checkSecret():
        db = DataAccess()
        idu = req.form['iduser']
        try:
            query = """SELECT pr.*
                     FROM projects as pr
                     WHERE pr.idUser = %s
                  """ % (idu)
            db.Cursor.execute(query)
            result = db.Cursor.fetchall()
            dd = []
            if (result <> None ):
                if (len(result) > 0):
                    for row in result:
                        d = {}
                        d['id'] = row['id']
                        d['nome'] = row['nome']
                        dd.append(d)
                    db.closeConnection()
                    return esitMessage(1, dd)
                else:
                    db.closeConnection()
                    return esitMessage(2, 'No existing project')
            else:
                db.closeConnection()
                return esitMessage(20, 'Problem server')
        except MySQLdb.Error:
            db.closeConnection()
            return esitMessage(20, 'Problem server')
    else:
        return esitMessage(5, 'Server Error')


@app.route('/getproject', methods=['POST'])
def getproject():
    if checkSecret():
        db = DataAccess()
        idu = req.form['iduser']
        idp = req.form['idproject']
        try:
            query = """SELECT pr.*
                     FROM projects as pr
                     WHERE pr.idUser = %s AND pr.id = %s
                  """ % (idu, idp)
            db.Cursor.execute(query)
            result = db.Cursor.fetchone()
            if (result <> None ):
                d = {}
                d['id'] = result['id']
                d['nome'] = result['nome']
                db.closeConnection()
                return esitMessage(1, d)
            else:
                db.closeConnection()
                return esitMessage(20, 'Problem server')
        except MySQLdb.Error:
            db.closeConnection()
            return esitMessage(20, 'Problem server')
    else:
        return esitMessage(5, 'Server Error')


@app.route('/renameproject', methods=['POST'])
def renameproject():
    if checkSecret():
        db = DataAccess()
        idu = req.form['iduser']
        id = req.form['idproject']
        nome = formGet(req.form['nome'])
        try:
            query = """UPDATE projects
                     SET nome = '%s'
                     WHERE projects.idUser = %s AND projects.id =%s
                  """ % (nome, idu, id)
            if (db.Cursor.execute(query) > 0):
                db.conn.commit()
                db.closeConnection()
                return esitMessage(1, 'Renaming Success')
            else:
                db.closeConnection()
                return esitMessage(0, 'Renaming Failed')
        except MySQLdb.Error:
            db.closeConnection()
            return esitMessage(20, 'Problem server')

    else:
        return esitMessage(5, 'Server Error')


@app.route('/deleteproject', methods=['POST'])
def deleteproject():
    if checkSecret():
        db = DataAccess()
        idu = req.form['iduser']
        idp = req.form['idproject']
        try:
            query = """SELECT fl.*
                     FROM files as fl
                     WHERE fl.idUser = %s AND fl.idProject = %s
                  """ % (idu, idp)
            db.Cursor.execute(query)
            result = db.Cursor.fetchall()
            #DELETE ALL FILE
            if (result <> None):
                for row in result:
                    idf = row['id']
                    idu = row['idUser']
                    idp = row['idProject']
                    #CREATION PATH FILES
                    query = """SELECT fl.url
                         FROM files as fl
                         WHERE fl.id= %s AND fl.idUser = %s AND fl.idProject = %s
                      """ % (idf, idu, idp)
                    db.Cursor.execute(query)
                    result = db.Cursor.fetchone()
                    path = result['url']
                    #DELETE FILE ON DB
                    idf = row['id']
                    query = """DELETE FROM  files
                             WHERE files.id= %s AND files.idUser = %s AND files.idProject = %s
                          """ % (idf, idu, idp)
                    if (db.Cursor.execute(query) > 0):
                        #DELETE FILE ON SYSTEM
                        abspath = ROOT + '/' + path
                        try:
                            os.remove(abspath)
                        except OSError:
                            db.conn.rollback()
                            db.closeConnection()
                            return esitMessage(0, 'Deleting File Failed')
                            #ATTENZIONE GESTIONE FILE CANCELLATI PRECEDENTEMENTE
                        db.conn.commit()
                    else:
                        db.closeConnection()
                        return esitMessage(0, 'Deleting File Failed')

            #CREATION PATH DIRECTORY PROJECT
            query = """SELECT pr.nome
                    FROM projects as pr
                    WHERE pr.id= %s AND pr.idUser = %s
                    """ % (idp, idu)
            db.Cursor.execute(query)
            result = db.Cursor.fetchone()
            nome = result['nome']
            query = """ SELECT us.username
                    FROM users as us
                    WHERE us.id = %s
                    """ % (idu)
            db.Cursor.execute(query)
            result = db.Cursor.fetchone()
            usr = result['username']
            path = ROOT + '/' + usr + '/' + nome
            #DELETE PROJECT ON DB  
            query = """DELETE FROM  projects
                    WHERE id= %s AND idUser = %s 
                    """ % (idp, idu)
            if (db.Cursor.execute(query) > 0):
                #DELETE PROJECT ON SYSTEM
                try:
                    os.rmdir(path)
                except OSError:
                    db.conn.rollback()
                    db.closeConnection()
                    return esitMessage(0, 'Deleting Project Failed')
                db.conn.commit()
            else:
                db.closeConnection()
                return esitMessage(0, 'Deleting Project Failed')
        except MySQLdb.Error:
            db.closeConnection()
            return esitMessage(20, 'Problem server')
    else:
        return esitMessage(5, 'Server Error')


@app.route('/createfile', methods=['POST'])
def createfile():
    if checkSecret():
        db = DataAccess()
        idu = req.form['iduser']
        idp = req.form['idproject']
        tipo = req.form['tipo']
        nomef = formGet(req.form['nome'])
        try:
            query = """ SELECT fl.*
                    FROM files as fl
                    WHERE fl.nome = '%s' AND fl.idUser = %s AND fl.idProject = %s
                    """ % (nomef, idu, idp)
            if (db.Cursor.execute(query) > 0):
                db.closeConnection()
                return esitMessage(2, 'Existing File')
        except MySQLdb.Error:
            db.closeConnection()
            print "ciao"
            return esitMessage(20, 'Problem server')
        try:
            query = """SELECT us.username
                     FROM users as us
                     WHERE us.id = %s
                  """ % (idu)
            db.Cursor.execute(query)
            result = db.Cursor.fetchone()
            if (result <> None):
                nomeu = result['username']
            else:
                db.closeConnection()
                return esitMessage(0, 'User does not exist')
            query = """SELECT pr.nome
                     FROM projects as pr
                     WHERE pr.id = %s AND pr.idUser = %s
                  """ % (idp, idu)
            db.Cursor.execute(query)
            result = db.Cursor.fetchone()
            if (result <> None):
                nomep = result['nome']
            else:
                db.closeConnection()
                return esitMessage(0, 'Project does not exist')
        except MySQLdb.Error:
            db.closeConnection()
            print "ciao1"
            return esitMessage(20, 'Problem server')
        print tipo
        if tipo == '1':
            path = '/' + nomeu + '/' + nomep + '/' + nomef + '.txt'
        else:
            path = '/' + nomeu + '/' + nomep + '/' + nomef + '.pl'
        try:
            query = """INSERT INTO files (nome,idUser,idProject,tipo,url)
                     VALUE ('%s',%s,%s,'%s','%s')
                  """ % (nomef, idu, idp, tipo, path)
            if (db.Cursor.execute(query) > 0):
                idf = db.Cursor.lastrowid
                abspath = ROOT + path
                try:
                    fo = open(abspath, "wb")
                    fo.close()
                except OSError:
                    db.conn.rollback()
                    return esitMessage(0, 'Creating File Failed')
                d = {}
                d['id'] = idf
                d['nome'] = nomef
                d['tipo'] = tipo
                db.conn.commit()
                db.closeConnection()
                return esitMessage(1, d)
            else:
                db.closeConnection()
                return esitMessage(0, 'Creating File Failed')
        except MySQLdb.Error:
            db.closeConnection()
            print "ciao2"
            return esitMessage(20, 'Problem server')

    else:
        return esitMessage(5, 'Server Error')


@app.route('/deletefile', methods=['POST'])
def deletefile():
    if checkSecret():
        db = DataAccess()
        idu = req.form['iduser']
        idp = req.form['idproject']
        idf = req.form['id']
        try:
            query = """SELECT fl.url
                     FROM files as fl
                     WHERE fl.id= %s AND fl.idUser = %s AND fl.idProject = %s
                  """ % (idf, idu, idp)
            db.Cursor.execute(query)
            result = db.Cursor.fetchone()
            path = result['url']
            query = """DELETE FROM  files
                     WHERE files.id= %s AND files.idUser = %s AND files.idProject = %s
                  """ % (idf, idu, idp)
            if (db.Cursor.execute(query) > 0):
                abspath = ROOT + '/' + path
                try:
                    os.remove(abspath)
                except OSError:
                    db.conn.rollback()
                    return esitMessage(0, 'Deleting File Failed')
                db.conn.commit()
                db.closeConnection()
                return esitMessage(1, 'Deleting File Success')
            else:
                db.closeConnection()
                return esitMessage(0, 'Deleting File Failed')
        except MySQLdb.Error:
            db.closeConnection()
            return esitMessage(20, 'Problem server')

    else:
        return esitMessage(5, 'Server Error')


@app.route('/getfiles', methods=['POST'])
def getfiles():
    if checkSecret():
        db = DataAccess()
        idu = req.form['iduser']
        idp = req.form['idproject']
        try:
            query = """SELECT fl.*
                     FROM files as fl
                     WHERE fl.idProject = %s AND fl.idUser = %s
                  """ % (idp, idu)
            db.Cursor.execute(query)
            result = db.Cursor.fetchall()
            dd = []
            if (result <> None ):
                if (len(result) > 0):
                    for row in result:
                        d = {}
                        d['id'] = row['id']
                        d['nome'] = row['nome']
                        d['tipo'] = row['tipo']
                        dd.append(d)
                    db.closeConnection()
                    return esitMessage(1, dd)
                else:
                    db.closeConnection()
                    return esitMessage(2, 'No existing files')
            else:
                db.closeConnection()
                return esitMessage(20, 'Problem server')
        except MySQLdb.Error:
            db.closeConnection()
            return esitMessage(20, 'Problem server')
    else:
        return esitMessage(5, 'Server Error')


@app.route('/getfile', methods=['POST'])
def getfile():
    if checkSecret():
        db = DataAccess()
        idf = req.form['idfile']
        idp = req.form['idproject']
        idu = req.form['iduser']
        try:
            query = """SELECT fl.*
                     FROM files as fl
                     WHERE fl.idProject = %s AND fl.idUser = %s AND id = %s
                  """ % (idp, idu, idf)
            db.Cursor.execute(query)
            result = db.Cursor.fetchone()
            if (result <> None):
                d = {}
                d['id'] = result['id']
                d['nome'] = result['nome']
                d['tipo'] = result['tipo']
                if result['tipo'] == "1":
                    extention = ['txt', 'plv', 'plf', 'ple', 'pl']
                    path = result['url']
                    pathnoext = path.split('.txt')[0] + '.'

                    text = {}
                    for ext in extention:
                        abspath = ROOT + '/' + pathnoext + ext
                        if os.path.isfile(abspath):
                            f = open(abspath, "rb")
                            text[ext] = f.read()
                    d['text'] = text['txt']
                else:
                    path = result['url']
                    abspath = ROOT + '/' + path
                    f = open(abspath, "rb")
                    text = f.read()
                    d['text'] = text
                db.closeConnection()
                return esitMessage(1, d)
            else:
                db.closeConnection()
                return esitMessage(20, 'Problem server')
        except MySQLdb.Error:
            db.closeConnection()
            return esitMessage(20, 'Problem server')
    else:
        return esitMessage(5, 'Server Error')


@app.route('/savefile', methods=['POST'])
def savefile():
    if checkSecret():
        db = DataAccess()
        idf = req.form['idfile']
        idp = req.form['idproject']
        idu = req.form['iduser']
        text = req.form['text']
        try:
            query = """SELECT fl.*
                     FROM files as fl
                     WHERE fl.idProject = %s AND fl.idUser = %s AND id = %s
                  """ % (idp, idu, idf)
            db.Cursor.execute(query)
            result = db.Cursor.fetchone()
            if (result <> None):
                path = result['url']
                abspath = ROOT + '/' + path
                f = open(abspath, "wb")
                text = f.write(text)
                f.close()
                db.closeConnection()
                return esitMessage(1, 'OK Save')
            else:
                db.closeConnection()
                return esitMessage(20, 'Problem server')
        except MySQLdb.Error:
            db.closeConnection()
            return esitMessage(20, 'Problem server')
    else:
        return esitMessage(5, 'Server Error')

def esitMessage(esit, message):
    KEY_ESIT = 'esit'
    KEY_MESSAGE = 'result'

    dd = {}
    dd[KEY_ESIT] = esit
    dd[KEY_MESSAGE] = message

    return json.dumps(dd)


def formGet(value):
    return value.replace("'", "''")


class RootResource(resource.Resource):
    def __init__(self):
        resource.Resource.__init__(self)

    def getChild(self, name, request):
        if name == "api":
            return WSGIResource(reactor, reactor.getThreadPool(), app)
        elif name == 'app':
            return File('app')
        else:
            return resource.NoResource()


def checkSecret():
    if req.headers.has_key('di') and 'sk' in session and req.headers['di'] == session['sk']:
        return True
    else:
        if req.form.has_key('abracadabra'):
            return True
        return False


application = service.Application(SECRET_KEY)

reactor.listenTCP(int(configFile.get('Server', 'ServerPort')), server.Site(RootResource()))
reactor.run()
