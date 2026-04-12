from textcomps import template_builder
t = "Coins: {coins[].@s}, Credits: {credits[].@s}"
r = template_builder(t)

print(t)
print()
print(r)
print()
print(r.to_dictionary())