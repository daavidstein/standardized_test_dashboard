from scipy.stats import t, norm
import numpy as np
import streamlit as st
from streamlit.components.v1 import html
from matplotlib import pyplot as plt
import datetime


#MCAT sem = std*sqrt(1-r)
# MCAT r = 0.9, std = 10.8
# => MCAT sem = 3.42
#FIXME look into the standard error of estimation
#  it's easier to estimate students near the middle than at the tails
#TODO drop down to select which test
# this automatically sets the SEm, mean, st and score range of the test.
#explore how discrimination changes htings

def conf_interval(se=2.6, conf_level=0.95, sample_size=100):
    return np.array(t.interval(conf_level,df=sample_size -1))*se

def get_bins(width,n_scores):

    if width <= n_scores:
        bins = int(n_scores // width)
        #bins = N_SCORES / width
        increment = n_scores / bins
        rbin =[score_range[0] +i*increment for i in range(1,int(bins))]
    else:
        bins = 0
    return bins, rbin

def get_figure(mean_score, test_stats,test_name, reported_score,conf_level_text, sample_size, rbin):
    fig, ax = plt.subplots(1, 1)
    x = np.arange(score_range[0],
                  score_range[1], 1)
    # this says that most tests have a SD of 15
    # https://www.patoss-dyslexia.org/write/MediaUploads/Resources/Standard_Error_of_Measurement_and_Confidence_Intervals_PATOSS_Updated_June_2020.pdf
    # supposedly LSAT is 10
    ax.plot(x, norm.pdf(x, loc=mean_score, scale=test_stats[test_name]["sd"]),
            'b-', lw=5, alpha=0.6, label='norm pdf')

    ax.plot(reported_score, 0.000, marker="o", markersize=10, markeredgecolor="red", markerfacecolor="blue")
    # xerr can't be negative, so have to use the second value
    plt.errorbar(x=reported_score, y=0.000, xerr=interval[1])
    if bins > 0:
        plt.vlines(rbin, ymin=0.000, ymax=norm.pdf(rbin, loc=mean_score, scale=test_stats[test_name]["sd"]),
                   linestyle="--")
    plt.title(f"{test_name} Score Distribution and {conf_level_text} score buckets\nSEm: {se}, n={sample_size}")
    plt.xlabel(f"{test_name} Score")
    fig = plt.gcf()

    return fig

def get_link(anchor_text, url):
    return f"<a href={url}>{anchor_text}</a>"


def get_source_links(sources, test_stats, test_name):

    stats = test_stats[test_name]
    sem_source, mean_source, sd_source = stats["sem_source"], stats["mean_source"], stats["sd_source"]
    sem_link = get_link(anchor_text=sem_source, url=sources[sem_source])
    mean_link = get_link(anchor_text=mean_source,url=sources[mean_source])
    sd_link = get_link(anchor_text=sd_source, url=sources[sd_source])

    return sem_link, mean_link, sd_link


sources = {"LSAC": "https://web.archive.org/web/20230529145804/https://www.lsac.org/lsat/taking-lsat/lsat-scoring/lsat-score-bands",
           "Best Accredited Colleges": "https://bestaccreditedcolleges.org/articles/careers-and-education/what-is-the-standard-deviation-of-lsat-scores.html",
           "ETS": "https://www.ets.org/pdfs/gre/gre-guide-to-the-use-of-scores.pdf",
           "GMAC": "https://www.gmac.com/-/media/files/gmac/gmat/gmat_institutionuserguide_fnl.pdf",
           "mba.com": "https://www.mba.com/exams/gmat-exam/scores/understanding-your-score"}

test_stats = {"LSAT": {"sem": 2.6, "range":(120, 180), "sd": 9.95, "mean": 152,
                       "sem_source": "LSAC",
                       "mean_source": "Best Accredited Colleges",
                       "sd_source": "Best Accredited Colleges"},
             "MCAT": {"sem": 3.42, "range":(472, 528), "sd": 10.8, "mean": 502},
             "GMAT":{"sem": 29.0,  "sed": 41.0, "range": (200,800), "sd": 111.13, "mean": 582,
                     "sem_source": "GMAC","mean_source": "mba.com", "sd_source": "mba.com"},
             "GRE": {"sem": 2.3, "range": (260,340), "sd": 18.26, "mean": 306,
                     "sem_source": "ETS",
                     "mean_source": "ETS",
                     "sd_source": "ETS"}
              #"SAT": {"sem": 32.0, "range"}

              }

with st.sidebar:
    #test_name = st.text_input(label="Test Name", value="LSAT")
    test_name = st.selectbox(
        'Test',
        #rm mcat until we correct the SEm
        #('LSAT', 'MCAT', 'GMAT'))
        ('LSAT', 'GMAT', 'GRE'))

    se = st.slider('standard error of measurement', min_value=0.5, max_value=5.0, value=test_stats[test_name]["sem"], step=0.01)
    score_range  = test_stats[test_name]["range"]
    n_scores = score_range[1] - score_range[0]
    mean_score = test_stats[test_name]["mean"]
    #mean_score = int((score_range[0] + score_range[1]) / 2 )
    conf_level = st.slider("confidence level", min_value=0.5, max_value=0.99, value=0.95, step=0.01)
    sample_size = st.slider("sample size", min_value=10,max_value=100_000,value=100, step=10)
    reported_score = st.slider(f"Reported {test_name} Score", min_value=score_range[0],max_value=score_range[1],value=mean_score, step=1)

interval = conf_interval(se=se,conf_level=conf_level,sample_size=sample_size)
width = interval[1] - interval[0]

conf_level_text = f"{int(conf_level * 100)}%"

bins, rbin = get_bins(width, n_scores)

fig =get_figure(mean_score, test_stats,test_name, reported_score,conf_level_text, sample_size, rbin)
st.pyplot(fig)

sem_link, mean_link, sd_link = get_source_links(sources, test_stats, test_name)
year = datetime.date.today().year

main_info =f"""<html><p>If the {test_name} has a standard error of measurement (SEm) of {se}, then it can reliably
        sort students into {bins} bins (assign them one of {bins} ranks) with {conf_level_text} confidence . <br><br>
        These bins will have a width of about {int(width)} scaled {test_name} score points <p>
        
        If a student receives a score of {reported_score} when taking the {test_name}, their "true" score will be between {int(reported_score +interval[0])} and {int(reported_score +interval[1])} with {conf_level_text} confidence
        </p></html>"""

source_html = f"""<hr>The following  {test_name} statistics are used in this app:  <p>
    <ul>
    <li>SEm: {test_stats[test_name]["sem"]} (Source: {sem_link} ) </li>
    <li>Mean {test_stats[test_name]["mean"]} (Source: {mean_link})</li>
    <li>Standard Deviation: {test_stats[test_name]["sd"]} (Source: {sd_link})</li>
    </ul>

    The SEm is used to populate the default value on the slider used to determine the width of the score buckets. <p>
    The mean and standard deviation of scores are used to determine the shape of the bell-shaped distribution on the plot above.
    They aren't used to determine the score buckets (vertical dashed lines)
    <p>
    Only mathematical formulas and the above cited statistics were used to make this app. No student data from ETS, LSAC, The College Board nor anywhere else was used.
    <hr>
    Copyright {year} Daavid Stein. All rights reserved."""




html(main_info, height=140)
html(source_html, height=310)
