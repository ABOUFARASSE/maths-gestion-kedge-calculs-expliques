import json, math

def _fmt(x, digits=2):
    return round(float(x), digits)

def solve(case_id, p):
    if case_id == "budget":
        total=p["total"]; digital=total*p["digital"]/100; training=total*p["training"]/100; equipment=total*p["equipment"]/100
        remaining=total-digital-training-equipment; minimum=total*p["reserve_min"]/100
        ok=remaining>=minimum
        return {"metrics":[["Budget disponible",_fmt(total),"€"],["Total engagé",_fmt(total-remaining),"€"],["Réserve",_fmt(remaining),"€"],["Marge sur réserve",_fmt(remaining-minimum),"€"]],
                "steps":[
                    ["1. Communication",f"{total:,.0f} × {p['digital']:.0f} % = {digital:,.0f} €","On transforme le pourcentage en proportion puis on le multiplie par le budget."],
                    ["2. Formation et équipement",f"{total:,.0f} × {p['training']:.0f} % = {training:,.0f} € ; {total:,.0f} × {p['equipment']:.0f} % = {equipment:,.0f} €","Chaque poste est calculé séparément sur le même budget total."],
                    ["3. Réserve disponible",f"{total:,.0f} − {digital:,.0f} − {training:,.0f} − {equipment:,.0f} = {remaining:,.0f} €","La réserve est ce qui reste après les dépenses prévues."],
                    ["4. Contrôle de la contrainte",f"Réserve minimale = {total:,.0f} × {p['reserve_min']:.0f} % = {minimum:,.0f} €","On compare la réserve disponible au minimum demandé."]],
                "chart":{"type":"pie","labels":["Communication","Formation","Équipement","Réserve"],"values":[digital,training,equipment,remaining]},
                "decision":("Répartition soutenable" if ok else "Répartition à réviser"),
                "explanation":(f"La réserve atteint {_fmt(remaining/total*100,1)} % du budget, contre un minimum exigé de {p['reserve_min']} %." if total else "Budget nul."),
                "alert":not ok}
    if case_id == "growth":
        years=int(p["years"]); initial=p["initial"]; rates=[p["pessimistic"],p["central"],p["optimistic"]]
        names=["Prudent","Central","Dynamique"]; xs=list(range(years+1)); series=[]
        for name,r in zip(names,rates): series.append({"name":name,"x":xs,"y":[initial*(1+r/100)**t for t in xs]})
        final=series[1]["y"][-1]; gap=final-p["capacity"]
        return {"metrics":[["Valeur initiale",initial,"€"],["Prévision centrale",_fmt(final),"€"],["Croissance cumulée",_fmt((final/initial-1)*100,1),"%"],["Écart à la capacité",_fmt(gap),"€"]],
                "steps":[
                    ["1. Coefficient annuel",f"1 + {p['central']:.0f}/100 = {1+p['central']/100:.2f}","Une hausse en pourcentage devient un coefficient multiplicateur."],
                    ["2. Valeur après la période",f"{initial:,.0f} × {(1+p['central']/100):.2f}^{years} = {final:,.2f} €","La puissance traduit la répétition de la croissance pendant plusieurs années."],
                    ["3. Croissance totale",f"({final:,.2f} ÷ {initial:,.0f} − 1) × 100 = {(final/initial-1)*100:.1f} %","Le taux cumulé n'est pas simplement le taux annuel multiplié par le nombre d'années."],
                    ["4. Capacité",f"{final:,.2f} − {p['capacity']:,.0f} = {gap:,.2f} €","Un écart positif indique que la capacité actuelle sera insuffisante."]],
                "chart":{"type":"lines","series":series},"decision":("Capacité à renforcer" if gap>0 else "Capacité suffisante"),
                "explanation":f"Au scénario central, l'activité atteint {_fmt(final):,.0f} € après {years} ans. La croissance composée représente {_fmt((final/initial-1)*100,1)} % sur la période.","alert":gap>0}
    if case_id == "supplier":
        q=p["quantity"]; ca=p["fixed_a"]+p["unit_a"]*q; cb=p["fixed_b"]+p["unit_b"]*q
        den=p["unit_b"]-p["unit_a"]; threshold=(p["fixed_a"]-p["fixed_b"])/den if den else None
        winner="A" if ca<cb else "B" if cb<ca else "A ou B"
        xmax=max(q*1.6,(threshold or q)*1.35,10); xs=[xmax*i/40 for i in range(41)]
        return {"metrics":[["Coût fournisseur A",_fmt(ca),"€"],["Coût fournisseur B",_fmt(cb),"€"],["Économie",_fmt(abs(ca-cb)),"€"],["Seuil d'indifférence",_fmt(threshold) if threshold is not None else "—","unités"]],
                "steps":[
                    ["1. Coût de l'offre A",f"{p['fixed_a']:,.0f} + {p['unit_a']:.0f} × {q:.0f} = {ca:,.0f} €","On additionne le forfait et le coût des unités."],
                    ["2. Coût de l'offre B",f"{p['fixed_b']:,.0f} + {p['unit_b']:.0f} × {q:.0f} = {cb:,.0f} €","La même méthode est appliquée à la seconde offre."],
                    ["3. Seuil d'indifférence",(f"({p['fixed_a']:,.0f} − {p['fixed_b']:,.0f}) ÷ ({p['unit_b']:.0f} − {p['unit_a']:.0f}) = {threshold:.0f} unités" if threshold is not None else "Les coûts unitaires sont identiques."),"Au seuil, les deux coûts totaux sont égaux."],
                    ["4. Décision",f"Écart = |{ca:,.0f} − {cb:,.0f}| = {abs(ca-cb):,.0f} €","L'offre la moins chère au volume prévu est retenue."]],
                "chart":{"type":"lines","series":[{"name":"Fournisseur A","x":xs,"y":[p['fixed_a']+p['unit_a']*x for x in xs]},{"name":"Fournisseur B","x":xs,"y":[p['fixed_b']+p['unit_b']*x for x in xs]}],"marker":{"x":q,"y":min(ca,cb)}},
                "decision":f"Choisir le fournisseur {winner}","explanation":f"Pour {q:.0f} unités, l'offre {winner} minimise le coût total. Le choix peut changer lorsque le volume franchit le seuil d'indifférence.","alert":False}
    if case_id == "break_even":
        margin=p["price"]-p["unit_cost"]; threshold=p["fixed"]/margin if margin>0 else math.inf; forecast=p["forecast"]
        profit=margin*forecast-p["fixed"]; safety=forecast-threshold if math.isfinite(threshold) else -math.inf
        xs=[p["capacity"]*i/50 for i in range(51)]
        return {"metrics":[["Marge unitaire",_fmt(margin),"€"],["Seuil de rentabilité",math.ceil(threshold) if math.isfinite(threshold) else "Impossible","unités"],["Bénéfice prévisionnel",_fmt(profit),"€"],["Marge de sécurité",_fmt(safety) if math.isfinite(safety) else "—","unités"]],
                "steps":[
                    ["1. Marge sur une unité",f"{p['price']:.0f} − {p['unit_cost']:.0f} = {margin:.0f} €","Chaque vente contribue de ce montant à la couverture des coûts fixes."],
                    ["2. Point mort",(f"{p['fixed']:,.0f} ÷ {margin:.0f} = {threshold:.2f}, soit {math.ceil(threshold)} unités" if math.isfinite(threshold) else "Prix ≤ coût unitaire : aucun seuil rentable."),"On arrondit à l'unité supérieure pour couvrir tous les coûts."],
                    ["3. Bénéfice prévu",f"{margin:.0f} × {forecast:.0f} − {p['fixed']:,.0f} = {profit:,.0f} €","Le bénéfice est la marge totale diminuée des coûts fixes."],
                    ["4. Marge de sécurité",(f"{forecast:.0f} − {threshold:.2f} = {safety:.2f} unités" if math.isfinite(threshold) else "Non calculable"),"Elle mesure la distance entre les ventes prévues et le point mort."]],
                "chart":{"type":"lines","series":[{"name":"Recettes","x":xs,"y":[p['price']*x for x in xs]},{"name":"Coûts","x":xs,"y":[p['fixed']+p['unit_cost']*x for x in xs]}],"marker":{"x":forecast,"y":p['price']*forecast}},
                "decision":("Projet rentable au volume prévu" if profit>0 else "Projet non rentable au volume prévu"),"explanation":f"La prévision de {forecast:.0f} ventes est {'au-dessus' if safety>=0 else 'en dessous'} du point mort de {math.ceil(threshold) if math.isfinite(threshold) else '—'} unités.","alert":profit<=0}
    if case_id == "marginal":
        q=p["quantity"]; exact_c=p["a"]+p["b"]*((q+1)**2-q**2); mc=p["a"]+2*p["b"]*q
        mr=p["price"]-2*p["d"]*q; mp=mr-mc; exact_p=(p["price"]*(q+1)-p["d"]*(q+1)**2-p["fixed"]-p["a"]*(q+1)-p["b"]*(q+1)**2)-(p["price"]*q-p["d"]*q*q-p["fixed"]-p["a"]*q-p["b"]*q*q)
        xs=[max(0,q-60)+i*3 for i in range(41)]
        return {"metrics":[["Coût marginal",_fmt(mc),"€/unité"],["Coût exact de l'unité suivante",_fmt(exact_c),"€"],["Recette marginale",_fmt(mr),"€/unité"],["Profit marginal",_fmt(mp),"€/unité"]],
                "steps":[
                    ["1. Coût marginal",f"C′({q:.0f}) = {p['a']:.0f} + 2 × {p['b']:.3f} × {q:.0f} = {mc:.2f} €","La dérivée approche le coût de l'unité suivante."],
                    ["2. Vérification exacte",f"C({q+1:.0f}) − C({q:.0f}) = {exact_c:.2f} €","La valeur exacte est très proche de l'approximation marginale."],
                    ["3. Recette marginale",f"R′({q:.0f}) = {p['price']:.0f} − 2 × {p['d']:.3f} × {q:.0f} = {mr:.2f} €","Elle mesure ce que rapporte approximativement une unité supplémentaire."],
                    ["4. Profit marginal",f"{mr:.2f} − {mc:.2f} = {mp:.2f} €","Si le résultat est positif, une légère hausse de production améliore encore le profit."]],
                "chart":{"type":"lines","series":[{"name":"Recette marginale","x":xs,"y":[p['price']-2*p['d']*x for x in xs]},{"name":"Coût marginal","x":xs,"y":[p['a']+2*p['b']*x for x in xs]}],"marker":{"x":q,"y":mc}},
                "decision":("Augmenter légèrement la production" if mp>0 else "Ne pas augmenter la production"),"explanation":f"Autour de {q:.0f} unités, une unité supplémentaire modifie le profit d'environ {_fmt(mp)} €. La variation exacte est de {_fmt(exact_p)} €.","alert":mp<0}
    if case_id == "optimization":
        raw=p["b"]/(2*p["a"]); q=max(0,min(p["capacity"],raw)); profit=-p["a"]*q*q+p["b"]*q-p["fixed"]
        xs=[p["capacity"]*i/50 for i in range(51)]; ys=[-p["a"]*x*x+p["b"]*x-p["fixed"] for x in xs]
        constrained=raw>p["capacity"]
        return {"metrics":[["Point critique",_fmt(raw),"unités"],["Quantité réalisable",_fmt(q),"unités"],["Profit maximal réalisable",_fmt(profit),"€"],["Capacité",p["capacity"],"unités"]],
                "steps":[
                    ["1. Dérivée du profit",f"P′(q) = −{2*p['a']:.2f}q + {p['b']:.0f}","L'optimum éventuel se trouve lorsque la dérivée est nulle."],
                    ["2. Point critique",f"q* = {p['b']:.0f} ÷ (2 × {p['a']:.2f}) = {raw:.2f} unités","Avant ce point le profit augmente; après ce point il diminue."],
                    ["3. Contrainte de capacité",f"Quantité retenue = min({raw:.2f}, {p['capacity']:.0f}) = {q:.2f}","Une solution mathématique doit rester réalisable."],
                    ["4. Profit associé",f"−{p['a']:.2f} × {q:.2f}² + {p['b']:.0f} × {q:.2f} − {p['fixed']:,.0f} = {profit:,.2f} €","On remplace q par la quantité réalisable dans la fonction de profit."]],
                "chart":{"type":"lines","series":[{"name":"Profit","x":xs,"y":ys}],"marker":{"x":q,"y":profit}},"decision":("Produire à la capacité maximale" if constrained else f"Produire environ {q:.0f} unités"),"explanation":("L'optimum théorique dépasse la capacité : la meilleure décision réalisable se situe à la borne." if constrained else "La dérivée passe de positive à négative au point critique : le profit y atteint son maximum."),"alert":profit<0}
    if case_id == "launch":
        budget=p["budget"]; marketing=budget*p["marketing_share"]/100; demand=p["base_demand"]*(1+p["growth"]/100)+p["ad_effect"]*math.sqrt(max(marketing,0)/1000)
        ca=p["fixed_a"]+p["unit_a"]*demand; cb=p["fixed_b"]+p["unit_b"]*demand; supplier="A" if ca<cb else "B"; supply=min(ca,cb)
        unit_supply=(p["unit_a"] if supplier=="A" else p["unit_b"]); launch_fixed=budget-marketing+(p["fixed_a"] if supplier=="A" else p["fixed_b"])
        margin=p["price"]-unit_supply; be=launch_fixed/margin if margin>0 else math.inf; profit=margin*demand-launch_fixed
        scenarios=[-.15,0,.15]; labels=["Prudent","Central","Dynamique"]; values=[margin*demand*(1+s)-launch_fixed for s in scenarios]
        return {"metrics":[["Demande prévue",_fmt(demand),"unités"],["Fournisseur retenu",supplier,""],["Point mort",math.ceil(be) if math.isfinite(be) else "Impossible","unités"],["Profit prévisionnel",_fmt(profit),"€"]],
                "steps":[
                    ["1. Budget marketing",f"{budget:,.0f} × {p['marketing_share']:.0f} % = {marketing:,.0f} €","On réserve une part du budget au soutien commercial."],
                    ["2. Demande prévue",f"{p['base_demand']:.0f} × (1 + {p['growth']:.0f}/100) + effet publicité = {demand:.2f} unités","La demande de base est ajustée par la croissance et l'effort publicitaire."],
                    ["3. Choix fournisseur",f"Coût A = {ca:,.2f} € ; coût B = {cb:,.2f} € → fournisseur {supplier}","On retient l'offre la moins chère au volume attendu."],
                    ["4. Rentabilité",(f"Point mort = {launch_fixed:,.2f} ÷ {margin:.2f} = {be:.2f} unités ; profit = {profit:,.2f} €" if math.isfinite(be) else "La marge unitaire est négative."),"La décision finale combine le volume attendu, le point mort et le profit."]],
                "chart":{"type":"bars","labels":labels,"values":values},"decision":("Lancer sous les hypothèses retenues" if profit>0 and demand>=be else "Revoir le projet avant lancement"),"explanation":f"Le scénario central prévoit {demand:.0f} unités pour un point mort de {math.ceil(be) if math.isfinite(be) else '—'}. Le fournisseur {supplier} minimise le coût d'approvisionnement à ce volume.","alert":profit<=0}
    raise ValueError("Cas inconnu")

def solve_json(case_id, params_json):
    return json.dumps(solve(case_id, json.loads(params_json)), ensure_ascii=False)
