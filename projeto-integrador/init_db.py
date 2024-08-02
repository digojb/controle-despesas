from models import db, app, Category

with app.app_context():
    db.create_all()

    # Adicionar categorias de exemplo
    if not Category.query.first():
        categorias = ['Alimentação', 'Transporte', 'Moradia', 'Lazer', 'Saúde', 'Educação', 'Salário']
        for nome in categorias:
            categoria = Category(name=nome)
            db.session.add(categoria)

        db.session.commit()
        print("Tabelas e categorias de exemplo criadas com sucesso!")
    else:
        # Verificar se a categoria "Salário" já existe
        if not Category.query.filter_by(name='Salário').first():
            salario_categoria = Category(name='Salário')
            db.session.add(salario_categoria)
            db.session.commit()
            print("Categoria 'Salário' adicionada com sucesso!")
        else:
            print("Categoria 'Salário' já existe.")
