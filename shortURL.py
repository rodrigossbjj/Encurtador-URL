from flask import Flask, request, jsonify, redirect
import string
import random
import pymysql

app = Flask(__name__)

# Dicionário para armazenar as URLs (em memória)
short_to_full = {}
full_to_short = {}

# Configuração do banco de dados PostgreSQL hospedado na AWS
DATABASE_CONFIG = {
    "user": "",
    "password": "",
    "host": "",
    "port": 0,
    "database": ""
}

# Função para obter conexão com o banco de dados
def get_db_connection():
    return pymysql.connect(
        user=DATABASE_CONFIG["user"],
        password=DATABASE_CONFIG["password"],
        host=DATABASE_CONFIG["host"],
        port=DATABASE_CONFIG["port"],
        database=DATABASE_CONFIG["database"]
    )

# Geração de um código curto aleatório
def generate_short_code():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))


@app.route('/')
def index():
    return "Servidor Flask está funcionando!"

@app.route('/shorten', methods=['POST'])
def shorten():
    data = request.json
    original_url = data.get('url')
    
    # Se a URL já foi encurtada, retorne o mesmo código
    if original_url in full_to_short:
        short_code = full_to_short[original_url]
    else:
        # Caso contrário, gere um novo código
        short_code = generate_short_code()
        short_to_full[short_code] = original_url
        full_to_short[original_url] = short_code

        # Inserção das URL's no Banco de Dados 
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO UrlEncurtador (url_full, url_encurtada) VALUES (%s, %s)",
                (original_url, short_code)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            return jsonify({'error': f"Erro ao inserir no banco de dados: {str(e)}"}), 500

    # Resposta com o link encurtado
    return jsonify({'short_url': f"http://dominio.com/{short_code}"})

@app.route('/<short_code>')
def redirect_to_url(short_code):
    # Redireciona para a URL correspondente, se existir
    if short_code in short_to_full:
        return redirect(short_to_full[short_code])
     
    # Caso não esteja no dicionário, busca no banco de dados
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fazendo a busca no banco de dados
        cursor.execute("SELECT url_full FROM UrlEncurtador WHERE url_encurtada = %s", (short_code,))
        result = cursor.fetchone()
        conn.close()

        if result:
            # Salva nos dicionários para uso futuro
            original_url = result[0]
            short_to_full[short_code] = original_url
            full_to_short[original_url] = short_code
            return redirect(original_url)
        else:
            return "URL not found", 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

if __name__ == '__main__':
    #app.run()
    app.run(debug=True, host="0.0.0.0", port=80)
    