from flask import Flask, render_template, make_response, request, redirect, url_for
app = Flask(__name__)
import cs304dbi as dbi

@app.route('/')
def home():
    return render_template("base.html")

@app.route('/tt/<tt>', methods=["GET"])
def movie_page(tt):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('select * from movie limit 10')
    curs.execute('select title from movie where tt=%s', [tt])
    movieResult = curs.fetchall()
    name = movieResult[0].get('title')
    releaseYear = movieResult[0].get('release')
    conn.commit()
    return render_template("movie.html")

@app.route('/nm/<nm>', methods=["GET"])
def person_page(nm):

    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    curs.execute('select name,birthdate from person where nm=%s', [nm])
    personRes = curs.fetchall()
    if (curs.rowcount == 1):
        name = personRes[0].get('name')
        birthDate = personRes[0].get('birthdate')
    else:
        name = None
        birthDate = None

    curs.execute('select title, movie.tt from movie inner join credit on credit.tt=movie.tt where nm=%s', [nm])
    movieRes = curs.fetchall()
    if curs.rowcount == 0:
        movieRes = None

    conn.commit()
    
    return render_template("actor.html", name=name, adder="Leila Peterson", birthdate=birthDate, movies=movieRes)


@app.before_first_request
def init_db():
    dbi.cache_cnf()
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