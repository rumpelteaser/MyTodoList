# ==================== Web To-Do List Main Module ==================== #
#
# Minimalistic implementation - should be improved implementing fancier layout and responsive design
#

# Import needed modules
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField

# Start Flask Application
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

# Create Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

global sort_up
global sort_down
sort_up = False
sort_down = False


# Define DB Table
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(500), nullable=False)
    done = db.Column(db.Boolean, nullable=False)
    priority = db.Column(db.Boolean, nullable=False)


# Create Database
db.create_all()


# Define Add Task form
class AddingForm(FlaskForm):
    action = StringField('Enter action to do: ')
    date = StringField('Enter date for completion (YYYY-MM-DD): ')
    priority = BooleanField('Priority: ')
    submit = SubmitField('Add Task')


# Define save DB form
class SavingForm(FlaskForm):
    filename = StringField("Enter File Full Path Name (including '.csv' extension): ")
    submit = SubmitField("Save")


# Define SortDB class
class SortDB:
    up = False
    down = False


# Define procedure to export the database in a .CSV file
def sql_query_to_csv(query_output, columns_to_exclude=""):
    """	Converts output from a SQLAlchemy query to a .csv string.
    Parameters:
        query_output (list of <class 'SQLAlchemy.Model'>): output from an SQLAlchemy query.
        columns_to_exclude (list of str): names of columns to exclude from .csv output.
    Returns:
        csv (str): query_output represented in .csv format.
    Example usage:
        users = db.Users.query.filter_by(user_id=123)
        csv = sql_query_to_csv(users, ["id", "age", "address"]
    """
    separator = ";"     # "," to be used in US abd ";" in Europe
    rows = query_output
    columns_to_exclude = set(columns_to_exclude)
    # create list of column names
    column_names = [i for i in rows[0].__dict__]
    for column_name in columns_to_exclude:
        column_names.pop(column_names.index(column_name))
    # add column titles to csv
    column_names.sort()
    csv = separator.join(column_names) + "\n"
    # add rows of data to csv
    for row in rows:
        for column_name in column_names:
            if column_name not in columns_to_exclude:
                data = str(row.__dict__[column_name])
                # Escape (") symbol by preceeding with another (")
                data.replace('"', '""')
                # Enclose each datum in double quotes so commas within are not treated as separators
                csv += '"' + data + '"' + separator
        csv += "\n"
    # return the .CSV string
    return csv


# Display Main Page
@app.route('/')
def home():
    if SortDB.up:
        all_task = db.session.query(Todo).order_by(Todo.date.desc())
    elif SortDB.down:
        all_task = db.session.query(Todo).order_by(Todo.date.asc())
    else:
        all_task = db.session.query(Todo).all()
    return render_template("index.html", tasks=all_task)


# Display "Add Task" form
@app.route("/add", methods=["GET", "POST"])
def add_task():
    adding_form = AddingForm()
    if request.method == "POST":
        # print("Adding Form received")
        if (adding_form.validate_on_submit()) and not (adding_form.action.data == ""):
            # print("Adding Form validated")
            # Get task info from the form compiled in add-html
            task_action = adding_form.action.data
            task_date = adding_form.date.data
            task_priority = adding_form.priority.data
            # Insert new task in the Database
            new_task = Todo(action=task_action,
                            date=task_date,
                            priority=task_priority,
                            done=False
                            )
            db.session.add(new_task)
            db.session.commit()
            # Go back to main page
            return redirect(url_for('home'))
        else:
            # print("Adding Form not validated")
            return redirect(url_for('home'))
    else:  # request.method == "GET"
        # print("Presenting Adding Form")
        return render_template('add.html', form=adding_form)


# Implement "Task Done" action
@app.route("/done/<task_id>")
def task_done(task_id):
    print(task_id)
    task_completed = Todo.query.get(task_id)
    task_completed.done = True
    db.session.commit()
    return redirect(url_for('home'))


# Implement "Delete Task" action
@app.route("/delete/<task_id>")
def delete_task(task_id):
    task_to_delete = Todo.query.get(task_id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


# Define sorting order
@app.route("/sort/<order>")
def sort_list(order):
    if order == "up":
        print("Sort Up")
        SortDB.up = True
        SortDB.down = False
    elif order == "down":
        print("Sort Down")
        SortDB.up = False
        SortDB.down = True
    return redirect(url_for('home'))


# Save the DB content into a .CSV file
@app.route("/save", methods=["GET", "POST"])
def save_db():
    saving_form = SavingForm()
    if request.method == "POST":
        # print("Saving Form received")
        if saving_form.validate_on_submit():
            # print("Saving Form validated")
            # Open the specified file
            savefile = open(saving_form.filename.data, "a+")
            # Export DB in .CSV file
            query = db.session.query(Todo).order_by(Todo.date.desc())
            csv_1 = sql_query_to_csv(query, ["id", "_sa_instance_state"])
            savefile.write(csv_1)
            # Close the specified file
            savefile.close()
            # Go back to main page
            return redirect(url_for('home'))
        else:
            # print("Saving Form not validated")
            return redirect(url_for('home'))
    else:  # request.method == "GET"
        # print("Presenting Saving Form")
        return render_template('save.html', form=saving_form)


# Run the Application
if __name__ == "__main__":
    app.run(debug=True)
