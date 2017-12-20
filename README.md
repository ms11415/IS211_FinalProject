# IS211_FinalProject
A blogging web application.

To use this application, run
python pythonapp.py
and then open a web browser window to 127.0.0.1:5000

This blogging application presents blog entries in reverse chronological order
on the homepage.  The app includes three short blog entries for testing purposes.
Each post displays title, author, date published, permalink, and body of post.

Currently the app only supports one user, with assigned credentials of
"admin" and "password".  At the bottom of the homepage, log in status is shown.
If not logged in, it will show as Guest, with a link to the login page.  If
logged in, it will show the name of the logged in user, as well as links to the
dashboard and logout.

Once successfully logged in, the app redirects to a dashboard where a user can
add, edit or delete posts, as well as toggle the publish/unpublish aspect of the
post.  Unpublishing a post will retain it in the database, but it will not be
displayed on the homepage.

Each page except for the homepage verifies logged in status before displaying
information.  Any attempt to reach these pages without being logged in will
result in being redirected to the login page.  Each page also includes a link
to the homepage for easier navigation within the app.

Form fields are not allowed to be blank or use only white space, and form
validation is accomplished by using browser tags and also regex validation.

Because the app includes a database initialized with sample entries for testing
purposes, any changes to the database are lost whenever the app is restarted.