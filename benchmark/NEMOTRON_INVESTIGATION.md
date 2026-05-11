# Nemotron Investigation

**Date:** 2026-05-11

---

## Diagnostic : Nemotron est un reasoning model non listé

**Root cause identique à Kimi K2.6 / o3 / Gemini 2.5 Pro.**

Nemotron-3-Super-120B utilise des reasoning tokens invisibles. Avec `max_tokens=20`
(le budget des 3 tasks de classification), les 20 tokens sont consommés à 100%
par le raisonnement. Zéro token reste pour la réponse visible.

---

## Q1 : Format des empties

Appel live avec `max_tokens=20` :

```json
{
  "content": null,
  "finish_reason": "length",
  "usage": {
    "completion_tokens": 20,
    "completion_tokens_details": {
      "reasoning_tokens": 20
    }
  }
}
```

- **HTTP 200** (pas une erreur)
- **content: null** (pas une string vide — null)
- **finish_reason: "length"** (tronqué au budget)
- **reasoning_tokens: 20** = 100% du budget consommé par la réflexion
- **0 tokens visibles**

Ce n'est pas un échec API, pas un rate limit, pas un content filter.
C'est le modèle qui pense plus qu'il ne parle.

---

## Q2 : Comparaison avec les réponses valides

| max_tokens | reasoning | visible | content | finish_reason |
|-----------|-----------|---------|---------|---------------|
| 20 | 20 | 0 | null | length |
| 100 | 28 | 2 | "positive" | stop |
| 500 | 32 | 32 | "positive" | stop |

Avec un budget suffisant (≥100), Nemotron répond correctement.
Le problème est strictement le budget de 20 tokens sur les 3 tasks
de classification (sentiment_sst2, moderation_toxigen, intent_clinc150).

Les 18 tasks qui marchent ont toutes `max_output_tokens ≥ 200`.

---

## Q3 : Nemotron dans REASONING_MODELS ?

**Non.** `nvidia/nemotron-3-super-120b-a12b` n'est pas dans `REASONING_MODELS`.
`effective_max_tokens("nvidia/nemotron-3-super-120b-a12b", 20)` retourne 20
(pas de boost).

Avec le fix (ajout à REASONING_MODELS), il recevrait `max(20, 8192) = 8192`,
ce qui est largement suffisant.

---

## Q4 : Content filter ?

**Non.** Test live avec un prompt ToxiGen toxique ("Those people are all
criminals and should be deported") : Nemotron répond "toxic" correctement
avec `max_tokens=100`. Pas de refus, pas de filtre.

---

## Q5 : Routing OpenRouter ?

Non pertinent — le problème est côté token budget, pas côté provider.
Les headers OpenRouter ne montrent pas de sous-provider différent entre
les tasks qui marchent et celles qui échouent. La seule différence est
`max_tokens=20` vs `max_tokens≥200`.

---

## Fix

1. Ajouter `"nvidia/nemotron-3-super-120b-a12b"` à `REASONING_MODELS`
2. Supprimer les raw files vides pour les 3 tasks
3. Re-run : ~84 cases (28 + 32 + 24) via OpenRouter, coût < $0.01

---

## Pattern récurrent

C'est le **4ème modèle** qu'on découvre être un reasoning model non listé :

| Modèle | Découverte | Symptôme |
|--------|-----------|----------|
| Gemini 2.5 Pro | Session 1 | Empties, output_tokens = max |
| Kimi K2.6 | Cette session | output_tokens = 2000 exactement |
| deepseek/deepseek-v4-pro | Cette session | output_tokens = 1000 exactement |
| nvidia/nemotron | Cette session | output_tokens = 20, reasoning_tokens = 20 |

Le fix est toujours le même : ajouter à REASONING_MODELS → effective_max_tokens
boost à 8192.
