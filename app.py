import sqlite3

from flask import Flask, render_template, request, redirect

from flaskext.mysql import MySQL

app = Flask(__name__)

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'Database'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route("/")
def index():
    return render_template("home.html")


@app.route('/database')
def list_databases():
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]
    res = []
    for table in tables:
        cursor.execute(f"SELECT * FROM {table}")
        row_count = len(cursor.fetchall())
        res.append([table, row_count])
    db.close()
    return render_template('database.html', tables=res)



@app.route("/database/<string:name>",methods=['POST','GET'])
def database(name=None):
    db = mysql.connect()
    sql = db.cursor()
    sql.execute(f"SHOW COLUMNS FROM {name}")
    column_names = [value[0] for value in sql.fetchall()]
    if request.method == 'GET':
        sql.execute(f"SELECT * FROM {name}")
        data = sql.fetchall()
        db.commit()
        db.close()
        return render_template("table_display.html",name=name, data=data, column_names = column_names)
    if request.method == 'POST':
        filters = [[column] for column in column_names]

        for column in column_names:
            filters[column_names.index(column)].append(request.form[f"{column}_filter"])

        query = f"SELECT * FROM {name} WHERE 1=1"
        for val in filters:
            if val:
                query += f" AND {val[0]} LIKE '%{val[1]}%'"
        sql.execute(query)
        filtered_products = sql.fetchall()
        db.close()
        return render_template("table_display.html", name=name,data=filtered_products, column_names = column_names)

@app.route("/database/<string:name>/edit/<int:id>",methods=['POST','GET'])
def edit_deal(name,id):
    db = mysql.connect()
    sql = db.cursor()
    sql.execute(f"SHOW COLUMNS FROM {name}")
    column_names =  [value[0] for value in sql.fetchall()]
    sql.execute(f"SELECT * FROM {name} WHERE id = {id}")
    data = sql.fetchall()[0]
    if request.method == 'GET':
        db.commit()
        db.close()
        return render_template("edit_record.html", id = id, name=name,data=data, column_names = column_names)
    if request.method == 'POST':
        if request.form['action'] == 'edit':
            column_names_tmp = column_names.copy()
            column_names_tmp.remove("id")
            edits = [[column] for column in column_names_tmp]

            for column in column_names_tmp:
                edits[column_names_tmp.index(column)].append(request.form[f"{column}_edit"])

            query = f"UPDATE {name} SET "
            for val in edits:
                if val:
                    query += f"{val[0]} = '{val[1]}', "
            query = query.rstrip(', ')
            query += f"WHERE id = {id}"
            sql.execute(query)
            db.commit()
            db.close()
            data = [data[0]] + [val[1] for val in edits]

            return render_template("edit_record.html", id=id, name=name, data=data, column_names=column_names)
        if request.form['action'] == 'delete':
            sql.execute(f"DELETE FROM {name} WHERE id = {id}")
            db.commit()
            db.close()
            return redirect(f'/database/{name}')
        else:
            return redirect(f'/database/{name}')


@app.route("/database/<string:name>/add", methods=['GET','POST'])
def add_deal(name):
    db = mysql.connect()
    sql = db.cursor()
    sql.execute(f"SHOW COLUMNS FROM {name}")
    column_names = [value[0] for value in sql.fetchall()]
    sql.execute(f"SELECT * FROM {name}")
    data = sql.fetchall()
    if request.method == 'GET':
        return render_template('add_deal.html', name=name, column_names = column_names)
    if request.method == 'POST':
        max_id = max([val[0] for val in data]) + 1
        column_names_tmp = column_names.copy()
        column_names_tmp.remove("id")

        values = [request.form[f"{column}_add"] for column in column_names_tmp]

        column_names_str = ', '.join(column_names_tmp)

        values_sql = ', '.join([f"'{value}'" for value in values])

        query = f"INSERT INTO {name} (id,{column_names_str}) VALUES ({max_id}, {values_sql});"
        sql.execute(query)
        db.commit()

        return redirect(f'/database/{name}')

    else:
        return redirect(f'/database/{name}')

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == "__main__":
    app.run(debug=True)
