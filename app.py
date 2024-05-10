from flask import Flask, request, render_template
import csv
import random
import logging

""" Create the Flask app with basic logging configuration """


def create_app():
    app = Flask(__name__)
    logging.basicConfig(filename='log/app.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')
    app.logger.info("Application created")
    return app


""" Initialize the Flask app """
app = create_app()
images_data = []
recently_shown_images = []


""" Load image data from a CSV file """


def load_images_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=';')
            for row in reader:
                images_data.append({
                    'url': row[0],
                    'shows_left': int(row[1]),
                    'categories': set(row[2:])
                })
        app.logger.info(f"Data from file {filename} successfully loaded")
    except Exception as e:
        app.logger.error(f"Error reading file {filename}: {e}")


""" Route to show an image based on requested categories """


@app.route('/')
def show_image():
    requested_categories = set(request.args.getlist('category'))
    app.logger.debug(f"Requested categories: {requested_categories}")
    return get_image(requested_categories)


""" Select and display an image based on requested categories """


def get_image(requested_categories):
    valid_images = [image for image in images_data if image['shows_left'] > 0 and
                    (not requested_categories or image['categories'].intersection(requested_categories)) and
                    image['url'] not in recently_shown_images]

    if not valid_images:
        reset_shows_left()
        return get_image(requested_categories)

    image = random.choice(valid_images)
    image['shows_left'] -= 1
    manage_recently_shown(image['url'])
    app.logger.info(f"Image displayed: {image['url']} with categories: {image['categories']}")

    return render_template('image_viewer.html', url=image['url'], categories=image['categories'])


""" Manage the list of recently shown images """


def manage_recently_shown(url):
    recently_shown_images.append(url)
    if len(recently_shown_images) > 5:
        recently_shown_images.pop(0)
    app.logger.debug(f"Recently shown images list updated: {recently_shown_images}")


""" Reset the show counts for images with zero shows left """


def reset_shows_left():
    for image in images_data:
        if image['shows_left'] == 0:
            image['shows_left'] = 1
    app.logger.debug("Show counters reset for all images")


""" Load image data and run the Flask app in debug mode """
if __name__ == '__main__':
    load_images_data('images.csv')
    app.run(debug=True)