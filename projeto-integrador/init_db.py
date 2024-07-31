from models import db, app, Category

with app.app_context():
    db.create_all()

    # Adicionar categorias de exemplo
    if not Category.query.first():
        categorias = ['Alimentação', 'Transporte', 'Moradia', 'Lazer', 'Saúde', 'Educação']
        for nome in categorias:
            categoria = Category(name=nome)
            db.session.add(categoria)

        db.session.commit()
        print("Tabelas e categorias de exemplo criadas com sucesso!")
    else:
        print("Categorias já existem, nenhuma nova categoria adicionada.")
