# from flask import request, render_template
from .options import render_options_page
from . import app
# from wtforms import Form, StringField, validators, FieldList

# class OptionWTForm(Form):
#     game_options = FieldList(StringField("Name"))
#     uName = StringField("Name")

@app.route("/")
def index():
    # form = type("OptionWTForm", (Form,), {"uName": StringField("Name")})(request.form)
    # form = OptionWTForm(request.form)
    # return render_template("playerOptions/test.html", form=form, options=["uName"])
    return render_options_page(
        "playerOptions/playerOptions.html",
        "TUNIC",
        # form=form
        )


app.run(host="0.0.0.0", port=50100, debug=True)
