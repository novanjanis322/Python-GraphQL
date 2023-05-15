from flask import Flask
from flask_mysqldb import MySQL
from flask_graphql import GraphQLView
import graphene



app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost' 
app.config['MYSQL_USER'] = 'root' 
app.config['MYSQL_PORT'] = 3360 
app.config['MYSQL_PASSWORD'] = '' 
app.config['MYSQL_DB'] = 'perpustakaan' 
mysql = MySQL (app)

class mahasiswa(graphene.ObjectType):
    # Define the fields for the 'mahasiswa' type
    NIM = graphene.Int()
    nama_mahasiswa = graphene.String()
    jurusan = graphene.String()
    tanggal_lahir = graphene.Date()
    usia = graphene.Int()
    jenis_kelamin = graphene.String()
    alamat = graphene.String()
    no_hp = graphene.String()

    # Add more fields based on your database schema
class Updatemahasiswa(graphene.Mutation):
    class Arguments:
        NIM = graphene.Int(required=True)
        nama_mahasiswa = graphene.String()
        jurusan = graphene.String()
        tanggal_lahir = graphene.Date()
        usia = graphene.Int()
        jenis_kelamin = graphene.String()
        alamat = graphene.String()
        no_hp = graphene.String()

    mahasiswa = graphene.Field(mahasiswa)

    def mutate(self, info, NIM, nama_mahasiswa, jurusan, tanggal_lahir, usia, jenis_kelamin, alamat, no_hp):
        cursor = mysql.connection.cursor()
        query = "update tb_mahasiswa set nama_mahasiswa=%s, jurusan=%s, tanggal_lahir=%s, usia=%s, jenis_kelamin=%s, alamat=%s, no_hp=%s where NIM=%s"
        values = ( nama_mahasiswa, jurusan, tanggal_lahir, usia, jenis_kelamin, alamat, no_hp, NIM)
        cursor.execute(query, values)
        mysql.connection.commit()

        # Retrieve the inserted mahasiswa record
        cursor.execute("SELECT * FROM tb_mahasiswa WHERE NIM = %s", (NIM,))
        col_names = [i[0] for i in cursor.description]
        data = cursor.fetchone()
        inserted_mahasiswa = dict(zip(col_names, data))
        return Createmahasiswa(mahasiswa=mahasiswa(**inserted_mahasiswa))

class Createmahasiswa(graphene.Mutation):
    class Arguments:
        NIM = graphene.Int(required=True)
        nama_mahasiswa = graphene.String(required=True)
        jurusan = graphene.String(required=True)
        tanggal_lahir = graphene.Date(required=True)
        usia = graphene.Int(required=True)
        jenis_kelamin = graphene.String(required=True)
        alamat = graphene.String(required=True)
        no_hp = graphene.String(required=True)

    mahasiswa = graphene.Field(mahasiswa)

    def mutate(self, info, NIM, nama_mahasiswa, jurusan, tanggal_lahir, usia, jenis_kelamin, alamat, no_hp):
        cursor = mysql.connection.cursor()
        query = "INSERT INTO tb_mahasiswa (NIM, nama_mahasiswa, jurusan, tanggal_lahir, usia, jenis_kelamin, alamat, no_hp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        values = (NIM, nama_mahasiswa, jurusan, tanggal_lahir, usia, jenis_kelamin, alamat, no_hp)
        cursor.execute(query, values)
        mysql.connection.commit()

        # Retrieve the inserted mahasiswa record
        cursor.execute("SELECT * FROM tb_mahasiswa WHERE NIM = %s", (NIM,))
        col_names = [i[0] for i in cursor.description]
        data = cursor.fetchone()
        inserted_mahasiswa = dict(zip(col_names, data))
        return Createmahasiswa(mahasiswa=mahasiswa(**inserted_mahasiswa))


class Query(graphene.ObjectType):
    mahasiswa = graphene.List(mahasiswa)
    mahasiswaByNIM = graphene.Field(mahasiswa, NIM=graphene.Int(required=True))


    def resolve_mahasiswa(self, info):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM tb_mahasiswa")
        col_names = [i[0] for i in cursor.description]
        data = []
        for row in cursor.fetchall():
            data.append(dict(zip(col_names, row)))
        return [mahasiswa(**item) for item in data]
    
    def resolve_mahasiswaByNIM(self, info, NIM):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM tb_mahasiswa WHERE NIM = %s", (NIM,))
        col_names = [i[0] for i in cursor.description]
        data = cursor.fetchone()

        if data is not None:
            return mahasiswa(**dict(zip(col_names, data)))
        else:
            return []
        
class Deletemahasiswa(graphene.Mutation):
    class Arguments:
        NIM = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, NIM):
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM tb_mahasiswa WHERE NIM = %s", (NIM,))
        mysql.connection.commit()

        # Check if any row was affected by the delete operation
        success = cursor.rowcount > 0

        return Deletemahasiswa(success=success)

class Mutation(graphene.ObjectType):
    create_mahasiswa = Createmahasiswa.Field()
    update_mahasiswa = Updatemahasiswa.Field()
    delete_mahasiswa = Deletemahasiswa.Field()
    
schema = graphene.Schema(query=Query, mutation=Mutation)

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True)
)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=50, debug=True)

