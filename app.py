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
engine = create_engine("sqlite:///belly_button_biodiversity.sqlite", echo=False)
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

    
    return jsonify(names)



@app.route("/otu")
def otu_description():
    """Return description of otu"""

    # query for description in otu table
    results=session.query(otu.lowest_taxonomic_unit_found).all()
    descp=[i[0] for i in results]
    
    return jsonify(descp)

@app.route("/metadata/<sample>")
def meta_data(sample):

    #extract the id number of sample name eg. BB_940 into 940 for search
    search=int(sample[3:])
    print(sample)
    result =session.query(meta).filter(meta.SAMPLEID==search).all()
    #convert result into dictionary
    dict_result=result[0].__dict__
    # last part of dictionary is _sa_instance_state and needs to be removed
    del dict_result['_sa_instance_state']
    return jsonify(dict_result)

@app.route("/wfreq/<sample>")
def wfreq_data(sample):
    #extract the id number of sample name eg. BB_940 into 940 for search
    search=int(sample[3:])
    print(sample)
    result =session.query(meta.WFREQ).filter(meta.SAMPLEID==search).all()[0][0]
    return jsonify(result)

@app.route('/samples/<sample>')
def sample_data(sample):
    search=sample
    # session.query(sample)
    sel='samples.{}'.format(search)
    print(sel)
    result_1=session.query(samples.otu_id,sel).all()
    
    data=pd.DataFrame(result_1,columns=['OTU_ID','Sample_Values']).sort_values('Sample_Values',ascending=False)
    
    #convert the int into string so it can be jsonified

    otu_id_str=list(data['OTU_ID'].astype('str'))
    values_str=list(data['Sample_Values'].astype('str'))
    return_dict={'otu_ids':otu_id_str,'sample_values':values_str}
    print(return_dict)

    return jsonify(return_dict)



if __name__ == '__main__':
    app.run(debug=True)
