"""
Modelos y Simulación 2026 - TP Unidad 3
Generación de variables aleatorias.

Todos los generadores parten únicamente de random.random() (U ~ Uniforme(0,1)).
numpy / scipy se usan SOLO para graficar y para calcular las curvas teóricas.
"""
import math
import random
import bisect
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

random.seed(42)


def U():
    """Uniforme(0,1) abierta (evita log(0))."""
    u = random.random()
    while u == 0.0:
        u = random.random()
    return u


# ----------------------------------------------------------------------
# Punto 1: transformada inversa (ejemplo: exponencial)
# ----------------------------------------------------------------------
def exponencial(lam):
    """F(x)=1-exp(-lam x)  ->  x = -ln(1-u)/lam  ~  -ln(u)/lam"""
    return -math.log(U()) / lam


# ----------------------------------------------------------------------
# Punto 2: aceptación y rechazo (ejemplo: Beta(2,5) con propuesta uniforme)
# ----------------------------------------------------------------------
def beta_aceptacion_rechazo(a=2, b=5):
    """Beta(a,b) en [0,1]. Propuesta g(x)=1 (uniforme), c = máximo de f."""
    moda = (a - 1) / (a + b - 2)
    B = math.exp(math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b))
    f = lambda x: x ** (a - 1) * (1 - x) ** (b - 1) / B
    c = f(moda)                       # f(x) <= c * g(x) = c
    intentos = 0
    while True:
        intentos += 1
        y = random.random()           # 1) y ~ g
        u = random.random()           # 2) u ~ U(0,1)
        if u <= f(y) / c:             # 3) acepto con prob f(y)/(c g(y))
            return y, intentos


# ----------------------------------------------------------------------
# Punto 3: discreta empírica con lista de probabilidades de largo arbitrario
# ----------------------------------------------------------------------
def discreta_empirica(probs, valores=None):
    """
    Devuelve UN valor aleatorio según la distribución discreta (probs, valores).
    probs   : lista de probabilidades (deben sumar 1)
    valores : lista de valores a generar (por defecto 0, 1, 2, ...)
    """
    if valores is None:
        valores = list(range(len(probs)))
    if len(probs) != len(valores):
        raise ValueError("probs y valores deben tener el mismo largo")
    if abs(sum(probs) - 1.0) > 1e-9:
        raise ValueError("las probabilidades deben sumar 1")
    acum, s = [], 0.0
    for p in probs:
        s += p
        acum.append(s)
    i = bisect.bisect_left(acum, random.random())   # primer i con acum[i] >= u
    return valores[min(i, len(valores) - 1)]


def simular_demanda(dias, probs, valores):
    return [discreta_empirica(probs, valores) for _ in range(dias)]


# ----------------------------------------------------------------------
# Punto 4: generadores de cada distribución
# ----------------------------------------------------------------------
def uniforme_continua(a, b):
    return a + (b - a) * random.random()


def uniforme_discreta(a, b):
    """Entero uniforme en {a, a+1, ..., b}."""
    return a + int((b - a + 1) * random.random())


def normal(mu, sigma):
    """Box-Muller (devuelve un valor; descarta el segundo)."""
    r = math.sqrt(-2.0 * math.log(U()))
    z = r * math.cos(2.0 * math.pi * random.random())
    return mu + sigma * z


def poisson(lam):
    """Método de Knuth: multiplicar uniformes hasta que el producto < e^-lam."""
    L = math.exp(-lam)
    k, p = 0, 1.0
    while True:
        p *= random.random()
        if p <= L:
            return k
        k += 1


def triangular(a, c, b):
    """Inversa por tramos. a=mínimo, c=moda, b=máximo."""
    u = random.random()
    Fc = (c - a) / (b - a)
    if u < Fc:
        return a + math.sqrt(u * (b - a) * (c - a))
    return b - math.sqrt((1 - u) * (b - a) * (b - c))


