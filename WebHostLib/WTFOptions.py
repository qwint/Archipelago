from flask import request, render_template
from .options import render_options_page
from . import app
from wtforms import Form, StringField, validators

# class OptionWTForm(Form):
#     uName = StringField("Name")

@app.route("/")
def index():
    # form = type("OptionWTForm", (Form,), {"uName": StringField("Name")})(request.form)
    # form = OptionWTForm(request.form)
    # return render_template("playerOptions/test.html", form=form)
    return render_options_page(
        "playerOptions/playerOptions.html",
        "Hollow Knight",
        # form=form
        )


app.run(host="0.0.0.0", port=50100, debug=True)
