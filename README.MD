# Agenda Psicóloga

Sistema profissional desenvolvido em Streamlit, com autenticação e
banco de dados no Supabase.

## Recursos

- Login e cadastro por e-mail/senha (Supabase Auth)
- Agenda mensal/semanal/diária, atualizada automaticamente a partir das
  consultas cadastradas
- Cadastro de pacientes
- Prontuário clínico (conteúdo criptografado no banco)
- Controle de pagamentos por consulta (pago/pendente)
- Dashboard com números reais (consultas do dia/semana, pacientes,
  próximos atendimentos)

## Configurar o Supabase

1. Crie um projeto em [supabase.com](https://supabase.com).
2. Em **Project Settings -> API**, copie a **Project URL** e a chave
   **anon public** — vão em `SUPABASE_URL` e `SUPABASE_KEY`.
3. Em **Project Settings -> Database -> Connection string -> URI**,
   copie a connection string do Postgres — vai em `DATABASE_URL`
   (troque `[YOUR-PASSWORD]` pela senha do banco definida na criação
   do projeto).
4. Em **Authentication -> Providers -> Email**, deixe o provedor de
   e-mail/senha habilitado (é o padrão). Em **Authentication ->
   Settings**, você decide se quer exigir confirmação por e-mail antes
   do primeiro login (recomendado em produção).

## Executar

```
python -m venv venv
```

Windows:
```
venv\Scripts\activate
```

Linux/Mac:
```
source venv/bin/activate
```

```
pip install -r requirements.txt
```

Copie `.env.example` para `.env` e preencha `DATABASE_URL`,
`SUPABASE_URL`, `SUPABASE_KEY` e `SECRET_KEY` (veja acima e os
comentários no próprio arquivo):

```
cp .env.example .env
```

Crie as tabelas no banco (SQLite local ou Postgres do Supabase,
conforme `DATABASE_URL`):

```
python -m dados.migrations
```

Rode o app:

```
streamlit run app.py --server.port 8501
```

Na primeira execução, crie sua conta pela aba "Criar conta" na tela de
login.
