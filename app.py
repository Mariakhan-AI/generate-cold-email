import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
import re
from urllib.parse import urlparse


def is_valid_url(url):
    """Validate if the URL is properly formatted"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def extract_skills_from_text(text):
    """Extract relevant skills/keywords from job posting text"""
    # Common tech skills and job-related keywords
    tech_keywords = [
        'python', 'javascript', 'java', 'react', 'nodejs', 'sql', 'aws', 'docker',
        'kubernetes', 'machine learning', 'data science', 'frontend', 'backend',
        'fullstack', 'devops', 'api', 'database', 'html', 'css', 'git', 'agile',
        'scrum', 'tensorflow', 'pytorch', 'django', 'flask', 'spring', 'mongodb',
        'postgresql', 'redis', 'elasticsearch', 'microservices', 'cloud', 'azure',
        'gcp', 'ci/cd', 'testing', 'automation', 'analytics', 'visualization'
    ]
    
    text_lower = text.lower()
    found_skills = []
    
    # Extract skills that appear in the text
    for skill in tech_keywords:
        if skill in text_lower:
            found_skills.append(skill)
    
    # Also extract some key words from the text (remove common words)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text_lower)
    common_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'had', 'but', 'what', 'were', 'they', 'have', 'this', 'from', 'that', 'will', 'with', 'been', 'said', 'each', 'which', 'their', 'time', 'about', 'would', 'there', 'could', 'other', 'after', 'first', 'well', 'water', 'than', 'many', 'them', 'these', 'come', 'made', 'then', 'more', 'very', 'when', 'much', 'before', 'here', 'through', 'just', 'good', 'should', 'because', 'each', 'those', 'people', 'most', 'some', 'time', 'very', 'when', 'much', 'new', 'write', 'would', 'like', 'where', 'right', 'see', 'him', 'two', 'how', 'its', 'who', 'oil', 'sit', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'has', 'may', 'his', 'old', 'take', 'cat', 'again', 'give', 'after', 'came', 'show', 'every', 'good', 'me', 'give', 'our', 'under', 'name', 'very', 'through', 'just', 'form', 'sentence', 'great', 'think', 'say', 'help', 'low', 'line', 'differ', 'turn', 'cause', 'much', 'mean', 'before', 'move', 'right', 'boy', 'old', 'too', 'same', 'tell', 'does', 'set', 'three', 'want', 'air', 'well', 'also', 'play', 'small', 'end', 'put', 'home', 'read', 'hand', 'port', 'large', 'spell', 'add', 'even', 'land', 'here', 'must', 'big', 'high', 'such', 'follow', 'act', 'why', 'ask', 'men', 'change', 'went', 'light', 'kind', 'off', 'need', 'house', 'picture', 'try', 'again', 'animal', 'point', 'mother', 'world', 'near', 'build', 'self', 'earth', 'father', 'head', 'stand', 'own', 'page', 'should', 'country', 'found', 'answer', 'school', 'grow', 'study', 'still', 'learn', 'plant', 'cover', 'food', 'sun', 'four', 'between', 'state', 'keep', 'eye', 'never', 'last', 'let', 'thought', 'city', 'tree', 'cross', 'farm', 'hard', 'start', 'might', 'story', 'saw', 'far', 'sea', 'draw', 'left', 'late', 'run', 'don', 'while', 'press', 'close', 'night', 'real', 'life', 'few', 'north', 'open', 'seem', 'together', 'next', 'white', 'children', 'begin', 'got', 'walk', 'example', 'ease', 'paper', 'group', 'always', 'music', 'those', 'both', 'mark', 'often', 'letter', 'until', 'mile', 'river', 'car', 'feet', 'care', 'second', 'book', 'carry', 'took', 'science', 'eat', 'room', 'friend', 'began', 'idea', 'fish', 'mountain', 'stop', 'once', 'base', 'hear', 'horse', 'cut', 'sure', 'watch', 'color', 'face', 'wood', 'main', 'enough', 'plain', 'girl', 'usual', 'young', 'ready', 'above', 'ever', 'red', 'list', 'though', 'feel', 'talk', 'bird', 'soon', 'body', 'dog', 'family', 'direct', 'leave', 'song', 'measure', 'door', 'product', 'black', 'short', 'numeral', 'class', 'wind', 'question', 'happen', 'complete', 'ship', 'area', 'half', 'rock', 'order', 'fire', 'south', 'problem', 'piece', 'told', 'knew', 'pass', 'since', 'top', 'whole', 'king', 'space', 'heard', 'best', 'hour', 'better', 'during', 'hundred', 'five', 'remember', 'step', 'early', 'hold', 'west', 'ground', 'interest', 'reach', 'fast', 'verb', 'sing', 'listen', 'six', 'table', 'travel', 'less', 'morning', 'ten', 'simple', 'several', 'vowel', 'toward', 'war', 'lay', 'against', 'pattern', 'slow', 'center', 'love', 'person', 'money', 'serve', 'appear', 'road', 'map', 'rain', 'rule', 'govern', 'pull', 'cold', 'notice', 'voice', 'unit', 'power', 'town', 'fine', 'certain', 'fly', 'fall', 'lead', 'cry', 'dark', 'machine', 'note', 'wait', 'plan', 'figure', 'star', 'box', 'noun', 'field', 'rest', 'correct', 'able', 'pound', 'done', 'beauty', 'drive', 'stood', 'contain', 'front', 'teach', 'week', 'final', 'gave', 'green', 'oh', 'quick', 'develop', 'ocean', 'warm', 'free', 'minute', 'strong', 'special', 'mind', 'behind', 'clear', 'tail', 'produce', 'fact', 'street', 'inch', 'multiply', 'nothing', 'course', 'stay', 'wheel', 'full', 'force', 'blue', 'object', 'decide', 'surface', 'deep', 'moon', 'island', 'foot', 'system', 'busy', 'test', 'record', 'boat', 'common', 'gold', 'possible', 'plane', 'stead', 'dry', 'wonder', 'laugh', 'thousands', 'ago', 'ran', 'check', 'game', 'shape', 'equate', 'hot', 'miss', 'brought', 'heat', 'snow', 'tire', 'bring', 'yes', 'distant', 'fill', 'east', 'paint', 'language', 'among', 'grand', 'ball', 'yet', 'wave', 'drop', 'heart', 'present', 'heavy', 'dance', 'engine', 'position', 'arm', 'wide', 'sail', 'material', 'size', 'vary', 'settle', 'speak', 'weight', 'general', 'ice', 'matter', 'circle', 'pair', 'include', 'divide', 'syllable', 'felt', 'perhaps', 'pick', 'sudden', 'count', 'square', 'reason', 'length', 'represent', 'art', 'subject', 'region', 'energy', 'hunt', 'probable', 'bed', 'brother', 'egg', 'ride', 'cell', 'believe', 'fraction', 'forest', 'sit', 'race', 'window', 'store', 'summer', 'train', 'sleep', 'prove', 'lone', 'leg', 'exercise', 'wall', 'catch', 'mount', 'wish', 'sky', 'board', 'joy', 'winter', 'sat', 'written', 'wild', 'instrument', 'kept', 'glass', 'grass', 'cow', 'job', 'edge', 'sign', 'visit', 'past', 'soft', 'fun', 'bright', 'gas', 'weather', 'month', 'million', 'bear', 'finish', 'happy', 'hope', 'flower', 'clothe', 'strange', 'gone', 'jump', 'baby', 'eight', 'village', 'meet', 'root', 'buy', 'raise', 'solve', 'metal', 'whether', 'push', 'seven', 'paragraph', 'third', 'shall', 'held', 'hair', 'describe', 'cook', 'floor', 'either', 'result', 'burn', 'hill', 'safe', 'cat', 'century', 'consider', 'type', 'law', 'bit', 'coast', 'copy', 'phrase', 'silent', 'tall', 'sand', 'soil', 'roll', 'temperature', 'finger', 'industry', 'value', 'fight', 'lie', 'beat', 'excite', 'natural', 'view', 'sense', 'ear', 'else', 'quite', 'broke', 'case', 'middle', 'kill', 'son', 'lake', 'moment', 'scale', 'loud', 'spring', 'observe', 'child', 'straight', 'consonant', 'nation', 'dictionary', 'milk', 'speed', 'method', 'organ', 'pay', 'age', 'section', 'dress', 'cloud', 'surprise', 'quiet', 'stone', 'tiny', 'climb', 'bad', 'oil', 'blood', 'touch', 'grew', 'cent', 'mix', 'team', 'wire', 'cost', 'lost', 'brown', 'wear', 'garden', 'equal', 'sent', 'choose', 'fell', 'fit', 'flow', 'fair', 'bank', 'collect', 'save', 'control', 'decimal', 'gentle', 'woman', 'captain', 'practice', 'separate', 'difficult', 'doctor', 'please', 'protect', 'noon', 'whose', 'locate', 'ring', 'character', 'insect', 'caught', 'period', 'indicate', 'radio', 'spoke', 'atom', 'human', 'history', 'effect', 'electric', 'expect', 'crop', 'modern', 'element', 'hit', 'student', 'corner', 'party', 'supply', 'bone', 'rail', 'imagine', 'provide', 'agree', 'thus', 'capital', 'won', 'chair', 'danger', 'fruit', 'rich', 'thick', 'soldier', 'process', 'operate', 'guess', 'necessary', 'sharp', 'wing', 'create', 'neighbor', 'wash', 'bat', 'rather', 'crowd', 'corn', 'compare', 'poem', 'string', 'bell', 'depend', 'meat', 'rub', 'tube', 'famous', 'dollar', 'stream', 'fear', 'sight', 'thin', 'triangle', 'planet', 'hurry', 'chief', 'colony', 'clock', 'mine', 'tie', 'enter', 'major', 'fresh', 'search', 'send', 'yellow', 'gun', 'allow', 'print', 'dead', 'spot', 'desert', 'suit', 'current', 'lift', 'rose', 'continue', 'block', 'chart', 'hat', 'sell', 'success', 'company', 'subtract', 'event', 'particular', 'deal', 'swim', 'term', 'opposite', 'wife', 'shoe', 'shoulder', 'spread', 'arrange', 'camp', 'invent', 'cotton', 'born', 'determine', 'quart', 'nine', 'truck', 'noise', 'level', 'chance', 'gather', 'shop', 'stretch', 'throw', 'shine', 'property', 'column', 'molecule', 'select', 'wrong', 'gray', 'repeat', 'require', 'broad', 'prepare', 'salt', 'nose', 'plural', 'anger', 'claim', 'continent', 'oxygen', 'sugar', 'death', 'pretty', 'skill', 'women', 'season', 'solution', 'magnet', 'silver', 'thank', 'branch', 'match', 'suffix', 'especially', 'fig', 'afraid', 'huge', 'sister', 'steel', 'discuss', 'forward', 'similar', 'guide', 'experience', 'score', 'apple', 'bought', 'led', 'pitch', 'coat', 'mass', 'card', 'band', 'rope', 'slip', 'win', 'dream', 'evening', 'condition', 'feed', 'tool', 'total', 'basic', 'smell', 'valley', 'nor', 'double', 'seat', 'arrive', 'master', 'track', 'parent', 'shore', 'division', 'sheet', 'substance', 'favor', 'connect', 'post', 'spend', 'chord', 'fat', 'glad', 'original', 'share', 'station', 'dad', 'bread', 'charge', 'proper', 'bar', 'offer', 'segment', 'slave', 'duck', 'instant', 'market', 'degree', 'populate', 'chick', 'dear', 'enemy', 'reply', 'drink', 'occur', 'support', 'speech', 'nature', 'range', 'steam', 'motion', 'path', 'liquid', 'log', 'meant', 'quotient', 'teeth', 'shell', 'neck'}
    
    # Get unique non-common words
    extracted_words = list(set([word for word in words if word not in common_words]))[:15]
    
    # Combine and limit to reasonable number
    all_skills = found_skills + extracted_words
    return list(set(all_skills))[:20]  # Return unique skills, max 20


def create_app(chain, portfolio):
    st.title("📧 Cold Email Generator")
    st.markdown("Generate personalized cold emails based on job postings and your portfolio")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.markdown("**Instructions:**")
        st.markdown("1. Enter a job posting URL")
        st.markdown("2. Click 'Generate Cold Email'")
        st.markdown("3. Review and copy the generated email")
        
        # Add some portfolio info
        st.markdown("---")
        st.markdown("**Portfolio Status:**")
        try:
            portfolio.load_portfolio()
            st.success("✅ Portfolio loaded successfully")
        except Exception as e:
            st.error(f"❌ Portfolio loading failed: {str(e)}")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        url = st.text_input(
            "Job Posting URL:", 
            placeholder="https://careers.company.com/job/123456",
            help="Enter the full URL of the job posting you want to apply for"
        )
    
    with col2:
        st.write("")  # Add some spacing
        st.write("")  # Add some spacing
        submit = st.button("🚀 Generate Cold Email", type="primary")
    
    # URL validation
    if url and not is_valid_url(url):
        st.error("⚠️ Please enter a valid URL (including https://)")
        return
    
    if submit and url:
        if not is_valid_url(url):
            st.error("⚠️ Please enter a valid URL")
            return
            
        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Fetch job posting
            status_text.text("📥 Fetching job posting...")
            progress_bar.progress(25)
            
            loader = WebBaseLoader([url])
            documents = loader.load()
            
            if not documents:
                st.error("❌ Could not fetch content from the URL. Please check if the URL is accessible.")
                return
            
            raw_text = documents[0].page_content
            
            # Check if we got meaningful content
            if len(raw_text.strip()) < 100:
                st.warning("⚠️ The fetched content seems too short. This might not be a job posting.")
            
            progress_bar.progress(50)
            
            # Step 2: Load portfolio
            status_text.text("📂 Loading portfolio...")
            portfolio.load_portfolio()
            progress_bar.progress(75)
            
            # Step 3: Extract skills and find relevant links
            status_text.text("🔍 Analyzing job requirements...")
            skills = extract_skills_from_text(raw_text)
            
            if not skills:
                st.warning("⚠️ Could not extract relevant skills from the job posting.")
                skills = ["general", "software", "development"]  # fallback
            
            progress_bar.progress(90)
            
            # Step 4: Query portfolio
            relevant_links = portfolio.query_links(skills)
            
            # Step 5: Generate email
            status_text.text("✍️ Generating cold email...")
            email = chain.write_mail(raw_text, relevant_links)
            progress_bar.progress(100)
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Display results
            st.success("🎉 Cold email generated successfully!")
            
            # Show analysis results
            with st.expander("📊 Analysis Results", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("🎯 Extracted Skills/Keywords")
                    if skills:
                        for skill in skills:
                            st.badge(skill)
                    else:
                        st.info("No specific skills extracted")
                
                with col2:
                    st.subheader("🔗 Matching Portfolio Projects")
                    if relevant_links:
                        st.success(f"Found {len(relevant_links)} matching projects")
                        for link in relevant_links:
                            st.write(f"• {link}")
                    else:
                        st.warning("No matching portfolio projects found")
                
                # Show job posting preview
                st.subheader("📄 Job Posting Preview")
                preview_text = raw_text[:500] + "..." if len(raw_text) > 500 else raw_text
                st.text_area("Job Content:", preview_text, height=100, disabled=True)
            
            # Display the generated email
            st.subheader("📨 Generated Cold Email")
            st.code(email, language="text")
            
            # Add copy button functionality
            if st.button("📋 Copy Email to Clipboard"):
                st.success("Email copied to clipboard! (Use Ctrl+C to copy the text above)")
            
            # Additional tips
            with st.expander("💡 Tips for Using This Email", expanded=False):
                st.markdown("""
                **Before sending:**
                - Review and personalize the email further
                - Add specific details about the company
                - Double-check all links work correctly
                - Ensure the tone matches your style
                - Add your contact information
                - Proofread for any errors
                """)
                
        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ Error generating email: {str(e)}")
            
            # Show debug information in expander
            with st.expander("🔧 Debug Information", expanded=False):
                st.write(f"**Error Type:** {type(e).__name__}")
                st.write(f"**Error Message:** {str(e)}")
                st.write(f"**URL:** {url}")
                
                # Test URL accessibility
                st.write("**URL Validation:**")
                if is_valid_url(url):
                    st.write("✅ URL format is valid")
                else:
                    st.write("❌ URL format is invalid")


if __name__ == "__main__":
    st.set_page_config(
        layout="wide", 
        page_title="Cold Email Generator", 
        page_icon="📧",
        initial_sidebar_state="expanded"
    )
    
    try:
        chain = Chain()
        portfolio = Portfolio()
        create_app(chain, portfolio)
    except Exception as e:
        st.error(f"❌ Failed to initialize application: {str(e)}")
        st.markdown("**Possible solutions:**")
        st.markdown("- Check if all required modules are installed")
        st.markdown("- Verify your ChromaDB setup is working")
        st.markdown("- Ensure your environment variables are set correctly")
