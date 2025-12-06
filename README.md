# AI Vendor Trust Pilot (MVP)

MVP listo para demo comercial que evalúa el riesgo de proveedores (con o sin IA) según expectativas de cumplimiento europeas/España.

## ¿Qué problema resuelve?
Las áreas de seguridad y legal en la UE piden evidencias de: residencia de datos, mecanismos de transferencia (SCCs), cifrado, certificaciones (ISO 27001/SOC 2) y guardrails de IA. Este servicio genera un informe automático y argumentado para acelerar ventas enterprise.

## Endpoints principales
- `GET /health`: ping.
- `POST /vendors`: registra un proveedor.
- `POST /vendors/{vendor_name}/risk`: calcula un informe de riesgo (si el proveedor no existe usa un perfil por defecto para simular due diligence en vivo).
- `POST /data-sovereignty`: comprueba residencia de datos y subprocesadores.
- `GET /demo`: devuelve un ejemplo preparado para un proveedor "IberiaCloud AI" listo para enseñar en demos.

## Ejecutar localmente
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Abre `http://localhost:8000/docs` para probar el MVP.

## Cómo venderlo ya
1. **Discovery express:** Introduce datos básicos del proveedor y muestra el informe en `/vendors/{name}/risk` durante la llamada.
2. **Diferenciador UE/Spain:** Resalta que incluye residencia de datos UE/EEA, SCCs y guardrails de IA (alineado con exigencias de clientes bancarios/retail españoles).
3. **Próximos upsells:** exportar PDF del informe, conectores a GRC (OneTrust/Vanta), y monitoreo continuo de subprocesadores.
