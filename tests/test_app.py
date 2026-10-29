"""Smoke test de todas las pantallas e interacción básica."""
from pathlib import Path
from streamlit.testing.v1 import AppTest
ROOT=Path(__file__).resolve().parents[1]
app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=60).run()
assert not app.exception,app.exception
pages=list(app.sidebar.radio[0].options)
for page in pages:
    app.sidebar.radio[0].set_value(page).run()
    assert not app.exception,(page,app.exception)
    print('OK:',page)
app.sidebar.radio[0].set_value('5. Categóricas').run()
app.selectbox[0].set_value(app.selectbox[0].options[1]).run()
assert not app.exception
app.sidebar.radio[0].set_value('7. Serie de tiempo').run()
app.slider[0].set_value((100,200)).run()
assert not app.exception
print('Interacciones de par categórico y rango horario: OK')
