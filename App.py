import streamlit as st
import pandas as pd
import base64
import time
import datetime
import random
# Libraries to parse the resume PDF files
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io
from streamlit_tags import st_tags
from PIL import Image
import pymysql
from Courses import ds_course, web_course, android_course, ios_course, uiux_course
import plotly.express as px
import nltk
nltk.download('stopwords')
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity  




def get_table_download_link(df, filename, text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    # href = f'<a href="data:file/csv;base64,{b64}">Download Report</a>'
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

   

def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()

    # Close open handles
    converter.close()
    fake_file_handle.close()
    return text

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations 🎓**")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course

# Connect to database
# Load environment variables from secrets.toml



# Connect to database
connection = pymysql.connect(host='localhost', user='root', password='Igdtuw@123', db='cv')
cursor = connection.cursor()


def insert_data(name, email, res_score, timestamp, skills, role):
    DB_table_name = 'user_database'

    # Ensure that SQL placeholders are consistent with pymysql's requirements
    insert_sql = "INSERT INTO " + DB_table_name + " (Name, Email_ID, resume_score, Timestamp, Skills, Role) VALUES (%s, %s, %s, %s, %s, %s)"
   
    # Prepare data tuple
    rec_values = (name, email, res_score, timestamp, skills, role)
    # Execute the query
    cursor.execute(insert_sql, rec_values)
    connection.commit()



st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon='./Logo/logo2.png',
)
# Increase font size with CSS
st.write(
    f"""
    <style>
    /* Increase font size for markdown headers */
    h3 {{
        font-size: 20px !important;
       
    }}
    /* Increase font size for markdown paragraphs */
    p {{
        font-size: 20px !important;
        
    }}
     /* Increase font size for st.text() */
    .stText > div > div {{
        font-size: 20px !important;
    }}
   
    </style>
    """,
    unsafe_allow_html=True
)

    


