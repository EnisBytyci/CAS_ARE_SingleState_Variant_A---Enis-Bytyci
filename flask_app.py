import os
from flask import Flask, jsonify, render_template, request, send_file

from chatbot.chatbot import Chatbot

PYTHONANYWHERE_USERNAME = "carvice"
PYTHONANYWHERE_WEBAPPNAME = "mysite"

app = Flask(__name__)

my_type_role = """
Als intelligentes Erinnerungswerkzeug und Informationssystem helfe ich Ihnen, sich an Gedanken zu erinnern, die Ihnen momentan schwerfallen abzurufen. 
Um Ihnen effektiv zu assistieren, werde ich Ihnen spezifische Fragen stellen, basierend auf Antworten. 
Diese Fragen sind darauf ausgerichtet, Ihnen zu helfen, die Verbindungen zwischen Ihren Gedanken und den schwer fassbaren Informationen zu finden. 
Bitte beschreiben Sie, was Ihnen durch den Kopf geht, und ich werde Ihnen gezielte Fragen stellen, um den Nebel um Ihre flüchtigen Gedanken zu lichten.
"""

my_instance_context = """
Zusätzlich zu spezifischen Fragen werde ich offene Fragen verwenden, um Ihnen zu helfen, breiter über das Thema nachzudenken, das Ihnen im Moment entgleitet. 
Ich werde Sie ermutigen, Ihre Gedanken und Empfindungen frei zu äussern, um verschiedene Aspekte und mögliche Verknüpfungen Ihrer Erinnerungen zu erkunden. 
Beispielsweise könnte ich fragen: Was fällt Ihnen ein, wenn Sie an das Thema denken? Können Sie beschreiben, welche Gefühle oder Eindrücke Sie haben, wenn Sie an das 
spezifische Ereignis denken oder gibt es bestimmte Wörter oder Bilder, die ihnen in den Sinn kommen, wenn Sie über dieses Thema nachdenken? 
"""

my_instance_starter = """
Guten Tag! Ich bin hier, um Ihnen zu helfen, sich an die Dinge zu erinnern, die Ihnen gerade schwerfallen zu erfassen. 
Denken Sie gerade an etwas Bestimmtes, das Ihnen 'auf der Zunge liegt? 
Bitte teilen Sie mir mit, um welches Thema es geht, oder beschreiben Sie, was Ihnen dazu einfällt. Gemeinsam können wir die fehlenden Puzzleteile finden
"""

bot = Chatbot(
    database_file="database/chatbot.db", 
    type_id="coach",
    user_id="daniel",
    type_name="VarianteA",
    type_role=my_type_role,
    instance_context=my_instance_context,
    instance_starter=my_instance_starter
)

bot.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/mockups.pdf', methods=['GET'])
def get_first_pdf():
    script_directory = os.path.dirname(os.path.realpath(__file__))
    files = [f for f in os.listdir(script_directory) if os.path.isfile(os.path.join(script_directory, f))]
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    if pdf_files:
        # Get the path to the first PDF file
        pdf_path = os.path.join(script_directory, pdf_files[0])

        # Send the PDF file as a response
        return send_file(pdf_path, as_attachment=True)

    return "No PDF file found in the root folder."

@app.route("/<type_id>/<user_id>/chat")
def chatbot(type_id: str, user_id: str):
    return render_template("chat.html")


@app.route("/<type_id>/<user_id>/info")
def info_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: dict[str, str] = bot.info_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/conversation")
def conversation_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: list[dict[str, str]] = bot.conversation_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/response_for", methods=["POST"])
def response_for(type_id: str, user_id: str):
    user_says = None
    # content_type = request.headers.get('Content-Type')
    # if (content_type == 'application/json; charset=utf-8'):
    user_says = request.json
    # else:
    #    return jsonify('/response_for request must have content_type == application/json')

    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    assistant_says_list: list[str] = bot.respond(user_says)
    response: dict[str, str] = {
        "user_says": user_says,
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)


@app.route("/<type_id>/<user_id>/reset", methods=["DELETE"])
def reset(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    bot.reset()
    assistant_says_list: list[str] = bot.start()
    response: dict[str, str] = {
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)