def gamma(k, theta):
    """Gamma(k, theta) por Marsaglia-Tsang (aceptación y rechazo sobre normal)."""
    if k < 1:                                   # truco de aumento de forma
        return gamma(k + 1, theta) * U() ** (1.0 / k)
    d = k - 1.0 / 3.0
    c = 1.0 / math.sqrt(9.0 * d)
    while True:
        x = normal(0, 1)
        v = (1 + c * x) ** 3
        if v <= 0:
            continue
        u = U()
        if math.log(u) < 0.5 * x * x + d - d * v + d * math.log(v):
            return theta * d * v


def beta(a, b):
    """Beta(a,b) = X/(X+Y) con X~Gamma(a,1), Y~Gamma(b,1)."""
    x = gamma(a, 1.0)
    y = gamma(b, 1.0)
    return x / (x + y)


def weibull(k, lam):
    """F(x)=1-exp(-(x/lam)^k) -> x = lam (-ln u)^(1/k)."""
    return lam * (-math.log(U())) ** (1.0 / k)


# ----------------------------------------------------------------------
# Gráficos: fdp teórica + histograma generado / FA teórica + FA empírica
# ----------------------------------------------------------------------
def figura(nombre, titulo, muestra, dist, discreta=False, carpeta="graficos"):
    os.makedirs(carpeta, exist_ok=True)
    muestra = np.asarray(muestra)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    if discreta:
        xs = np.arange(int(muestra.min()), int(muestra.max()) + 1)
        ax[0].bar(xs - 0.2, dist.pmf(xs), width=0.4, label="fdp teórica (pmf)")
        frec = np.array([(muestra == x).mean() for x in xs])
        ax[0].bar(xs + 0.2, frec, width=0.4, alpha=0.7, label="muestra generada")
        ax[1].step(xs, dist.cdf(xs), where="post", label="FA teórica")
        ax[1].step(xs, np.cumsum(frec), where="post", linestyle="--",
                   label="FA empírica")
    else:
        lo, hi = np.percentile(muestra, [0.05, 99.95])
        xs = np.linspace(lo, hi, 400)
        ax[0].hist(muestra, bins=50, density=True, alpha=0.5,
                   label="muestra generada")
        ax[0].plot(xs, dist.pdf(xs), "r", lw=2, label="fdp teórica")
        ordenada = np.sort(muestra)
        ax[1].plot(xs, dist.cdf(xs), "r", lw=2, label="FA teórica")
        ax[1].plot(ordenada, np.arange(1, len(ordenada) + 1) / len(ordenada),
                   "b--", lw=1, label="FA empírica")
    ax[0].set_title(f"{titulo}: función de probabilidad")
    ax[1].set_title(f"{titulo}: función acumulada")
    for a in ax:
        a.legend()
        a.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(carpeta, nombre + ".png"), dpi=110)
    plt.close(fig)


