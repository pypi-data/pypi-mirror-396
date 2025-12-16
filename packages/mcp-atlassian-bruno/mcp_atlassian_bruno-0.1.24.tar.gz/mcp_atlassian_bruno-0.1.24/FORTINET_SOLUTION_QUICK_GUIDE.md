# Fortinet FortiGate SSL Inspection - Guía de Soluciones

## 🔴 Problema Identificado

Tu Jira on-premise (192.168.11.118) está siendo interceptada por **Fortinet FortiGate** con SSL Deep Packet Inspection (DPI).

**Síntoma:** Error "Expecting value: line 1 column 1" - recibiendo HTML en lugar de JSON

---

## 5 Soluciones (Ordenadas por Recomendación)

### **OPCIÓN 1: Certificado CA de Fortinet (RECOMENDADO ⭐⭐⭐)**

**Pasos:**
1. Obtener certificado CA de Fortinet (contactar equipo de infraestructura)
2. Copiar a servidor MCP: `/etc/ssl/certs/fortinet-ca.pem`
3. Configurar en `.env`:
   ```
   JIRA_CERT=/etc/ssl/certs/fortinet-ca.pem
   JIRA_SSL_VERIFY=true
   ```
4. Reiniciar MCP

**Ventajas:**
- ✅ Soluciona el problema de raíz
- ✅ SSL verification sigue activa (seguro)
- ✅ Funciona para todas las herramientas que usan HTTPS

**Desventajas:**
- Requiere certificado de Fortinet

---

### **OPCIÓN 2: Exclusión en Fortinet (MEJOR A LARGO PLAZO ⭐⭐⭐)**

**Acciones (coordinar con equipo de infraestructura/seguridad):**

En FortiGate - CLI:
```
config firewall ssl-ssh-profile
    edit "monitor-all"
        config ssl-exempt
            edit 1
                set type server-address
                set address "192.168.11.118"
            next
        end
    next
end
```

O en Web UI:
- Security Profiles → SSL/SSH Inspection
- Agregar excepción para IP/dominio de Jira

**Ventajas:**
- ✅ Solución permanente
- ✅ No requiere cambios en MCP
- ✅ Mejora rendimiento

**Desventajas:**
- Requiere acceso FortiGate (infraestructura)

---

### **OPCIÓN 3: Deshabilitar Verificación SSL (RÁPIDO - NO RECOMENDADO)**

En `.env`:
```
JIRA_SSL_VERIFY=false
```

**Ventajas:**
- ✅ Solución inmediata
- ✅ No requiere certificado

**Desventajas:**
- ❌ Vulnerable a ataques MITM
- ❌ No es seguro para producción
- ❌ Solo para testing/desarrollo

---

### **OPCIÓN 4: Ruta Alternativa (Si disponible)**

Si existe DNS interno para Jira:
```
JIRA_URL=https://jira-internal.ingeteamenergy.com
```

En lugar de:
```
JIRA_URL=https://192.168.11.118
```

**Ventajas:**
- ✅ Podría evitar inspección de Fortinet
- ✅ Mejor para DNS resolution

**Desventajas:**
- Requiere configuración DNS disponible

---

### **OPCIÓN 5: Proxy Corporativo**

Si existe proxy que no inspecciona HTTPS:
```
JIRA_HTTP_PROXY=http://proxy.corp:8080
JIRA_HTTPS_PROXY=http://proxy.corp:8080
```

**Ventajas:**
- ✅ Centraliza control de tráfico

**Desventajas:**
- Requiere proxy disponible
- Tráfico sigue visible a proxy

---

## 🔍 Diagnóstico

### Verificar si es Fortinet:

```bash
# Descargar respuesta de Jira (ignorando SSL)
curl -k -v -u usuario:token https://192.168.11.118/rest/api/2/project 2>&1

# Buscar indicadores de Fortinet en respuesta:
# - "fgtauth"
# - "FortiWeb" en Server header
# - "X-FortiWeb-" headers
# - HTML en lugar de JSON
```

### Script de diagnóstico:
```bash
uv run python diagnose_fortinet.py
```

---

## ✅ Verificación Final

Después de aplicar solución, verificar:
```bash
# 1. Conectar a MCP
mcp-atlassian

# 2. En cliente MCP, llamar:
{
  "method": "tools/call",
  "params": {
    "name": "jira_get_all_projects",
    "arguments": {"include_archived": false}
  }
}

# 3. Debe retornar lista JSON, no HTML/error
```

---

## 📋 Resumen de Configuración Actual

```
JIRA_URL = https://jira.ingeteamenergy.com
JIRA_SSL_VERIFY = false (actualmente deshabilitado)
JIRA_CERT = NO CONFIGURADO
```

**Recomendación:** 
1. **Corto plazo:** Usar OPCIÓN 1 (Certificado CA)
2. **Largo plazo:** Usar OPCIÓN 2 (Exclusión Fortinet)
3. **Producción:** NUNCA usar OPCIÓN 3 (SSL_VERIFY=false)

---

## 📞 Escalación

Si problema persiste:
1. Contactar equipo de Infraestructura/Networking
2. Solicitar:
   - Certificado CA de Fortinet FortiGate, O
   - Exclusión de 192.168.11.118:443 de SSL Inspection
3. Compartir error exacto: "Expecting value: line 1 column 1 (char 0)"

---

## 📚 Referencias

- [Fortinet FortiGate Docs](https://docs.fortinet.com/product/fortigate)
- [Jira API Auth](https://developer.atlassian.com/cloud/jira/rest/authenticate-asapp/)
- [Python SSL Verification](https://docs.python-requests.org/en/latest/user/advanced/#ssl-warnings)
