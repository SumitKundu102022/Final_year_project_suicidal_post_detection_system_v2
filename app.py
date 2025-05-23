import streamlit as st
from dotenv import load_dotenv
import os
import requests
import pickle
# import tweepy

from keras.preprocessing.sequence import pad_sequences
from keras.models import load_model


from bdi_tool import calculate_bdi_score
from prediction_method import display_prediction

# Load environment variables
load_dotenv()

# Utility function to download model/tokenizer if not present
def download_file(url, local_filename):
    if not os.path.exists(local_filename):
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

# URLs for model and tokenizer
MODEL_URL = os.getenv("MODEL_URL")        # Replace with actual URL
TOKENIZER_URL = os.getenv("TOKENIZER_URL")    # Replace with actual URL
# TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Download model/tokenizer if not already present
download_file(MODEL_URL, "model.h5")
download_file(TOKENIZER_URL, "tokenizer.pkl")              


# Load necessary files
token_form = pickle.load(open('tokenizer.pkl', 'rb'))
model = load_model("model.h5", compile=False)

# Twitter client setup
# client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
# def extract_tweet_text(tweet_url):
#     try:
#         tweet_id = tweet_url.strip("/").split("/")[-1].split("?")[0]
#         response = client.get_tweet(tweet_id, tweet_fields=["text"])
#         return response.data["text"]
#     except Exception as e:
        # return f"Error fetching tweet: {e}"
        
# Function to reset the form
# Initialize session state
if 'post_content' not in st.session_state:
    st.session_state['post_content'] = ''
if 'input_method' not in st.session_state:
    st.session_state['input_method'] = 'Paste Post Content'
if 'trigger_rerun' not in st.session_state:
    st.session_state['trigger_rerun'] = False


# Reset function
def reset_form():
    st.session_state['post_content'] = ''
    st.session_state['input_method'] = 'Paste Post Content'
    st.session_state['trigger_rerun'] = True
    # st.rerun()  # Properly resets UI components

def main():
    """Main function to run the Streamlit app."""
    
    st.set_page_config(page_title="Suicidal Post Detection System", page_icon="🎯", layout="centered")
    
    col1, col2 = st.columns([10, 1])
    with col1:
        st.markdown("""
        <h1 style='text-align: center; color: #1A5276;'>Suicidal Post Detection System</h1>
        <p style='text-align: center; color: #34495E;'>
            Enter the content of the post below to check for potential suicidal ideation:
        </p>
    """, unsafe_allow_html=True)
    
    with col2:
        st.button("🔄", on_click=reset_form)
             

    
    # sentence = st.text_input("Enter your post content here")
    # responses = []
    option = st.radio("Choose input method:", ["Paste Post Content", "Paste Link (for article-based content only)"],key="input_method")

    sentence = ""
    # 🔧 Initialize responses list outside any condition
    responses = []

    if option == "Paste Link (for article-based content only)":
        url = st.text_input("Paste the URL here (e.g., blog, news article):")
        unsupported_domains = ["instagram.com","twitter.com","x.com", "facebook.com", "linkedin.com"]
        if url:
            if any(domain in url for domain in unsupported_domains):
                st.error(f"⚠ The domain `{url.split('/')[2]}` is currently unsupported. Please paste the post content manually.")
                st.stop()
            # elif "twitter.com" in url or "x.com" in url:
            #     # Extract tweet text using the Twitter API
            #     sentence = extract_tweet_text(url)
            #     if sentence.startswith("Error"):
            #         st.warning(sentence)
            #         sentence = ""
            #         st.stop()
            #     else:
            #         st.success("✅ Tweet content extracted:")
            #         st.write(sentence)
            else:
                try:
                    from newspaper import Article
                    article = Article(url)
                    article.download()
                    article.parse()
                    sentence = article.text.strip()
                    if not sentence:
                        st.warning("Unable to extract content from this link.")
                    else:
                        st.success("✅ Content extracted:")
                        st.write(sentence)
                except Exception as e:
                    st.error(f"Error fetching content: {e}")
    else:
        sentence = st.text_area("Paste your post content here:", key="post_content")
        
        # BDI-II Section BDI-II Depression Severity Assessment
        st.markdown("""
        ### Check For Depression Severity Assessment(BDI-II)
        Select the statement that best describes how you have been feeling during the past two weeks.
        """)
        
        questions = [
        "Sadness", "Pessimism", "Past Failure", "Loss of Pleasure", "Guilty Feelings", "Punishment Feelings",
        "Self-Dislike", "Self-Criticalness", "Suicidal Thoughts or Wishes", "Crying", "Agitation", "Loss of Interest",
        "Indecisiveness", "Worthlessness", "Loss of Energy", "Changes in Sleeping Pattern", "Irritability",
        "Changes in Appetite", "Concentration Difficulty", "Tiredness or Fatigue", "Loss of Interest in Sex"
        ]
        
        for i, question in enumerate(questions, start=1):
            # response = st.slider(f"{i}. {question} (0: None, 3: Severe)", 0, 3, 0)
            response = st.slider(
                        f"{i}. {question}", 
                        min_value=0, 
                        max_value=3, 
                        value=0, 
                        step=1, 
                        format="%d"  # Ensures the number line is shown
            )
            responses.append(response)
    
    
    # Prediction button
    predict_btt = st.button("Predict", key="predict_button", help="Click to analyze the post")
    
    if st.session_state.get('trigger_rerun', False):
        st.session_state['trigger_rerun'] = False  # Reset flag
        st.rerun()

    if predict_btt:
        if not sentence.strip():
            st.error("⚠ Please enter some text for analysis.")
            return
        
        st.markdown(f"*Post content:* {sentence}")
        
        # Preprocess input text
        twt = token_form.texts_to_sequences([sentence])
        twt = pad_sequences(twt, maxlen=50)
        prediction = model.predict(twt)[0][0]
        
        # Only calculate and display BDI-II if manual content is selected
        if option == "Paste Post Content":
            try:
                bdi_score, severity = calculate_bdi_score(responses)
            except ValueError as e:
                st.error(str(e))
                return
        else:
            bdi_score, severity = None, None
        
        # Display prediction results
        display_prediction(prediction, bdi_score, severity)
if __name__ == '__main__':
    main()
