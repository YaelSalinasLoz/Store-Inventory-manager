import sys
from PyQt6.uic import loadUi
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import *
from PyQt6.QtSql import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import sqlite3 as sql
    
username_global = ''

class WelcomeScreen(QMainWindow):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        loadUi("ventanaPrincipal.ui", self)
        self.pushButton.clicked.connect(self.gotoRegister)
        self.pushButton_2.clicked.connect(self.loginFunction)

    def gotoRegister(self):
        register = registerScreen()
        widget.addWidget(register)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
    def loginFunction(self):
        username = self.lineEdit.text()
        password = self.lineEdit_2.text()
        if len(username) == 0 or len(password) == 0:
            self.aviso_lineedit.setText("Por favor llena todos los campos.")
        if (username == "admin" and password == "admin"):
         self.gotoAdminPage()
        if (len(username) != 0 or len(password) != 0):
            con = sql.connect("user_data.db")
            cursor = con.cursor()
            cursor.execute("SELECT username, password, rol FROM usuario WHERE username = ? AND password = ? AND rol = 'admin'", (username, password))
            if cursor.fetchall():
                self.gotoAdminPage()
            else:
                pass
        if (len(username) != 0 or len(password) != 0):
            con = sql.connect("user_data.db")
            cursor = con.cursor()
            cursor.execute("SELECT username, password FROM usuario WHERE username = ? AND password = ? AND rol = 'usuario'", (username, password))
            if cursor.fetchall():
                global username_global 
                username_global = username
                self.user_entrar()
                
            else:
                self.aviso_lineedit.setText("El usuario o la contraseña son incorrectos")
    
    def user_entrar(self):
        user = userScreen()
        widget.addWidget(user)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotoAdminPage(self):
        admin = adminScreen()
        widget.addWidget(admin)
        widget.setCurrentIndex(widget.currentIndex()+1)
    



class registerScreen(QMainWindow):
    def __init__(self):
        super(registerScreen, self).__init__()
        loadUi("ventanaRegistro.ui", self)
        self.pushButton_3.clicked.connect(self.gotoLogin)
        self.registrar.clicked.connect(self.registerFunction)

    def gotoLogin(self):
        login = WelcomeScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def registerFunction(self):
        username = self.user_lineedit.text()
        password = self.password_lineedit.text()
        rol = "usuario"
        if len(username) == 0 or len(password) == 0:
            self.aviso.setText("Por favor llena todos los campos.")
        else:
            q = QSqlQuery()
            if (q.prepare("insert into usuario (username, password, rol) values (?,?,?)")):
                q.addBindValue(username)
                q.addBindValue(password)
                q.addBindValue(rol)
                if (q.exec()):      
                    self.aviso.setText("")
                    self.exito.setText("Usuario creado con éxito")      
                    self.user_lineedit.clear()
                    self.password_lineedit.clear()
                else:
                    self.aviso.setText("Usuario ya utilizado. Intente con otro")


