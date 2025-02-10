from flask import Flask
from flask_restful import Api
from capital_gains import CapitalGains  # Import the existing CapitalGains class

app = Flask(__name__)
api = Api(app)

# Register the CapitalGains resource with the Flask app
api.add_resource(CapitalGains, '/capital-gains')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)  # Run on port 8080
