#!/usr/bin/env python3
"""
Fortinet FortiGate SSL Inspection Issue - Solutions and Workarounds

PROBLEMA:
=========
Cuando el MCP intenta conectar a Jira on-premise a través de Fortinet FortiGate,
las peticiones HTTPS son interceptadas y redirigidas al portal de autenticación:
  https://192.168.11.118/fgtauth?...

El MCP recibe HTML en lugar de JSON, causando errores de parseo:
  "Expecting value: line 1 column 1 (char 0)"

CAUSAS:
=======
1. Fortinet FortiGate hace SSL Deep Packet Inspection (DPI)
2. Fortinet intercepta conexiones HTTPS y requiere autenticación adicional
3. El MCP no es un navegador y no puede procesar HTML/fgtauth portal

SOLUCIONES:
===========
"""

import os
from dotenv import load_dotenv

load_dotenv()

print(__doc__)

print("\n" + "=" * 80)
print("SOLUCIONES PARA FORTINET FORTIGATE SSL INSPECTION")
print("=" * 80)

print("""
OPCIÓN 1: DESHABILITAR VERIFICACIÓN SSL (RÁPIDA - NO RECOMENDADO PRODUCCIÓN)
============================================================================

En .env:
    JIRA_SSL_VERIFY=false

Esto:
✅ Deshabilita validación de certificados SSL
✅ Permite conexión incluso si el certificado es inválido
❌ Vulnerable a ataques MITM
❌ No soluciona el problema de fondo

Comando para probar:
    curl -k -u usuario:token https://192.168.11.118/rest/api/2/project


OPCIÓN 2: INSTALAR CERTIFICADO CA DE FORTINET (RECOMENDADO)
===========================================================

Pasos:
1. Exportar certificado de Fortinet FortiGate:
   - Conectar a FortiGate (SSH/Web Console)
   - Exportar el certificado CA: Administration > System Settings > Certificates
   - Guardar como: fortinet-ca.pem

2. Copiar a contenedor/servidor MCP:
   - Copiar fortinet-ca.pem a /etc/ssl/certs/ o directorio accesible

3. Configurar MCP en .env:
   JIRA_CERT=/path/to/fortinet-ca.pem
   JIRA_SSL_VERIFY=true

4. Verificar con:
   curl --cacert /path/to/fortinet-ca.pem -u usuario:token https://192.168.11.118/rest/api/2/project

Ventajas:
✅ Seguro (SSL validation sigue habilitada)
✅ Soluciona problema de Fortinet
✅ Mantiene protección de certificados


OPCIÓN 3: CONFIGURAR FORTINET PARA EXCLUIR JIRA (RECOMENDADO A LARGO PLAZO)
===========================================================================

En FortiGate:
1. Log in como administrador
2. Ir a: Security Profiles > SSL/SSH Inspection > SSL Inspection
3. Crear excepción (bypass) para:
   - Servidor Jira: 192.168.11.118
   - Puerto: 443
   - O dominio: *.jira.local / jira.ingeteamenergy.com

Comando CLI FortiGate:
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

Ventajas:
✅ Solución permanente y segura
✅ No requiere cambios en MCP
✅ Mejora rendimiento (no inspecciona HTTPS para Jira)
❌ Requiere acceso de administración a FortiGate


OPCIÓN 4: USAR RUTA INTERNA ALTERNATIVA (SI DISPONIBLE)
======================================================

Si existe un nombre DNS interno para Jira:
    JIRA_URL=https://jira-internal.local
    
En lugar de IP directa:
    JIRA_URL=https://192.168.11.118

Esto puede:
✅ Evitar reglas específicas de DPI
✅ Usar ruta de red diferente que no pasa por FortiGate
❌ Requiere configuración DNS interna


OPCIÓN 5: USAR PROXY SIN INSPECCIÓN HTTPS (SI DISPONIBLE)
========================================================

Si existe un proxy corporativo que no inspecciona HTTPS:
    HTTP_PROXY=http://proxy.corp:8080
    HTTPS_PROXY=http://proxy.corp:8080

En MCP .env:
    HTTP_PROXY=http://proxy.corp:8080
    HTTPS_PROXY=http://proxy.corp:8080
    JIRA_HTTP_PROXY=http://proxy.corp:8080
    JIRA_HTTPS_PROXY=http://proxy.corp:8080

Ventajas:
✅ Centraliza control de tráfico
✅ Posible bypass de SSL inspection
❌ Requiere proxy disponible
❌ Tráfico sigue siendo visible a proxy


DIÁGNOSTICO Y DEBUGGING
=======================

Para verificar si Fortinet está interceptando:

1. Verificar si respuesta es HTML (Fortinet):
   python diagnose_fortinet.py

2. Ver headers de respuesta:
   curl -v -k -u usuario:token https://192.168.11.118/rest/api/2/project 2>&1 | grep -i "server\\|x-"

3. Buscar indicadores de Fortinet:
   - Server: FortiWeb
   - X-FortiWeb-*
   - Contenido HTML con "fgtauth"

4. Verificar certificado:
   openssl s_client -connect 192.168.11.118:443 -showcerts

5. En logs del MCP, buscar:
   - "Expecting value: line 1 column 1"
   - Respuestas con "<html"
   - Redirecciones a /fgtauth


VERIFICACIÓN FINAL
==================

Después de aplicar solución, verificar:
   - MCP puede conectar a Jira: ✓
   - get_all_projects() retorna lista: ✓
   - Logs no muestran errores HTML: ✓
   - Respuestas son JSON válido: ✓


SOPORTE TÉCNICO
===============

Si problema persiste:
1. Contactar equipo de red/seguridad
2. Compartir logs: diagnose_fortinet.py output
3. Solicitar: Certificado CA de Fortinet O exclusión de Jira
4. Documentar: IP/puerto/dominio exacto de Jira


REFERENCIAS
===========

- Fortinet FortiGate SSL Inspection: https://docs.fortinet.com/product/fortigate
- Jira API Authentication: https://developer.atlassian.com/cloud/jira/rest/authenticate-asapp/
- Python Requests SSL Verification: https://docs.python-requests.org/en/latest/user/advanced/#ssl-warnings
""")

print("\n" + "=" * 80)
print("CONFIGURACIÓN ACTUAL")
print("=" * 80)

print(f"""
JIRA_URL = {os.getenv('JIRA_URL', 'NO CONFIGURADO')}
JIRA_SSL_VERIFY = {os.getenv('JIRA_SSL_VERIFY', 'true')}
JIRA_CERT = {os.getenv('JIRA_CERT', 'NO CONFIGURADO')}
HTTP_PROXY = {os.getenv('HTTP_PROXY', 'NO CONFIGURADO')}
HTTPS_PROXY = {os.getenv('HTTPS_PROXY', 'NO CONFIGURADO')}
JIRA_HTTP_PROXY = {os.getenv('JIRA_HTTP_PROXY', 'NO CONFIGURADO')}
JIRA_HTTPS_PROXY = {os.getenv('JIRA_HTTPS_PROXY', 'NO CONFIGURADO')}
""")

print("=" * 80)