def run():
    img = Image.open('./Logo/logo2.jpg')
    st.image(img)
    st.title("AI Resume Analyser")
    st.sidebar.markdown("# Choose the option")
    activities = ["Resume Analyser", "Score Board"]
    choice = st.sidebar.selectbox("select the given options:", activities)
    

    # Create the DB
    db_sql = """CREATE DATABASE IF NOT EXISTS CV;"""
    cursor.execute(db_sql)

    # Create table
    DB_table_name = 'user_database'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                     Name varchar(500) NOT NULL,
                     Email_ID VARCHAR(500) NOT NULL,
                     resume_score VARCHAR(8) NOT NULL,
                     Timestamp VARCHAR(50) NOT NULL,
                     Skills VARCHAR(5000) NOT NULL,
                     Role VARCHAR(500) NOT NULL, 
                     PRIMARY KEY (ID));
                    """
    cursor.execute(table_sql)

    if choice == 'Resume Analyser':
        # Job Description Box
        st.markdown("<h3 style='color:orange;'>Job Description:</h3>", unsafe_allow_html=True)
        job_description = st.text_area("Enter Job Description", "")

        # Role and Skills Entry
        role = st.text_input("Enter Role", "")
        required_skills = st.text_input("Enter Required Skills (comma-separated)", "")

        if st.button("Submit Job Description"):
            if not job_description:
                st.warning("Please enter a job description.")
            else:
                st.success("Job description submitted successfully!")

                
        st.markdown('''<h5 style='text-align: left; color: orange;'> Upload resume, and get smart recommendations</h5>''', unsafe_allow_html=True)
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            with st.spinner('Uploading  Resume...'):
                time.sleep(4)
            save_image_path = './Uploaded_Resumes/' + pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)

            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                resume_text = pdf_reader(save_image_path)
                st.header("**Resume Analysis**")
                st.success("Name of Candiadate :  " + resume_data['name'])
                st.markdown('''<h4 style='text-align: left; color: orange;'>Basic Information!''',
                                unsafe_allow_html=True)
                try:
                    st.markdown(f"<span style='font-size: 20px;'>Name: {resume_data['name']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='font-size: 20px;'>Email: {resume_data['email']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='font-size: 20px;'>Contact: {resume_data['mobile_number']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='font-size: 20px;'>Resume pages: {resume_data['no_of_pages']}</span>", unsafe_allow_html=True)
                except:
                    pass
                cand_level = ''
                if resume_data['no_of_pages'] == 1:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: orange;'>At Fresher level!</h4>''',
                                unsafe_allow_html=True)
                elif resume_data['no_of_pages'] == 2:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: orange;'>At intermediate level!</h4>''',
                                unsafe_allow_html=True)
                elif resume_data['no_of_pages'] >= 3:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: orange;'>At experience level!''',
                                unsafe_allow_html=True)
                # Extracting skills from the resume data
                resume_skills = resume_data.get('skills', [])

                keywords = st_tags(label='### Current Skills',
                                   text='skills recommendation below',
                                   value=resume_data['skills'], key='1  ')

                ds_keyword = ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep Learning', 'flask', 'streamlit',
                 'distributed systems', 'data engineering', 'data pipelines', 'neural networks', 'reinforcement learning',
                  'natural language processing', 'computer vision', 'time series analysis', 'anomaly detection',
                  'model deployment', 'model serving', 'tensorflow serving', 'kubernetes', 'docker', 'apache spark',
                  'hadoop', 'pyspark', 'big data']

                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress', 'javascript',
                            'angular js', 'c#', 'flask', 'html', 'css', 'bootstrap', 'jquery', 'restful apis', 'graphql',
                            'websockets', 'single-page applications (spa)', 'responsive design', 'cross-browser compatibility',
                            'seo (search engine optimization)', 'performance optimization', 'web security', 'authentication',
                            'authorization', 'web standards']

                android_keyword = ['android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy', 'android studio',
                                'material design', 'android sdk', 'android jetpack', 'firebase', 'google play services',
                                'android ndk', 'android ui design', 'android app architecture', 'google play store',
                                'android performance optimization', 'android testing (junit, espresso)', 'android security',
                                'androidx']

                ios_keyword = ['ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode', 'interface builder',
                            'core data', 'core animation', 'auto layout', 'app store connect', 'testflight', 'icloud',
                            'push notifications', 'core location', 'core motion', 'core bluetooth', 'swiftui',
                            'combine framework', 'catalyst', 'ios app extensions']

                uiux_keyword = ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes', 'storyframes',
                            'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator', 'illustrator', 'adobe after effects',
                            'after effects', 'adobe premier pro', 'premier pro', 'adobe indesign', 'indesign', 'wireframe',
                            'solid', 'grasp', 'user research', 'user experience', 'design thinking', 'usability', 'accessibility',
                            'information architecture', 'interaction design', 'visual design', 'user interface design',
                            'user-centered design (ucd)', 'responsive design', 'mobile design', 'design systems', 'a/b testing',
                            'heatmaps', 'clickstream analysis', 'persona creation', 'journey mapping']
                
                backend_keyword = ['rest api', 'graphql', 'microservices', 'serverless', 'orm (object-relational mapping)',
                   'database design', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis', 'memcached',
                   'api security', 'authentication', 'authorization', 'jwt (json web tokens)', 'oauth']

                devops_keyword = ['ci/cd (continuous integration/continuous deployment)', 'jenkins', 'travis ci', 'gitlab ci',
                                'circleci', 'docker', 'kubernetes', 'helm', 'terraform', 'ansible', 'puppet', 'chef',
                                'monitoring', 'logging', 'alerting', 'infrastructure as code (iac)', 'aws', 'azure',
                                'google cloud platform (gcp)']

                fullstack_keyword = ['express.js', 'asp.net', 'spring boot', 'ruby on rails', 'flask', 'django', 'vue.js',
                                    'angular', 'ember.js', 'mean stack', 'mern stack', 'lamp stack', 'server-side rendering',
                                    'progressive web apps (pwa)', 'websockets', 'real-time applications',
                                    'web security best practices', 'owasp top 10']

                software_engineer_keyword = ['algorithms', 'data structures', 'design patterns', 'object-oriented programming (oop)',
                                            'functional programming', 'test-driven development (tdd)', 'agile methodology', 'scrum',
                                            'kanban', 'code review', 'refactoring', 'debugging', 'version control (git, svn)',
                                            'software architecture', 'system design', 'performance optimization', 'code profiling']

                cybersecurity_keyword = ['penetration testing', 'vulnerability assessment', 'ethical hacking', 'network security',
                                        'web application security', 'endpoint security', 'siem (security information and event management)',
                                        'ids/ips (intrusion detection/prevention system)', 'firewall configuration',
                                        'security compliance (e.g., gdpr, hipaa)', 'incident response', 'threat intelligence',
                                        'cryptography', 'pki (public key infrastructure)', 'secure coding practices']
                
                business_analyst_keyword = ['requirements gathering', 'stakeholder management', 'business process modeling',
                                            'use case analysis', 'user stories', 'business requirements documentation',
                                            'functional requirements', 'non-functional requirements', 'gap analysis',
                                            'swot analysis', 'cost-benefit analysis', 'roi (return on investment)',
                                            'kpis (key performance indicators)', 'business case development',
                                            'stakeholder interviews', 'data analysis', 'data visualization',
                                            'business intelligence tools', 'process improvement', 'change management',
                                            'project management methodologies (e.g., agile, waterfall)', 'business domain knowledge']
                
                category_scores = {
                    'Data Scientist': 0,
                    'Web Developer': 0,
                    'Android Developer': 0,
                    'IOS Developer': 0,
                    'UI-UX Developer': 0,
                    'backend Developer':0,
                    'Devops Engineer':0,
                    'Full-stack Developer':0,
                    'Software Engineer' :0,
                    'Cybersecurity' :0,
                    'Business Analyst':0,
                }
                
                for skill in resume_data['skills']:
                    skill_lower = skill.lower()
                    # Update the score for each category based on the presence of the skill
                    if skill_lower in ds_keyword:
                        category_scores['Data Scientist'] += 1
                    if skill_lower in web_keyword:
                        category_scores['Web Developer'] += 1
                    if skill_lower in android_keyword:
                        category_scores['Android Developer'] += 1
                    if skill_lower in ios_keyword :
                        category_scores['IOS Developer'] += 1
                    if skill_lower in uiux_keyword :
                        category_scores['UI-UX Developer'] += 1
                    if skill_lower in backend_keyword:
                        category_scores['backend Developer'] += 1
                    if skill_lower in devops_keyword:
                        category_scores['Devops Engineer'] += 1
                    if skill_lower in fullstack_keyword:
                        category_scores['Full-stack Developer'] += 1
                    if skill_lower in software_engineer_keyword:
                        category_scores['Software Engineer'] += 1
                    if skill_lower in cybersecurity_keyword :
                        category_scores['Cybersecurity'] += 1
                    if skill_lower in  business_analyst_keyword:
                        category_scores['Business Analyst'] += 1
                    
                best_match = max(category_scores, key=category_scores.get)
                st.success(f"**Perfect for {best_match} Jobs.**")   
                
                



                recommended_skills = []
                

                if "data scientist" in role.lower():
                    # Code for Data Scientist recommendation
                    reco_field = 'Data Scientist'
                   
                    recommended_skills = ['Data Visualization', 'Predictive Analysis', 'Statistical Modeling',
                                        'Data Mining', 'Clustering & Classification', 'Data Analytics',
                                        'Quantitative Analysis', 'Web Scraping', 'ML Algorithms', 'Keras',
                                        'Pytorch', 'Probability', 'Scikit-learn', 'Tensorflow', "Flask",
                                        'Streamlit']
                    # Display recommended skills
                    recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                text='Recommended skills generated from System',
                                                value=recommended_skills, key='6')
                    st.markdown(...)
                    rec_course = course_recommender(ds_course)

                elif "web developer" in role.lower():
                    # Code for Web Developer recommendation
                    reco_field = 'Web Developer'
                   
                    recommended_skills = ['React', 'Django', 'Node JS', 'React JS', 'php', 'laravel', 'Magento',
                                        'wordpress', 'Javascript', 'Angular JS', 'c#', 'Flask', 'SDK']
                    # Display recommended skills
                    recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                text='Recommended skills generated from System',
                                                value=recommended_skills, key='6')
                    st.markdown(...)
                    rec_course = course_recommender(web_course)

                elif "android developer" in role.lower():
                    # Code for Web Developer recommendation
                    recommended_skills = ['Android', 'Android development', 'Flutter', 'Kotlin', 'XML', 'Java',
                                            'Kivy', 'GIT', 'SDK', 'SQLite']
                        
                    recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                text='Recommended skills generated from System',
                                                value=recommended_skills, key='6')
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                        unsafe_allow_html=True)
                    rec_course = course_recommender(android_course)
                
                elif "IOS developer" in role.lower():
                    recommended_skills = ['IOS', 'IOS Development', 'Swift', 'Cocoa', 'Cocoa Touch', 'Xcode',
                                            'Objective-C', 'SQLite', 'Plist', 'StoreKit', "UI-Kit",
                                            'AV Foundation', 'Auto-Layout']
                        
                    recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                text='Recommended skills generated from System',
                                                value=recommended_skills, key='6')
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                        unsafe_allow_html=True)
                    rec_course = course_recommender(ios_course)
                elif "UI/UX developer" in role.lower():
                    recommended_skills = ['UI', 'User Experience', 'Adobe XD', 'Figma', 'Zeplin', 'Balsamiq',
                                            'Prototyping', 'Wireframes', 'Storyframes', 'Adobe Photoshop',
                                            'Editing', 'Illustrator', 'After Effects', 'Premier Pro', 'Indesign',
                                            'Wireframe', 'Solid', 'Grasp', 'User Research']
                    
                    recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                text='Recommended skills generated from System',
                                                value=recommended_skills, key='6')
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                        unsafe_allow_html=True)
                    rec_course = course_recommender(uiux_course)    

                elif "backend  developer" in role.lower():
                    recommended_skills = ['REST API', 'GraphQL', 'Microservices', 'Serverless', 'ORM (Object-Relational Mapping)',
                                            'Database Design', 'SQL', 'NoSQL', 'MongoDB', 'PostgreSQL', 'MySQL', 'Redis', 'Memcached',
                                            'API Security', 'Authentication', 'Authorization', 'JWT (JSON Web Tokens)', 'OAuth']
                        
                    recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                text='Recommended skills generated from System',
                                                value=recommended_skills, key='6')
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                        unsafe_allow_html=True)
                        
                elif "Devops engineer" in role.lower():
                    recommended_skills = ['CI/CD (Continuous Integration/Continuous Deployment)', 'Jenkins', 'Travis CI', 'GitLab CI',
                                            'CircleCI', 'Docker', 'Kubernetes', 'Helm', 'Terraform', 'Ansible', 'Puppet', 'Chef',
                                            'Monitoring', 'Logging', 'Alerting', 'Infrastructure as Code (IaC)', 'AWS', 'Azure',
                                            'Google Cloud Platform (GCP)']
                        
                    recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                text='Recommended skills generated from System',
                                                value=recommended_skills, key='6')
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                        unsafe_allow_html=True)

                elif "full-stack developer" in role.lower():
                    recommended_skills = ['Express.js', 'ASP.NET', 'Spring Boot', 'Ruby on Rails', 'Flask', 'Django', 'Vue.js',
                                            'Angular', 'Ember.js', 'MEAN stack', 'MERN stack', 'LAMP stack', 'Server-side rendering',
                                            'Progressive Web Apps (PWA)', 'WebSockets', 'Real-time applications',
                                            'Web security best practices', 'OWASP Top 10']
                        
                    recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                text='Recommended skills generated from System',
                                                value=recommended_skills, key='6')
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                        unsafe_allow_html=True)
                
                elif "software engineer" in role.lower():
                    recommended_skills = ['Algorithms', 'Data Structures', 'Design Patterns', 'Object-Oriented Programming (OOP)',
                                            'Functional Programming', 'Test-driven Development (TDD)', 'Agile Methodology', 'Scrum',
                                            'Kanban', 'Code Review', 'Refactoring', 'Debugging', 'Version Control (Git, SVN)',
                                            'Software Architecture', 'System Design', 'Performance Optimization', 'Code Profiling']
                        
                    recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                text='Recommended skills generated from System',
                                                value=recommended_skills, key='6')
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                        unsafe_allow_html=True)
                    
                elif "cybersequrity" in role.lower():
                    recommended_skills = ['Penetration Testing', 'Vulnerability Assessment', 'Ethical Hacking', 'Network Security',
                                            'Web Application Security', 'Endpoint Security', 'SIEM (Security Information and Event Management)',
                                            'IDS/IPS (Intrusion Detection/Prevention System)', 'Firewall Configuration',
                                            'Security Compliance (e.g., GDPR, HIPAA)', 'Incident Response', 'Threat Intelligence',
                                            'Cryptography', 'PKI (Public Key Infrastructure)', 'Secure Coding Practices']
                        
                    recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                text='Recommended skills generated from System',
                                                value=recommended_skills, key='6')
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                        unsafe_allow_html=True)  

                elif "business analyst" in role.lower():
                    recommended_skills = ['Penetration Testing', 'Vulnerability Assessment', 'Ethical Hacking', 'Network Security',
                                            'Web Application Security', 'Endpoint Security', 'SIEM (Security Information and Event Management)',
                                            'IDS/IPS (Intrusion Detection/Prevention System)', 'Firewall Configuration',
                                            'Security Compliance (e.g., GDPR, HIPAA)', 'Incident Response', 'Threat Intelligence',
                                            'Cryptography', 'PKI (Public Key Infrastructure)', 'Secure Coding Practices']
                        
                    recommended_keywords = st_tags(label='### Recommended skills for you.',
                                                text='Recommended skills generated from System',
                                                value=recommended_skills, key='6')
                    st.markdown(
                        '''<h4 style='text-align: left; color: #1ed760;'>Adding this skills to resume will boost🚀 the chances of getting a Job💼</h4>''',
                        unsafe_allow_html=True)  
                

                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date + '_' + cur_time)

                st.subheader("**Resume Tips & Ideas💡**")
                    
                
                # Initialize resume_score as numeric value
                resume_score = 0

                
                def calculate_cosine_similarity(role_keywords, skills):
                    # Convert role_keywords and skills into TF-IDF vectors
                    vectorizer = TfidfVectorizer()
                    vectors = vectorizer.fit_transform(role_keywords + skills)

                    # Calculate cosine similarity between role_keywords and skills
                    similarity_matrix = cosine_similarity(vectors)

                    # Get the similarity score between role_keywords and skills
                    similarity_score = similarity_matrix[0, 1:].max()

                    return similarity_score

                def match_skills_with_role(role, skills):
                    role_keywords_mapping = {
                        "data scientist": ds_keyword,
                        "web developer": web_keyword,
                        "android developer": android_keyword,
                        "ios developer": ios_keyword,
                        "ui/ux designer": uiux_keyword,
                        "backend developer": backend_keyword,
                        "devops engineer": devops_keyword,
                        "fullstack developer": fullstack_keyword,
                        "software engineer": software_engineer_keyword,
                        "cybersecurity ": cybersecurity_keyword,
                        "business analyst": business_analyst_keyword
                    }

                    role_keywords = role_keywords_mapping.get(role.lower())
                    if role_keywords:
                        # Calculate cosine similarity between role_keywords and skills
                        similarity_score = calculate_cosine_similarity(role_keywords, skills)
                        
                        # Convert cosine similarity to percentage
                        similarity_percentage = int(similarity_score * 80)

                        return similarity_percentage
                    else:
                        return 0
                    
                score1=match_skills_with_role(role,resume_skills)

                # Check for additional resume features
                
                
                
               
                

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
                # Display progress bar

                def calculate_role_score(best_match, role):
                    score2 = 0  # Initialize score
                    if best_match.lower() == role.lower():
                        score2 = 20  # Assign score if there's a match
                    return score2

                matching_score= calculate_role_score(best_match, role)
                resume_score = score1+ matching_score
                score = 0

                # Display progress bar
                my_bar = st.progress(resume_score)

                for percent_complete in range(resume_score):
                    score += 1
                    time.sleep(0.1)
                    if my_bar is not None:
                        my_bar.progress(percent_complete + 1)

                # Display success message
                st.success('** Your Resume Writing Score: ' + str(resume_score) + '**')
                st.warning("** Note: This score is calculated based on the content that  in Resume. **")


                insert_data(resume_data['name'], resume_data['email'], str(resume_score), timestamp,
                            str(resume_data['skills']), role)

            

                connection.commit()
            else:
                st.error("** Sorry, we couldn't process your resume. Please try again later. **")


    else:
        ## Admin Side
        st.success('Welcome to Scoreboard')
        
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')
        ad_role = st.text_input("Enter Role")  # New input field for entering the role
        
        if st.button('Login'):
            if ad_user == 'reema123' and ad_password == '1234':
                st.success("Welcome")
                # Display Data
                # Execute SQL query to fetch data including resume_score
                cursor.execute('''SELECT Name, Email_ID, resume_score, Timestamp FROM user_database WHERE Role = %s''', (ad_role,))
                data = cursor.fetchall()
                
                # Create DataFrame with fetched data and appropriate column names
                df = pd.DataFrame(data, columns=['Name', 'Email', 'resume_score', 'Timestamp'])
                # Sort the DataFrame by 'resume_score' column in descending order
                df_sorted = df.sort_values(by='resume_score', ascending=False)
        
                # Display the sorted DataFrame
                st.dataframe(df_sorted)
            
                st.markdown(get_table_download_link(df_sorted, 'User_Data.csv', 'Download Report'), unsafe_allow_html=True)
            else:
                st.error("Wrong ID & Password Provided")

run()

         
