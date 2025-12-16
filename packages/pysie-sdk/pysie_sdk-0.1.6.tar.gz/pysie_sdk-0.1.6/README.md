# PYSIE SDK
[SDK](https://pypi.org/project/pysie-sdk/) for get the principal Mexican financial indicators from SIE


## Installation
1. `pip install pysie_sdk`

2. Generate a Token in [SIE](https://www.banxico.org.mx/SieAPIRest/service/v1/token)

3. Add the generated token in `SIE_API_KEY` envvar


## Usage

```
from pysie_sdk.client import SIE

sie_client = SIE()

sie_client.get_cetes() # Retrieve dictionary data for yield of cetes 28 days
"""
{
    'idSerie': 'SF43936',
    'titulo': 'Valores gubernamentales Resultados de la subasta semanal Tasa de rendimiento Cetes a 28 días',
    'datos': [{
        'fecha': '22/05/2025',
        'dato': '8.15'
    }]
}
"""
```


## Available Indicators

| Indicator            | Method                           | Description                                                                                                                              |
|----------------------|----------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| Cetes 28 days        | `sie_client.get_cetes()`         | Valores gubernamentales Resultados de la subasta semanal Tasa de rendimiento Cetes a 28 días                                             |
| Dollar Exchange Rate | `sie_client.get_exchange_rate()` | Tipo de cambio Pesos por dólar E.U.A. Tipo de cambio para solventar obligaciones denominadas en moneda extranjera Fecha de determinación |
| Inflation            | `sie_client.get_inflation()`     | Inflación No subyacente (nueva definición) Anual                                                                                         |
| TIIE                 | `sie_client.get_tiie()`          | TIIE de Fondeo a Un Día Hábil Bancario, Mediana ponderada por volumen                                                                    |
| UDI                  | `sie_client.get_udi()`           | Valor de UDIS (Unidad de Medida de Inflación)                                                                                            |
| Yield Target         | `sie_client.get_yield_target()`  | Tasa objetivo                                                                                                                            |
| Counterfeit bills 20 | `sie_client.get_counterfeit_bills_20()` | Piezas falsas captadas al año por denominación (billete nacional), 20 pesos |
| Counterfeit bills 50 | `sie_client.get_counterfeit_bills_50()` | Piezas falsas captadas al año por denominación (billete nacional), 50 pesos |
| Counterfeit bills 100 | `sie_client.get_counterfeit_bills_100()` | Piezas falsas captadas al año por denominación (billete nacional), 100 pesos |
| Counterfeit bills 200 | `sie_client.get_counterfeit_bills_200()` | Piezas falsas captadas al año por denominación (billete nacional), 200 pesos |
| Counterfeit bills 500 | `sie_client.get_counterfeit_bills_500()` | Piezas falsas captadas al año por denominación (billete nacional), 500 pesos |
| Counterfeit bills 1000 | `sie_client.get_counterfeit_bills_1000()` | Piezas falsas captadas al año por denominación (billete nacional), 1000 pesos |
| Tarjetas de crédito usadas | `sie_client.get_used_credit_cards()` | Tarjetas de crédito utilizadas durante el último trimestre |
| Tarjetas de débito  usadas | `sie_client.get_used_debit_cards()` | Tarjetas de débito utilizadas durante el último trimestre |
| Bill average duration 20 | `sie_client.get_bill_avg_duration_20()` | Duración promedio en meses para billete de $20mxn |
| Bill average duration 50 | `sie_client.get_bill_avg_duration_50()` | Duración promedio en meses para billete de $50mxn |
| Bill average duration 100 | `sie_client.get_bill_avg_duration_100()` | Duración promedio en meses para billete de $100mxn |
| Bill average duration 200 | `sie_client.get_bill_avg_duration_200()` | Duración promedio en meses para billete de $200mxn |
| Bill average duration 500 | `sie_client.get_bill_avg_duration_500()` | Duración promedio en meses para billete de $500mxn |
| Bill average duration 1000 | `sie_client.get_bill_avg_duration_1000()` | Duración promedio en meses para billete de $1000mxn |
| Bill in circulation 20 | `sie_client.get_bill_in_circulation_20()` | Billetes en circulación de $20mxn en millones de piezas |
| Bill in circulation 50 | `sie_client.get_bill_in_circulation_50()` | Billetes en circulación de $50mxn en millones de piezas |
| Bill in circulation 100 | `sie_client.get_bill_in_circulation_100()` | Billetes en circulación de $100mxn en millones de piezas |
| Bill in circulation 200 | `sie_client.get_bill_in_circulation_200()` | Billetes en circulación de $200mxn en millones de piezas |
| Bill in circulation 500 | `sie_client.get_bill_in_circulation_500()` | Billetes en circulación de $500mxn en millones de piezas |
| Bill in circulation 1000 | `sie_client.get_bill_in_circulation_1000()` | Billetes en circulación de $1000mxn en millones de piezas |
