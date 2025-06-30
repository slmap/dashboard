# Post-Soviet Index Dashboard

This is a live dashboard built with Dash and Plotly. It tracks:
- Freedom Index (Freedom House)
- Economic Freedom (Heritage)
- GDP PPP (World Bank)

## Deployment
1. Push to GitHub
2. Connect to Render.com
3. Use build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:server`