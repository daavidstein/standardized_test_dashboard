from scipy.stats import t, norm
import numpy as np
import streamlit as st
from streamlit.components.v1 import html
from matplotlib import pyplot as plt


#MCAT sem = std*sqrt(1-r)
# MCAT r = 0.9, std = 10.8
# => MCAT sem = 3.42
#FIXME look into the standard error of estimation
#  it's easier to estimate students near the middle than at the tails
#TODO drop down to select which test
# this automatically sets the SEm, mean, st and score range of the test.
#explore how discrimination changes htings
SCORE_RANGE = [120,180]
N_SCORES = SCORE_RANGE[1] - SCORE_RANGE[0]
MEAN_SCORE = (SCORE_RANGE[0] + SCORE_RANGE[1])/2
def conf_interval(se=2.6, conf_level=0.95, sample_size=100):
    return np.array(t.interval(conf_level,df=sample_size -1))*se

with st.sidebar:
    test_name = st.text_input(label="Test Name", value="LSAT")
    se = st.slider('standard error of measurement', min_value=0.01, max_value=20.0, value=2.6, step=0.01)
    conf_level = st.slider("confidence level", min_value=0.01, max_value=0.99, value=0.95, step=0.01)
    sample_size = st.slider("sample size", min_value=10,max_value=100_000,value=100, step=10)
    reported_score = st.slider(f"Reported {test_name} Score", min_value=120,max_value=180,value=150, step=1)

interval = conf_interval(se=se,conf_level=conf_level,sample_size=sample_size)
#st.text(interval)
width = interval[1] - interval[0]
#st.text(f"interval width: {width}")


conf_level_text = f"{int(conf_level * 100)}%"
if width <= N_SCORES:
    bins = int(N_SCORES // width)
    increment = N_SCORES/ bins
    rbin =[SCORE_RANGE[0] +i*increment for i in range(1,bins+1)]
else:
    bins = 0


fig, ax = plt.subplots(1, 1)
x = np.arange(SCORE_RANGE[0],
                SCORE_RANGE[1], 1)
#this says that most tests have a SD of 15
#https://www.patoss-dyslexia.org/write/MediaUploads/Resources/Standard_Error_of_Measurement_and_Confidence_Intervals_PATOSS_Updated_June_2020.pdf
#supposedly LSAT is 10
ax.plot(x, norm.pdf(x,loc=MEAN_SCORE,scale=14),
       'b-', lw=5, alpha=0.6, label='norm pdf')

ax.plot(reported_score, 0.003, marker="o", markersize=10, markeredgecolor="red", markerfacecolor="blue")
plt.errorbar(x=reported_score, y=0.003, xerr=interval[0])
if bins > 0:
    plt.vlines(rbin,ymin=0.0027,ymax=norm.pdf(rbin,loc=MEAN_SCORE,scale=14)*0.98,linestyle="--")
plt.title(f"{test_name} Score Distribution and {conf_level_text} score buckets\nSEm: {se}, n={sample_size}")
plt.xlabel(f"{test_name} Score")
fig = plt.gcf()

st.pyplot(fig)

html(f"""<html><p>If the {test_name} has a standard error of measurement of {se}, then it can reliably
        sort students into {bins} bins (assign them one of {bins} ranks) with {conf_level_text} confidence . <br><br>
        These bins will have a width of about {int(width)} scaled {test_name} score points
        </p></html>""")
html(f"""<html><p>
        <a href="https://www.lsac.org/{test_name}/taking-{test_name}/{test_name}-scoring/{test_name}-score-bands#:~:text=The%20standard%20error%20of%20measurement%20provides%20an%20estimate%20of%20the,about%202.6%20scaled%20score%20points.">The standard error of measurement</a> is a measure of the accuracy of the {test_name} test.
         <br> <br>
         If a student receives a score of {reported_score} when taking the {test_name}, their "true" score will be between {int(reported_score +interval[0])} and {int(reported_score +interval[1])} with {conf_level_text} confidence
        </p></html>""")

st.text("Only mathematical formulas were used to make this app. ")
st.text("No student data from LSAC or anywhere else was used to create this app.")