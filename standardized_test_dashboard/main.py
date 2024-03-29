from scipy.stats import t, skewnorm
import numpy as np
import streamlit as st
from streamlit.components.v1 import html
from matplotlib import pyplot as plt
import datetime

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

def get_figure(sem, sed,mean_score, test_stats,test_name, reported_score,score_band,conf_level_text, sample_size, bins, rbin ):
    fig, ax = plt.subplots(1, 1)
    x = np.arange(score_range[0],
                  score_range[1], 1)

    a =-0.4 if test_name in ["GMAT", "GRE"] else 0


    ax.plot(x, skewnorm.pdf(x, a,loc=mean_score, scale=test_stats[test_name]["sd"]),
            'b-', lw=5, alpha=0.6, label='pdf')

    ax.plot(reported_score, 0.000, marker="o", markersize=10, markeredgecolor="red", markerfacecolor="blue")
    # xerr can't be negative, so have to use the second value
    plt.errorbar(x=reported_score, y=0.000, xerr=score_band[1])
    if bins > 0:
        plt.vlines(rbin, ymin=0.000, ymax=skewnorm.pdf(rbin, a,loc=mean_score, scale=test_stats[test_name]["sd"]),
                   linestyle="--")
    plt.title(f"{test_name} {conf_level_text} Score Buckets\nSEM: {sem}, SED: {sed}, n={sample_size}")
    plt.xlabel(f"{test_name} Score")
    fig = plt.gcf()

    return fig

def get_link(anchor_text, url):
    return f"<a href={url} target={anchor_text}>{anchor_text}</a>"

def get_source_links(sources, test_stats, test_name):

    stats = test_stats[test_name]
    sem_source, mean_source, sd_source = stats["sem_source"], stats["mean_source"], stats["sd_source"]
    sem_link = get_link(anchor_text=sem_source, url=sources[sem_source])
    mean_link = get_link(anchor_text=mean_source,url=sources[mean_source])
    sd_link = get_link(anchor_text=sd_source, url=sources[sd_source])

    return sem_link, mean_link, sd_link

# def update_test_name(test_name):
#   st.session_state.test_name = test_name


sources = {"LSAC": "https://web.archive.org/web/20230529145804/https://www.lsac.org/lsat/taking-lsat/lsat-scoring/lsat-score-bands",
           "Best Accredited Colleges": "https://bestaccreditedcolleges.org/articles/careers-and-education/what-is-the-standard-deviation-of-lsat-scores.html",
           "ETS": "https://www.ets.org/pdfs/gre/gre-guide-to-the-use-of-scores.pdf",
           "GMAC": "https://www.gmac.com/-/media/files/gmac/gmat/gmat_institutionuserguide_fnl.pdf",
           "mba.com": "https://www.mba.com/exams/gmat-exam/scores/understanding-your-score",
           "AAMC": "https://www.aamc.org/media/18901/download?attachment",
            "College Board [1]": "https://satsuite.collegeboard.org/media/pdf/understanding-sat-scores.pdf",
           "College Board [2]": "https://reports.collegeboard.org/media/pdf/2022-total-group-sat-suite-of-assessments-annual-report.pdf",
           "ACT [1]": "https://www.act.org/content/dam/act/unsecured/documents/Using-Your-ACT-Results-20-21.pdf",
           "ACT [2]": "https://www.act.org/content/dam/act/unsecured/documents/MultipleChoiceStemComposite.pdf"
           }

test_stats = {"LSAT": {"sem": 2.6, "range":(120, 180), "sd": 9.95, "mean": 152,
                       "sem_source": "LSAC",
                       "mean_source": "Best Accredited Colleges",
                       "sd_source": "Best Accredited Colleges"},
             "MCAT": {"sem": 2.0, "range":(472, 528), "sd": 11.0, "mean": 501,
                      "sem_source": "AAMC","mean_source":"AAMC", "sd_source": "AAMC"},
             "GMAT":{"sem": 29.0,  "sed": 41.0, "range": (200,800), "sd": 111.13, "mean": 582,
                     "sem_source": "GMAC","mean_source": "mba.com", "sd_source": "mba.com"},
             "GRE": {"sem": 2.3, "range": (260,340), "sd": 18.26, "mean": 306,
                     "sem_source": "ETS",
                     "mean_source": "ETS",
                     "sd_source": "ETS"},
              "SAT": {"sem": 40.0, "range": (400,1600), "sd":216.0, "mean":1050,
                      "sem_source": "College Board [1]",
                      "mean_source": "College Board [2]",
                      "sd_source": "College Board [2]"},
              "ACT": {"sem": 1.0, "range": (1,36), "sd": 6.0, "mean": 20,
                      "sem_source":"ACT [1]",
                      "mean_source": "ACT [2]",
                      "sd_source": "ACT [2]"}

              }

