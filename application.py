from flask import Flask, request, render_template
from typing import cast
from src.pipeline.predict_pipeline import CustomData, PredictPipeline

application = Flask(__name__)

app = application  

## Route for home page
@app.route("/")
@app.route("/projectdata")
def index():
    return render_template("home.html")


@app.route('/predictdata',methods=['GET','POST'])
def predict_datapoint() -> str:
    if request.method == 'GET':
        return cast(str, render_template('home.html'))
    else:
        data = CustomData(
            gender = cast(str, request.form.get('gender')),
            race_ethnicity = cast(str, request.form.get('race_ethnicity')),
            parental_level_of_education = cast(str, request.form.get('parental_level_of_education')),
            lunch = cast(str, request.form.get('lunch')),
            test_preparation_course = cast(str, request.form.get('test_preparation_course')),
            reading_score = int(cast(str, request.form.get('reading_score'))),
            writing_score = int(cast(str, request.form.get('writing_score')))
        )
        
        pred_df = data.get_data_as_data_frame()
        print(pred_df)
        
        predict_pipeline = PredictPipeline()
        results = predict_pipeline.predict(pred_df)
        return render_template('home.html', results=results[0])
    


if __name__ == "__main__":
    app.run(host="0.0.0.0")