def main(N=10000):
    # ---- Punto 3: aplicación a una demanda ----
    probs, valores = [0.1, 0.3, 0.4, 0.2], [5, 7, 8, 9]
    dem = simular_demanda(N, probs, valores)
    print("== Punto 3: demanda diaria ==")
    print("Esperanza teórica:", sum(p * v for p, v in zip(probs, valores)))
    print("Media simulada   :", round(sum(dem) / N, 3))
    for v, p in zip(valores, probs):
        print(f"  P(D={v}) teórica {p:.2f}  simulada {dem.count(v) / N:.3f}")
    print("  Ejemplo con otra lista [0.5,0.3,0.2]:",
          [discreta_empirica([0.5, 0.3, 0.2]) for _ in range(10)])
    print("  Demanda de 15 días:", simular_demanda(15, probs, valores))

    # ---- Punto 2: eficiencia de aceptación y rechazo ----
    res = [beta_aceptacion_rechazo(2, 5) for _ in range(N)]
    xs = [r[0] for r in res]
    prom_int = sum(r[1] for r in res) / N
    print("\n== Punto 2: Beta(2,5) por aceptación y rechazo ==")
    print("Intentos promedio:", round(prom_int, 3), "(teórico c =", 
          round(30 * 0.2 * 0.8 ** 4, 4), ")")
    print("Media:", round(np.mean(xs), 4), "(teórica", round(2 / 7, 4), ")")
    figura("beta_aceptacion_rechazo", "Beta(2,5) por aceptación y rechazo",
           xs, stats.beta(2, 5))

    # ---- Punto 4: todas las distribuciones ----
    casos = [
        ("normal", "Normal(50,10)", lambda: normal(50, 10),
         stats.norm(50, 10), False),
        ("uniforme_continua", "Uniforme continua(2,8)",
         lambda: uniforme_continua(2, 8), stats.uniform(2, 6), False),
        ("uniforme_discreta", "Uniforme discreta{1..6}",
         lambda: uniforme_discreta(1, 6), stats.randint(1, 7), True),
        ("poisson", "Poisson(4)", lambda: poisson(4), stats.poisson(4), True),
        ("exponencial", "Exponencial(0.5)", lambda: exponencial(0.5),
         stats.expon(scale=2), False),
        ("triangular", "Triangular(1,3,8)", lambda: triangular(1, 3, 8),
         stats.triang(c=(3 - 1) / (8 - 1), loc=1, scale=7), False),
        ("beta", "Beta(2,5)", lambda: beta(2, 5), stats.beta(2, 5), False),
        ("gamma", "Gamma(k=3, theta=2)", lambda: gamma(3, 2),
         stats.gamma(3, scale=2), False),
        ("weibull", "Weibull(k=2, lambda=3)", lambda: weibull(2, 3),
         stats.weibull_min(2, scale=3), False),
    ]
    print("\n== Punto 4: verificación (N =", N, ") ==")
    print(f"{'Distribución':28s}{'media sim':>11s}{'media teo':>11s}"
          f"{'var sim':>10s}{'var teo':>10s}{'p KS/chi2':>11s}")
    for arch, tit, gen, dist, disc in casos:
        m = np.array([gen() for _ in range(N)])
        if disc:
            xs = np.arange(int(m.min()), int(m.max()) + 1)
            obs = np.array([(m == x).sum() for x in xs], dtype=float)
            esp = dist.pmf(xs) * N
            esp[-1] += N - esp.sum()          # cola al último casillero
            ok = esp >= 5
            o2 = np.append(obs[ok], obs[~ok].sum())
            e2 = np.append(esp[ok], esp[~ok].sum())
            if e2[-1] < 1e-9:
                o2, e2 = o2[:-1], e2[:-1]
            p = stats.chisquare(o2, e2 * o2.sum() / e2.sum()).pvalue
        else:
            p = stats.kstest(m, dist.cdf).pvalue
        print(f"{tit:28s}{m.mean():11.3f}{dist.mean():11.3f}"
              f"{m.var():10.3f}{dist.var():10.3f}{p:11.3f}")
        figura(arch, tit, m, dist, disc)

    # ---- Punto 5: ejemplo de ajuste de datos empíricos ----
    datos = [weibull(2, 3) for _ in range(500)]      # "datos reales" de ejemplo
    print("\n== Punto 5: ajuste de datos a distribuciones teóricas ==")
    for nom, d in [("expon", stats.expon), ("gamma", stats.gamma),
                   ("weibull_min", stats.weibull_min), ("norm", stats.norm)]:
        par = d.fit(datos, floc=0) if nom != "norm" else d.fit(datos)
        ks = stats.kstest(datos, d(*par).cdf)
        ll = np.sum(d(*par).logpdf(datos))
        aic = 2 * len(par) - 2 * ll
        print(f"  {nom:12s} KS={ks.statistic:.4f} p={ks.pvalue:.3f} AIC={aic:.1f}")


if __name__ == "__main__":
    main()
