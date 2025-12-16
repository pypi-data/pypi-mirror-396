pobyaryan is a lightweight Python package that turns a command-line interface into a smart AI agent named PO, built by ARYAN.


🧠 What PO Can Do:
 
 ✔ Understand natural language commands

 ✔ Build scalable, robust frontend code

 ✔ Assist with development

 ✔ Manage your filesystem 

 ✔ Execute shell/terminal commands safely

 ✔ Chat interactively in a REPL

 

 🚀 Installation

pip install pobyaryan



🏃 How to use PO ?

   💡 PO uses Google GenAI API 💡 

   ● Run PO directly from your terminal:

     🔑 Set Your API Key (Required):
     po --api-key YOUR_KEY

     eg -> po --api-key AIzaSyC9CCCKDKpcAg98zsrBBEPEDwEMVNralX0 


   ● PO is now activated and You can interact with him, as the 'USER', via terminal!

      eg -> USER : create me a frontend for wedding site # USE DETAILED PROMPTS TO BUILD MORE SPECIFIC ACCORDING TO UR CONVINIENCE ✨
            PO   : Sure! I’ll create a clean and elegant wedding website frontend for you.

                   I’ll include:
                   - A hero section with the couple’s names
                   - Date & venue section
                   - A love story/about section
                   - RSVP button
                   - Soft pastel theme
                   
                   Creating project structure...
                   
                   📁 Creating folder: wedding_site
                   📄 Creating files:
                   - wedding_site/index.html
                   - wedding_site/styles.css
                   - wedding_site/script.js
                   Let me know if you want animations, a gallery, timeline section, or a more modern aesthetic!


     👋 To terminate/deactivate the session:
            
            ● Use 'over n out'
            eg ->
                 USER : over n out
                 PO   : Over and out! 👋
     

       💡  IF ANY ERROR IS FACED THEN GENERATE A NEW API KEY TO ACTIVATE THE PO!




🖥️   TO RUN LOCALLY, FOLLOW THE STEPS ->
       
       ● requires python >= 3.9

       ● set a virtual environment/ 'py -m {name} venv' followed by '{name}/Scripts/activate' -> terminal

       ● clone this repo ->terminal

       ● pip install -r requirements.txt -> terminal

       ● set env var / ' $env:PO_GENAI_API_KEY = "YOUR_KEY_HERE" ' -> terminal

       ● run the command ' python -m pobyaryank.agent ' ->terminal


















