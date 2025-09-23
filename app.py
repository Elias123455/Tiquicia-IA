# -----------------------------------------------------------------------------
# ARCHIVO: app.py (VERSIÓN 15.0 - ESTRUCTURA COMENTADA Y ROBUSTA)
# -----------------------------------------------------------------------------

# --- A1: IMPORTACIONES ---
# Aquí cargamos todas las herramientas que necesitamos para el proyecto.
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import supabase
import os
import pickle
import numpy as np
import random
import nltk
from nltk.stem import SnowballStemmer
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY

# --- A2: CONEXIÓN CON LA BASE DE DATOS ---
# Establecemos la conexión principal con Supabase usando nuestra llave de administrador.
try:
    supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    print("✅ Conexión con Supabase (como admin) establecida con éxito.")
except Exception as e:
    print(f"!!!!!!!!!! ERROR DE CONEXIÓN CON SUPABASE !!!!!!!!!!!\nError: {e}")
    supabase_client = None

# --- B1: CLASE DEL CEREBRO DE LA IA (NEURAL NETWORK) ---
# Esta clase contiene toda la lógica de la inteligencia artificial.
class NeuralNetwork:
    # --- B2: INICIALIZACIÓN DE LA IA ---
    # Al crear la IA, intentamos cargar su cerebro desde un archivo guardado.
    def __init__(self):
        self.model_file = "model_data.pkl"
        self.words, self.classes, self.weights1, self.weights2, self.data = [], [], None, None, None
        if os.path.exists(self.model_file):
            print("Cargando cerebro pre-entrenado...")
            self._load_model()
        else:
            print("¡ADVERTENCIA! No se encontró 'model_data.pkl'. La IA no podrá responder.")
            
    # --- B3: MÉTODO PARA CARGAR EL CEREBRO ---
    # Lee el archivo 'model_data.pkl' y carga los datos de la IA en memoria.
    def _load_model(self):
        try:
            with open(self.model_file, 'rb') as file:
                saved_data = pickle.load(file)
            self.words, self.classes, self.weights1, self.weights2, self.data = saved_data['words'], saved_data['classes'], saved_data['weights1'], saved_data['weights2'], saved_data['data']
            print("Cerebro cargado exitosamente.")
        except Exception as e: print(f"Error al cargar el cerebro: {e}")
            
    # --- B4: FUNCIONES MATEMÁTICAS DE LA RED NEURONAL ---
    # Estas son las operaciones internas que permiten a la red "pensar".
    def _sigmoid(self, x): return 1 / (1 + np.exp(-x))

    def _bag_of_words(self, sentence):
        stemmer = SnowballStemmer('spanish')
        try: sentence_words = nltk.word_tokenize(sentence, language='spanish')
        except LookupError: nltk.download('punkt', quiet=True); sentence_words = nltk.word_tokenize(sentence, language='spanish')
        sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
        bag = [0] * len(self.words)
        for s in sentence_words:
            for i, w in enumerate(self.words):
                if w == s: bag[i] = 1
        return np.array(bag)

    # --- B5: MÉTODO PRINCIPAL DE PREDICCIÓN ---
    # Recibe una frase del usuario y devuelve una respuesta inteligente.
    def predict(self, sentence):
        if self.weights1 is None or self.weights2 is None: return "Lo siento, mi cerebro no está cargado."
        try:
            bow = self._bag_of_words(sentence)
            layer1 = self._sigmoid(np.dot(bow, self.weights1))
            results = self._sigmoid(np.dot(layer1, self.weights2))
            ERROR_THRESHOLD = 0.25
            results_list = [[i, r] for i, r in enumerate(results) if r > ERROR_THRESHOLD]
            if not results_list: return "No estoy segura de cómo responder a eso."
            results_list.sort(key=lambda x: x[1], reverse=True)
            tag = self.classes[results_list[0][0]]
            for intent in self.data['intents']:
                if intent['tag'] == tag: return random.choice(intent['responses'])
            return "No estoy segura de cómo responder a eso."
        except Exception as e:
            print(f"!!!!!!!!!! ERROR DURANTE LA PREDICCIÓN !!!!!!!!!!!\nError: {e}")
            return "Lo siento, tuve un problema interno al procesar tu solicitud."

# --- C1: CONFIGURACIÓN DE FLASK E INSTANCIA DE LA IA ---
# Aquí preparamos la aplicación web y creamos el objeto principal de la IA.
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)
nn = NeuralNetwork()

# --- D1: FUNCIÓN DE AYUDA PARA AUTENTICACIÓN ---
# Esta función revisa la "llave" (token JWT) del usuario para saber quién es.
def get_user_from_token(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '): return None
    jwt = auth_header.split(' ')[1]
    try:
        temp_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)
        user_response = temp_client.auth.get_user(jwt)
        return user_response.user
    except Exception as e: return None

