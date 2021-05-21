from flask import Flask, render_template, request
from tinydb import TinyDB, Query
from redis import Redis
from rq import Queue, Retry
from worker import worker_func
import os
import validators

app = Flask(__name__, template_folder="static")
q = Queue(connection=Redis())
db = TinyDB('db.json')


@app.route('/')
def home():
    return "Bem vindo ao teste do Duarte. Acesse /links ou /screenshots para continuar"


@app.route('/links', methods=['GET', 'POST', 'DELETE'])
def links():
    url = request.form.get("url")
    url_found = db.search(Query().url == url)
    if request.method == 'POST' and 'delete' not in request.form.keys():
        if url_found:   # Evitar duplicadas
            msg = "Url já existe"
            return return_with_url_list_msg(msg)

        elif not validators.url(url):  # Validar Url
            msg = "A Url não é valida"
            return return_with_url_list_msg(msg)

        else:
            user_input = {'url': url}
            db.insert(user_input)
            msg = 'Nova url cadastrada'
            result = q.enqueue(worker_func, url, retry=Retry(max=3, interval=[10, 30, 60]))
            return return_with_url_list_msg(msg)

    if request.method == 'POST' and 'delete' in request.form.keys():
        db.remove(Query().url == request.form['delete'])
        msg = "Url deletada"
        return return_with_url_list_msg(msg)

    return return_with_url_list_msg()


def return_with_url_list_msg(msg=''):
    url_list = [x['url'] for x in db.all()]
    return render_template('index.html', message=msg, url_list=url_list)


@app.route('/screenshots')
def screenshots():
    url_list = [x['url'].split('www.')[1] for x in db.all()]

    files = os.listdir("./ss/")

    url_list_with_ss = group_screenshots_by_origin(files, url_list)

    sort_screenshots(url_list_with_ss)

    return render_template('ss.html', url_list_with_ss=url_list_with_ss)


def group_screenshots_by_origin(files, url_list):
    url_list_with_ss = dict()
    for url in url_list:
        if url not in url_list_with_ss.keys():
            url_list_with_ss[url] = list()
        for file_name in files:
            if url in file_name and file_name not in url_list_with_ss[url]:
                url_list_with_ss[url].append(f'/ss/{file_name}')
    return url_list_with_ss


def sort_screenshots(url_list_with_ss):
    for entry in url_list_with_ss.keys():
        url_list_with_ss[entry].sort(reverse=True)


if __name__ == '__main__':
    app.run()
