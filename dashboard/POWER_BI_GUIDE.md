# Guía del dashboard en Power BI

## Fuentes

Importar desde `data/processed/`:

- `power_bi_revenue_monthly.csv`
- `power_bi_revenue_forecast.csv`

Usar `dashboard/theme.json` desde **Vista > Temas > Examinar temas**.

## Página 1 - Resumen ejecutivo

- Tarjetas: Total Emitido, Total Recaudado, Deuda Pendiente y Cobrabilidad.
- Línea: evolución mensual de emisión y recaudación.
- Barras: recaudación por tipo de tasa.
- Mapa de calor o matriz: cobrabilidad por zona y categoría.
- Segmentadores: período, tasa, zona y categoría.

## Página 2 - Cobrabilidad y deuda

- Barras apiladas: emitido, recaudado y deuda por zona.
- Matriz: indicadores por categoría.
- Línea: evolución del porcentaje de cobrabilidad.
- Árbol de descomposición: deuda por tasa, zona y categoría.

## Página 3 - Forecasting

- Línea con `series` como leyenda para comparar valores reales y proyectados.
- Tarjetas con MAE, RMSE y MAPE desde `data/metrics/forecast_metrics.json`.
- Texto aclaratorio: datos completamente sintéticos con fines demostrativos.

## Formato recomendado

- Fondo: `#F5F7FB`
- Texto principal: `#172033`
- Color primario: `#6C63FF`
- Éxito/recaudación: `#00B8A9`
- Advertencia/deuda: `#E76F51`
- Mantener máximo seis visuales por página.