# --- E1: RUTAS PARA SERVIR PÁGINAS HTML ---
# Estas funciones le dicen a Flask qué página HTML mostrar en cada URL.
@app.route('/')
def auth_page(): return render_template('index.html')

@app.route('/chat')
def chat_page(): return render_template('chat.html')

@app.route('/admin')
def admin_page(): return render_template('admin.html')

# --- F1: RUTAS DE API (LA "COCINA" DE LA APLICACIÓN) ---
# Estas funciones son los puntos de conexión que el JavaScript usa para hablar con el servidor.

# --- F2: API DE ROLES ---
# Verifica el rol de un usuario (user o admin) consultando nuestra base de datos.
@app.route('/get-user-role', methods=['GET'])
def get_user_role():
    user = get_user_from_token(request)
    if not user: return jsonify({"error": "No autorizado"}), 401
    try:
        profile_response = supabase_client.table('users').select('role').eq('id', user.id).single().execute()
        role = profile_response.data.get('role', 'user') if profile_response.data else 'user'
        return jsonify({"role": role})
    except Exception as e: return jsonify({"role": "user"})

# --- F3: API DE GESTIÓN DE CHATS ---
# Permite obtener, crear y eliminar las conversaciones de un usuario.
@app.route('/api/chats', methods=['GET'])
def get_chats():
    user = get_user_from_token(request)
    if not user: return jsonify({"error": "No autorizado"}), 401
    try:
        chats_response = supabase_client.table('chats').select('id, title, created_at').eq('user_id', user.id).order('created_at', desc=True).execute()
        return jsonify(chats_response.data), 200
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/api/chats', methods=['POST'])
def create_chat():
    user = get_user_from_token(request)
    if not user: return jsonify({"error": "No autorizado"}), 401
    try:
        # Lógica de "Conversación Inicial"
        count_response = supabase_client.table('chats').select('id', count='exact').eq('user_id', user.id).execute()
        chat_title = 'Conversación Inicial' if len(count_response.data) == 0 else 'Nueva Conversación'
        response = supabase_client.table('chats').insert({'user_id': user.id, 'title': chat_title}).select().single().execute()
        
        if response.data: return jsonify(response.data), 201
        else: raise Exception("La creación del chat no devolvió datos.")
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/api/chats/<int:chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    user = get_user_from_token(request)
    if not user: return jsonify({"error": "No autorizado"}), 401
    try:
        # Lógica para no poder eliminar la última conversación
        count_response = supabase_client.table('chats').select('id', count='exact').eq('user_id', user.id).execute()
        if len(count_response.data) <= 1:
            return jsonify({"error": "No se puede eliminar la última conversación."}), 400

        # Verificación de propiedad antes de borrar
        chat_owner_response = supabase_client.table('chats').select('user_id').eq('id', chat_id).eq('user_id', user.id).single().execute()
        if not chat_owner_response.data: return jsonify({"error": "Acceso denegado"}), 403
        
        supabase_client.table('chats').delete().eq('id', chat_id).execute()
        return jsonify({"message": "Chat eliminado"}), 200
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- F4: API DE GESTIÓN DE MENSAJES ---
# Permite obtener y guardar mensajes en un chat específico.
@app.route('/api/chats/<int:chat_id>/messages', methods=['GET'])
def get_messages(chat_id):
    user = get_user_from_token(request)
    if not user: return jsonify({"error": "No autorizado"}), 401
    try:
        # Verificación de propiedad
        chat_owner_response = supabase_client.table('chats').select('user_id').eq('id', chat_id).eq('user_id', user.id).single().execute()
        if not chat_owner_response.data: return jsonify({"error": "Acceso denegado"}), 403
        
        messages_response = supabase_client.table('messages').select('*').eq('chat_id', chat_id).order('created_at').execute()
        return jsonify(messages_response.data), 200
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/predict', methods=['POST'])
def handle_prediction():
    user = get_user_from_token(request)
    if not user: return jsonify({"error": "No autorizado"}), 401
    data = request.get_json()
    question, chat_id = data.get('question'), data.get('chat_id')
    if not question or not chat_id: return jsonify({"error": "Faltan datos"}), 400
    try:
        # Guardar mensaje de usuario y respuesta de la IA en la base de datos
        supabase_client.table('messages').insert({'chat_id': chat_id, 'sender': 'user', 'content': question}).execute()
        ia_answer = nn.predict(question)
        supabase_client.table('messages').insert({'chat_id': chat_id, 'sender': 'ia', 'content': ia_answer}).execute()
        return jsonify({'answer': ia_answer})
    except Exception as e: return jsonify({"error": str(e)}), 500

# --- G1: PUNTO DE ENTRADA DE LA APLICACIÓN ---
# Esta es la línea que finalmente enciende el motor del servidor.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

