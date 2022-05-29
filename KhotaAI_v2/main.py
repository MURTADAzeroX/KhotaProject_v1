from Website import create_app

app = create_app()


def search_by_id(location, ID):
    return location.query.filter_by(id=ID).first()


if __name__ == '__main__':
    app.run(debug=True)
