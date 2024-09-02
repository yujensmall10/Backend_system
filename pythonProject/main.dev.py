from app import create_app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True,port=12000, host='0.0.0.0',ssl_context=('C:/Users/USER2226/ChangJiang/pythonProject/ssl/cert.pem', 'C:/Users/USER2226/ChangJiang/pythonProject/ssl/key.pem'))
