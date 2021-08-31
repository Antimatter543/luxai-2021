For tournament mode:

```

lux-ai-2021 --rankSystem="trueskill" --tournament solidbot1.py devastate.py solidbot2.py --storeReplay=false --storeLogs=false

lux-ai-2021 --rankSystem="trueskill" --tournament variant.py devastate.py --storeReplay=false --storeLogs=false


lux-ai-2021 --rankSystem="trueskill" --tournament planetarydevastation.py devastate.py --storeReplay=false --storeLogs=false

```


Let's just say agent 1 will be our best bot. Whoever has the highest score becomes agent1 (i.e main.py).

main2.py is our developing bot, which will hopefully ascend beyond main1.

If you want to test between 2 small variations of a given agent, copy paste its code over to 'variant.py' (agent) and then make the change.

Then, run the variant.py (main.py) vs your original agent and see what happens.

```
lux-ai-2021 --rankSystem="trueskill" --tournament variant.py  devastate.py --storeReplay=false --storeLogs=false
``

lux-ai-2021 devastate.py variant.py