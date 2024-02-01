from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return render_template(
        'frame.html',
        title='rock paper scissors',
        frame_image='https://img.freepik.com/free-psd/isolated-golden-luxury-photo-frame_1409-3600.jpg',
        content='welcome to rock paper scissors!'
    ), 200


@app.route('/matchup')
def about():
    return 'matchup info', 200
