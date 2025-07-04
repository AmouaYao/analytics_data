# 📦 Module Odoo – Analyse Couverture Stock

Ce module Odoo permet d'analyser la couverture de stock des produits par entrepôt et par société. Il calcule automatiquement :
- le stock disponible en magasin (hors entrepôt central),
- les ventes des 14 derniers jours,
- la vente moyenne journalière (VMJ),
- le nombre de jours de couverture,
- et attribue un statut intelligent au produit : `Suffisant`, `Seuil d'alerte`, `À commander`, `Plus de stock`.

---

## ✅ Fonctionnalités

- Vue personnalisée des produits avec :
  - Stock entrepôt (`WH/Stock`)
  - Stock magasin (autres emplacements internes)
  - Ventes sur 14 jours (hors entrepôt)
  - VMJ = Ventes / 14
  - Couverture = Stock magasin / VMJ
  - Date de dernière vente
  - Statut de stock intelligent

- Couverture mise à jour automatiquement (vue SQL)

---

## 📊 Statuts

| Statut        | Signification |
|---------------|---------------|
| `ok`          | Stock suffisant (>14j de couverture) |
| `order`       | À commander (entre 7 et 14 jours de couverture) |
| `low`         | Seuil d'alerte (<7 jours de couverture) |
| `out`         | Plus de stock en magasin |
| `unknown`     | Pas de ventes enregistrées |

---

## 🛠️ Installation

1. Copier le dossier `analytics_data` dans `addons/custom/` de votre instance Odoo.
2. Redémarrer le serveur Odoo.
3. Activer le mode développeur.
4. Aller dans **Apps > Mettre à jour la liste des modules**, puis dans Inventaire, Opérations choisissez tout en bas l'action Contrôle Spécial.
5. Rechercher **Analyse Couverture Stock** et installer.

---

## 🧠 Techniques utilisées

- Vue SQL déclarée via `init()` pour des performances optimales
- Requêtes `WITH` pour stock magasin, entrepôt, ventes 14j, dernière vente
- Regroupement par `product.template` (et non `product.product`)
- Calculs conditionnels pour couverture et VMJ
- Statuts logiques basés sur la couverture réelle

---

## 📅 Auteur

**YAO AMOUA JAURÈS KOUADIO**  
Développeur Odoo | Côte d'Ivoire  
[GitHub](https://github.com/ton-utilisateur)

---

## 🔐 Licence

Ce module est distribué sous licence **AGPL-3.0**.

Et est en cour de production.

---

