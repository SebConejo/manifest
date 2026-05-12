# Mistral Large Investigation

**Date:** 2026-05-10
**RESOLVED (2026-05-12)** — Both fixes applied (429 detection + exponential backoff
retry). mistral-large-latest completed all 21/21 tasks in ~50 minutes at ~$0.60.
Now among the 47 complete models.

---

## Q1: Quelle version exacte ?

`mistral-large-latest` résout vers **`mistral-large-2512`** (la version la plus récente).

**Preuve:** L'endpoint `/v1/models` retourne `mistral-large-latest` et `mistral-large-2512` avec le même `max_context_length: 262144`. L'ancienne version `mistral-large-2411` a `max_context_length: 131072`.

Le runner utilise `"mistral-large-latest"` comme model ID (run_batch.py ligne 128). L'API retourne `"model": "mistral-large-latest"` dans la réponse (ne résout pas vers le dated ID dans la réponse).

**Conséquence sur le rate limit :** Selon la doc Mistral, `mistral-large-2512` devrait avoir 6 req/s (tier 2+). Mais les headers réels retournent **15 req/min** (= 0.25 req/s), ce qui correspond au tier le plus bas ("Tier 0 - free" ou "Tier 1 - $0-8 spend"). Le compte Mistral a $20 de crédits mais n'a probablement pas été upgradé de tier.

---

## Q2: Que retourne l'API quand ça casse ?

### Réponse 429 réelle (confirmée par test)

```
HTTP 429

Headers:
  x-ratelimit-limit-req-minute: 15
  x-ratelimit-remaining-req-minute: 0

Body:
{
  "object": "error",
  "message": "Rate limit exceeded",
  "type": "rate_limited",
  "param": null,
  "code": "1300",
  "raw_status_code": 429
}
```

**C'est une 429 standard**, pas un 200 avec content vide. Mon test précédent montrant des "réponses vides" était probablement dû à un cooldown partiel où le rate limit était presque reset.

### Le bug du runner

Le runner ne catch PAS cette 429. La réponse Mistral met le message dans `"message"`, pas dans `"error"`. Le check du runner :

```python
if "error" in response:  # line 799
    # ... handle error
```

Retourne `False` pour `{"object": "error", "message": "Rate limit exceeded", ...}` car il n'y a pas de clé `"error"` au top level. Ensuite :

```python
choices = response.get("choices", [])  # line 806
if not choices:
    continue  # silently skip — no raw file written, no error logged
```

Le case est **silencieusement perdu**. Pas d'erreur affichée, pas de raw file, comme si le case n'existait pas.

### Rate limit headers sur un call réussi

```
x-ratelimit-limit-req-minute: 15
x-ratelimit-remaining-req-minute: 14
x-ratelimit-limit-tokens-minute: 400000
x-ratelimit-remaining-tokens-minute: 399991
```

**15 req/min = 1 requête toutes les 4 secondes.**

---

## Q3: Quel délai ?

Avec 15 req/min, le délai minimum théorique est `60/15 = 4.0s`. Avec une marge de 10% : **4.4s**.

Mais un délai aveugle n'est pas le bon fix. Le vrai fix est double :

### Fix 1: Détecter la 429 dans `call_mistral`

```python
def call_mistral(model, messages, max_tokens):
    import requests as req
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {os.environ['MISTRAL_API_KEY']}", "Content-Type": "application/json"}
    body = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0}
    resp = req.post(url, json=body, headers=headers, timeout=180)
    if resp.status_code == 429:
        return {"error": "Rate limit exceeded (429)"}
    data = resp.json()
    if data.get("object") == "error":
        return {"error": data.get("message", str(data))}
    return data
```

Ça fait remonter l'erreur au runner qui logge `ERROR mistral-large-latest case X: Rate limit exceeded (429)` et fait `continue`.

### Fix 2: Retry avec backoff dans le runner

Quand le runner voit une erreur de rate limit, au lieu de `continue` (perdre le case), il wait et retry :

```python
if "error" in response:
    err = response["error"]
    if isinstance(err, str) and "rate limit" in err.lower():
        # Wait for rate limit reset and retry
        time.sleep(5)
        response = call_model(model_name, messages, task_def["max_output_tokens"])
        if "error" in response:
            print(f"  ERROR {model_name} case {case_idx} (retry failed): {err}")
            continue
    else:
        print(f"  ERROR {model_name} case {case_idx}: {err}")
        continue
```

### Pourquoi pas un simple délai ?

Un délai de 4.4s entre tous les calls Mistral ralentirait aussi `mistral-small-latest` et `ministral-3b-latest` qui n'ont pas ce rate limit (ou ont un limit plus haut). Le retry ciblé ne pénalise que quand on est effectivement rate-limité.

---

## Impact estimé

- 16 tasks incomplètes × ~35 cases manquantes = **~560 cases**
- À 4.4s/case = **~41 minutes** de runtime
- Coût : ~$1-2 (les appels sont bon marché, c'est le temps qui coûte)
- Résultat : mistral-large-latest passe de 5/21 à **21/21**

---

## Root cause résumée

| Facteur | Détail |
|---------|--------|
| Rate limit réel | 15 req/min (tier bas malgré $20 crédits) |
| Format d'erreur | `{"object": "error", "message": "..."}` — pas de clé `"error"` |
| Bug runner | `if "error" in response` ne match pas la structure Mistral |
| Conséquence | Cases silencieusement perdues (pas de log, pas de raw file) |
| Fix | Détecter `resp.status_code == 429` + `data.get("object") == "error"`, retry avec backoff |
