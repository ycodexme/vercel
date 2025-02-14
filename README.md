# Flask Temp SMS

This is a Flask application for sending temporary SMS messages. It allows users to select a country, choose a phone number, and send SMS messages to recipients.

## Project Structure

The project has the following file structure:

```
flask_temp_sms
├── app.py
├── templates
│   ├── base.html
│   ├── index.html
│   ├── countries.html
│   ├── numbers.html
│   └── messages.html
├── static
│   └── styles.css
├── requirements.txt
└── README.md
```

## Files

- `app.py`: This file is the main Python file for the Flask application. It contains the Flask app object and defines the routes and logic for handling HTTP requests.

- `templates/base.html`: This file is an HTML template that serves as the base layout for other templates. It can include common elements such as the header and footer.

- `templates/index.html`: This file is an HTML template that represents the home page of the application. It can display information or forms related to sending SMS messages.

- `templates/countries.html`: This file is an HTML template that displays a list of countries. It can be used to select the country for sending SMS messages.

- `templates/numbers.html`: This file is an HTML template that displays a list of phone numbers. It can be used to select the recipient's phone number for sending SMS messages.

- `templates/messages.html`: This file is an HTML template that displays the SMS messages sent. It can show the message content, sender, and recipient information.

- `static/styles.css`: This file is a CSS file that contains styles for the HTML templates. It can be used to customize the appearance of the web pages.

- `requirements.txt`: This file lists the Python dependencies required for the project. It specifies the packages and their versions that need to be installed for the Flask application to run.

- `README.md`: This file contains the documentation for the project. It provides instructions on how to set up and run the Flask application, as well as any additional information about the project.

## Setup

To set up and run the Flask application, follow these steps:

1. Clone the repository to your local machine.
2. Install the required Python dependencies by running the following command:
   ```
   pip install -r requirements.txt
   ```
3. Start the Flask application by running the following command:
   ```
   python app.py
   ```
4. Open your web browser and navigate to `http://localhost:5000` to access the application.

## Usage

- On the home page (`index.html`), you can enter the message content and select the country and phone number.
- After submitting the form, the message will be sent and displayed on the messages page (`messages.html`).
- You can also view the list of available countries on the countries page (`countries.html`) and select a phone number on the numbers page (`numbers.html`).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.#   c o d e x  
 #   c o d e x  
 