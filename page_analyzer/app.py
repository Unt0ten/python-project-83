from flask import Flask, render_template
import jinja2

app = Flask(__name__)
my_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader(['templates']),
    ])
app.jinja_loader = my_loader


@app.route('/')
def open_main():
    return render_template('index.html')
