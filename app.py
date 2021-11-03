from flask import Flask, render_template, make_response, request, redirect, url_for
app = Flask(__name__)
import cs304dbi as dbi

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/tt/<tt>', methods=["GET"])
def movie_page(tt):
    if not str.isdigit(tt):
        return render_template("error.html")

    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('select title,`release`, addedby from movie where tt=%s', [tt])
    movieResult = curs.fetchall()
    if (curs.rowcount == 1):
        title = movieResult[0].get('title')
        releaseYear = movieResult[0].get('release')
        adder = movieResult[0].get('addedby')
    else:
        title = None
        releaseYear = None
        adder = None
    if adder:
        curs.execute('select name from staff where uid={}'.format(adder))
        staffRes = curs.fetchall()
        if curs.rowcount == 1:
            adder = staffRes[0].get('name')
        else:
            adder= None

    curs.execute('select name, person.nm, birthdate from person inner join credit on person.nm=credit.nm where tt=%s', [tt])
    personResult = curs.fetchall()
    if curs.rowcount == 0:
        personResult = None
    conn.commit()
    return render_template("movie.html", title=title, release = releaseYear, adder=adder, cast = personResult)

@app.route('/nm/<nm>', methods=["GET"])
def person_page(nm):
    if not str.isdigit(nm):
        return render_template("error.html")

    conn = dbi.connect()   
    curs = dbi.dict_cursor(conn)
    curs.execute('select name,birthdate, addedby from person where nm=\'{}\''.format(nm))
    personRes = curs.fetchall()
    if (curs.rowcount == 1):
        name = personRes[0].get('name')
        birthDate = personRes[0].get('birthdate')
        adder = personRes[0].get('addedby')
    else:
        name = None
        birthDate = None
        adder = None
    if adder:
        curs.execute('select name from staff where uid={}'.format(adder))
        staffRes = curs.fetchall()
        if curs.rowcount == 1:
            adder = staffRes[0].get('name')
        else:
            adder = None

    curs.execute('select title, `release`, movie.tt from movie inner join credit on credit.tt=movie.tt where nm=%s', [nm])
    movieRes = curs.fetchall()
    if curs.rowcount == 0:
        movieRes = None

    curs.execute
    conn.commit()
    
    return render_template("person.html", name=name, adder=adder, birthdate=birthDate, movies=movieRes)

@app.route('/query/', methods=["GET"])
def query_page():
    kind = request.args.get("kind")
    query = request.args.get("query")
    returnTemplate = render_template("error.html")
    conn = dbi.connect()   
    curs = dbi.dict_cursor(conn)
    if kind == 'movie':
        curs.execute( ('select title, `release`, tt from movie where lower(title) like lower(\'%{}%\')'.format(query)) )
        movieRes = curs.fetchall()
        if curs.rowcount == 1:
            tt = movieRes[0].get('tt')
            returnTemplate = redirect( url_for('movie_page', tt=str(tt)) )
        else:
            returnTemplate = render_template("movie-query.html", query=query, movies = movieRes)
    if kind == 'person':
        curs.execute( ('select name, birthdate, nm from person where lower(name) like lower(\'%{}%\')'.format(query)) )
        personRes = curs.fetchall()
        if curs.rowcount == 1:
            nm = personRes[0].get('nm')
            returnTemplate = redirect( url_for('person_page', nm=str(nm)) )
        else:
            returnTemplate = render_template("person-query.html", query=query, persons = personRes)
    conn.commit()
    return returnTemplate

@app.before_first_request
def init_db():
    dbi.cache_cnf(db='wmdb')
    # we omit the dbi.use() so that you'll get your personal db

if __name__ == '__main__':
    import sys,os
    if len(sys.argv) > 1:
        # arg, if any, is the desired port number
        port = int(sys.argv[1])
        assert(port>1024)
    else:
        port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)