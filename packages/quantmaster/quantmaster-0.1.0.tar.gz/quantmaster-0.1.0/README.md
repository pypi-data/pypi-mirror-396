# Quantmaster

Biblioteca de features quantitativas para adicionar colunas em `pandas.DataFrame` com dados OHLCV.

## Instalação (desenvolvimento)

```bash
pip install -e ".[dev]"
```

## Uso rápido

```python
from quantmaster.features.momentum import rsi
from quantmaster.features.volatility import har_rv

df["rsi_10"] = rsi(df, window=10)
df = df.join(har_rv(df))
```

## Estrutura

- Features ficam em `src/quantmaster/features/` separadas por categoria (Momentum, Trend, Volatility, etc.).
- Cada feature é uma função que recebe `DataFrame` (ou `Series`) e retorna `Series` (ou `DataFrame`) alinhado ao índice.
