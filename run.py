from app import create_app  # Asegúrate de importar la función create_app desde tu módulo app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
