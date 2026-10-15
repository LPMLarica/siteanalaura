# Agenda Psicóloga Ana Laura

Sistema de consultório para psicóloga, feito em Streamlit, com login e
banco de dados no Supabase.

## O que o sistema faz

- **Início** — sessões do dia, próximos 14 dias, confirmações de amanhã
  com link pronto para o WhatsApp, recebido no mês e valores a receber.
- **Agenda** — calendário (mês/semana/dia/lista) em português. Clique num
  horário para agendar, arraste uma consulta para remarcar, clique numa
  consulta para mudar status, registrar pagamento, remarcar ou excluir.
  Sessões semanais recorrentes, detecção de conflito, horários de
  atendimento e bloqueios (férias/feriados).
- **Pacientes** — cadastro com validação de CPF/e-mail, busca, filtro por
  status e ficha completa: visão geral, histórico de consultas,
  prontuário, financeiro e edição.
- **Prontuário** — evoluções por sessão, **criptografadas** antes de irem
  para o banco, com busca, edição registrada e exportação em PDF.
- **Financeiro** — recebido, a receber e previsto por mês; planilha CSV;
  pendências de meses anteriores.
- **Configurações** — perfil (CRP, valor e duração padrão), horários de
  atendimento, bloqueios, troca de senha e registro de atividades.

## Como a segurança funciona

| Camada | Proteção |
|---|---|
| Login | Supabase Auth (e-mail + senha, confirmação de e-mail, recuperação por código) |
| Dados | Cada registro pertence a um usuário; todas as consultas filtram pelo usuário logado |
| API pública do Supabase | RLS ligado e sem políticas + permissões revogadas: a chave pública não lê nada |
| Prontuário | Texto criptografado com Fernet (`SECRET_KEY`) — nem quem acessa o banco consegue ler |
| Sessão | Expira após inatividade (`SESSION_TIMEOUT_MINUTES`) |
| Auditoria | Acessos a prontuário, exportações e exclusões ficam registrados |

> **Guarde a `SECRET_KEY` em local seguro.** Se ela for perdida ou
> trocada, os prontuários já gravados não podem mais ser lidos.

## Estrutura

```
app.py                  ponto de entrada (configuração, login, navegação)
config/settings.py      leitura de st.secrets / .env
auth/                   Supabase Auth e sessão
dados/                  conexão SQLAlchemy e modelos
services/               regras de negócio (agenda, pacientes, pagamentos...)
security/encryption.py  criptografia do prontuário
views/                  telas
components/             diálogos, formulários e peças visuais
sql/001_schema.sql      schema do banco (Supabase)
.streamlit/             tema e exemplo de secrets
```

## 1. Supabase

O projeto `kzwwtywsvwhywlbzyidd` (Ana Laura's Project, São Paulo) **já está
pronto**: as 8 tabelas foram criadas com `sql/001_schema.sql`, com RLS
ligado e acesso público revogado. Para outro projeto, rode esse arquivo em
**SQL Editor → New query → Run**.

Valores dos secrets:

| Secret | Onde pegar |
|---|---|
| `SUPABASE_URL` | `https://kzwwtywsvwhywlbzyidd.supabase.co` (já no exemplo) |
| `SUPABASE_KEY` | chave *publishable* `sb_publishable_...` (já no exemplo; é pública por natureza) |
| `DATABASE_URL` | botão **Connect** (topo do painel) → **Connection String** → Method **Session pooler** → copie a URI e troque `[YOUR-PASSWORD]` pela senha do banco. Esqueceu a senha? **Project Settings → Database → Reset database password** |
| `SECRET_KEY` | se ficar vazia, o próprio app mostra uma chave gerada na hora; ou rode `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |

> Use o **Session pooler**. A conexão direta (`db.<ref>.supabase.co`) só
> funciona via IPv6 e não conecta a partir do Streamlit Cloud. Nunca use a
> chave `service_role`/secret no app.

Ajustes em **Authentication** (uma vez só):

- **URL Configuration → Site URL**: o endereço do app publicado
  (ex.: `https://agendapsiana.streamlit.app`) — é para onde aponta o
  link de confirmação de e-mail.
- **Emails → Templates → Reset Password**: inclua o código no corpo, por
  exemplo `<p>Seu código: <strong>{{ .Token }}</strong></p>` (a tela
  "Esqueci a senha" pede esse código).
- O envio de e-mails padrão do Supabase só entrega para membros da equipe
  do projeto e tem limite por hora. Para uma única profissional isso basta;
  para mais usuários, configure um SMTP próprio em **Emails → SMTP Settings**.
- Depois de criar a conta da Ana Laura, desligue novos cadastros:
  `ALLOW_SIGNUP = false` nos secrets e, no Supabase, **Sign In / Providers →
  Allow new users to sign up** desligado.

> Projetos gratuitos do Supabase são pausados após ~7 dias sem acesso. Se o
> app mostrar "Não foi possível conectar ao banco", entre no painel do
> Supabase e clique em **Restore project** (leva alguns minutos).

## 2. Publicar no Streamlit Community Cloud

1. Garanta que o código esteja no GitHub (branch `main`).
2. Acesse <https://share.streamlit.io>, entre com o GitHub e clique em
   **Create app → Deploy a public app from GitHub**.
3. Repositório `LPMLarica/siteanalaura`, branch `main`, arquivo
   `app.py`. Escolha um endereço em **App URL**.
4. **Advanced settings**: Python **3.12** e, em **Secrets**, cole o
   conteúdo de `.streamlit/secrets.toml.example` preenchido.
5. **Deploy**. A primeira instalação leva alguns minutos.
6. Volte ao Supabase e coloque o endereço do app em **Site URL**.
7. Abra o app, crie a conta em **Criar conta**, confirme o e-mail e entre.

Para mudar secrets depois: no app, **⋮ → Settings → Secrets** (o app
reinicia sozinho).

## Rodar localmente

```
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # e preencha
streamlit run app.py
```

Sem `DATABASE_URL`, o app usa um SQLite local em `storage/` (só para
testes). `python -m dados.migrations` verifica a conexão e cria as
tabelas que faltarem, sem apagar nada.

Testes automáticos: `pip install pytest && pytest` (SQLite). Para testar
contra Postgres: `TEST_DATABASE_URL=postgresql://... pytest`.
