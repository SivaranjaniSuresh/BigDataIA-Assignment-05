from diagrams import Cluster, Diagram, Edge
from diagrams.aws.storage import S3
from diagrams.custom import Custom
from diagrams.onprem.client import User
from diagrams.onprem.workflow import Airflow
from diagrams.programming.language import Python

graph_attr = {
    "splines": "ortho",
    "overlap": "false",
    "nodesep": "1.0",
    "ranksep": "1.5",
    "fontsize": "12",
    "fontname": "Verdana",
}

with Diagram("MP3 Transcript Workflow", show=False, graph_attr=graph_attr):
    user = User("Streamlit User")

    with Cluster("Streamlit App"):
        streamlit_app = Custom("Streamlit App", "architechture\streamlit.png")
        youtube_vlog = Python("Youtube Vlog")
        translation = Python("Translation")
        phrasebook = Python("PhraseBook")
        forex = Python("Forex Management")
        emergency_contact = Python("Emergency Contacts")

    with Cluster("APIs"):
        open_ai = Custom("OpenAI", r"architechture\openai.png")
        google_text_to_speech = Custom("Google Text-To-Speech", r"architechture\text_to_speech.png")
        unsplash = Custom("Unsplash", r"architechture\unsplash.png")
    
    with Cluster("Core Functionality"):
         generate_itenary = Python("Generate Itenary")
         download_audio = Python("Youtube - to- Audio")
         forex_library = Python("Forex Library")
         prompt_engineering = Python("Prompt Engineering")
    ########################################################################################################
    ### Workflow connections
    ########################################################################################################

    ## UserFlow
    user >> streamlit_app >> youtube_vlog
    streamlit_app >> translation 
    streamlit_app >> phrasebook 
    streamlit_app >> forex  
    streamlit_app >> emergency_contact

    
    ## Functionaility
    youtube_vlog >> download_audio >> prompt_engineering >> open_ai >> unsplash >> generate_itenary
    phrasebook >> prompt_engineering >> open_ai
    translation  >> prompt_engineering >> open_ai >> google_text_to_speech
    forex >> forex_library
    emergency_contact >> prompt_engineering >> open_ai

    streamlit_app << open_ai
    streamlit_app << google_text_to_speech
    streamlit_app << unsplash
    streamlit_app << generate_itenary
    user << streamlit_app
