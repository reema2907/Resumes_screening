import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def calculate_final_score(required_skills, resume_skills, resume_text):
    # Initialize resume_score
    resume_score = 0

    # Calculate Role Match Score
    

    # Check for Achievements and add score
    if 'Achievements' in resume_text:
        resume_score += 20
        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Achievements</h5>''', unsafe_allow_html=True)
    else:
        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Achievements. It will show that you are capable for the required position.</h5>''', unsafe_allow_html=True)

    # Check for Projects and add score
    if 'Projects' in resume_text:
        resume_score += 20
        st.markdown('''<h5 style='text-align: left; color: #1ed760;'>[+] Awesome! You have added your Projects</h5>''', unsafe_allow_html=True)
    else:
        st.markdown('''<h5 style='text-align: left; color: #000000;'>[-] Please add Projects. It will show that you have done work related to the required position or not.</h5>''', unsafe_allow_html=True)

    # Calculate Cosine Similarity Score
    cosine_similarity_score = calculate_cosine_similarity(required_skills, resume_skills)

    # Calculate the final resume score considering all factors and weightage
    final_score = (cosine_similarity_score * 50) + resume_score 

    return final_score

def calculate_cosine_similarity(required_skills, resume_skills):
    # Convert lists of skills to strings
    job_skills_str = ", ".join(required_skills)
    resume_skills_str = ", ".join(resume_skills)

    # Tokenize job skills and resume skills
    text_list = [job_skills_str, resume_skills_str]

    # Vectorize the text
    vectorizer = CountVectorizer().fit_transform(text_list)
    vectors = vectorizer.toarray()

    # Calculate cosine similarity
    similarity_score = cosine_similarity(vectors)[0, 1]

    return similarity_score



    # Calculate final resume score
final_resume_score = calculate_final_score(required_skills, resume_skills, resume_text)

# Display the resume score
st.subheader("**Resume Score📝**")
st.markdown(
"""
<style>
    .stProgress > div > div > div > div {
        background-color: #d73b5c;
    }
</style>""",
unsafe_allow_html=True,
)
my_bar = st.progress(0)
score = 0
for percent_complete in range(int(final_resume_score)):

    score += 1
    time.sleep(0.1)
    my_bar.progress(percent_complete + 1)
st.success('** Your Resume Writing Score: ' + str(score) + '**')
st.warning("** Note: This score is calculated based on the content that you have in your Resume. **")

