import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import (
    Flask,
    render_template,
    jsonify)

#################################################
# Reflect Database
#################################################
#connect to belly_button_biodiversity.sqlite 
engine = create_engine("sqlite:///db/belly_button_biodiversity.sqlite", echo=False)
#use automap base
# Reflect Database into ORM classes 
Base = automap_base()
Base.prepare(engine, reflect=True)

#set up session queries
session=Session(engine)

#Assign tables as objects

otu=Base.classes.otu
samples=Base.classes.samples
meta=Base.classes.samples_metadata

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """Render Home Page."""
    return render_template("index.html")

@app.route("/names")
def sample_names():
    """Return sample names"""

    # sample names are column (from the 2nd column) names for the table samples
    names = samples.__table__.columns.keys()[1:]

    # # Generate the plot trace
    # plot_trace = {
    #     "x": emoji_char,
    #     "y": scores,
    #     "type": "bar"
    # }
    return jsonify(names)



@app.route("/otu")
def otu_description():
    """Return description of otu"""

    # query for description in otu table
    results=session.query(otu.lowest_taxonomic_unit_found).all()
    descp=[i[0] for i in results]
    
    # # Format the data for Plotly
    # plot_trace = {
    #         "x": df["emoji_id"].values.tolist(),
    #         "y": df["score"].values.tolist(),
    #         "type": "bar"
    # }
    return jsonify(descp)

@app.route("/metadata/<sample>")
def meta_data(sample):
    """Return emoji score and emoji name"""

    # query for the top 10 emoji data
    search=int(sample[3:])
    print(sample)
    result =session.query(meta).filter(meta.SAMPLEID==search).all()
    dict_result=result[0].__dict__
    del dict_result['_sa_instance_state']

    # # Format the data for Plotly
    # plot_trace = {
    #         "x": df["name"].values.tolist(),
    #         "y": df["score"].values.tolist(),
    #         "type": "bar"
    # }
    return jsonify(dict_result)

@app.route("/wfreq/<sample>")
def wfreq_data(sample):
    """Return emoji score and emoji name"""

    # query for the top 10 emoji data
    search=int(sample[3:])
    print(sample)
    result =session.query(meta.WFREQ).filter(meta.SAMPLEID==search).all()[0][0]
    

    # # Format the data for Plotly
    # plot_trace = {
    #         "x": df["name"].values.tolist(),
    #         "y": df["score"].values.tolist(),
    #         "type": "bar"
    # }
    return jsonify(result)

@app.route('/samples/<sample>')
def sample_data(sample):
    """Return emoji score and emoji name"""

    # query for the top 10 emoji data
    search=sample
    # session.query(sample)
    sel='samples.{}'.format(search)
    print(sel)
    result_1=session.query(samples.otu_id,sel).all()
    
    data=pd.DataFrame(result_1,columns=['OTU_ID','Sample_Values']).sort_values('Sample_Values',ascending=False)
    
    #convert the int into string so it can be jsonified
    # I only returned the top 10 samples

    otu_id_str=list(data['OTU_ID'].astype('str'))
    values_str=list(data['Sample_Values'].astype('str'))
    return_dict={'otu_ids':otu_id_str,'sample_values':values_str}
    print(return_dict)

    # # Format the data for Plotly
    # plot_trace = {
    #         "x": df["name"].values.tolist(),
    #         "y": df["score"].values.tolist(),
    #         "type": "bar"
    # }
    return jsonify(return_dict)



if __name__ == '__main__':
    app.run(debug=True)
