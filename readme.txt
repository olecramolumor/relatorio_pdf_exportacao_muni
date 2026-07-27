GERAL
    #relatorio_pdf_exportacao_muni
    versão: 1.0
    Descrição: Executavel para geração de .pdf sobre dados de Exportação Municipal de Rondônia

ESTUTURA DO .env:
    DB_DRIVER= Biblioteca do **SQLAlchemy** 
    DB_HOST=127.0.0.1
    DB_NAME=nome_do_banco
    DB_USER=seu_usuario
    DB_PASSWORD=sua_senha
    DB_PORT=123456789
    DB_TAB=nome_da_tabela

    # Configurações de E-mail (Envio de Logs)
    EMAIL_LOGIN=seu_email@dominio.com
    EMAIL_SENHA=sua_senha_ou_app_password
    EMAIL_DESTINATARIOS=destino1@email.com,destino2@email.com

ARQUITETURA SCRIPTS
    main.py:
    onto de entrada (Main) do projeto. Orquestra a execução de todos os scripts e fluxo da aplicação.

    relatorio_csv.py:
    Conecta ao banco de dados e identifica todos os países e anos disponíveis na base para compor os filtros do relatório.

    relatorio_dataframe.py:
    Consulta o banco de dados e extrai os dados filtrados por um país e ano específicos, estruturando-os para processamento.

    relatorio_modelo.py:
    Responsável pela construção visual e estrutural do documento PDF utilizando a biblioteca **ReportLab**.

    relatorio_janela_main.py:
    Módulo da interface gráfica (GUI) que permite ao usuário interagir visualmente com o sistema.
