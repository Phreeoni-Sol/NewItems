# Règles de design et d’équilibrage

Ces règles sont proposées pour les nouveaux objets. Elles ne décrivent aucune limite prouvée du moteur.

## Vocabulaire

- « Porteur » : unité équipée ; pour un consommable ou un projectile consommable, lire « utilisateur » si une dépense ou une réserve personnelle est mentionnée.
- « Alliés » : unités du même camp ; « autre allié » exclut le porteur. Une cible explicitement choisie doit avoir une sélection validée par le prototype ; si plusieurs candidats sont automatiques, prendre le plus proche, puis le plus blessé en proportion, puis l’ordre d’unité stable validé. Ne pas supposer un identifiant moteur disponible.
- « Réserve », « marque », « dette », « crédit » : données temporaires du mod. Ne pas les mapper arbitrairement à un statut vanilla et ne pas changer le comportement global de Poison, Silence, Protection, etc.
- « Contrôle » : compétence ayant pour objectif un statut négatif ; liste exacte à classifier à partir des compétences réelles. « Soutien musical », « soutien », « projectile », « sort payé », « dégâts magiques/physiques » demandent aussi une classification validée, pas une liste inventée.
- Pour les consommables nouveaux, « retire » un statut nécessite ce statut initial pour le bonus conditionné au traitement. Un objet inefficace ne doit pas produire gratuitement sa réserve bonus ; comportement et consommation sur cible invalide à prototyper.
- Percentages de dégâts, soins et coût : multiplicateurs relatifs sur la valeur effectivement calculée, arrondis vers le bas. « +N % de précision » est une proposition relative, pas N points ; esquive sans symbole % est une proposition en points. Les points d’application dans la formule réelle sont `UNKNOWN`. Toujours conserver les règles natives de plafonnement et de réussite ; aucun effet ne garantit un coup.
- « Plus haut », « végétation », « eau », « face/côté/dos », « direction opposée » nécessitent une définition fondée sur les données terrain et orientation réelles. Deux événements successifs sont comptés sur les tours du porteur, sauf indication explicite.

## Réserves, compteurs et cumul

Au plus un déclenchement d’un même objet par action. Aucun soin secondaire, remboursement, suppression de marque ou dégât secondaire ne relance un effet d’équipement. Pas d’action, tour, tir ou déplacement gratuit. Sur un coup multiple, une activation par action, pas par impact. Les réserves se consomment à la première tentative éligible, y compris si l’action échoue ; les récompenses nécessitant explicitement un succès exigent ce succès.

Même nature de bonus : retenir le maximum, ne pas additionner. Réductions de dégâts concurrentes : maximum. Un crédit MP ne rembourse jamais plus que le coût payé et ne rend jamais le coût d’un sort normalement payant inférieur à 1. Aucun débit ne peut créer des MP négatifs. Un sacrifice de PV laisse au moins 1 PV au porteur. Les bonus de soin ne peuvent dépasser les PV manquants, sauf réserve d’excédent explicitement définie ; celle-ci n’augmente pas les PV maximaux.

La fiche prime pour sa durée et ses limites. Toute réserve non datée expire à la fin du prochain tour du porteur ; aucun report d’une bataille à l’autre. Les réserves disparaissent à la mise hors combat. Une promesse explicitement liée à un allié KO reste dans le registre du porteur vivant et expire à la fin de la bataille ; elle ne fournit pas de réanimation. Les compteurs redémarrent en début de bataille. La persistance pendant une sauvegarde de bataille reste à vérifier.

Les bonus occasionnels de Saut sont réservés à un déplacement, limités à +1 au total dans ce design et consommés même s’ils ne changent pas le trajet ; cette règle n’est pas une limite moteur. Aucun bonus permanent de Vitesse ou modification de CT n’est ajouté.

## Budget et prix

Les valeurs sont dans `items.json` et les paramètres numériques dans `mechanics.json`. Les textes numériques sont rendus depuis les gabarits et paramètres ; Claude doit les traduire en paramètres nommés selon l’opération exacte avant le codage. Ne pas traiter leur contexte textuel comme une unité moteur fiable.

Les caractéristiques de puissance/PV/MP de l’ancienne proposition sont multipliées par 0,95 / 0,92 / 0,90 / 0,85 / 0,85 selon commun / peu commun / rare / légendaire / unique, arrondies vers le bas. Les contreparties qui indiquent une réduction spécifique de puissance priment. Portée et esquives de profil sont conservées. Retrait des anciens bonus permanents Mouvement, Saut, PA, MA. Cette première répartition de budget n’est pas un équilibrage validé.

Les prix hors consommables sont la référence native × 1,10 / 1,20 / 1,35 selon commun / peu commun / rare, arrondis à 25 gils, minimum 50 ; en l’absence de prix natif utilisable, conserver le précédent comme ancrage. Les 16 consommables ont des prix explicites dans le générateur. Revente proposée à moitié pour les objets de boutique. Légendaires et uniques hors boutique, revente désactivée, prix 0 signifie absence de commerce et jamais gratuité en boutique.

## Préservation vanilla

Créer des entrées nouvelles seulement après vérification des collisions et des possibilités d’ajout. Aucune entrée native, job natif, compétence native ou règle globale n’est rééquilibré ici. Les réactions vanilla restent actives ; les annulations indiquées dans certaines fiches concernent seulement les réserves ou réactions des nouveaux équipements. Tout effet n’existe que si le nouvel objet est équipé ou utilisé.
