# Agenda Psicóloga

Sistema profissional desenvolvido em Streamlit.

## Recursos

- Login Google

- Agenda

- Google Calendar

- Consultas

- Pacientes

- Dashboard

## Executar

python -m venv venv

Windows

venv\Scripts\activate

Linux

source venv/bin/activate

pip install -r requirements.txt

streamlit run app.py --server.port 8501

## Configurar login Google

No Google Cloud Console, abra o cliente OAuth do tipo Web e adicione exatamente
o URI abaixo em "Authorized redirect URIs":

http://localhost:8501

O endereço precisa ser idêntico ao valor de `GOOGLE_REDIRECT_URI` no arquivo
`.env`, incluindo protocolo, porta e ausência ou presença da barra final.