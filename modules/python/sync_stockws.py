#!/usr/bin/env python3
import os
import pyodbc
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv('/home/admin/scripts/python/venv/.env')

# Configuración de conexión
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
AUTH = (API_KEY, '')

# Calcular límite de 60 minutos
tiempo_actual = datetime.now()
tiempo_inicio = tiempo_actual - timedelta(minutes=60)

# Consulta SQL solo para cambios recientes
SQL_QUERY = f"""
SELECT
    idconecta,
    quantity,
    available_date,
    out_of_stock
FROM VIS_FUR_StockWebService
WHERE LastModified IS NOT NULL
  AND LastModified >= CONVERT(DATETIME, '{tiempo_inicio.strftime('%Y-%m-%d %H:%M:%S')}', 120);
"""

def get_ws_resource(endpoint, params=None):
    print(f"[INFO] GET {endpoint} {params}")
    r = requests.get(f"{API_URL}/{endpoint}", auth=AUTH, params=params)
    r.raise_for_status()
    return r.content

def find_combination_by_idconecta_via_ws(idconecta):
    try:
        xml = get_ws_resource("combinations", {"filter[idconecta]": idconecta})
        tree = ET.fromstring(xml)
        combination_node = tree.find(".//combination")
        if combination_node is None:
            print(f"[AVISO] No se encontró combinación con idconecta: {idconecta}")
            return None, None

        comb_id = combination_node.attrib["id"]

        # Obtener id_product desde combinación
        xml_comb = get_ws_resource(f"combinations/{comb_id}")
        tree_comb = ET.fromstring(xml_comb)
        id_product = tree_comb.find(".//id_product").text

        return comb_id, id_product

    except Exception as e:
        print(f"[ERROR] Fallo al buscar combinación para {idconecta}: {e}")
        return None, None

def update_stock_available(stock_id, id_product, id_product_attribute, quantity, out_of_stock):
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
    print(f"[OK] Stock actualizado para stock_id {stock_id}")
    return response.status_code

def update_stock_available_if_needed(stock_id, id_product, id_product_attribute, quantity, out_of_stock):
    xml_current = get_ws_resource(f"stock_availables/{stock_id}")
    current_tree = ET.fromstring(xml_current)
    stock_node = current_tree.find("stock_available")

    current_qty = int(stock_node.find("quantity").text)
    current_oos = int(stock_node.find("out_of_stock").text)

    if current_qty == quantity and current_oos == out_of_stock:
        print(f"[SKIP] Stock sin cambios para {stock_id}")
        return "Sin cambios"
    return update_stock_available(stock_id, id_product, id_product_attribute, quantity, out_of_stock)

def update_combination_if_needed(comb_id, available_date):
    xml = get_ws_resource(f"combinations/{comb_id}")
    tree = ET.fromstring(xml)
    combo = tree.find("combination")

    current_date = combo.find("available_date").text or ''
    new_date = available_date.strftime("%Y-%m-%d")

    if current_date == new_date:
        print(f"[SKIP] Fecha sin cambios en combinación {comb_id}")
        return "Sin cambios"

    combo.find("available_date").text = new_date
    xml_data = ET.tostring(tree, encoding="utf-8")
    response = requests.put(f"{API_URL}/combinations/{comb_id}", auth=AUTH, data=xml_data, headers={"Content-Type": "application/xml"})
    response.raise_for_status()
    print(f"[OK] Fecha actualizada en combinación {comb_id}")
    return response.status_code

def main():
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

                print(f"\n[PROCESANDO] {idconecta}")
                comb_id, id_product = find_combination_by_idconecta_via_ws(idconecta)

                if not comb_id:
                    results.append((idconecta, "No encontrada en Webservice"))
                    continue

                try:
                    xml = get_ws_resource("stock_availables", {
                        "filter[id_product]": id_product,
                        "filter[id_product_attribute]": comb_id
                    })no rec
                    stock_tree = ET.fromstring(xml)
                    stock_node = stock_tree.find(".//stock_available")
                    if stock_node is None:
                        print(f"[AVISO] No se encontró stock para combinación {comb_id}")
                        results.append((idconecta, "Stock no encontrado"))
                        continue

                    stock_id = stock_node.attrib['id']

                    update_stock_available_if_needed(stock_id, id_product, comb_id, quantity, out_of_stock)
                    update_combination_if_needed(comb_id, available_date)

                    results.append((idconecta, "Actualizado o sin cambios"))

                except Exception as e:
                    print(f"[ERROR] {idconecta}: {e}")
                    results.append((idconecta, f"Error: {e}"))

    except Exception as e:
        print(f"[FATAL] Error general: {e}")
        results.append(("ERROR GENERAL", str(e)))

    print("\n[RESULTADOS]")
    for r in results:
        print(f"{r[0]}: {r[1]}")

if __name__ == "__main__":
    main()