st.set_page_config(page_title=f"Standardized Test Reliability")
if "test_name" not in st.session_state:
    st.session_state["test_name"] = "LSAT"

with st.sidebar:

    st.header(f'{st.session_state["test_name"]} reliability')
    test_name = st.selectbox(
        'Test',
        ('LSAT', 'GMAT', 'GRE', 'MCAT', 'SAT', 'ACT'),key="test_name")

    sem = st.slider('standard error of measurement', min_value=0.5, max_value=5.0, value=test_stats[test_name]["sem"], step=0.01)
    sed = round(np.sqrt(2 * (sem ** 2)), 2)

    # use_se = st.radio(
    #     "Compute Score Buckets Using",
    #     ["SEm", "SED"],
    #     captions=["Standard Error of Measurement", "Standard Error of Differences"])
    #
    # if use_se == "SEm":
    #     se = sem
    # else:
    #     se = round(np.sqrt(2*(sem**2)),2)

    score_range  = test_stats[test_name]["range"]
    n_scores = score_range[1] - score_range[0]
    mean_score = test_stats[test_name]["mean"]
    #mean_score = int((score_range[0] + score_range[1]) / 2 )
    conf_level = st.slider("confidence level", min_value=0.5, max_value=0.99, value=0.95, step=0.01)
    sample_size = st.slider("sample size", min_value=10,max_value=100_000,value=100, step=10)
    reported_score = st.slider(f"Reported {test_name} Score", min_value=score_range[0],max_value=score_range[1],value=mean_score, step=1)

#st.header(f"{st.session_state.test_name} Score Bands &   {st.session_state.test_name} Score")
#html(f"<h1 align='center'>{st.session_state.test_name} Score Bands & {st.session_state.test_name} Score </h1>")
score_band = conf_interval(se=sem,conf_level=conf_level,sample_size=sample_size)
difference_interval = conf_interval(se=sed,conf_level=conf_level,sample_size=sample_size)
width = difference_interval[1] - difference_interval[0]

conf_level_text = f"{int(conf_level * 100)}%"

bins, rbin = get_bins(width, n_scores)

fig =get_figure(sem, sed,mean_score, test_stats,test_name, reported_score,score_band,conf_level_text, sample_size, bins, rbin )

sem_link, mean_link, sd_link = get_source_links(sources, test_stats, test_name)
year = datetime.date.today().year


score_band_para = f"""<html><p>
      If the {test_name} has an SEm of {sem}, then a student who receives a score of {reported_score} when taking the {test_name}
      will have a "true" score between {round(reported_score +score_band[0])} and {round(reported_score +score_band[1])} with {conf_level_text} confidence. 
      This score band is represented on the graphic above by the red error bars."""

score_buckets_para = f"""
       <p>
       If the {test_name} has an SED of {sed}, then it can reliably
        sort students into {bins} bins (assign them one of {bins} ranks) with {conf_level_text} confidence . <br><br>
        These bins will have a width of about {int(width)} scaled {test_name} score points.
         They are represented on the graphic above by the blue vertical dashed lines.</p></html>"""
        


source_html = f"""The following  {test_name} statistics are used in this app:  <p>
    <ul>
    <li>SEm: {test_stats[test_name]["sem"]} (Source: {sem_link} ) </li>
    <li>Mean {test_stats[test_name]["mean"]} (Source: {mean_link})</li>
    <li>Standard Deviation: {test_stats[test_name]["sd"]} (Source: {sd_link})</li>
    </ul>
"""

about_html= f"""
    The SEm is used to populate the default value on the slider and to determine the "true score" confidence interval.
     The SEm is also used to compute the SED, which is then used to determine the width of the score buckets. <p>
    The mean and standard deviation of scores are used to determine the shape of the normal distribution on the plot above.
    They aren't used to determine the score band or score buckets.
    The (skew) normal distribution is used for graphical illustration purposes only, and doesn't necessarily reflect the shape of the actual score distribution.
    For instance, compare the app's plot for MCAT with the graph on page 15 of the AAMC reference. This graphical liberty does not affect the confidence intervals
    or score buckets.
    
    <p>
    Only mathematical formulas and the above cited statistics were used to make this app. No student data from ETS, LSAC, The College Board nor anywhere else was used.
   """

st.title(f"Visualizing {st.session_state.test_name} Measurement Error" )
st.pyplot(fig)
st.subheader(f"{st.session_state.test_name} Score Band")
html(score_band_para, height=70)
st.subheader(f"{st.session_state.test_name} Score Buckets",)
html(score_buckets_para, height=50)
with st.expander("Sources"):
    html(source_html, height=110)
with st.expander("About this app"):
    html(about_html, height =300)
html(f'<hr>Copyright {year}  {get_link(anchor_text="Daavid Stein",url="http://www.linkedin.com/in/daavidstein")}. All rights reserved.')