class adminScreen(QMainWindow):
    def __init__(self):
        super(adminScreen, self).__init__()
        loadUi("ventanaAdmin.ui", self)
        self.alta_boton.clicked.connect(self.registerFunction)
        self.refresh_button.clicked.connect(self.refreshTables)
        self.salirButton.clicked.connect(self.gotoLogin)

        self.modificarTimer = QTimer(self)
        self.modificarTimer.setSingleShot(True)
        self.modificarTimer.setInterval(1000)
        self.modificarTimer.timeout.connect(self.modificarTimers)

        self.buscarModel = QSqlQueryModel(self)
        self.buscarModel.setQuery("select * from productos")
        self.buscar_tableview.setModel(self.buscarModel)
        self.buscar_lineedit.textEdited.connect(self.buscarNombre)

        self.modificarModel = QSqlTableModel(self)
        self.modificarModel.setTable("productos")
        self.modificarModel.select()
        self.editar_table.setModel(self.modificarModel)
        self.modificarModel.beforeUpdate.connect(self.modificarModel_update)

        self.buscarHistorial = QSqlQueryModel(self)
        self.buscarHistorial.setQuery("select * from historial")
        self.ver_historial.setModel(self.buscarHistorial)
        self.buscar_lineedit_2.textEdited.connect(self.buscarNombre_histo)
        
        self.verModel = QSqlTableModel(self)
        self.verModel.setTable("usuario")
        self.verModel.select()
        self.ver_users.setModel(self.verModel)
        self.verModel.beforeUpdate.connect(self.modificarModel_update)

        self.eliminarModel = QSqlTableModel(self)
        self.eliminarModel.setTable("productos")
        self.eliminarModel.select()
        self.eliminar_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.eliminar_table.setModel(self.eliminarModel)
        self.eliminar_table.clicked.connect(self.eliminarTable)
        
    def modificarModel_update(self, row, record):
        self.modificarTimer.start()

    def refreshTables(self):
        self.buscarModel.setQuery("select * from productos")
        self.eliminarModel.select()
        self.modificarModel.select()

    def modificarTimers(self):
        self.refreshTables()

    def eliminarTable(self, idx):
        row = idx.row()
        if(self.eliminarModel.removeRow(row)):
            self.eliminarModel.select()
 
    def buscarNombre(self, txt):
        self.buscarModel.setQuery("select * from productos where nombre_producto like '%" + txt + "%'")
    
    def buscarNombre_histo(self, txt):
        self.buscarHistorial.setQuery("select * from historial where nombre_cliente like '%" + txt + "%'")

    def registerFunction(self):
        producto = self.producto_lineedit.text()
        cantidad = self.cantidad_lineedit.text()
        precio = self.precio_lineedit.text()
        if len(producto) == 0 or len(cantidad) == 0 or len(precio) == 0:
            self.aviso.setText("Por favor llena todos los campos.")
        elif int(precio) < 0:
            self.aviso.setText("Precio inválido.")
        else:
            q = QSqlQuery()
            if (q.prepare("insert into productos (nombre_producto, cantidad, precio) values (?,?,?)")):
                q.addBindValue(producto)
                q.addBindValue(cantidad)
                q.addBindValue(precio)
                if (q.exec()):      
                    self.aviso.setText("")
                    self.exito_lineedit.setText("Producto añadido con éxito")  
                    self.producto_lineedit.clear()    
                    self.cantidad_lineedit.clear()
                    self.precio_lineedit.clear()
                else:
                    self.exito_lineedit.setText("")
                    self.aviso.setText("Producto ya en existencia. Intente otro")
        self.refreshTables()

    def gotoLogin(self):
        login = WelcomeScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class userScreen(QMainWindow):
    def __init__(self):
        global username_global
        username = username_global
        super(userScreen, self).__init__()
        loadUi("ventanaUser.ui", self)
        
        self.salirButton.clicked.connect(self.gotoLogin)
        self.confirmar_compra.clicked.connect(self.comprarFuncion)
        self.refresh_button.clicked.connect(self.refreshTables)
        self.refresh_button.clicked.connect(self.borrarLabel)

        self.modificarTimer = QTimer(self)
        self.modificarTimer.setSingleShot(True)
        self.modificarTimer.setInterval(1000)
        self.modificarTimer.timeout.connect(self.modificarTimers)

        self.buscarModel = QSqlQueryModel(self)
        self.buscarModel.setQuery("select * from productos")
        self.buscar_tableview.setModel(self.buscarModel)
        self.buscar_lineedit.textEdited.connect(self.buscarNombre)

        self.buscarHistorial = QSqlQueryModel(self)
        self.buscarHistorial.setQuery("select * from historial where nombre_cliente like '%" + username + "%'")
        self.ver_historial.setModel(self.buscarHistorial)

        #Cambiar usuario
        self.confirmar_boton_2.clicked.connect(self.modificar_user)
        #Cambiar contraseña
        self.confirmar_boton_3.clicked.connect(self.modificar_pass)

    def agregarUsuario(self, username):
        self.lista_temp.append(username)
        self.username = username
        print(username)

    
    def borrarLabel(self):
        self.aviso_compra.setText("")
        self.aviso_compra_2.setText("")


    def refreshTables(self):
        global username_global
        username = username_global
        self.buscarModel.setQuery("select * from productos")
        self.buscarHistorial.setQuery("select * from historial where nombre_cliente like '%" + username + "%'")


    def modificarTimers(self):
        self.refreshTables()

    
    def comprarFuncion(self):
        
        global username_global
        username = username_global

        conn = sql.connect("user_data.db")
        cursor = conn.cursor()
        temp_nombre = self.nombre_comprar.text()
        temp_cantidad = self.cantidad_comprar.text()
        
        if len(temp_cantidad) == 0 or len(temp_nombre) == 0:
            self.aviso_compra.setText("Rellene los campos")
        elif int(temp_cantidad) < 1:
            self.aviso_compra.setText("Cantidad no válida")
        elif len(temp_cantidad) != 0 and len(temp_nombre) != 0:
            if("SELECT * FROM productos WHERE nombre_producto = ?", (temp_nombre,)):
                instruccion_temp = (f"SELECT cantidad FROM productos WHERE nombre_producto = '{temp_nombre}'")
                cursor.execute(instruccion_temp)
                cantidad_vieja = cursor.fetchone()
                if((cantidad_vieja) is not None):
                    cantidad_vieja_ = cantidad_vieja[0]
                    if(int(cantidad_vieja_) < int(temp_cantidad)):
                        self.aviso_compra.setText("No hay productos suficientes")
                        self.aviso_compra_2.setText("")
                    else:
                        cantidad_nueva = int(cantidad_vieja_) - int(temp_cantidad) 
                        cursor.execute("UPDATE productos SET cantidad = ? WHERE nombre_producto= ?",(cantidad_nueva, temp_nombre))
                        self.aviso_compra.setText("")
                        self.nombre_comprar.clear()
                        self.cantidad_comprar.clear()
                        self.aviso_compra_2.setText("Compra realizada correctamente")
                        #CREAMOS EL HISTORIAL DE LA COMPRA
                        cantidad_total = temp_cantidad
                        instruccion_temp_3 = (f"SELECT precio FROM productos WHERE nombre_producto = '{temp_nombre}'")
                        cursor.execute(instruccion_temp_3)
                        precio_temp = cursor.fetchone()
                        total = float(cantidad_total) * float(precio_temp[0])
                        instruccion_temp_2 = (f"INSERT INTO historial (nombre_cliente, nombre_producto, cantidad, total) values ('{(username)}','{temp_nombre}',{temp_cantidad},{total})")
                        cursor.execute(instruccion_temp_2)
                        
                else:
                    self.aviso_compra.setText("")
                    self.aviso_compra_2.setText("")
                    self.aviso_compra.setText("Nombre no encontrado")
        cursor.close()
        conn.commit()
        conn.close()

    def conectar(self):
        conexion = sql.connect("user_data.db")
        cursor = conexion.cursor()
        return conexion, cursor

    def buscarNombre(self, txt):
        self.buscarModel.setQuery("select * from productos where nombre_producto like '%" + txt + "%'")

    def modificar_user(self):
        nombre_actual = self.contra_lineedit_2.text()
        cambiar_usuario = self.contra_lineedit_3.text()
        conexion, cursor = self.conectar()
        if len(nombre_actual) == 0 or len(cambiar_usuario) == 0:
            self.aviso_label.setText("Complete todos los datos")
        elif len(nombre_actual) != 0 or len(cambiar_usuario) != 0:
            if("SELECT * FROM usuario WHERE username = ?",(cambiar_usuario,)):
                instrucion_temp = (f"SELECT username FROM usuario WHERE username = '{cambiar_usuario}'")
                cursor.execute(instrucion_temp)
                user_temp = cursor.fetchone()
                if(user_temp is not None):
                    if(user_temp[0] == cambiar_usuario):
                        self.aviso_label.setText("Usuario ya utilizado, intente con otro.")
                else:
                    cursor.execute("UPDATE usuario SET username= ? WHERE username=?",(cambiar_usuario, nombre_actual))
                    self.contra_lineedit_2.clear()
                    self.contra_lineedit_3.clear()
                    self.aviso_label.setText("Listo")
        cursor.close()
        conexion.commit()
        conexion.close()
        
    def modificar_pass(self):
        nombre_actual = self.contra_lineedit_5.text()
        cambiar_contrasena = self.contra_lineedit_4.text()
        conexion, cursor = self.conectar()
        if len(nombre_actual) == 0 or len(cambiar_contrasena) == 0:
            self.aviso_label.setText("Complete todos los datos")
        else:
            cursor.execute("UPDATE usuario SET password = ? WHERE username = ?",(cambiar_contrasena, nombre_actual))
            self.contra_lineedit_4.clear()
            self.contra_lineedit_5.clear()
            self.aviso_label_2.setText("Listo")
        cursor.close()
        conexion.commit()
        conexion.close()

    def confirmarPass(self):
        usuario_confirm = self.contra_lineedit.text()
        if len(usuario_confirm) == 0:
            self.aviso_lineedit.setText("ERROR. Llene el campo")
        else:
            con = sql.connect("user_data.db")
            cursor = con.cursor()
            cursor.execute("SELECT * FROM usuario WHERE username = ?",(usuario_confirm,))
            if(cursor.fetchall()):
                self.aviso_lineedit.setText("")
                self.verModel = QSqlQueryModel(self)
                self.verModel.setQuery("select * from usuario where username like '%" + usuario_confirm + "%'")
                self.buscar_tableview.setModel(self.verModel)
            else:
                self.aviso_lineedit.setText("Usuario incorrecto")

    def gotoLogin(self):
        global username_global
        username_global = ''
        login = WelcomeScreen()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex() + 1)


def prepareDatabase():
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName("user_data.db")
    if (db.open()):
        q = QSqlQuery()
        if (q.prepare("create table if not exists usuario(id integer primary key autoincrement not null, username type UNIQUE, password text not null, rol not null)")):
            if (q.exec()):
                print("Tabla usuario creada con éxito...")
        if (q.prepare("create table if not exists productos(id integer primary key autoincrement not null, nombre_producto type UNIQUE, cantidad integer not null, precio real not null)")):
            if (q.exec()):
                print("Tabla productos creada con éxito...")
        if (q.prepare("create table if not exists historial(id integer primary key autoincrement not null, nombre_cliente text not null, nombre_producto text not null, cantidad integer not null, total real not null)")):
            if (q.exec()):
                print("Tabla historial creada con éxito...")
        

    

# Main
prepareDatabase()
app = QApplication(sys.argv)
welcome = WelcomeScreen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(welcome)
widget.show()
try:
    sys.exit(app.exec())
except:
    print("Saliendo")