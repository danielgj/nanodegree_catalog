# Full Stack Development Nanodegree - Project Catalog Documentation

Catalog project main goal is to demonstrate the knowledge acquired on Python, Flask and CRUD web applications. To achieve that, we need to develop a web applications to implement several CRUD operations on a SQLite database.

This document describes the design and considerations in order to fulfill the project specification.

## Project Requirements

The Item Catalog project consists of developing an application that provides a list of items within a variety of categories, as well as provide a user registration and authentication system.

There will be following routes:
 * **Home:** the homepage displays all current categories along with the latest added items.

![Home Page](https://d17h27t6h515a5.cloudfront.net/topher/2017/August/598e0c98_localhost8080/localhost8080.png "Home Page")

 * **Category page:** Selecting a specific category shows you all the items available for that category.

![Category Page](https://d17h27t6h515a5.cloudfront.net/topher/2017/August/598e0d0e_snowboarding/snowboarding.png "Category Page")

 * **Item add:** Displays a form to add new items. This route is only available to logged users.
 * **Item detail:** Selecting a specific item shows you specific information of that item.

![Item Detail](https://d17h27t6h515a5.cloudfront.net/topher/2017/August/598e0d7a_item/item.png "Item Detail")

 * **Item edit:** For logged users a form will be displayed to edit their own items. One user won't be able to edit an item created by other user.

![Item Detail](https://d17h27t6h515a5.cloudfront.net/topher/2017/August/598e0e8c_snowboardedit/snowboardedit.png "Item Edit")

 * **Item delete:** For logged users a form will be displayed to remove their own items. One user won't be able to remove an item created by other user.

![Item Delete](https://d17h27t6h515a5.cloudfront.net/topher/2017/August/598e0ec8_snowboarddelete/snowboarddelete.png "Item Delete")

 * **Login page**: Should provide a login with external services like Google.

* **JSON endpoint:** A route to access a JSON list for all items in database will be also provided.

![JSON endpoint](https://d17h27t6h515a5.cloudfront.net/topher/2017/August/598e0f11_catalogjson/catalogjson.png "JSON endpoint")

## Initial Setup

To be able to run and test the application, some initial setup steps are needed.

### Preparing the Database
Catalog app stores all categories, items and users in a SQLite database.

To prepare the Database two python scripts are needed to run:

* **Create the database:** Running `python database_setup.py`
* **Create default categories:** Running `python prepare_categories.py`
  
### Setup Oauth Login with Google

To setup Oauth login woth Google, you need a Project created under Google Developer Console. Follow the instructions on the course materials or Google documentation:

Project details should be added to a file with that route _/client_secret_google.json_.

Additionaly, the Google project client Id should be added also to the file _templates/login.html_ under the start function in line 18.

## How to Run the project

To run the project, on the VM symply run `python catalog.py`.

Web application is accessible on `http://localhost:5000`.

## Additional comments

To ensure that python good coding practices has been achieved, [PEP8 style guide](https://www.python.org/dev/peps/pep-0008/) has been reviewed and `pycodestyle` tool has been used until no errors were shown.