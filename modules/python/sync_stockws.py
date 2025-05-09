import os
import pyodbc
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('/home/admin/scripts/python/venv/.env')

# Configuración
SQL_CFG = {
    'driver': '{ODBC Driver 18 for SQL Server}',
    'server': os.getenv('SQL_SERVER_HOST'),
    'database': os.getenv('SQL_SERVER_DB'),
    'port': os.getenv('SQL_SERVER_PORT'),
    'username': os.getenv('SQL_SERVER_USER'),
    'password': os.getenv('SQL_SERVER_PASS'),
}

DOMAIN = os.getenv('DOMAIN_SANDBOX')
API_KEY = os.getenv('API_KEY_SANDBOX')
API_URL = f"https://{DOMAIN}/api"

# Encabezados para la autenticación
AUTH = (API_KEY, '')

# Consulta SQL
SQL_QUERY = """
SELECT 
    idconecta,
    quantity,
    available_date,
    out_of_stock
FROM VIS_MB_EstocsWEB
WHERE CodigoArticulo NOT IN ('SILLA165', 'MESA006', 'MESA039', 'LAMP031');
"""

# Función auxiliar para hacer GETs
def get_ws_resource(endpoint, params=None):
    try:
        print(f"[INFO] GET {endpoint} con params {params}")
        response = requests.get(f"{API_URL}/{endpoint}", auth=AUTH, params=params)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"[ERROR] Error en GET {endpoint}: {e}")
        raise

# Función auxiliar para actualizar stock_available
def update_stock_available(stock_id, id_product, id_product_attribute, quantity, out_of_stock):
    try:
        print(f"[INFO] Actualizando stock_available ID {stock_id} - Quantity: {quantity}, OutOfStock: {out_of_stock}")
        xml = get_ws_resource("stock_availables", {"schema": "blank"})
        tree = ET.fromstring(xml)
        stock_node = tree.find("stock_available")
        stock_node.find("id").text = str(stock_id)
        stock_node.find("id_product").text = str(id_product)
        stock_node.find("id_product_attribute").text = str(id_product_attribute)
        stock_node.find("quantity").text = str(quantity)
        stock_node.find("depends_on_stock").text = "0"
        stock_node.find("out_of_stock").text = str(out_of_stock)

        xml_data = ET.tostring(tree, encoding="utf-8")
        response = requests.put(f"{API_URL}/stock_availables/{stock_id}", auth=AUTH, data=xml_data, headers={"Content-Type": "application/xml"})
        response.raise_for_status()
        print(f"[OK] Stock actualizado correctamente.")
        return response.status_code
    except Exception as e:
        print(f"[ERROR] Fallo al actualizar stock_available {stock_id}: {e}")
        raise

# Función auxiliar para actualizar combinación
def update_combination(comb_id, available_date):
    try:
        print(f"[INFO] Actualizando combinación ID {comb_id} con fecha {available_date}")
        xml = get_ws_resource(f"combinations/{comb_id}")
        tree = ET.fromstring(xml)
        combo = tree.find("combination")
        combo.find("available_date").text = available_date.strftime("%Y-%m-%d")

        xml_data = ET.tostring(tree, encoding="utf-8")
        response = requests.put(f"{API_URL}/combinations/{comb_id}", auth=AUTH, data=xml_data, headers={"Content-Type": "application/xml"})
        response.raise_for_status()
        print(f"[OK] Fecha de disponibilidad actualizada.")
        return response.status_code
    except Exception as e:
        print(f"[ERROR] Fallo al actualizar combinación {comb_id}: {e}")
        raise

# Ejecutar sincronización
results = []
try:
    print("[INFO] Conectando a SQL Server...")
    conn_str = (
        f"DRIVER={SQL_CFG['driver']};SERVER={SQL_CFG['server']},{SQL_CFG['port']};"
        f"DATABASE={SQL_CFG['database']};UID={SQL_CFG['username']};PWD={SQL_CFG['password']};"
        "Encrypt=yes;TrustServerCertificate=yes;"
    )
    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        cursor.execute(SQL_QUERY)
        for row in cursor.fetchall():
            idconecta = row.idconecta
            quantity = row.quantity
            available_date = row.available_date
            out_of_stock = row.out_of_stock
            print(f"\n[PROCESANDO] {idconecta} - Qty: {quantity} - Fecha: {available_date} - OutOfStock: {out_of_stock}")

            try:
                # Paso 1: Obtener id_product_attribute vía idconecta
                xml = get_ws_resource("product_attribute", {"filter[idconecta]": f"[{idconecta}]"})
                tree = ET.fromstring(xml)
                attrs = tree.findall(".//product_attribute")
                if not attrs:
                    print(f"[AVISO] No encontrado id_product_attribute para {idconecta}")
                    results.append((idconecta, "id_product_attribute not found"))
                    continue

                comb_id = attrs[0].attrib['id']

                # Paso 2: Obtener id_product desde combinación
                xml = get_ws_resource(f"product_attribute/{comb_id}")
                tree = ET.fromstring(xml)
                id_product = tree.find(".//id_product").text

                # Paso 3: Obtener stock_available
                xml = get_ws_resource("stock_availables", {
                    "filter[id_product]": f"[{id_product}]",
                    "filter[id_product_attribute]": f"[{comb_id}]"
                })
                stock_tree = ET.fromstring(xml)
                stock_id = stock_tree.find(".//stock_available").attrib['id']

                # Paso 4: Actualizar stock_available y combinación
                update_stock_available(stock_id, id_product, comb_id, quantity, out_of_stock)
                update_combination(comb_id, available_date)

                results.append((idconecta, "OK"))

            except Exception as e:
                print(f"[ERROR] Error procesando {idconecta}: {e}")
                results.append((idconecta, str(e)))

except Exception as e:
    print(f"[FATAL] Error general en la sincronización: {e}")
    results.append(("ERROR", str(e)))

import pandas as pd
import ace_tools as tools; tools.display_dataframe_to_user(name="Resultado sincronización stock", dataframe=pd.DataFrame(results, columns=["IDConecta", "Resultado"]))
