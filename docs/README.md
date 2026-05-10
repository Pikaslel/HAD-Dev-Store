# Documentación — Prueba Técnica Shopify Developer

Índice de entregables y documentación técnica de la prueba.

---

## Entregables por punto

### Reto 1 — Auditoría Técnica
**Archivo:** `Reto #1.pdf`

---

### Reto 2 — Desarrollo de Funcionalidades en el Tema
**Archivo:** `Reto #2.pdf`

---

### Reto 3 — Integración con Webhook
**Archivo:** `Reto #3.pdf`

Implementación de un flujo de webhook desde Shopify hacia un servidor
externo usando ngrok como túnel y webhook.site como receptor final.

Flujo implementado:
```
Shopify (evento order/paid)
        ↓
Servidor local Python (ngrok tunnel → puerto expuesto)
        ↓
Reenvío al receptor externo (webhook.site)
```

El código del servidor se encuentra en:
```
/services/webhook-paid/main.py
```

Contenido del documento:
- Configuración del webhook en Shopify Admin
- Setup de ngrok y exposición del servidor local
- Código del servidor Python con explicación
- Evidencia del flujo funcionando end-to-end

---

### Reto 4 — Preguntas Técnicas
**Archivo:** `Reto #4.pdf`

## Estructura de archivos relevantes

```
/
├── docs/
│   ├── README.md                        ← este archivo
│   ├── Reto #1.pdf
│   ├── Reto #2.pdf
│   ├── Reto #3.pdf
│   └── Reto #4.pdf
│
└── services/
    └── webhook-paid/
        └── main.py                      ← servidor Python del Reto 3
```
